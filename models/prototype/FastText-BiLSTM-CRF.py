from flair.data import MultiCorpus
from flair.data import Sentence
from flair.datasets import UD_ENGLISH, UD_SPANISH
from flair.embeddings import StackedEmbeddings, FastTextEmbeddings, WordEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

def build_and_train_model():
    # use combined spanish and english corpora
    corpus = MultiCorpus([
        UD_ENGLISH(in_memory=False),
        UD_SPANISH(in_memory=False)
    ])
    tag_dictionary = corpus.make_label_dictionary(label_type='upos')

    # initalize model
    embeddings = StackedEmbeddings(embeddings=
                                   [WordEmbeddings('en'), WordEmbeddings('es')])
    tagger = SequenceTagger(hidden_size=256,
                            embeddings=embeddings,
                            tag_dictionary=tag_dictionary,
                            tag_type='upos',
                            rnn_type='LSTM',
                            bidirectional=True,
                            use_crf=True,
                            reproject_embeddings=False)
    # train model
    trainer = ModelTrainer(tagger, corpus)
    trainer.train('upos-spanglish-fasttext-BiLSTM-CRF',
                  embeddings_storage_mode='gpu',
                  train_with_dev=True,
                  max_epochs=100)
