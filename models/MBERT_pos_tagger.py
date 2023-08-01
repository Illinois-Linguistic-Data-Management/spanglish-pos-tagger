import sys
from flair.data import MultiCorpus
from flair.data import Sentence
from flair.datasets import UD_ENGLISH, UD_SPANISH, ColumnCorpus
from flair.embeddings import TransformerWordEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

def build_and_train_model(use_CRF=True, use_whole_bm_herring=False):
    BM_corpus_columns = {0: 'text', 1: 'upos'}
    if use_all_bm_herring:
        BangorMiami_corpus = ColumnCorpus('data/bangor_miami_corpus', BM_corpus_columns, train_file='BM_herring.corpus')
    else:
        BangorMiami_corpus = ColumnCorpus('data/bangor_miami_corpus', BM_corpus_columns, train_file='BM_herring_code_switching.corpus')
    # combine monolingual English and Spanish corpora with Bangor Miami corpus
    corpus = MultiCorpus([
        UD_ENGLISH(in_memory=False),
        UD_SPANISH(in_memory=False),
        BangorMiami_corpus
    ])
    tag_dictionary = corpus.make_label_dictionary(label_type='upos')

    # initalize model
    tagger = SequenceTagger(hidden_size=256,
                            embeddings=TransformerWordEmbeddings('bert-base-multilingual-cased', layers='-1', fine_tune=True, subtoken_pooling='all'),
                            tag_dictionary=tag_dictionary,
                            use_crf=use_CRF,
                            use_rnn=False,
                            tag_type='upos',
                            reproject_embeddings=False
                            )
    # train model
    trainer = ModelTrainer(tagger, corpus, checkpoint=True)
    trainer.train('multilingual-bert-code-switch',
                  embeddings_storage_mode='gpu',
                  train_with_dev=True,
                  max_epochs=10,
                  save_model_each_k_epochs=1,
                  write_weights=True,
                  save_optimizer_state=True)
    return tagger

if __name__ == "__main__":
    try:
        use_CRF = sys.argv[1] == "1"
        use_whole_bm_herring = sys.argv[2] == "1"
    except:
        print("Usage: python models/MBERT_pos_tagger.py <use_CRF> <use_whole_bm_herring>")
        print("Ex: python models/MBERT_pos_tagger.py 1 0")
    
    build_and_train_model(use_CRF=use_CRF, use_whole_bm_herring=use_whole_bm_herring)