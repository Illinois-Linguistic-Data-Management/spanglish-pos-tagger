import os, csv
from matplotlib import pyplot as plt

translation_dict = {'ADV': 'ADV', 'PRON': 'PRON', 'V': 'VERB', 'PREP': 'ADP', 'DET': 'DET',
                    'N': 'NOUN', 'CONJ': 'CCONJ', 'ADJ': 'ADJ', 'REL': 'DET', 'NUM': 'NUM', 'SV': 'VERB', 'IM': 'INTJ',
                    'ADJ+ADV': 'ADV', 'DEM': 'DET', 'AV': 'ADV', 'ORD': 'ADJ', 'INT': 'INTJ', 'E': 'INTJ', 'PREP+DET': 'ADP'}

english_modals = ['can', 'could', 'may', 'might' 'shall', 'should', 'will', 'would', 'must']

punct_list = ['.', ',', '?', '!']

def tokenize_UD(word: str, annotation: str, lang_id: str):
    toks = []
    # annotations are formatted: gloss.tag.more.fine.grained.tags
    try:
        if word in punct_list:
            translated_tag = 'PUNCT'
        else:
            tag = annotation.split('.')[1]
            translated_tag = translation_dict[tag]
    except:
        translated_tag = 'X' # 'other' tag if BM tag not in translation dictionary
    # tokenize according to English UD rules https://universaldependencies.org/en/
    if lang_id == 'eng': 
        # clitics get split into 2 tokens
        #first look for english clitic negation
        if 'n\'t' in word:
            toks.append((word.split('n\'t')[0], translated_tag))
            toks.append(("n\'t", 'PART'))
        # cannot is specially called out in the UD doc
        elif word == 'cannot':
            toks.append(('can', 'AUX'))
            toks.append(('not', 'PART'))
        elif len(word.split('\'')) > 1:
            word_parts = word.split('\'')
            # BM corpus doesnt have the AUX tag, but auxilary clitics are specifically called out
            # in the UD doc
            if word_parts[0] in english_modals or word_parts[0] == 'wo': # won't is a special case as it is not just willn't
                toks.append((word_parts[0], 'AUX'))
                toks.append(('\'' + word_parts[1], 'PART')) # clitics get labeled 'particle'
            # default for possessive genitive markers and anything else
            else:
                toks.append((word_parts[0], translated_tag))
                toks.append(('\'' + word_parts[1], 'PART')) # clitics get labeled 'particle'
        else:
            toks.append((word, translated_tag))
        return toks
    # tokenize according to Spanish UD rules https://universaldependencies.org/es/
    else:
        # first split prep + det contractions
        if word == 'al':
            toks.append(('a', 'PREP'))
            toks.append(('el', 'DET'))
        elif word == 'del':
            toks.append(('de', 'PREP'))
            toks.append(('el', 'DET'))
        # TODO split contractions like 'damelo' or 'lavarse'
        else: # assume single word
            toks.append((word, translated_tag))
        return toks

def write_tokens_to_column_corpus(tokens: list, outFile):
    for token in tokens:
        outFile.write(token[0])
        outFile.write(' ')
        outFile.write(token[1])
        outFile.write('\n')
    outFile.write('\n')

cs_count = 0
non_cs_count = 0
with open ('bangor_miami_corpus/MB_herring.corpus', 'w') as outFile: # write to new file formatted in CoNLL-U
    for filename in os.listdir('bangor_miami_corpus'):
        if filename.split(".")[-1] != "tsv":
            continue
        print(filename)
        with open('bangor_miami_corpus/' + filename, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            language = None
            most_recent_speaker = None
            code_switched = False
            utt = []
            for row in reader:
                word = row["surface"]
                annotation = row["auto"]
                lang_id = row["langid"]
                speaker = row['speaker']

                if language is None:
                        language = lang_id
                        code_switched = False
                elif language != lang_id and lang_id in ['eng', 'spa']:
                    code_switched = True
                # now write to outfile
                if word in ['.', '!', '?']:
                    if code_switched:
                        cs_count += 1
                        write_tokens_to_column_corpus(utt, outFile)
                    else:
                        non_cs_count += 1
                    code_switched = False
                    language = None
                    utt = []
                    continue
                if not most_recent_speaker:
                    most_recent_speaker = speaker
                # a new speaker means new utterance
                elif most_recent_speaker != speaker:
                    most_recent_speaker = speaker
                    if code_switched:
                        cs_count += 1
                        write_tokens_to_column_corpus(utt, outFile)
                    else:
                        non_cs_count += 1
                    code_switched = False
                    language = None
                    utt = []
                    continue
                # tokenize and write tokens to .corpus plain text file
                tokens = tokenize_UD(word, annotation, lang_id)
                for tok in tokens:
                    utt.append((tok[0], tok[1]))

print(cs_count, non_cs_count)
plt.rc('font', size=16)
fig, ax = plt.subplots()
slice_sizes = [cs_count / (cs_count+non_cs_count), non_cs_count/(cs_count+non_cs_count)]
ax.pie(slice_sizes, labels=['code switched', 'non code switched'], autopct='%1.1f%%')
plt.show()