import flair
from flair.embeddings import MuseCrosslingualEmbeddings
from flair.data import Sentence, Corpus, MultiCorpus
from flair.datasets import UD_ENGLISH, UD_SPANISH, ColumnCorpus
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

from NaiveBayes_LangId import LanguageIdentifier

from pathlib import Path
from typing import List

import gensim
from gensim.models import KeyedVectors
from gensim.models.fasttext import FastTextKeyedVectors, load_facebook_vectors

import numpy as np
import io

# this function is adapted from the example in the MUSE repo
# https://github.com/facebookresearch/MUSE/blob/main/demo.ipynb
def load_muse_vec(emb_path, nmax=50000):
    words = {}
    word_embeddings = {}
    
    with io.open(emb_path, 'r', encoding='utf-8', newline='\n', errors='ignore') as f:
        next(f)
        for i, line in enumerate(f):
            word, vect = line.rstrip().split(' ', 1)
            vect = np.fromstring(vect, sep=' ')
            assert word not in words, 'word found twice'
            words[word] = len(words)
            word_embeddings[word] = vect
            if len(words) == nmax:
                break
    return word_embeddings

class SpanglishBilingualEmbeddings(MuseCrosslingualEmbeddings):
    
    def __init__(self):
        super().__init__()

        print("Loading bilingual English model")
        self.language_embeddings["en"] = load_muse_vec('english_muse_embeddings.txt')

        print("Loading bilingual Spanish model")
        self.language_embeddings["es"] = load_muse_vec('spanish_muse_embeddings.txt')

        self.language_identifier = LanguageIdentifier()

    def _add_embeddings_internal(self, sentences: List[Sentence]) -> List[Sentence]:
        for i, sentence in enumerate(sentences):
            for token, token_idx in zip(sentence.tokens, range(len(sentence.tokens))):
                token_language_code = self.language_identifier.identify_token(token.text)
                word_embedding = self.get_cached_vec(language_code=token_language_code, word=token.text)
                token.set_embedding(self.name, word_embedding)
        return sentences

def build_and_train_model():
    BM_corpus_columns = {0: 'text', 1: 'upos'}
    BangorMiami_corpus = ColumnCorpus('./', BM_corpus_columns, train_file='BM_herring.corpus')
    # combine monolingual English and Spanish corpora with Bangor Miami
    corpus = MultiCorpus([
        UD_ENGLISH(in_memory=False),
        UD_SPANISH(in_memory=False),
        BangorMiami_corpus
    ])
    tag_dictionary = corpus.make_label_dictionary(label_type='upos')

    # initalize model
    tagger = SequenceTagger(hidden_size=256,
                            embeddings=SpanglishBilingualEmbeddings(),
                            tag_dictionary=tag_dictionary,
                            tag_type='upos',
                            rnn_type='LSTM',
                            bidirectional=True,
                            use_crf=True,
                            reproject_embeddings=False)
    # train model
    trainer = ModelTrainer(tagger, corpus)
    trainer.train('upos-spanglish-MUSE-BiLSTM-CRF',
                  embeddings_storage_mode='cpu',
                  train_with_dev=True,
                  max_epochs=50)

