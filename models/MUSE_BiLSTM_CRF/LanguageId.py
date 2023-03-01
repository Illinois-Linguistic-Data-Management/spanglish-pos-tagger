from nltk.lm import Laplace, preprocessing
from flair.data import Sentence
from flair.datasets import UD_ENGLISH, UD_SPANISH

class LanguageIdentifier():
    
    def __init__(self):
        self.n_gram_order = 6

        en_corpus = UD_ENGLISH(in_memory=False)
        english_token_characters = [token for token in en_corpus.make_vocab_dictionary(-1, 3).get_items()] # every token that appears more than 3 times in corpus
        english_ngrams, english_vocab = preprocessing.padded_everygram_pipeline(self.n_gram_order, english_token_characters)
        self.english_language_model = Laplace(self.n_gram_order) # N-gram model with Laplace smoothing
        self.english_language_model.fit(english_ngrams, english_vocab)

        es_corpus = UD_SPANISH(in_memory=False)
        spanish_token_characters = [token for token in es_corpus.make_vocab_dictionary(-1, 3).get_items()] # every token that appears more than 3 times in corpus
        spanish_ngrams, spanish_vocab = preprocessing.padded_everygram_pipeline(self.n_gram_order, spanish_token_characters)
        self.spanish_language_model = Laplace(self.n_gram_order) # N-gram model with Laplace smoothing
        self.spanish_language_model.fit(spanish_ngrams, spanish_vocab)

    def _score_token(self, language_model, token: str) -> float:
        score_product = 1
        context = ["<s>"] # history starts w start tag
        for character in token:
            score_product *= language_model.score(character, context)
            context.append(character)
        score_product *= language_model.score("</s>", context) # pre processing uses start and stop tags
        return score_product
        
    def identify_token(self, token: str) -> str:
        english_score = self._score_token(self.english_language_model, token)
        spanish_score = self._score_token(self.spanish_language_model, token)
        return "en" if english_score > spanish_score else "es"