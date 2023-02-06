from flair.data import Sentence

def sentence_to_tsv(sentence, path):
    with open (path, 'w') as stream:
        stream.write("word\t tag\n")
        for token in sentence:
            tag = token.get_label('upos')
            stream.write(token.text)
            stream.write("\t ")
            stream.write(tag.value)
            stream.write('\n')
