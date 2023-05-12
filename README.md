# Spanglish POS Tagger

This repository includes several tools for the automation of the annotation of multilinugual corpora.

## The Problem

Monologues were recorded from bilingual research participants at the University of Illinois's [Second Language Acquisition and Bilingualism Lab](https://publish.illinois.edu/uiuc-slab/) and then manually transcribed. We are interested in extracting insights from these participants' speech production so we would like for our data to be annotated for various linguistic features (syntactic tags & morphological tags) so that we can extract statistics from this largely unstructured text data.

Automated grammatical tagging is not particularly new, systems to solve this problem have been devised since the late 80s/90s (see [Tagging English Text with a Probabilistic
Model, Merialdo 1994](https://aclanthology.org/J94-2001.pdf)) and modern state of the art approaches acheive >95% accuracy, but such publicly available tools are trained on monolingual datasets and struggle immensly in contexts where code switching is common.

Here are examples of different existing part-of-speech taggers trying to tag the same code switched English-Spanish text:

[Spacy](https://spacy.io/) es_core_news_lg (Monolingual Spanish trained on news dataset)
```
So PROPN , PUNCT la DET niña NOUN está VERB , PUNCT yo PRON creo VERB que SCONJ se PRON ve VERB que SCONJ , PUNCT you PROPN know PROPN , PUNCT está AUX hablando VERB con ADP su DET abuela NOUN , PUNCT o CCONJ bailando VERB . PUNCT Okay PROPN , PUNCT y CCONJ la DET niña NOUN se PRON va VERB con ADP , PUNCT se PRON va VERB de ADP su DET casa NOUN y CCONJ va VERB en ADP un DET camino NOUN con ADP su DET comida NOUN . PUNCT Y CCONJ allí ADV está VERB un DET lobo NOUN . PUNCT Y CCONJ la DET niña NOUN no ADV lo PRON ve VERB al ADP lobo NOUN , PUNCT pero CCONJ el DET lobo PROPN quiere VERB comer VERB a ADP la DET niña NOUN . PUNCT Y CCONJ el DET lobo PROPN va VERB a ADP la DET casa NOUN , PUNCT yo PRON creo VERB de ADP la DET abuela NOUN , PUNCT y CCONJ el DET lobo PROPN ataca VERB a ADP la DET abuelita NOUN . PUNCT Y CCONJ allí ADV llega VERB la DET niña NOUN con ADP las DET flores NOUN y CCONJ no ADV sabe VERB que SCONJ , PUNCT este PRON , PUNCT el DET lobo PROPN comió VERB su DET abuelita NOUN . PUNCT Y CCONJ la DET niña NOUN va AUX a ADP ver VERB a ADP su DET abuelita NOUN . PUNCT La PRON veo VERB pero CCONJ ella PRON no ADV sé VERB que SCONJ es AUX su DET abuela NOUN . PUNCT Entonces ADV el DET lobo PROPN brinca PROPN de ADP la DET cama NOUN y CCONJ va AUX a ADP atacar VERB a ADP la DET niña NOUN . PUNCT Pero CCONJ los DET hombres NOUN vienen VERB con ADP una DET pistola NOUN y CCONJ un DET perro NOUN . PUNCT Y CCONJ el DET lobo PROPN comió VERB a ADP la DET niña NOUN . PUNCT Pero CCONJ el DET hombre NOUN tiene VERB su DET , PUNCT mm NOUN , PUNCT no ADV , PUNCT I CCONJ don't PROPN know PROPN ... PUNCT I CCONJ forgot PROPN what PROPN that PROPN is PROPN . PUNCT I'm CCONJ a ADP ... PUNCT scissors PROPN . PUNCT I'm CCONJ just PROPN gonna PROPN say PROPN scissors PROPN . PUNCT Y CCONJ lo PRON corta VERB al ADP lobo NOUN de ADP su DET estómago NOUN , PUNCT y CCONJ allí ADV sale VERB la DET niña NOUN y CCONJ la DET abuela NOUN . PUNCT Y CCONJ aquí ADV viene VERB la DET niña NOUN con ADP rocas NOUN y CCONJ el DET perro NOUN también ADV . PUNCT Y CCONJ el DET hombre NOUN va AUX a ADP poner VERB los DET rocas NOUN en ADP el DET lobo NOUN . PUNCT Y CCONJ el DET lobo PROPN va AUX corriendo VERB , PUNCT se PRON cae VERB . PUNCT Y CCONJ todos PRON están AUX riendo VERB del ADP lobo PROPN . PUNCT Entonces ADV ya ADV se PRON va VERB la DET niña NOUN con ADP el DET hombre NOUN y CCONJ perro NOUN y CCONJ dicen VERB adiós NOUN a ADP la DET abuelita NOUN . PUNCT
```

This monolingual Spanish model does a decent job tagging the Spanish words but has a strong bias to labelling any English word as a proper noun.

[Spacy](https://spacy.io/) en_core_web_sm (Monolingual English trained on web dataset)
```
So ADV , PUNCT la DET niña ADJ está NOUN , PUNCT yo PROPN creo PROPN que PROPN se X ve VERB que NOUN , PUNCT you PRON know VERB , PUNCT está PROPN hablando PROPN con PROPN su PROPN abuela PROPN , PUNCT o NOUN bailando NOUN . PUNCT Okay INTJ , PUNCT y PROPN la PROPN niña ADJ se PROPN va PROPN con PROPN , PUNCT se PROPN va PROPN de PROPN su PROPN casa PROPN y PROPN va PROPN en PROPN un PROPN camino PROPN con PROPN su PROPN comida PROPN . PUNCT Y PROPN allí PROPN está PROPN un PROPN lobo PROPN . PUNCT Y PROPN la NOUN niña NOUN no DET lo PROPN ve VERB al PROPN lobo PROPN , PUNCT pero PROPN el PROPN lobo PROPN quiere PROPN comer PROPN a DET la X niña ADJ . PUNCT Y PROPN el PROPN lobo PROPN va PROPN a DET la PROPN casa NOUN , PUNCT yo PROPN creo VERB de PROPN la PROPN abuela PROPN , PUNCT y PROPN el PROPN lobo PROPN ataca PROPN a DET la DET abuelita NOUN . PUNCT Y PROPN allí PROPN llega PROPN la PROPN niña PROPN con PROPN las PROPN flores PROPN y PROPN no DET sabe ADJ que NOUN , PUNCT este NOUN , PUNCT el PROPN lobo PROPN comió PROPN su PROPN abuelita PROPN . PUNCT Y PROPN la PROPN niña ADJ va PROPN a DET ver NOUN a DET su PROPN abuelita NOUN . PUNCT La PROPN veo ADJ pero NOUN ella NOUN no DET sé NOUN que VERB es ADP su PROPN abuela PROPN . PUNCT Entonces PROPN el PROPN lobo PROPN brinca VERB de X la PROPN cama NOUN y PROPN va PROPN a DET atacar NOUN a DET la ADJ niña ADJ . PUNCT Pero PROPN los PROPN hombres PROPN vienen PROPN con PROPN una PROPN pistola NOUN y PROPN un PROPN perro PROPN . PUNCT Y PROPN el PROPN lobo PROPN comió PROPN a DET la ADJ niña ADJ . PUNCT Pero PROPN el PROPN hombre PROPN tiene PROPN su PROPN , PUNCT mm PROPN , PUNCT no INTJ , PUNCT I PRON do AUX n't PART know VERB ... PUNCT I PRON forgot VERB what PRON that PRON is AUX . PUNCT I PRON 'm AUX a DET ... NOUN scissors NOUN . PUNCT I PRON 'm AUX just ADV gon VERB na PART say VERB scissors NOUN . PUNCT Y PROPN lo PROPN corta PROPN al PROPN lobo PROPN de PROPN su PROPN estómago PROPN , PUNCT y PROPN allí PROPN sale PROPN la DET niña ADJ y PROPN la PROPN abuela PROPN . PUNCT Y PROPN aquí NOUN viene NOUN la DET niña ADJ con PROPN rocas PROPN y PROPN el PROPN perro PROPN también NOUN . PUNCT Y PROPN el PROPN hombre PROPN va PROPN a DET poner NOUN los PROPN rocas PROPN en PROPN el PROPN lobo PROPN . PUNCT Y PROPN el PROPN lobo PROPN va PROPN corriendo PROPN , PUNCT se X cae NOUN . PUNCT Y PROPN todos VERB están PROPN riendo PROPN del PROPN lobo NOUN . PUNCT Entonces NOUN ya PRON se PROPN va PROPN la PROPN niña PROPN con PROPN el PROPN hombre PROPN y PROPN perro PROPN y PROPN dicen VERB adiós VERB a DET la PRON abuelita NOUN . PUNCT
```

The monolingual English model of course does horribly on mostly Spanish text but does properly assign labels to English words.

[Flair multi-upos (LSTM-CRF with multilingual character embeddings)](https://huggingface.co/flair/upos-multi)
```
So ADV , PUNCT la DET niña NOUN está VERB , PUNCT yo PRON creo VERB que SCONJ se PRON ve VERB que SCONJ , PUNCT you X know VERB , PUNCT está AUX hablando VERB con ADP su DET abuela NOUN , PUNCT o CCONJ bailando VERB . PUNCT Okay PROPN , PUNCT y CCONJ la DET niña NOUN se PRON va VERB con ADP , PUNCT se PRON va VERB de ADP su DET casa NOUN y CCONJ va VERB en ADP un DET camino NOUN con ADP su DET comida NOUN . PUNCT Y CCONJ allí ADV está VERB un DET lobo NOUN . PUNCT Y CCONJ la DET niña NOUN no ADV lo PRON ve VERB al ADP lobo NOUN , PUNCT pero CCONJ el DET lobo NOUN quiere VERB comer VERB a ADP la DET niña NOUN . PUNCT Y CCONJ el DET lobo NOUN va VERB a ADP la DET casa NOUN , PUNCT yo PRON creo VERB de ADP la DET abuela NOUN , PUNCT y CCONJ el DET lobo NOUN ataca VERB a ADP la DET abuelita NOUN . PUNCT Y CCONJ allí ADV llega VERB la DET niña NOUN con ADP las DET flores NOUN y CCONJ no ADV sabe VERB que SCONJ , PUNCT este PRON , PUNCT el DET lobo NOUN comió VERB su DET abuelita NOUN . PUNCT Y CCONJ la DET niña NOUN va AUX a ADP ver VERB a ADP su DET abuelita NOUN . PUNCT La DET veo NOUN pero CCONJ ella PRON no ADV sé VERB que SCONJ es VERB su DET abuela NOUN . PUNCT Entonces ADV el DET lobo NOUN brinca VERB de ADP la DET cama NOUN y CCONJ va AUX a ADP atacar VERB a ADP la DET niña NOUN . PUNCT Pero CCONJ los DET hombres NOUN vienen VERB con ADP una DET pistola NOUN y CCONJ un DET perro NOUN . PUNCT Y CCONJ el DET lobo NOUN comió VERB a ADP la DET niña NOUN . PUNCT Pero CCONJ el DET hombre NOUN tiene VERB su DET , PUNCT mm X , PUNCT no PROPN , PUNCT I PROPN do PROPN n't X know PROPN ... PUNCT I X forgot PROPN what X that PROPN is PROPN . PUNCT I PROPN 'm PROPN a PROPN ... PUNCT scissors PROPN . PUNCT I PROPN 'm PROPN just PROPN gonna PROPN say PROPN scissors PROPN . PUNCT Y CCONJ lo PRON corta VERB al ADP lobo NOUN de ADP su DET estómago NOUN , PUNCT y CCONJ allí ADV sale VERB la DET niña NOUN y CCONJ la DET abuela NOUN . PUNCT Y CCONJ aquí ADV viene VERB la DET niña NOUN con ADP rocas NOUN y CCONJ el DET perro NOUN también ADV . PUNCT Y CCONJ el DET hombre NOUN va AUX a ADP poner VERB los DET rocas NOUN en ADP el DET lobo NOUN . PUNCT Y CCONJ el DET lobo NOUN va AUX corriendo VERB , PUNCT se PRON cae VERB . PUNCT Y CCONJ todos PRON están AUX riendo VERB del ADP lobo NOUN . PUNCT Entonces ADV ya ADV se PRON va VERB la DET niña NOUN con ADP el DET hombre NOUN y CCONJ perro NOUN y CCONJ dicen VERB adiós NOUN a ADP la DET abuelita NOUN . PUNCT
```

This model does better than the purely monolingual models but still labels many words in code switched sentences as `X` (unknown).

## The Solution

### A Multilingual Part of Speech Classifier For Code-Switched Text

I trained several different multi-class classifiers on a combination of monolingual English and monolingual Spanish corpora from the [Universal Dependencies dataset](https://universaldependencies.org/) as well as the [Bangor Miami corpus](http://bangortalk.org.uk/speakers.php?c=miami) which contains code switched dialog from native spanish speakers living in the southern United States.

The most successful model was a classifier which utilized contextualized text embeddings from a version of [Multilingual-BERT](https://github.com/google-research/bert/blob/master/multilingual.md) that was fine tuned on our dataset. The multilingual nature of MBERT's pretraining set provides a very good foundational representation of the context in which both Spanish and English words are used and fine tuning with a domain specific dataset and an additional attention layer allows the model to better learn how to handle code switching.

My model's response to the same prompt that was given to the models in the `The Problem` section:

```
So ADV , PUNCT la DET niña NOUN está VERB , PUNCT yo PRON creo VERB que SCONJ se PRON ve VERB que SCONJ , PUNCT you PRON know VERB , PUNCT está VERB hablando VERB con ADP su DET abuela NOUN , PUNCT o CCONJ bailando VERB . PUNCT Okay INTJ , PUNCT y CCONJ la DET niña NOUN se PRON va VERB con ADP , PUNCT se PRON va VERB de ADP su DET casa NOUN y CCONJ va VERB en ADP un DET camino NOUN con ADP su DET comida NOUN . PUNCT Y CCONJ allí ADV está VERB un DET lobo NOUN . PUNCT Y CCONJ la DET niña NOUN no ADV lo PRON ve VERB al ADP lobo NOUN , PUNCT pero CCONJ el DET lobo NOUN quiere VERB comer VERB a ADP la DET niña NOUN . PUNCT Y CCONJ el DET lobo NOUN va VERB a ADP la DET casa NOUN , PUNCT yo PRON creo VERB de ADP la DET abuela NOUN , PUNCT y CCONJ el DET lobo NOUN ataca VERB a ADP la DET abuelita NOUN . PUNCT Y CCONJ allí ADV llega VERB la DET niña NOUN con ADP las DET flores NOUN y CCONJ no ADV sabe VERB que SCONJ , PUNCT este PRON , PUNCT el DET lobo NOUN comió VERB su DET abuelita NOUN . PUNCT Y CCONJ la DET niña NOUN va VERB a ADP ver VERB a ADP su DET abuelita NOUN . PUNCT La DET veo NOUN pero CCONJ ella PRON no ADV sé VERB que SCONJ es AUX su DET abuela NOUN . PUNCT Entonces ADV el DET lobo NOUN brinca VERB de ADP la DET cama NOUN y CCONJ va VERB a ADP atacar VERB a ADP la DET niña NOUN . PUNCT Pero CCONJ los DET hombres NOUN vienen VERB con ADP una DET pistola NOUN y CCONJ un DET perro NOUN . PUNCT Y CCONJ el DET lobo NOUN comió VERB a ADP la DET niña NOUN . PUNCT Pero CCONJ el DET hombre NOUN tiene VERB su DET , PUNCT mm X , PUNCT no ADV , PUNCT I PRON do AUX n't PART know VERB ... PUNCT I PRON forgot VERB what PRON that PRON is AUX . PUNCT I PRON 'm AUX a ADP ... PUNCT scissors NOUN . PUNCT I PRON 'm AUX just ADV gonna VERB say VERB scissors NOUN . PUNCT Y CCONJ lo PRON corta NOUN al ADP lobo NOUN de ADP su DET estómago NOUN , PUNCT y CCONJ allí ADV sale VERB la DET niña NOUN y CCONJ la DET abuela NOUN . PUNCT Y CCONJ aquí ADV viene VERB la DET niña NOUN con ADP rocas NOUN y CCONJ el DET perro NOUN también ADV . PUNCT Y CCONJ el DET hombre NOUN va VERB a ADP poner VERB los DET rocas NOUN en ADP el DET lobo NOUN . PUNCT Y CCONJ el DET lobo NOUN va VERB corriendo VERB , PUNCT se PRON cae VERB . PUNCT Y CCONJ todos PRON están AUX riendo VERB del ADP lobo NOUN . PUNCT Entonces ADV ya ADV se PRON va VERB la DET niña NOUN con ADP el DET hombre NOUN y CCONJ perro NOUN y CCONJ dicen VERB adiós ADV a ADP la DET abuelita NOUN . PUNCT
```

### A Multilingual Multilabel Morphological Tag Classifier For Code-Switched Text

After such success with the multilingual part of speech tagger, I tweaked the best performing model to train with the binary cross entropy loss function and re-processed the Bangor Miami corpus to use multihot encoded vectors for the labels so that it could learn to assign several labels at once. This currently exists as a proof of concept in the MBERT-Multilabel folder and works well for assigning gender (M/F) and tense (Present/Past/Future) tags.

## How to use

### Dependencies

* Python3
* PySide6
* PyTorch
* Flair
* NLTK

For convenience I provide a requirements.txt file which lists all packages installed on my (Ben's) system. You can install from my frozen list by running `python3 -m pip install -r requirements.txt`

### Training the model

The majority of the models found in the `models` folder can be trained simply by running the associated python program.

For instance, `cd models && python3 models/MBERT-CRF.py`

The only exception is the `MUSE-BiLSTM-CRF` model which requires the projected Spanish and English word embedding vectors to be downloaded from [Facebook's FastText](https://github.com/facebookresearch/fastText)

### The GUI-Tagger

To provide a more user friendly and accessible way of using these models I have built a simple Graphical User Interface utilizing the [Qt graphics library](https://www.qt.io/qt-for-python).

Once you have trained your model, make sure to name it `gui-model.pt` and place it in the `models` folder for a complete relative path of `models/gui-model.pt` so that the GUI program will be able to find it. Then you can start the GUI program by running `python3 gui_tagger.py`.

#### Usage

Provide a .cha file as input with the button labeled "Choose an input file". Then click the "Choose an output file" to provide the location to store the output file. Once you have clicked "Predict Tags" a new .cha file will be written to your specified save location. The newly output .cha file will contain an additional `%pos` layer after each utterance. A comment with a timestamp stating that the file was generated by this program.

![GUI Tagger screenshot](gui_tagger.png)