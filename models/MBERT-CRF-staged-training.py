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
    tagger = SequenceTagger.load('./gui-model.pt')
    # train model
    trainer = ModelTrainer(tagger, corpus)
    trainer.resume(tagger, base_path='gui-model-resume',max_epochs=1)

build_and_train_model()