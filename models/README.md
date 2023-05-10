# Models

## Part of Speech Tagging

### Fine Tuned Multilingual BERT with CRF


### BiLSTM-CRF with Muse Projected Bilingual Word Embeddings and Naive Bayes Language ID

Early bilingual POS tagging systems utilized various token level language identification techniques in combination with a multi-class classification technique. [Part of Speech Tagging for Code Switched Data 2016](https://arxiv.org/pdf/1909.13006.pdf), [Joint Part-of-Speech and Language ID Tagging for Code-Switched Data 2018](https://aclanthology.org/W18-3201/)

This model builds on those works and nearly replicates [Leveraging Pretrained Word Embeddings for Part-of-Speech Tagging of Code Switching Data 2019](https://aclanthology.org/W19-1410/) which acheives state of the art results by training a BiLSTM-CRF neural network architecture that leverages pretrained word embeddings, which have been shown to greatly improve model accuracy when the training dataset is small [Efficient Estimation of Word Representations in
Vector Space 2013](https://arxiv.org/pdf/1309.4168.pdf).

This model uses a simple language model based on 6 grams of characters using an MLE based on Naive Bayes with Laplace smoothing to classify individual tokens as either English or Spanish.
This is used to decide whether to use English or Spanish word embeddings. [Egnlish and Spanish Crosslingual Muse Embeddings](https://github.com/facebookresearch/MUSE), which are [FastText](https://arxiv.org/abs/1607.04606) embeddings that have been projected to a single vector space using a translation algorithm like that proposed in [Exploiting Similarities among Languages for Machine Translation](https://arxiv.org/pdf/1309.4168.pdf).
The embeddings are used as input for a bidirectional LSTM network that uses conditional random fields for classification.

The model was trained over a shuffled mix of a monolingual English corpus and a Spanish monolingual corpus from the [Universal Dependencies Treebank](https://github.com/UniversalDependencies) and the code switched [Bangor Miami Corpus](http://bangortalk.org.uk/speakers.php?c=miami) which.

## Prototype Models

### BiLSTM FastText Stacked Monolingual

#### Description
This approach uses a bidirectional long short term memory network (BiLSTM) as a multi class sequence classifier similar to the first model from [Soto & Hirschberg 2018](https://aclanthology.org/W18-3201/)
The feature set is different however, as I use pretrained [FastText](https://arxiv.org/abs/1607.04606) English and Spanish word embeddings to leverage word knowledge outside this training set.


#### Model Intuition

Although many words only have a single syntactic/part-of-speech category (eg "the" or "cat"), there are many words which can take on one of many syntactic roles. For example, in the sentences "Can you call me after work?" and "I missed your call while I was at work", the word "call" can be either a verb as in the first sentence or a noun as in the second sentence. [The lexical nature of syntactic ambiguity resolution, MacDonald, M. C., Pearlmutter, N. J., & Seidenberg, M. S. (1994)](https://pubmed.ncbi.nlm.nih.gov/7984711/) provides an excellent overview of the problem of syntactic ambiguity in language. They argue that context is the key to decoding syntactic ambiguity, specifically a speaker/processor's knowledge of the syntactic constraints of a language and knowledge of semantic biases in language including thematic roles and plausibility, much of which they argue can be derived from knowledge of lexical frequency biases observed in language. The idea behind this model is that the Skip-Gram language modeling objective, introduced in [Mikolov et al's Efficient Estimation of Word Representations in Vector Space (2013)](https://arxiv.org/pdf/1309.4168.pdf) and utilized in FastText, can encode both syntactic and semantic information about a word into dense vector representations which gives the neural network an idea of how words are related to each other. [Elman, J. L. (1990). Finding structure in time](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog1402_1) demonstrated that recurrent neural networks do an excellent job of discovering contextual relationships in time series and natural language as they pass information about different words in a series from one step to another, providing a sort of short term memory for the model, an improvement over generic feed-forward neural networks which evaluate each input independently.

MacDonald, Pearlmutter & Seidenberg note that long-distance dependencies pose a challenge for learning local syntactic constraints, stating that "during comprehension, the processor must somehow keep track of a filler and match it with an appropriate gap location over a potentially long distance". As an improvement upon Elman's work, [Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. Neural Computation](https://dl.acm.org/doi/10.1162/neco.1997.9.8.1735) introduces the concept of additional memory cells to be used when computing the hidden states between tokens/time-steps. 
For this model I chose a variant of the LSTM architecture as I hypothesize that the LSTM gates will provide the network with a mechanism to keep track of long distance dependencies, aiding in the learning of syntactic and semantic constraints to guide the neural network in the task of syntactic disambiguation.

MacDonald, Pearlmutter & Seidenberg also discuss garden path sentences such as "the horse raced past the barn fell" in which the language processor is intially "tricked" or guided down the wrong path by expectations about structural frequencies and must re-evaluate the original parse after encountering some new information toward the end of the phrase. To address this challenge, I decided to use the bidirectional variant of the long short term memory network based on [Schuster and Paliwal's Bidirectional Recurrent Neural Networks (1997)](https://ieeexplore.ieee.org/document/650093) in which hidden states produced by evaluating the input starting from both directions is concatenated together in order to allow the network to evaluate earlier tokens with contextual knowledge of tokens appearing later in phrase.

### BiLSTM-CRF FastText Stacked Monolingual

The same as the previously mentioned model except the classification layer uses [Conditional Random Fields; Lafferty, McCallum, Pereira (2001)](https://repository.upenn.edu/cgi/viewcontent.cgi?article=1162&context=cis_papers).

#### Model Intuition

CRFs were designed specifically to label sequence data, which is exactly the same sort of task as part of speech tagging as we take a series of tokens as input and a series labels as output. In a CRF, the neighboring tokens are used in calculating label scores and feature a global normalization function over the probabilities of *all* possible label sequences. This allows CRFs to "relax strong independence assumptions" made by most generative models such as Gaussian Descrimitive Analysis and Hidden Markov Models. This is especially important to the task of part-of-speech tagging as MacDonald et al highlights the role of syntactic contextual contraints in part of speech disambiguation, meaning the lexical classes of words previously seen in a sentence clearly influence syntactic parsing of words seen later on in a sentence. Combining the recurrent neural network architecture with conditional random fields by using the hidden states from a BiLSTM as features for a CRF allows the model to learn contextual relationships in two distinct different ways.

### BERT-BETO Stacked RNN

This model uses the contextualized pretrained embeddings from [BERT](https://arxiv.org/abs/1810.04805) and its spanish adaptation [BETO](https://github.com/dccuchile/beto) concatenated together.

The embeddings are then passed through a RNN for classification. The performance turned out rather poor.

## Morhological Tagging

### MBERT Morphological Tagger

This program implements a multi label classifier from fine tuned multilingual BERT word embeddings.

`MBERT_morph_tagger.py` specifically trains on the Bangor Miami corpus.

It currently only supports tags for gender and tense as a proof-of-concept.