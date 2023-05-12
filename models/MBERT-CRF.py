from flair.data import MultiCorpus
from flair.data import Sentence
from flair.datasets import UD_ENGLISH, UD_SPANISH, ColumnCorpus
from flair.embeddings import StackedEmbeddings, TransformerWordEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

def build_and_train_model():
    BM_corpus_columns = {0: 'text', 1: 'upos'}
    BangorMiami_corpus = ColumnCorpus('./', BM_corpus_columns, train_file='BM_herring.corpus')
    # combine monolingual English and monolingual Spanish corpora with Bangor Miami code-switched corpus
    corpus = MultiCorpus([
        UD_ENGLISH(in_memory=False),
        UD_SPANISH(in_memory=False),
        BangorMiami_corpus
    ])

    tag_dictionary = corpus.make_label_dictionary(label_type='upos')

    # initalize model
    tagger = SequenceTagger(hidden_size=256,
                            embeddings=TransformerWordEmbeddings('bert-base-multilingual-cased ', layers='-1', fine_tune=True, subtoken_pooling='first_last'),
                            tag_dictionary=tag_dictionary,
                            tag_type='upos',
                            use_rnn=False,
                            use_crf=True,
                            reproject_embeddings=False)
    # train model
    trainer = ModelTrainer(tagger, corpus)
    trainer.train('spanglish-mbert-crf',
                  train_with_dev=True,
                  max_epochs=3)

build_and_train_model()