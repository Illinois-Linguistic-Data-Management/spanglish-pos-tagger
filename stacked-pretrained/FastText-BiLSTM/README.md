# BiLSTM

This approach uses a bidirectional long short term memory network (BiLSTM) as a multilabel sequence classifier similar to the first model from [Soto & Hirschberg 2018](https://aclanthology.org/W18-3201/)
The feature set is different however, as I use pretrained [FastText](https://arxiv.org/abs/1607.04606) English and Spanish word embeddings to leverage word knowledge outside this training set.