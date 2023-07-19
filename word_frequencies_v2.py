import re
import pprint
import json
from utils.util import get_cha_files_in_dir
from lexical_diversity import lex_div as ld
import matplotlib.pyplot as plt

def calc_ratio(numerator: float, denominator: float):
    if denominator == 0:
        return 0
    else:
        return round(float(numerator) / float(denominator),3)

class Corpus:
    def __init__(self, dir_path: str):
        self.dir = dir_path
        self.transcripts = self._parse_transcripts()

    def _parse_transcripts(self):
        result = []
        for file in get_cha_files_in_dir(self.dir):
            if "Tagged Transcriptions" not in file:
                continue
            result.append(Transcript(file))
        return result

class Transcript:
    def __init__(self, cha_file_path):
        self.filename = cha_file_path
        self.participant_id = self.detect_participant_id()
        langs = self.detect_languages()
        self.main_lang = langs[0]
        self.secondary_lang = None if len(langs) < 2 else langs[1]
        self.utterances = self.parse_utterances()
        self.types_tokens = self.count_types_tokens()
        self.duration = 0 if len(self.utterances) < 1 else int(self.utterances[-1]['time_end'])

    def detect_participant_id(self):
        participant_id = None
        with open(self.filename, 'r') as f:
            for line in f:
                if re.search(r'@Participants:', line):
                    participant_id = re.search(r'[0-9]+', line).group(0)
        assert participant_id is not None
        return int(participant_id)

    def detect_languages(self):
        with open(self.filename, 'r') as f:
            secondary_lang = None
            for line in f:
                if re.search(r'Languages:', line):
                    langs = [x.replace(' ', '').replace('\t', '').replace('\n', '') for x in line.split(":")[-1].split(',')]
                    main_lang = langs[0].strip(" ")
                    if len(langs) > 1:
                        secondary_lang = langs[1]
        return [main_lang, secondary_lang]

    def __str__(self):
        return json.dumps({
            'main_language': self.main_lang,
            'secondary_language': self.secondary_lang,
            'utterances': self.utterances,
            'lexical_diversity': self.measure_lexical_diversity(),
            'duration': self.duration
        })

    def measure_lexical_diversity(self):
        def calc_mattr(utterances: list, language:str=None):
            text = []
            for utterance in utterances:
                for token in utterance['tokens']:
                    word = token.split(".")[0]
                    if language:
                        lang_id = token.split(".")[2]
                        if lang_id == language:
                            text.append(word)
                    else:
                        text.append(word)
            return round(ld.mattr(text),3)
        def calc_mtld(utterances: list, language:str=None):
            text = []
            for utterance in utterances:
                for token in utterance['tokens']:
                    word = token.split(".")[0]
                    if language:
                        lang_id = token.split(".")[2]
                        if lang_id == language:
                            text.append(word)
                    else:
                        text.append(word)
            return round(ld.mtld(text),3)
        # get stats for whole narrative, including both languages
        # initialize overall/bilingual type counts
        total_types = 0
        total_content_types = 0 
        total_functional_types = 0
        # initialize english type counts
        english_types = 0
        english_content_types = 0
        english_functional_types = 0
        # initialize spanish type counts
        spanish_types = 0
        spanish_content_types = 0
        spanish_functional_types = 0
        # initialize overall token counts
        total_tokens = 0 
        total_content_tokens = 0 
        total_functional_tokens = 0 
        # initialize english token counts
        english_tokens = 0
        english_content_tokens = 0
        english_functional_tokens = 0 
        # initialize spanish token counts
        spanish_tokens = 0 
        spanish_content_tokens = 0 
        spanish_functional_tokens = 0
        words_seen = []
        for lang in self.types_tokens:
            for token_type in self.types_tokens[lang]:
                word = token_type.split(".")[0]
                part_of_speech = token_type.split(".")[1]
                if word in words_seen:
                    continue # only count homonyms once
                words_seen.append(word)
                token_freq = self.types_tokens[lang][token_type]
                total_types += 1
                total_tokens += token_freq
                if lang == "eng":
                    english_types += 1
                    english_tokens += token_freq
                    if part_of_speech in ['NOUN', 'VERB', 'ADJ', 'ADV']:
                        english_content_types += 1
                        english_content_tokens += token_freq
                        total_content_types += 1
                        total_content_tokens += token_freq
                    else:
                        english_functional_types += 1
                        english_functional_tokens += token_freq
                        total_functional_types += 1
                        total_functional_tokens += token_freq
                elif lang == "spa":
                    spanish_types += 1
                    spanish_tokens += token_freq
                    if part_of_speech in ['NOUN', 'VERB', 'ADJ', 'ADV']:
                        spanish_content_types += 1
                        spanish_content_tokens += token_freq
                        total_content_types += 1
                        total_content_tokens += token_freq
                    else:
                        spanish_functional_types += 1
                        spanish_functional_tokens += token_freq
                        total_functional_types += 1
                        total_functional_tokens += token_freq

        return {
            # overall/bilingual stats
            'total_types': total_types,
            'total_tokens': total_tokens,
            'total_type_token_ratio': calc_ratio(total_types, total_tokens),
            'total_mattr': calc_mattr(self.utterances),
            'total_mtld': calc_mtld(self.utterances),
            'total_content_tokens': total_content_tokens,
            'total_content_types': total_content_types,
            'total_content_ttr': calc_ratio(total_content_types, total_content_tokens),
            'total_functional_tokens': total_functional_tokens,
            'total_functional_types': total_functional_types,
            'total_functional_ttr': calc_ratio(total_functional_types, total_functional_tokens),
            # english only stats
            'english_types': english_types,
            'english_tokens': english_tokens,
            'english_type_token_ratio': calc_ratio(english_types, english_tokens),
            'english_mattr': calc_mattr(self.utterances, "eng"),
            'english_mtld': calc_mtld(self.utterances, "eng"),
            'english_content_tokens': english_content_tokens,
            'english_content_types': english_content_types,
            'english_content_ttr': calc_ratio(english_content_types, english_content_tokens),
            'english_functional_tokens': english_functional_tokens,
            'english_functional_types': english_functional_types,
            'english_functional_ttr': calc_ratio(english_functional_types, english_functional_tokens),
            # spanish only stats
            'spanish_types': spanish_types,
            'spanish_tokens': spanish_tokens,
            'spanish_type_token_ratio': calc_ratio(spanish_types, spanish_tokens),
            'spanish_mattr': calc_mattr(self.utterances, "spa"),
            'spanish_mtld': calc_mtld(self.utterances, "spa"),
            'spanish_content_tokens': spanish_content_tokens,
            'spanish_content_types': spanish_content_types,
            'spanish_content_ttr': calc_ratio(spanish_content_types, spanish_content_tokens),
            'spanish_functional_tokens': spanish_functional_tokens,
            'spanish_functional_types': spanish_functional_types,
            'spanish_functional_ttr': calc_ratio(spanish_functional_types, spanish_functional_tokens),
        }

    def _is_code_switched(self, participant_line: str, word: str):
        '''
        We can use the annotations from the original annotation layer marked *PAR:
        to tell if a word from the POS tagged layer is code switched. The annotations are:
            a) either [-eng] or [-spa] at the beginning of the line
            b) @s appended to the end of the word
        '''
        return '[- eng]' in participant_line or '[- spa]' in participant_line or f'{word}@s' in participant_line
    
    def _enhanced_token_w_lang(self, participant_line, token):
        '''
        Returns the input token with the language appended
        Eg: a.DET -> a.DET.eng
        '''
        if self._is_code_switched(participant_line, token.split(".")[0]):
            return f'{token}.{self.secondary_lang}'
        else:
            return f'{token}.{self.main_lang}'

    def parse_utterances(self):
        with open(self.filename, 'r') as cha_file:
            utterances = []
            timestamp = None
            for line in cha_file:
                if "%pos:" in line:
                    line_type = "%pos"
                    pos_line = line
                    tokens = []
                    tokens_raw = [x.strip("\n") for x in line.split(" ") if x.strip("\n").replace('.', '').isalpha()]
                    for token in tokens_raw:
                        token = self._enhanced_token_w_lang(par_line, token)
                        if token.split(".")[1] in ['SYM', 'X', 'PUNCT'] or token.split(".")[0] in ['xxx']:
                            continue # ignore non word tokens
                        tokens.append(token)
                    utterances.append({'transcription': par_line,'tokens': tokens, 'time_start': timestamp.split("_")[0], 'time_end': timestamp.split("_")[1]})
                elif "*PAR:" in line:
                    line_type = "*PAR"
                    if re.search(r'[0-9]+_[0-9]+', line):
                            par_line = line
                            timestamp = re.search(r'[0-9]+_[0-9]+', line).group(0)
                    else:
                        par_line = line
                        while not re.search(r'[0-9]+_[0-9]+', par_line): # CLAN forces a new line on long utterances, the timestamp is at the end of all utterances
                            par_line += cha_file.readline()
                        timestamp = re.search(r'[0-9]+_[0-9]+', par_line).group(0)
        return utterances

    def count_types_tokens(self):
        types_tokens = {"eng": {}, "spa": {}}
        for utterance in self.utterances:
            for token in utterance['tokens']:
                language_tag = token.split(".")[2]
                token_basic = f'{token.split(".")[0]}.{token.split(".")[1]}'
                if token_basic not in types_tokens[language_tag]:
                    types_tokens[language_tag][token_basic] = 1
                else:
                    types_tokens[language_tag][token_basic] += 1
        return types_tokens

class Visualizer:
    def __init__(self, corpus: Corpus):
        self.corpus = corpus

    # language pie
    def language_pie(self, output_dir:str):
        for transcript in self.corpus.transcripts:
            self.language_pie_transcript(output_dir, transcript)
        for group in [100, 200, 300, 400, 500, 600, 700]:
            self.language_pie_group(output_dir, group)
            self.language_pie_group(output_dir, group, "eng")
            self.language_pie_group(output_dir, group, "spa")

    def language_pie_group(self, output_dir:str, group:int, language:str=None):
        allowed_groups = [100, 200, 300, 400, 500, 600, 700]
        if group not in allowed_groups:
            raise Exception(f'{group} not in {allowed_groups}')
        tokens = []
        for transcript in self.corpus.transcripts:
            id_diff = transcript.participant_id-group
            if id_diff >=0 and id_diff < 100: # eg id 543 with group 500 gives id_diff 43
                if (language == None) or (language == transcript.main_lang):
                    for utterance in transcript.utterances:
                        for token in utterance['tokens']:
                            tokens.append(token)
        if len(tokens) < 1:
            return
        percentages = self._calc_language_percentage(tokens)
        fig, ax = plt.subplots()
        ax.pie([percentages['english'], percentages['spanish']], labels=["English", "Spanish"],autopct='%1.1f%%')
        if language:
            plt.savefig(f'{output_dir}\\{group}_group_{language}.png')
        else:
            plt.savefig(f'{output_dir}\\{group}_group.png')

    def language_pie_transcript(self, output_dir:str, transcript: Transcript):
        """
        Generate pie charts of tokens in English vs tokens in Spanish
        """
        tokens = []
        for utterance in transcript.utterances:
            for token in utterance['tokens']:
                tokens.append(token)
        if len(tokens) < 1:
            return
        percentages = self._calc_language_percentage(tokens)
        fig, ax = plt.subplots()
        ax.pie([percentages['english'], percentages['spanish']], labels=["English", "Spanish"],autopct='%1.1f%%')
        plt.savefig(f'{output_dir}\\{transcript.participant_id}_{transcript.main_lang}')

    def _calc_language_percentage(self, tokens):
            english_tokens = 0
            spanish_tokens = 0
            for token in tokens:
                language = token.split(".")[2]
                if language == "eng":
                    english_tokens += 1
                elif language == "spa":
                    spanish_tokens += 1
                else:
                    raise f'Unexpected language tag:{language}'
            total_tokens = english_tokens + spanish_tokens
            return {
                'english': calc_ratio(english_tokens, total_tokens),
                'spanish': calc_ratio(spanish_tokens, total_tokens)
            }
    
    # lexical diversity boxplots
    def lexical_diveristy_boxplots(self, outdir:str):
        self.mattr_boxplot(f'{outdir}\\mattr_all.png')
        self.mattr_boxplot(f'{outdir}\\mattr_eng.png', "eng")
        self.mattr_boxplot(f'{outdir}\\mattr_spa.png',"spa")
        self.mtld_boxplot(f'{outdir}\\mtld_all.png')
        self.mtld_boxplot(f'{outdir}\\mtld_eng.png', "eng")
        self.mtld_boxplot(f'{outdir}\\mtld_spa.png', "spa")

    def mtld_boxplot(self, outfile:str=None, target_lang:str=None):
        data = [[],[],[],[],[],[],[]]
        for transcript in self.corpus.transcripts:
            if target_lang and transcript.main_lang != target_lang:
                continue
            group_index = int(str(transcript.participant_id)[0])-1
            diversity = transcript.measure_lexical_diversity()
            if "eng" in transcript.main_lang:
                data[group_index].append(diversity['english_mtld'])
            if "spa" in transcript.main_lang:
                data[group_index].append(diversity['spanish_mtld'])
            if data[group_index][-1] == 0:
                print(transcript.participant_id)
        self.render_boxplot(data, outfile)

    def mattr_boxplot(self, outfile:str=None, target_lang:str=None):
        data = [[],[],[],[],[],[],[]]
        for transcript in self.corpus.transcripts:
            if target_lang and transcript.main_lang != target_lang:
                continue
            group_index = int(str(transcript.participant_id)[0])-1
            diversity = transcript.measure_lexical_diversity()
            if "eng" in transcript.main_lang:
                data[group_index].append(diversity['english_mattr'])
            if "spa" in transcript.main_lang:
                data[group_index].append(diversity['spanish_mattr'])
        self.render_boxplot(data, outfile)

    def render_boxplot(self, data, outfile:str=None):
        fig, ax = plt.subplots()
        ax.boxplot(data)
        if outfile:
            plt.savefig(outfile)
        else:
            plt.show()
        
    # type frequency barcharts
    def word_freq_barcharts_all(self, output_dir:str=None):
        self.word_freq_barchart_group(100, f'{output_dir}\\100_group_all.png')
        self.word_freq_barchart_group(100, f'{output_dir}\\100_group_eng.png', "eng")
        self.word_freq_barchart_group(100, f'{output_dir}\\100_group_spa.png', "spa")
        self.word_freq_barchart_group(200, f'{output_dir}\\200_group_all.png')
        self.word_freq_barchart_group(200, f'{output_dir}\\200_group_eng.png', "eng")
        self.word_freq_barchart_group(200, f'{output_dir}\\200_group_spa.png', "spa")
        self.word_freq_barchart_group(300, f'{output_dir}\\300_group_all.png')
        self.word_freq_barchart_group(300, f'{output_dir}\\300_group_eng.png', "eng")
        self.word_freq_barchart_group(300, f'{output_dir}\\300_group_spa.png', "spa")
        self.word_freq_barchart_group(400, f'{output_dir}\\400_group_all.png')
        self.word_freq_barchart_group(400, f'{output_dir}\\400_group_eng.png', "eng")
        self.word_freq_barchart_group(400, f'{output_dir}\\400_group_spa.png', "spa")
        self.word_freq_barchart_group(500, f'{output_dir}\\500_group_all.png')
        self.word_freq_barchart_group(500, f'{output_dir}\\500_group_eng.png', "eng")
        self.word_freq_barchart_group(500, f'{output_dir}\\500_group_spa.png', "spa")
        self.word_freq_barchart_group(600, f'{output_dir}\\600_group_all.png')
        self.word_freq_barchart_group(600, f'{output_dir}\\600_group_eng.png', "eng")
        self.word_freq_barchart_group(600, f'{output_dir}\\600_group_spa.png', "spa")
        self.word_freq_barchart_group(700, f'{output_dir}\\700_group_all.png')
        self.word_freq_barchart_group(700, f'{output_dir}\\700_group_eng.png', "eng")
        self.word_freq_barchart_group(700, f'{output_dir}\\700_group_spa.png', "spa")
    
    def word_freq_barchart_group(self, group:int=None, outfile:str=None, target_lang:str=None):
        data = {}
        for transcript in self.corpus.transcripts:
            if target_lang and transcript.main_lang != target_lang:
                    continue
            for lang in transcript.types_tokens:
                id_diff = None if not group else transcript.participant_id-group
                if (group == None) or (group and id_diff >=0 and id_diff < 100):
                    for token in transcript.types_tokens[lang]:
                        word = token.split(".")[0]
                        if word not in data:
                            data[word] = {lang: transcript.types_tokens[lang][token]}
                        elif word in data and lang not in data[word]:
                            data[word][lang] = transcript.types_tokens[lang][token]
                        else:
                            data[word][lang] += transcript.types_tokens[lang][token]
        x = []
        y = []
        colors = []
        for word in data.keys():
            counts = [0, 0]
            for lang in data[word]:
                if lang == "eng":
                    counts[0] += data[word][lang]
                else:
                    counts[1] += data[word][lang]
            if sum(counts) > 3:
                # first append bigger one so it is drawn in background
                if counts[0] > counts[1]:
                    x.append(word)
                    y.append(counts[0])
                    colors.append((0.5,0.1,0.3))
                    x.append(word)
                    y.append(counts[1])
                    colors.append((0.3,0.1,0.5))
                else:
                    x.append(word)
                    y.append(counts[1])
                    colors.append((0.3,0.1,0.5))
                    x.append(word)
                    y.append(counts[0])
                    colors.append((0.5,0.1,0.3))
        if group and target_lang:
            self.render_barchart(x, y, colors, outfile, width=50)
        elif group:
             self.render_barchart(x, y, colors, outfile, width=70)
        else:
            self.render_barchart(x, y, colors, outfile, width=120)

    def word_freq_barchart_transcript(self, transcript: Transcript):
        words = []
        counts = []
        colors = []
        for lang in transcript.types_tokens:
            for token in transcript.types_tokens[lang]:
                words.append(token)
                counts.append(transcript.types_tokens[lang][token])
                if lang == "eng":
                    colors.append((0.5,0.1,0.3))
                else:
                    colors.append((0.3,0.1,0.5))
        self.render_barchart(words, counts, colors)

    def render_barchart(self, X, Y, colors:list=None,outfile:str=None, width=50):
        plt.figure(figsize=(width, 10))  # Adjust the width and height as per your preference
        plt.bar(X, Y, color=colors)
        plt.xticks(X, X, rotation=90)
        plt.savefig(outfile)
        plt.close()

if __name__ == "__main__":
    corpus = Corpus('C:\\msys\\home\\Benjamin\\spanglish-pos-tagger\\transcriptions')
    viz = Visualizer(corpus)
    #viz.language_pie('C:\\msys\\home\\Benjamin\\spanglish-pos-tagger\\visualizations\\lexical\\language_pie')
    viz.lexical_diveristy_boxplots('C:\\msys\\home\\Benjamin\\spanglish-pos-tagger\\visualizations\\lexical\\lexical_diversity')
    #viz.word_freq_barcharts_all('C:\\msys\\home\\Benjamin\\spanglish-pos-tagger\\visualizations\\lexical\\word_frequencies\\barcharts')