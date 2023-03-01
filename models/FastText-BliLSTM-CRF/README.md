This approach is very similar to that of [AlGhamdi and Diab 2019](https://aclanthology.org/W19-1410/)
It is similar in that the model uses a BiLSTM-CRF for the neural network architecture with a mix of monolingual training samples from each language.
It is different in that it uses monolingual English and monolingual Epanish [FastText](https://arxiv.org/abs/1607.04606) pretrained word embeddings that are concatenated together to produce bilingual embeddings
rather than using a translation matrix.