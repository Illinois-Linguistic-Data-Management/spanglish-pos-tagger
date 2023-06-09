from flair.data import Sentence
import re, os

def get_cha_files_in_dir(directory):
    result = []
    for obj_name in os.listdir(directory):
        obj_absolute_path = directory + "/" + obj_name
        is_dir = len(obj_name.split('.')) == 1 # no . in the name means it is a folder not a file
        if is_dir:
            cha_files = get_cha_files_in_dir(obj_absolute_path)
            for cha_file in cha_files:
                result.append(cha_file)
        elif obj_name.split('.')[-1] == "cha": # if file extension is cha
            result.append(obj_absolute_path)
    return result

def preprocess_sentence_from_cha(line):
    if line[0] == "@": # comments start with @ in .cha
        return
    else:
        try:
            original_text = line.split("*PAR:\t")[1] # our project spec denotes each utterance begins with *PAR:
            preprocessed_text = original_text
            #preprocess out excluded material denoted as <> [e]
            preprocessed_text = re.sub(r'<.*?>\s*\[e\]', '', preprocessed_text)
            # preprocess out pause markers
            if re.search("(\([.]+\))", preprocessed_text):
                text = ""
                for part in re.split("(\([.]+\))", original_text):
                    if not re.search("(\([.]+\))", part):
                        text += part[:-1] # [:-1] to strip off extra space from regex splot
                preprocessed_text = text
            # remove parentheses that fill in incomplete words since the model wasn't trained on this formatting
            while parentheses := re.search("\(.+?\)", preprocessed_text):
                preprocessed_text = preprocessed_text[0:parentheses.start()] + preprocessed_text[parentheses.start()+1:parentheses.end()-1] + preprocessed_text[parentheses.end():]
            while parentheses := re.search("\<.+?\>", preprocessed_text):
                preprocessed_text = preprocessed_text[0:parentheses.start()] + preprocessed_text[parentheses.start()+1:parentheses.end()-1] + preprocessed_text[parentheses.end():]
            # preprocess out coded items like &-uh and &=coughs
            preprocessed_text = re.sub(r'&-\w+', '', preprocessed_text)
            preprocessed_text = re.sub(r'&=\w+', '', preprocessed_text)
            # preprocess out anything inside brackets []
            preprocessed_text = re.sub(r'\[[^\]]*\]\s?', '', preprocessed_text)
            # preprocess out @s tags that are sometimes added to code switched text
            preprocessed_text = re.sub(r'@s', '', preprocessed_text)
            # finally, use punctuation to hint removal of timestamps
            preprocessed_text = preprocessed_text.split(".")[0]
            preprocessed_text = preprocessed_text.split("?")[0]
            return preprocessed_text
        except:
            pass # print("failed to parse", line)

def parse_utterances_from_cha(input_filename):
    utterances = []
    with open(input_filename, 'r') as inFile:
        raw_lines = [line for line in inFile]
        i = 0
        while i < len(raw_lines):
            line = raw_lines[i]
            if raw_lines[i][0] == "@":
                utterances.append(line)
                i+=1
            elif "*PAR:" in raw_lines[i][:10]: # each utterance by the participant starts with this marker
                if re.search(r'[0-9]_[0-9]', line):
                    i+=1
                else:
                    while not re.search(r'[0-9]_[0-9]', line): # CLAN forces a new line on long utterances, the timestamp is at the end of all utterances
                        i+=1
                        line += raw_lines[i]
                utterances.append(line)
            else:
                i+=1
    return utterances

def sentence_to_tsv(sentence, path):
    with open (path, 'w', 'utf-16') as stream:
        stream.write("word\t tag\n")
        for token in sentence:
            tag = token.get_label('upos')
            stream.write(token.text)
            stream.write("\t ")
            stream.write(tag.value)
            stream.write('\n')
