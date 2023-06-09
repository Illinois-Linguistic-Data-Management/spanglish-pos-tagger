import os

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

with open ('bangor_miami_corpus/MB_herring.corpus', 'w') as outFile: # write to new file formatted in CoNLL-U
    for filename in os.listdir('bangor_miami_corpus'):
        if filename.split(".")[-1] != "tsv":
            continue
        print(filename)
        most_recent_speaker = None
        with open('bangor_miami_corpus/' + filename, 'r') as file:
                headers = file.readline().split('\t')
                print(headers)
                header_idx = {}
                i = 0
                for header in headers:
                    header_idx[header] = i
                    i += 1
                del i
                #print(header_idx)
                language = None
                code_switched = False
                utt = []
                for line in file:  
                    # read the input and re-tokenize
                    try:
                        split_line = line.split('\t')
                        word = split_line[3]
                        annotation = split_line[4]
                        lang_id = split_line[8]
                        speaker = split_line[header_idx['speaker']]
                        print(split_line)
                    except Exception as e:
                        print(e, line)

                    if language is None:
                        language = lang_id
                        code_switched = False
                    elif language != lang_id:
                        language = lang_id
                        code_switched = True
                    # now write to outfile
                    if word in ['.', '!', '?']:
                        outFile.write('\n') # sentence terminal punctuation signals end of utterance
                        if code_switched:
                            pass#print(utt)
                        code_switched = False
                        language = None
                        utt = []
                        continue
                    if not most_recent_speaker:
                        most_recent_speaker = speaker
                    # a new speaker means new utterance
                    elif most_recent_speaker != speaker:
                        outFile.write('\n')
                        most_recent_speaker = speaker
                        if code_switched:
                            pass#print(utt)
                        code_switched = False
                        language = None
                        utt = []
                        continue
                    # tokenize and write tokens to .corpus plain text file
                    tokens = tokenize_UD(word, annotation, lang_id)
                    for tok in tokens:
                        utt.append(tok[0])
                    
                    
        outFile.write('\n') # a new file also means a new utterance
