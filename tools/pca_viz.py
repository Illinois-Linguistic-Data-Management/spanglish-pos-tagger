import os, io, csv
from flair.data import Sentence
from flair.embeddings import TransformerWordEmbeddings, StackedEmbeddings, WordEmbeddings
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
import numpy as np
from mpl_toolkits import mplot3d
from matplotlib import pyplot as plt

def get_code_switch_utterances():
    cs_utterances = []
    with open ('data/bangor_miami_corpus/MB_herring.corpus', 'w') as outFile: # write to new file formatted in CoNLL-U
        for filename in os.listdir('data/bangor_miami_corpus'):
            if filename.split(".")[-1] != "tsv":
                continue
            print(filename)
            with open('data/bangor_miami_corpus/' + filename, 'r') as f:
                reader = csv.DictReader(f, delimiter='\t')
                language = None
                most_recent_speaker = None
                code_switched = False
                utt = []
                for row in reader:
                    word = row["surface"]
                    lang_id = row["langid"]
                    speaker = row['speaker']

                    if language is None:
                            language = lang_id
                            code_switched = False
                    elif language != lang_id and lang_id in ['eng', 'spa']:
                        code_switched = True
                    # now write to outfile
                    if word in ['.', '!', '?']:
                        if code_switched:
                            cs_utterances.append(utt)
                        code_switched = False
                        language = None
                        utt = []
                        continue
                    if not most_recent_speaker:
                        most_recent_speaker = speaker
                    # a new speaker means new utterance
                    elif most_recent_speaker != speaker:
                        most_recent_speaker = speaker
                        if code_switched:
                            cs_utterances.append(utt)
                        code_switched = False
                        language = None
                        utt = []
                        continue
                    # tokenize and write tokens to .corpus plain text file
                    utt.append((word, lang_id))
    return cs_utterances

# this function is adapted from the example in the MUSE repo
# https://github.com/facebookresearch/MUSE/blob/main/demo.ipynb
def load_muse_vec(emb_path):
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
    return word_embeddings

def prepare_data_from_corpus(embedding_model):
    cs_utterances = get_code_switch_utterances()
    data = []
    for utt in cs_utterances:
        utterance_words = [point[0] for point in utt]
        utt_sentence = Sentence(' '.join(utterance_words))
        embedding_model.embed(utt_sentence)
        for i, tok in enumerate(utt):
            if tok[1] in ['eng', 'spa', 'eng&spa']:
                data_point = {'word': tok[0], 'embedding': utt_sentence[i].embedding, 'utterance': utterance_words, 'language': tok[1]}
                data.append(data_point)
    return data

def pca_2d(embedding_matrix, data, outname):
    pca2d = PCA(n_components=2)
    pca2d.fit(embedding_matrix)
    projected_embeddings = pca2d.transform(embedding_matrix)
    print(projected_embeddings[0])
    for i, point in enumerate(data):
        point['pca_embedding'] = projected_embeddings[i]

    #data = data[0:250]

    plt.scatter(x=[data_point['pca_embedding'][0] for data_point in data], y=[data_point['pca_embedding'][1] for data_point in data], c=LabelEncoder().fit_transform([data_point['language'] for data_point in data]))

    #for i, datapoint in enumerate(data):
    #    ax.text(datapoint['pca_embedding'][0], datapoint['pca_embedding'][1], datapoint['pca_embedding'][2], datapoint['word'])

    plt.savefig(f'pca_2d_{outname}.png')
    plt.show()

def pca_3d(embedding_matrix, data, outname):
    pca3d = PCA(n_components=3)
    pca3d.fit(embedding_matrix)
    projected_embeddings = pca3d.transform(embedding_matrix)
    print(projected_embeddings[0])
    for i, point in enumerate(data):
        point['pca_embedding'] = projected_embeddings[i]

    #data = data[0:250]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter3D(xs=[data_point['pca_embedding'][0] for data_point in data],ys=[data_point['pca_embedding'][1] for data_point in data], zs=[data_point['pca_embedding'][2] for data_point in data], c=LabelEncoder().fit_transform([data_point['language'] for data_point in data]))

    #for i, datapoint in enumerate(data):
    #    ax.text(datapoint['pca_embedding'][0], datapoint['pca_embedding'][1], datapoint['pca_embedding'][2], datapoint['word'])

    fig.savefig(f'pca_3d_{outname}.png')
    plt.show()

def gen_plots(embedding_model, outname):
    data = prepare_data_from_corpus(embedding_model)
    embedding_matrix = np.array([datapoint['embedding'].numpy() for datapoint in data])
    pca_2d(embedding_matrix, data, outname)
    pca_3d(embedding_matrix, data, outname)

def gen_plots_muse():
    cs_utterances = get_code_switch_utterances()
    data = []
    english_muse_embeddings = load_muse_vec('/Users/ben/Documents/school/spanglish-pos-tagger/models/MUSE_BiLSTM_CRF/english_muse_embeddings.txt')
    spanish_muse_embeddings = load_muse_vec('/Users/ben/Documents/school/spanglish-pos-tagger/models/MUSE_BiLSTM_CRF/spanish_muse_embeddings.txt')


    for utt in cs_utterances:
        utterance_words = [point[0] for point in utt]
        english_utterance_embeddings = []
        skip_idx = []
        for i, word in enumerate(utterance_words):
            if word in english_muse_embeddings:
                english_utterance_embeddings.append(english_muse_embeddings[word])
            else:
                skip_idx.append(i)
        spanish_utterance_embeddings = []
        for i, word in enumerate(utterance_words):
            if word in spanish_muse_embeddings:
                spanish_utterance_embeddings.append(spanish_muse_embeddings[word])
            else:
                skip_idx.append(i)

        offset = 0
        for i, tok in enumerate(utt):
            if tok[1] in ['eng', 'spa', 'eng&spa'] and i not in skip_idx:
                if tok[1] in ['eng', 'eng&spa']:
                    embedding = english_utterance_embeddings[i-offset]
                else:
                    embedding = spanish_utterance_embeddings[i-offset]
                data_point = {'word': tok[0], 'embedding': embedding, 'utterance': utterance_words, 'language': tok[1]}
                data.append(data_point)
            elif i in skip_idx:
                offset += 1
            

    embedding_matrix = np.array([datapoint['embedding'] for datapoint in data])
    pca_2d(embedding_matrix, data, "MUSE")
    pca_3d(embedding_matrix, data, "MUSE")

'''
gen_plots(WordEmbeddings('en'), "English_FastText")
gen_plots(WordEmbeddings('es'), "Spanish_FastText")
gen_plots(StackedEmbeddings([WordEmbeddings('en'), WordEmbeddings('es')]), "stacked_FastText")
gen_plots_muse()
gen_plots(TransformerWordEmbeddings('bert-base-multilingual-cased',
                                    layers='-1',
                                    fine_tune=True,
                                    subtoken_pooling='mean',
                                    is_document_embedding=False
                                    ), "mbert_base")
'''