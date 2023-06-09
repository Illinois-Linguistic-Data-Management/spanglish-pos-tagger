import re, os
from utils.util import parse_utterances_from_cha, get_cha_files_in_dir

def extract_disfluencies_from_utterance(utterance: str):
    disfluencies = []
    if utterance[0] == "@":
        return disfluencies, utterance # skip comments
    
    # first get errors
    for error in extract_errors(utterance):
        disfluencies.append(error)

    utterance = re.sub(r'[\t|\n]', ' ', utterance) # turn tabs and new lines into spaces, we will split by spaces later on
    utterance = re.sub(r'(\([.]+\)\s?)', '', utterance) # remove dots inside parentesis (...)
    utterance = re.sub(r'<(.*?)>\s*\[e\]', '', utterance) # remove excluded [e] content

    # remove parentheses that fill in incomplete words since the model wasn't trained on this formatting
    while parentheses := re.search("\(.+?\)", utterance):
        utterance = utterance[0:parentheses.start()] + utterance[parentheses.start()+1:parentheses.end()-1] + utterance[parentheses.end():]

    # find and then remove disfluencies marked with <> [/] or <> [//] or <> [///]
    inside_disfluency = False
    for part in utterance.split():
        if part.startswith('<'):
            # Remove '<' and '>' and add the part to disfluencies
            disfluencies.append(part[1:].replace('>', ''))
            inside_disfluency = True
        elif inside_disfluency:
            if re.search(r'\[/{1,3}\]$', part):
                # Check if there is a last disfluency
                if disfluencies:
                    # Remove the tag and '>', then append the part to the last disfluency
                    disfluencies[-1] += ' ' + re.sub(r'\[/{1,3}\]$', '', part).replace('>', '')
                inside_disfluency = False
            else:
                # If we are inside a disfluency and there is no closing tag,
                # we append the part to the last disfluency
                disfluencies[-1] += ' ' + part.replace('>', '')

    if re.search(r'\b(\w+)\b\s*\[/\]', utterance):
        for disfluency in [m for m in re.search(r'\b(\w+)\b\s*\[/\]', utterance).groups()]:
            disfluencies.append(disfluency)
        utterance = re.sub(r'\b(\w+)\b\s*\[/\]', '', utterance)
    if re.search(r'\b(\w+)\b\s*\[//\]', utterance):
        for disfluency in [m for m in re.search(r'\b(\w+)\b\s*\[//\]', utterance).groups()]:
            disfluencies.append(disfluency)
        utterance = re.sub(r'\b(\w+)\b\s*\[//\]', '', utterance)
    if re.search(r'\b(\w+)\b\s*\[///\]', utterance):
        for disfluency in [m for m in re.search(r'\b(\w+)\b\s*\[///\]', utterance).groups()]:
            disfluencies.append(disfluency)
        utterance = re.sub(r'\b(\w+)\b\s*\[///\]', '', utterance)

    # now look for other disfluency markers eg um/uh, these are coded with a &- prefix
    for tok in utterance.split(" "):
        if tok == "*PAR:":
            continue
        if re.match(r'&-', tok):
            disfluencies.append(tok[2:]) # remove the &- prefix before appending to list
            utterance = re.sub(tok, '', utterance)
    return disfluencies, utterance


def extract_disfluencies_from_cha_file(filename):
    utts = parse_utterances_from_cha(filename)
    disfluencies = []
    for utt in utts:
        utterance_disfluencies, _ = extract_disfluencies_from_utterance(utt)
        for disfluency in utterance_disfluencies:
            disfluencies.append(disfluency)
    return disfluencies

def filter_disfluencies_from_utterance(utterance: str):
    _, utterance_without_disfluencies = extract_disfluencies_from_utterance(utterance)
    return utterance_without_disfluencies

def get_participant_speaking_time_total(utterances: list):
    total_milliseconds_speaking = 0
    for utterance in utterances:
        timestamp = re.search(r'[0-9]+_[0-9]+', utterance)
        if timestamp and "*PAR:" in utterance:
            timestamp = timestamp.group(0) # extract timestamp str from regex, assume only one timestamp per utterance
            start_stamp, end_stamp = timestamp.split("_")
            utterance_duration_ms = int(end_stamp) - int(start_stamp)
            total_milliseconds_speaking += utterance_duration_ms
    return total_milliseconds_speaking

def clean_token(token):
    return re.sub(r'[.|?|!|,| |\t|\n|&-]', '', token)

def extract_errors(text):
    # pattern to match is '[: some_word][*]'
    pattern = r'\[:\s*(\w+)\s*\]\[\*\]'
    
    # find all matches in text
    matches = re.findall(pattern, text)
    
    # return list of matches
    return matches

def convert_milliseconds_to_minutes(milliseconds: int):
    return milliseconds / 60000

class CorpusAnalysisTool:
    def __init__(self, dir_path, output_path):
        files = get_cha_files_in_dir(dir_path)
        with open(output_path, 'w') as outFile:
        # write headers
            outFile.write("language,participant_id,words,minutes,wpm,types,tokens,ttr,english_types,english_tokens,english_ttr,spanish_types,spanish_tokens,spanish_ttr,disfluencies,fluency_score\n")
            i = 0
            for file in files:
                try:
                    i += 1
                    if i > 10:
                        break
                    outFile.write(LexicalAnalysisTool(file).to_csv_row())
                    outFile.write("\n")
                except:
                    print("Error analyzing", file)

class LexicalAnalysisTool:

    def detect_langs(self):
        with open(self.filename, 'r') as f:
            for line in f:
                if re.search(r'Languages:', line):
                    langs = line.split(":")[-1].strip("\n").strip("\t").strip(" ").split(",")
                    self.main_language = langs[0]
                    self.secondary_language = langs[1] if len(langs) > 1 else None

    def get_participant_id(self):
        with open(self.filename, 'r') as f:
            for line in f:
                if re.search(r'@Participants:', line):
                    self.participant_id = re.search(r'[0-9]+', line).group(0)

    def __init__(self, filename: str):
        self.filename = filename
        self.detect_langs()
        self.get_participant_id()

        # counts over both languages
        self.words_count = 0 # stores the total number of words (regular tokens + disfluency tokens) seen in the transcript/document
        self.types_tokens = {} # key is the type and the value is the number of tokens of this type seen in the transcript/document
        self.disfluencies = [] # a list of examples of disfluencies extracted from this .cha file

        self.lang_specific_counts = {
            "eng": {
                "words_count" : 0,
                "types_tokens" : {}
            },
            "spa": {
                "words_count" : 0,
                "types_tokens" : {}
            }
        }

        self.disfluencies_count = self.count_disfluency_words()
        self.speaking_time = get_participant_speaking_time_total(parse_utterances_from_cha(self.filename)) # number of milliseconds the participant was speaking for

        self.count_fluent_words()
        self.types_count = len(self.types_tokens.keys())
        self.tokens_count = self._count_tokens()
  
        self.english_types_count = len(self.lang_specific_counts["eng"]["types_tokens"].keys())
        self.spanish_types_count = len(self.lang_specific_counts["spa"]["types_tokens"].keys())

        self.english_tokens_count = 0
        for token in self.lang_specific_counts["eng"]["types_tokens"].keys():
            self.english_tokens_count += self.lang_specific_counts["eng"]["types_tokens"][token]
        self.spanish_tokens_count = 0
        for token in self.lang_specific_counts["spa"]["types_tokens"].keys():
            self.spanish_tokens_count += self.lang_specific_counts["spa"]["types_tokens"][token]

    def types_tokens_to_str(self, dic: dict):
        for k in dic:
            print(k, dic[k])

    def calc_ratio(self, numerator, denominator):
        if denominator > 0:
            return round(numerator/denominator,3)
        else:
            return 0

    def to_csv_row(self):
        return f'{self.main_language},{self.participant_id},{self.words_count},{round(convert_milliseconds_to_minutes(self.speaking_time), 3)},{round(self.words_count / convert_milliseconds_to_minutes(self.speaking_time), 3)},{self.types_count},{self.tokens_count},{self.calc_ratio(self.types_count, self.tokens_count)},{self.english_types_count},{self.english_tokens_count},{self.calc_ratio(self.english_types_count, self.english_tokens_count)},{self.spanish_types_count},{self.spanish_tokens_count},{self.calc_ratio(self.spanish_types_count,self.tokens_count)},{self.disfluencies_count},{self.calc_ratio(self.words_count,self.disfluencies_count)}'
        

    def tally_token(self, token, code_switch=False):
        """
        Add a token to self.types_tokens if it is a new type,
        otherwise increment the token counter
        """
        if "" or None:
            return
        self.words_count += 1
        if token in self.types_tokens:
            self.types_tokens[token] += 1
        else:
            self.types_tokens[token] = 1
        
        if "@s" in token or code_switch: # this tag signals code switching
            token = re.sub(r'@s', '', token) # filter out @s tag
            self.lang_specific_counts[self.secondary_language]["words_count"] +=1
            if token in self.lang_specific_counts[self.secondary_language]["types_tokens"]:
                self.lang_specific_counts[self.secondary_language]["types_tokens"][token] += 1
            else:
                self.lang_specific_counts[self.secondary_language]["types_tokens"][token] = 1
        else:
            self.lang_specific_counts[self.main_language]["words_count"] +=1
            if token in self.lang_specific_counts[self.main_language]["types_tokens"]:
                self.lang_specific_counts[self.main_language]["types_tokens"][token] += 1
            else:
                self.lang_specific_counts[self.main_language]["types_tokens"][token] = 1


    def count_disfluency_words(self):
        self.disfluencies = extract_disfluencies_from_cha_file(self.filename)
        count = 0
        for disfluency_instance in self.disfluencies:
            for token in disfluency_instance.split(" "):
                self.words_count += 1
                self.tally_token(clean_token(token))
                count += 1
        return count
    
    def count_fluent_words(self):
        for utterance in parse_utterances_from_cha(self.filename):
            code_switch = re.search("\[- eng\]", utterance)
            filtered_utterance = filter_disfluencies_from_utterance(utterance)
            if not filtered_utterance or filtered_utterance[0] == "@":
                continue # skip comments
            for token in filtered_utterance.split(" "):
                if clean_token(token).isalpha() or re.sub(r'@s', '', clean_token(token)).isalpha():
                    self.tally_token(clean_token(token), code_switch)

    def _count_tokens(self):
        count = 0
        for type in self.types_tokens:
            count += self.types_tokens[type]
        return count

if __name__ == "__main__":
    CorpusAnalysisTool('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Transcriptions (group 100)', "lexical_counts_100.csv")
    CorpusAnalysisTool('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Transcriptions (group 200)', "lexical_counts_200.csv")
    CorpusAnalysisTool('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Transcriptions (group 300)', "lexical_counts_300.csv")
    CorpusAnalysisTool('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Transcriptions (group 400)', "lexical_counts_400.csv")
    CorpusAnalysisTool('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Transcriptions (group 500)', "lexical_counts_500.csv")
    CorpusAnalysisTool('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Transcriptions (group 600)', "lexical_counts_600.csv")
    CorpusAnalysisTool('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Transcriptions (group 700)', "lexical_counts_700.csv")
