# BiLSTM CRF with Language ID + MUSE crosslingual word embeddings

Early bilingual POS tagging systems utilized various token level language identification techniques in combination with a multi-class classification technique. [Part of Speech Tagging for Code Switched Data 2016](https://arxiv.org/pdf/1909.13006.pdf), [Joint Part-of-Speech and Language ID Tagging for Code-Switched Data 2018](https://aclanthology.org/W18-3201/)

This model builds on those works and nearly replicates [Leveraging Pretrained Word Embeddings for Part-of-Speech Tagging of Code Switching Data 2019](https://aclanthology.org/W19-1410/) which acheives state of the art results by training a BiLSTM-CRF neural network architecture that leverages pretrained word embeddings, which have been shown to greatly improve model accuracy when the training dataset is small [Efficient Estimation of Word Representations in
Vector Space 2013](https://arxiv.org/pdf/1309.4168.pdf).

This model uses a simple 6-gram language model with Laplace smoothing to classify individual tokens as either English or Spanish.
This is used to decide whether to use English or Spanish word embeddings. [Egnlish and Spanish Crosslingual Muse Embeddings](https://github.com/facebookresearch/MUSE), which are [FastText](https://arxiv.org/abs/1607.04606) embeddings that have been projected to a single vector space using a translation algorithm like that proposed in [Exploiting Similarities among Languages for Machine Translation](https://arxiv.org/pdf/1309.4168.pdf).
The embeddings are used as input for a bidirectional LSTM network that uses conditional random fields for classification.

The model was trained over a shuffled mix of a monolingual English corpus and a Spanish monolingual corpus from the [Universal Dependencies Treebank](https://github.com/UniversalDependencies) and the code switched [Bangor Miami Corpus](http://bangortalk.org.uk/speakers.php?c=miami) which.