# import deps
import os
from flair.data import MultiCorpus
from flair.data import Sentence
from flair.datasets import UD_ENGLISH, UD_SPANISH, ColumnCorpus
from flair.embeddings import StackedEmbeddings, WordEmbeddings, TransformerWordEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

def evaluate(tagger):
    evalset_dir = 'data/dr_silvina_montrul_corpus/evaluation_set'
    errors = 0
    examples = 0
    for file in os.listdir(evalset_dir):
        with open(f'{evalset_dir}/{file}', 'r') as evalFile:
            for line in evalFile:
                if '%pos:' in line:
                    sentence_words = []
                    sentence_tags = []
                    tokens = line.split(' ')
                    for token in tokens:
                        word = token.split('.')[0]
                        tag = token.split('.')[-1]
                        sentence_words.append(word)
                        sentence_tags.append(tag)
                    # now evaluate
                    flair_sent = Sentence(sentence_words)
                    tagger.predict(flair_sent)
                    for i, tok in enumerate(flair_sent):
                        if sentence_tags[i] in ['VERB', 'AUX'] and tok.tag not in ['VERB', 'AUX']:
                            errors += 1
                        elif sentence_tags[i] in ['SCONJ', 'CCONJ'] and tok.tag not in ['SCONJ', 'CCONJ']:
                            errors += 1
                        elif sentence_tags[i] in ['PREP', 'ADP'] and tok.tag not in ['PREP', 'ADP']:
                            errors += 1
                        elif sentence_tags[i] != tok.tag:
                            errors += 1
                        examples += 1
    return round(float(examples - errors) / float(examples), 3)

def build_and_train_model():
    # use combined spanish and english corpora with bangor miami code switched corpus
    BM_corpus_columns = {0: 'text', 1: 'upos'}
    BangorMiami_corpus = ColumnCorpus('./', BM_corpus_columns, train_file='BM_herring.corpus')

    corpus = MultiCorpus([
        UD_ENGLISH(in_memory=False),
        UD_SPANISH(in_memory=False),
        BangorMiami_corpus
    ])
    tag_dictionary = corpus.make_label_dictionary(label_type='upos')

    # initalize model
    embeddings = StackedEmbeddings(embeddings=
                                   [WordEmbeddings('en'), WordEmbeddings('es')])
    tagger = SequenceTagger(hidden_size=256,
                            embeddings=embeddings,
                            tag_dictionary=tag_dictionary,
                            tag_type='upos',
                            use_crf=False)
    # train model
    trainer = ModelTrainer(tagger, corpus)
    trainer.train('upos-spanglish-fasttext-stacked',
                  train_with_dev=True,
                  max_epochs=15,
                  save_model_each_k_epochs=5,
                  write_weights=True,
                  save_optimizer_state=True)
    return tagger

tagger = build_and_train_model()
print(evaluate(tagger))