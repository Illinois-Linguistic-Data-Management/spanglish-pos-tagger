from transformers import BertTokenizer, BertModel, AutoTokenizer
from torch import nn
from torch import optim
import torch
import os, sys, re

class MBERT_Tagger(nn.Module):

    def __init__(self, tokenizer, hidden_dim, tagset_size):
        super(MBERT_Tagger, self).__init__()
        self.hidden_dim = hidden_dim

        self.tokenizer = tokenizer
        self.mbert = BertModel.from_pretrained("bert-base-multilingual-cased", output_hidden_states=True)

        # The linear layer that maps from hidden state space to tag space
        self.hidden2tag = nn.Linear(768, tagset_size)

    def enable_gradients(self):
        self.mbert.train()

    def disable_gradients(self):
        self.mbert.eval()

    def embed_sentence(self, sentence):
        tokens = self.tokenizer.encode_plus(sentence, return_tensors="pt", is_split_into_words=True)
        token_embeddings = self.mbert(**tokens).last_hidden_state # use top most layer
        token_embeddings = token_embeddings.squeeze(0) # squeeze out batch dimension
        token_embeddings = token_embeddings[1:-1] # ignore [CLS] and [SEP] start/stop tokens
        word_ids = tokens.word_ids()[1:-1]

        # average embeddings for tokens that belong to the same word
        sentence_embedding = []
        tmp = []
        for i in range(len(word_ids)):
            if i+1 < len(word_ids) and word_ids[i] == word_ids[i+1]:
                #print(i, sentence[word_ids[i]], token_embeddings[i][0])
                tmp.append(token_embeddings[i])
            elif len(tmp) > 0:
                #print(i, sentence[word_ids[i]], token_embeddings[i][0])
                avg = torch.mean(torch.stack(tmp), dim=0)
                tmp = []
                sentence_embedding.append(avg)
            else:
                sentence_embedding.append(token_embeddings[i])
        sentence_embedding = torch.stack(sentence_embedding)
        return sentence_embedding
    
    def forward(self, sentence):
        embedded_sentence = self.embed_sentence(sentence)
        tag_space = self.hidden2tag(embedded_sentence)
        return tag_space

def multihotEncodeLabels(labels: list, label_space: dict):
    '''
    Multi hot encode labels

    :labels: The labels to encode
    :label_space: All possible labels for this task
    '''
    onehot_vect = [0 for label in label_space] # initialize vector as all zeros
    for label in labels:
        onehot_vect[label_space[label]] = 1
    return onehot_vect
    

def loadCorpus():
    tag2idx = {} # key tag, value index
    idx2tag = {}
    train_data_unencoded = []
    for filename in os.listdir('data/bangor_miami_corpus/'):
        print(filename + '\n')
        most_recent_speaker = None
        with open('data/bangor_miami_corpus/' + filename, 'r') as file:
                headers = file.readline().split('\t')
                print(headers)
                header_idx = {}
                i = 0
                for header in headers:
                    header_idx[header] = i
                    i += 1
                del i
                print(header_idx)
                for line in file:
                    if re.match(r'\([0-9]+ rows\)', line):
                        continue # the last line of each file tells the number of rows in the file, ignore
                # read the input and re-tokenize
                    try:
                        split_line = line.split('\t')
                        word = split_line[3]
                        annotation = split_line[4]
                        #lang_id = split_line[8]
                        #speaker = split_line[header_idx['speaker']]
                        # get morphological tags
                        morph_tags = []
                        # the data set may contain multiple annotations, we only use the first one
                        skip = 0
                        for i, tag in enumerate(annotation.split(".")):
                            if skip:
                                skip -= 1
                                continue
                            if i < 1:
                                continue
                            if "+" in tag:
                                continue
                            if tag == "[or]":
                                skip = 1 # skip the next tag as well
                                continue
                            if tag in ["PRES", "PAST", "M", "F"]:
                                if tag not in tag2idx:
                                    tag2idx[tag] = len(tag2idx)
                                    idx2tag[len(idx2tag)] = tag
                                morph_tags.append(tag)
                            print("word", word, "tag", tag)
                        #if len(morph_tags) > 0:
                        train_data_unencoded.append([word, morph_tags])
                    except Exception as e:
                        print(line, e)
                        quit()
                    #    print("!!", e)
        break # only use first file in corpus
    # once all data has been read, one hot encode the labels
    train_data = []
    sentence_text = []
    sentence_tags = []
    for entry in train_data_unencoded:
        #print("word", word)
        word = entry[0]
        tags = entry[1]
        sentence_text.append(word)
        sentence_tags.append(multihotEncodeLabels(tags, tag2idx))
        if word in [".", "!", "?"]:
            train_data.append({"words" : sentence_text, "tags" : sentence_tags})
            sentence_text = []
            sentence_tags = []
    return train_data, tag2idx, idx2tag

def prediction_to_tags(sentence, predictions, idx2tag):
    print("predictions", predictions.shape)
    for i, prediction in enumerate(predictions):
        for j, logit in enumerate(prediction):
            if logit >= 0:
                print(sentence[i], idx2tag[j])
            else:
                print("logit <= 0")
    return

if __name__ == '__main__':
    print(sys.argv)
    tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
    classifier = MBERT_Tagger(tokenizer, 6, 4)
    bangor_miami_corpus, tag2idx, idx2tag = loadCorpus()

    if sys.argv[1] == "train":
        # train classifier
        classifier.enable_gradients()
        criterion = nn.BCEWithLogitsLoss()
        optimizer = optim.SGD(classifier.parameters(), lr=0.01)
        TRAIN_EPOCHS = 1
        point_counter = 0
        corpus_size = len(bangor_miami_corpus)
        for epoch in range(TRAIN_EPOCHS):
            print("Epoch: ", epoch+1)
            for data_point in bangor_miami_corpus:
                #print(data_point)
                optimizer.zero_grad()
                output = classifier(data_point["words"])
                loss = criterion(output, torch.tensor(data_point["tags"], dtype=float))
                loss.backward()
                optimizer.step()
                point_counter += 1
                if point_counter % 100 == 0:
                    print(data_point)
                    print("loss", loss)
                    print(str(point_counter) + "/" + str(corpus_size))
        torch.save(classifier.state_dict(), "MBERT-MORPH-Tagger-1-epoch.pt")

    elif sys.argv[1] == "eval":
        classifier.state_dict(torch.load('models/MBERT-MORPH-Tagger-1-epoch.pt')) # load the saved model weights
        classifier.eval()

        predictions = classifier(["Ella", "no", "sabe", "hacer", "la", "macerena", "."])
        prediction_to_tags(["Ella", "no", "sabe", "hacer", "la", "macerena", "."], predictions, idx2tag)

        predictions = classifier(["I'm", "going", "to", "school", "after", "I", "drop", "her", "off", "at", "home", "."])
        prediction_to_tags(["I'm", "going", "to", "school", "after", "I", "drop", "her", "off", "at", "home", "."], predictions, idx2tag)