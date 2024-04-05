from flair.data import Sentence
from flair.models import SequenceTagger

spanglish_tagger = SequenceTagger.load('benevanoff/spanglish-upos')

example_sentence = "Caperucita Roja put rocks en el estómago de la del perro."

spanglish_tagger.predict(example_sentence)

for token in example_sentence:
    word = token.text
    upos_tag = token.labels[0] # there will only be one label per token
    print(f'The predicted UPOS tag for {word} is {upos_tag.value} with confidence of {upos_tag.score}')
