# import deps
from flair.data import MultiCorpus
from flair.data import Sentence
from flair.datasets import UD_ENGLISH, UD_SPANISH
from flair.embeddings import StackedEmbeddings, WordEmbeddings, TransformerWordEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

def sentence_to_tsv(sentence, path):
    with open (path, 'w') as stream:
        stream.write("word\t tag\n")
        for token in sentence:
            tag = token.get_label('upos')
            stream.write(token.text)
            stream.write("\t ")
            stream.write(tag.value)
            stream.write('\n')

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
                            use_crf=False)
    # train model
    trainer = ModelTrainer(tagger, corpus)
    trainer.train('upos-spanglish',
                  train_with_dev=True,
                  max_epochs=100)

tagger = SequenceTagger.load('./final-model.pt')

string = 'So, la niña está, yo creo que se ve que, you know, está hablando con su abuela, o bailando. Okay, \
y la niña se va con, se va de su casa y va en un camino con su comida. Y allí está un lobo. Y la \
niña no lo ve al lobo, pero el lobo quiere comer a la niña. Y el lobo va a la casa, yo creo de la \
abuela, y el lobo ataca a la abuelita. Y allí llega la niña con las flores y no sabe que, este, el lobo \
comió su abuelita. Y la niña va a ver a su abuelita. La veo pero ella no sé que es su abuela. \
Entonces el lobo brinca de la cama y va a atacar a la niña. Pero los hombres vienen con una \
pistola y un perro. Y el lobo comió a la niña. Pero el hombre tiene su, mm, no, I don’t know...I \
forgot what that is. I’m a...scissors. I’m just gonna say scissors. Y lo corta al lobo de su \
estómago, y allí sale la niña y la abuela. Y aquí viene la niña con rocas y el perro también. Y el \
hombre va a poner los rocas en el lobo. Y el lobo va corriendo, se cae. Y todos están riendo del \
lobo. Entonces ya se va la niña con el hombre y perro y dicen adiós a la abuelita.'

s = Sentence(string)
tagger.predict(s)
sentence_to_tsv(s, 'participant-109.tsv')




