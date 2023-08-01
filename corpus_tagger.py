"""
A script to annotate all .cha files in a given directory
with part of speech tags
"""

import os
import re
import datetime
from flair.data import Sentence
from flair.models import SequenceTagger
from util import parse_utterances_from_cha, preprocess_sentence_from_cha, get_cha_files_in_dir

def annotate_and_write_new_cha(input_filename, output_filename):
    tagger_model = SequenceTagger.load('./models/gui-model.pt')
    with open(output_filename, 'w') as outFile:
        utterances = parse_utterances_from_cha(input_filename)
        for utterance in utterances:
            print("utterance", utterance)
            outFile.write(utterance)
            preprocessed_sentence = preprocess_sentence_from_cha(utterance)
            print("preprocessed_sentence", preprocessed_sentence)
            if preprocessed_sentence and len(re.sub(r' ', '', preprocessed_sentence)) != 0:
                model_sentence = Sentence(preprocessed_sentence)
                tagger_model.predict(model_sentence)
                outStr = "%pos:"
                for token in model_sentence:
                    outStr += " " + token.text + "." + token.tag
                outFile.write(outStr+'\n')
        # write a final comment in the output that it was produced by this tool
        outFile.write("@Comment: %pos tags were generated using the Spanglish-MBERT-CRF-3-Epoch model on " + str(datetime.datetime.now()))

all_cha_files = get_cha_files_in_dir(os.getcwd() + "/transcriptions")
for cha_file in all_cha_files:
    split_filename = cha_file.split("/")
    output_file_parts = [re.sub(r'Transcriptions', 'Tagged Transcriptions', x) if "Transcriptions" in x else x for x in split_filename]
    output_file = "/".join(output_file_parts)
    print(output_file)
    annotate_and_write_new_cha(cha_file, output_file)