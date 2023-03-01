## BERT-BETO Stacked RNN

This model uses the contextualized pretrained embeddings [BERT](https://arxiv.org/abs/1810.04805) and its spanish adaptation [BETO](https://github.com/dccuchile/beto) concatenated together.

The embeddings are then passed through a RNN for classification. This turns out not to be the best way to fine tune the embeddings, it performs poorly.