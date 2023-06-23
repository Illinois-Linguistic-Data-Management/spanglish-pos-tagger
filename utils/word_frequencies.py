import re
from util import parse_utterances_from_cha, preprocess_sentence_from_cha

class WordFrequenciesCounter:

    def detect_langs(self):
        with open(self.filename, 'r') as f:
            for line in f:
                if re.search(r'Languages:', line):
                    langs = line.split(":")[-1].strip("\n").strip("\t").strip(" ").split(",")
                    self.main_language = langs[0]
                    self.secondary_language = langs[1] if len(langs) > 1 else None

    def __init__(self, cha_file_path: str):
        self.filename = cha_file_path
        self.detect_langs()
        

if __name__ == '__main__':
    path = '/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Tagged Transcriptions (group 100)/107_spanish.cha'
    counter = WordFrequenciesCounter(path)
    print(counter.main_language, counter.secondary_language)

    utts_w_comments = parse_utterances_from_cha(path)
    frquencies = {}
    for x in utts_w_comments:
        if x[0] != "@":
            print(x)
            sent = preprocess_sentence_from_cha(x)
            sent = sent.replace('\n', ' ')
            sent = sent.replace('\t', ' ')
            toks_split = sent.split(" ")
            for tok in sent.split(" "):
                if tok not in ['xxx', '']:    
                    if tok not in frquencies:
                        frquencies[tok] = 1
                    else:
                        frquencies[tok] += 1
    print(frquencies)