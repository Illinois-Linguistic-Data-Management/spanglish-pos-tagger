from flair.models import SequenceTagger
from flair.data import Sentence

from models.MUSE_BiLSTM_CRF.LanguageId import LanguageIdentifier

mbert_crf_tagger = SequenceTagger.load('./models/MBERT-CRF/mbert-3-epochs.pt')

text = """
So, la niña está, yo creo que se ve que, you know, está hablando con su abuela, o bailando. Okay,
y la niña se va con, se va de su casa y va en un camino con su comida. Y allí está un lobo. Y la
niña no lo ve al lobo, pero el lobo quiere comer a la niña. Y el lobo va a la casa, yo creo de la
abuela, y el lobo ataca a la abuelita. Y allí llega la niña con las flores y no sabe que, este, el lobo
comió su abuelita. Y la niña va a ver a su abuelita. La veo pero ella no sé que es su abuela.
Entonces el lobo brinca de la cama y va a atacar a la niña. Pero los hombres vienen con una
pistola y un perro. Y el lobo comió a la niña. Pero el hombre tiene su, mm, no, I don't know...I
forgot what that is. I'm a...scissors. I'm just gonna say scissors. Y lo corta al lobo de su
estómago, y allí sale la niña y la abuela. Y aquí viene la niña con rocas y el perro también. Y el
hombre va a poner los rocas en el lobo. Y el lobo va corriendo, se cae. Y todos están riendo del
lobo. Entonces ya se va la niña con el hombre y perro y dicen adiós a la abuelita.
"""
sentence = Sentence(text)
mbert_crf_tagger.predict(sentence)

for token in sentence:
    print(token.get_label('upos'))

sentence = Sentence("ya la dio a his momma la mañana")
mbert_crf_tagger.predict(sentence)

print("")
for token in sentence:
    print(token.get_label('upos'))

