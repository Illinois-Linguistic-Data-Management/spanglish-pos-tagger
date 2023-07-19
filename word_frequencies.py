import re
from utils.util import get_cha_files_in_dir
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from lexical_diversity import lex_div as ld


def get_data_from_file(cha_file, data, participants, texts):
    participant_id = None
    pos_line = ""
    par_line = ""
    line_type = ""
    if "eng" not in texts:
        texts["eng"] = {}
    if "spa" not in texts:
        texts["spa"] = {}
    for participant in participants:
        if participant not in texts["eng"]:
            texts["eng"][participant] = ""
        if participant not in texts["spa"]:
            texts["spa"][participant] = ""
    
    def is_code_switched(participant_line: str, word: str):
        '''
        We can use the annotations from the original annotation layer marked *PAR:
        to tell if a word from the POS tagged layer is code switched. The annotations are:
            a) either [-eng] or [-spa] at the beginning of the line
            b) @s appended to the end of the word
        '''
        return '[- eng]' in participant_line or '[- spa]' in participant_line or f'{word}@s' in participant_line
    def enhanced_token_w_lang(participant_line, token, main_lang):
        '''
        Returns the input token with the language appended
        Eg: a.DET -> a.DET.eng
        '''
        secondary_lang = "spa" if main_lang == "eng" else "eng"
        if is_code_switched(participant_line, token.split(".")[0]):
            return f'{token}.{secondary_lang}'
        else:
            return f'{token}.{main_lang}'
        
    for line in cha_file:
        if re.search(r'@Participants:', line):
            participant_id = re.search(r'[0-9]+', line).group(0) # then assume this will always come before the actual words
            if participant_id not in participants:
                participants.append(participant_id)
            texts[main_lang][participant_id] = ""

        if re.search(r'Languages:', line):
            langs = line.split(":")[-1].strip("\n").strip("\t").strip(" ").split(",")
            main_lang = langs[0].strip(" ")

        if "%pos:" in line:
            line_type = "%pos"
            pos_line = line
            tokens = [x.strip("\n") for x in line.split(" ") if x.strip("\n").replace('.', '').isalpha()]
            for token in tokens:
                token = enhanced_token_w_lang(par_line, token, main_lang)
                if token.split(".")[1] in ['SYM', 'X', 'PUNCT'] or token.split(".")[0] in ['xxx']:
                    continue # ignore non word tokens
                if token not in data:
                    data[token] = {participant_id: 1}
                elif participant_id not in data[token]:
                    data[token][participant_id] = 1
                else:
                    data[token][participant_id] += 1
                texts[main_lang][participant_id] += f'{token} '
        elif "*PAR:" in line:
            line_type = "*PAR"
            if re.search(r'[0-9]_[0-9]', line):
                    par_line = line
            else:
                par_line = line
                while not re.search(r'[0-9]_[0-9]', par_line): # CLAN forces a new line on long utterances, the timestamp is at the end of all utterances
                    par_line += cha_file.readline()

def get_data(path, data, participants, texts):
    for file in get_cha_files_in_dir(path):
        with open (file, 'r') as cha_file:
            get_data_from_file(cha_file, data, participants, texts)

def get_data_english(path, data, participants, texts):
    for file in get_cha_files_in_dir(path):
        participant_id = None
        with open (file, 'r') as cha_file:
            for line in cha_file:
                if re.search(r'@Participants:', line):
                    participant_id = re.search(r'[0-9]+', line).group(0) # then assume this will always come before the actual words
        if (int(participant_id) >= 300 and int(participant_id) < 500) or "eng" in file.split("/")[-1]:
            with open (file, 'r') as cha_filee:
                get_data_from_file(cha_filee, data, participants, texts)

def get_data_spanish(path, data, participants, texts):
    for file in get_cha_files_in_dir(path):
        participant_id = None
        with open (file, 'r') as cha_file:
            for line in cha_file:
                if re.search(r'@Participants:', line):
                    participant_id = re.search(r'[0-9]+', line).group(0) # then assume this will always come before the actual words
        if int(participant_id) >= 600 or "spa" in file.split("/")[-1]:
            with open (file, 'r') as cha_filee:
                get_data_from_file(cha_filee, data, participants, texts)

def calc_mtld(text, lang=None):
    if lang:
        text = [x.split(".")[0] for x in text.split(" ") if x.split(".")[0] != "" and x.split(".")[2] == lang]
    else:
        text = [x.split(".")[0] for x in text.split(" ") if x.split(".")[0] != ""]
    return round(ld.mtld(text),2)

def calc_mattr(text, lang=None):
    if lang:
        text = [x.split(".")[0] for x in text.split(" ") if x.split(".")[0] != "" and x.split(".")[2] == lang]
    else:
        text = [x.split(".")[0] for x in text.split(" ") if x.split(".")[0] != ""]
    return round(ld.mattr(text),2)

def write_frame(output_path, data, participants):
    with open(output_path, 'w') as outFile:
            # write header
            outFile.write('word,category,language')
            for participant_id in participants:
                outFile.write(f',{participant_id}')
            outFile.write('\n')
            # write the rest
            for token in data.keys():
                word = token.split(".")[0]
                category = token.split(".")[1]
                language = token.split(".")[2]
                word_type = "content" if category in ['NOUN', 'VERB', 'ADJ', 'ADV'] else "functional"
                outFile.write(f'{word},{category},{language}')
                for participant_id in participants:
                    if participant_id in data[token]:
                        outFile.write(f',{data[token][participant_id]}')
                    else:
                        outFile.write(',0')
                outFile.write('\n')

def write_frame_v2(output_path, data, participants, texts):
    with open(output_path, 'w') as outFile:
        # first write words row 
        outFile.write("word,")
        for token in data.keys():
            word = token.split(".")[0]
            outFile.write(f'{word},')
        # then write secondary table labels
        outFile.write('total_tokens,total_types,type_token_ratio')
        outFile.write(',content_tokens,content_types,content_ttr')
        outFile.write(',functional_tokens,functional_types,functional_ttr')
        outFile.write(',english_tokens,english_types,english_ttr')
        outFile.write(',english_content_tokens,english_content_types,english_content_ttr')
        outFile.write(',english_functional_tokens,english_functional_types,english_functional_ttr')
        outFile.write(',spanish_tokens,spanish_types,spanish_ttr')
        outFile.write(',spanish_content_tokens,spanish_content_types,spanish_content_ttr')
        outFile.write(',spanish_functional_tokens,spanish_functional_types,spanish_functional_ttr')
        outFile.write(',target_lang_mattr,target_lang_mtld')
        
        # now write lexical categories row
        outFile.write("\nlexical_category,")
        for token in data.keys():
            category = token.split(".")[1]
            outFile.write(f'{category},')
        # now write word types (lexical/functional)
        outFile.write("\nword_type,")
        for token in data.keys():
            category = token.split(".")[1]
            word_type = "content" if category in ['NOUN', 'VERB', 'ADJ', 'ADV'] else "functional"
            outFile.write(f'{word_type},')
        outFile.write("\nlanguage,")
        # now write language for each word
        for token in data.keys():
            lang = token.split(".")[2].upper()
            outFile.write(f'{lang},')
        # now write counts for each
        for participant_id in participants:
            outFile.write(f'\n{participant_id},')
            total_tokens = 0
            total_types = 0
            content_tokens = 0
            content_types = 0
            functional_tokens = 0
            functional_types = 0

            english_tokens = 0
            english_types = 0
            english_content_tokens = 0
            english_content_types = 0
            english_functional_tokens = 0
            english_functional_types = 0

            spanish_tokens = 0
            spanish_types = 0
            spanish_content_tokens = 0
            spanish_content_types = 0
            spanish_functional_tokens = 0
            spanish_functional_types = 0
            
            for token in data.keys():
                word_type = "content" if token.split(".")[1] in ['NOUN', 'VERB', 'ADJ', 'ADV'] else "functional"
                word_language = token.split(".")[2]
                if participant_id in data[token]:
                    outFile.write(f'{data[token][participant_id]},')
                    total_tokens += data[token][participant_id]
                    total_types += 1
                    if word_type == "content":
                        content_tokens += data[token][participant_id]
                        content_types += 1
                    else:
                        functional_tokens += data[token][participant_id]
                        functional_types += 1
                    if word_language == "eng":
                        english_tokens += data[token][participant_id]
                        english_types += 1
                        if word_type == "content":
                            english_content_tokens += data[token][participant_id]
                            english_content_types += 1
                        else:
                            english_functional_tokens += data[token][participant_id]
                            english_functional_types += 1
                    elif word_language == "spa":
                        spanish_tokens += data[token][participant_id]
                        spanish_types += 1
                        if word_type == "content":
                            spanish_content_tokens += data[token][participant_id]
                            spanish_content_types += 1
                        else:
                            spanish_functional_tokens += data[token][participant_id]
                            spanish_functional_types += 1
                else:
                    outFile.write('0,')
            if english_tokens > spanish_tokens: # simple heuristic
                main_lang = "eng"
            else:
                main_lang = "spa"

            # write total word count
            def calc_ratio(numerator, denominator):
                if denominator == 0:
                    return 0.0
                else:
                    return round(float(numerator)/float(denominator),2)
            outFile.write(f'{total_tokens},{total_types},{calc_ratio(total_types, total_tokens)}')
            outFile.write(f',{content_tokens},{content_types},{calc_ratio(content_types, content_tokens)}')
            outFile.write(f',{functional_tokens},{functional_types},{calc_ratio(functional_types, functional_tokens)}')
            outFile.write(f',{english_tokens},{english_types},{calc_ratio(english_types, english_tokens)}')
            outFile.write(f',{english_content_tokens},{english_content_types},{calc_ratio(english_content_types, english_content_tokens)}')
            outFile.write(f',{english_functional_tokens},{english_functional_types},{calc_ratio(english_functional_types, english_functional_tokens)}')
            outFile.write(f',{spanish_tokens},{spanish_types},{calc_ratio(spanish_types, spanish_tokens)}')
            outFile.write(f',{spanish_content_tokens},{spanish_content_types},{calc_ratio(spanish_content_types, spanish_content_tokens)}')
            outFile.write(f',{spanish_functional_tokens},{spanish_functional_types},{calc_ratio(spanish_functional_types, spanish_functional_tokens)}')
            outFile.write(f',{calc_mattr(texts[main_lang][participant_id], main_lang)},{calc_mtld(texts[main_lang][participant_id], main_lang)}')

def gen_word_cloud(data):
    wc = WordCloud(background_color="white", max_words=1000)
    wc.generate_from_frequencies(data)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()

def gen_all_english_frame():
    data = {}
    participants = []
    texts = {}
    get_data_english('transcriptions\\Tagged Transcriptions (group 100)', data, participants, texts)
    get_data_english('transcriptions\\Tagged Transcriptions (group 200)', data, participants, texts)
    get_data_english('transcriptions\\Tagged Transcriptions (group 300)', data, participants, texts)
    get_data_english('transcriptions\\Tagged Transcriptions (group 400)', data, participants, texts)
    get_data_english('transcriptions\\Tagged Transcriptions (group 500)', data, participants, texts)
    write_frame_v2('word_counts_all_english.csv', data, participants, texts)

def gen_all_spanish_frame():
    data = {}
    participants = []
    texts = {}
    get_data_spanish('transcriptions\\Tagged Transcriptions (group 100)', data, participants, texts)
    get_data_spanish('transcriptions\\Tagged Transcriptions (group 200)', data, participants, texts)
    get_data_spanish('transcriptions\\Tagged Transcriptions (group 500)', data, participants, texts)
    get_data_spanish('transcriptions\\Tagged Transcriptions (group 600)', data, participants, texts)
    get_data_spanish('transcriptions\\Tagged Transcriptions (group 700)', data, participants, texts)
    write_frame_v2('word_counts_all_spanish.csv', data, participants, texts)

def gen_all_frame():
    data = {}
    participants = []
    get_data('transcriptions\\Tagged Transcriptions (group 100)', data, participants)
    get_data('transcriptions\\Tagged Transcriptions (group 200)', data, participants)
    get_data('transcriptions\\Tagged Transcriptions (group 300)', data, participants)
    get_data('transcriptions\\Tagged Transcriptions (group 400)', data, participants)
    get_data('transcriptions\\Tagged Transcriptions (group 500)', data, participants)
    get_data('transcriptions\\Tagged Transcriptions (group 600)', data, participants)
    get_data('transcriptions\\Tagged Transcriptions (group 700)', data, participants)
    write_frame('word_counts_all.csv', data, participants)

def gen_group_frame(group):
    path = f'transcriptions\\Tagged Transcriptions (group {str(group)})'
    output_path = f'word_counts_{group}.csv'
    data = {}
    participants = []
    texts = {}
    get_data(path, data, participants, texts)          
    write_frame_v2(output_path, data, participants, texts)

def gen_group_frames():
    gen_group_frame(100)
    gen_group_frame(200)
    gen_group_frame(300)
    gen_group_frame(400)
    gen_group_frame(500)
    gen_group_frame(600)
    gen_group_frame(700)
                
def convert_to_wc_freqs(data):
    dats = {}
    for token in data:
        for participant in data[token]:
            word = token.split(".")[0]
            if word in dats:
                dats[word] += data[token][participant]
            else:
                dats[word] = data[token][participant]
    return dats

def gen_spanish_cloud(group: int):
    data = {}
    get_data_spanish(f'transcriptions\\Tagged Transcriptions (group {group})', data, [], {})
    gen_word_cloud(convert_to_wc_freqs(data))

def gen_english_cloud(group: int):
    data = {}
    get_data_english(f'transcriptions\\Tagged Transcriptions (group {group})', data, [], {})
    gen_word_cloud(convert_to_wc_freqs(data))

def gen_cloud(group: int):
    data = {}
    get_data(f'transcriptions\\Tagged Transcriptions (group {group})', data, [], {})
    gen_word_cloud(convert_to_wc_freqs(data))

def gen_combined_spanish_cloud():
    data = {}
    get_data_spanish(f'transcriptions\\Tagged Transcriptions (group 100)', data, [], {})
    get_data_spanish(f'transcriptions\\Tagged Transcriptions (group 200)', data, [], {})
    get_data_spanish(f'transcriptions\\Tagged Transcriptions (group 500)', data, [], {})
    get_data_spanish(f'transcriptions\\Tagged Transcriptions (group 600)', data, [], {})
    get_data_spanish(f'transcriptions\\Tagged Transcriptions (group 700)', data, [], {})
    gen_word_cloud(convert_to_wc_freqs(data))

def gen_combined_english_cloud():
    data = {}
    get_data_english(f'transcriptions\\Tagged Transcriptions (group 100)', data, [], {})
    get_data_english(f'transcriptions\\Tagged Transcriptions (group 200)', data, [], {})
    get_data_english(f'transcriptions\\Tagged Transcriptions (group 300)', data, [], {})
    get_data_english(f'transcriptions\\Tagged Transcriptions (group 400)', data, [], {})
    get_data_english(f'transcriptions\\Tagged Transcriptions (group 500)', data, [], {})
    gen_word_cloud(convert_to_wc_freqs(data))

def gen_all_spanish_clouds():
    gen_spanish_cloud(100)
    gen_spanish_cloud(200)
    gen_spanish_cloud(500)
    gen_spanish_cloud(600)
    gen_spanish_cloud(700)
    gen_combined_spanish_cloud()

def gen_all_english_clouds():
    gen_english_cloud(100)
    gen_english_cloud(200)
    gen_english_cloud(300)
    gen_english_cloud(400)
    gen_english_cloud(500)
    gen_combined_english_cloud()

if __name__ == "__main__":
    #gen_group_frames()
    gen_all_english_frame()
    gen_all_spanish_frame()
    gen_all_english_clouds()
    gen_all_spanish_clouds()