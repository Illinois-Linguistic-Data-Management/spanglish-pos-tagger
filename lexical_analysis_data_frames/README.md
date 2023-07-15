# Lexical Analysis Dataframes

This folder contains CSV files (dataframes) with information about the lexical usage of participants in the narrative task experiment.

Currently, there are two types of dataframes:

### Overall Counts

These dataframes provide a high level overview of the lexical choices for each narrative in the corpus.
The dataframes contain the following features:
* language: May be "eng" for English of "spa" for Spanish
* participant_id: The unique anonymized identifier for the participant that told the narrative
* words: The number of unique words, from each language and including disfluencies, used to tell the narrative
* minutes: The duration of the narrative in minutes, excluding any time in the recording annotated with the `[e]` exclusion tag.
* wpm: Words-per-minute. words/minutes
* types: The number of unique words, from each language and excluding disfluencies, used to tell the narrative.
* tokens: The number of total words used to tell the narrative. Repeated words get counted multiple times.
* ttr: Type-Token-Ratio. types/tokens
* english_types: The number of unique English words used to tell the narrative.
* english_tokens: The number of total English words used to tell the narrative. Repeated words get counted multiple times.
* english_ttr: The Type-Token-Ratio of English words used to tell the narrative.
* spanish_types: The number of unique Spanish words used to tell the narrative.
* spanish_tokens: The number of total Spanish words used to tell the narrative. Repeated words get counted multiple times.
* spanish_ttr: The Type-Token-Ratio of Spanish words used to tell the narrative.
* disfluencies: The number of disfluncies (eg "um" or "uh") found in the narrative transcription.
* fluency_score: The number of disfluencies divided by the number of total words.

### Word Frequencies

These dataframes provide more detailed data on the lexical choices for each narrative.

The header rows provide the following information:
* word: The surface form of the word found in the narrative transcript.
* lexical_category: The lexical category of the word (noun, verb, adjective, etc).
* word_type: "content" if the lexical category is one of ['NOUN', 'VERB', 'ADJ', 'ADV'], otherwise "functional"
* language: The language ID of the individual word

The rest of the rows have a participant ID on the left most column, and the following details are provided:
* words: The number of times each word is used by the participant to tell a narrative
* total_tokens
* total_types
* type_token_ratio
* content_tokens
* content_types
* content_ttr
* functional_content_tokens
* functional_content_types
* functional_content_ttr
* english_total_tokens
* english_total_types
* english_type_token_ratio
* english_content_tokens
* english_content_types
* english_content_ttr
* english_functional_content_tokens
* english_functional_content_types
* english_functional_content_ttr
* spanish_total_tokens
* spanish_total_types
* spanish_type_token_ratio
* spanish_content_tokens
* spanish_content_types
* spanish_content_ttr
* spanish_functional_content_tokens
* spanish_functional_content_types
* spanish_functional_content_ttr
* target_lang_mattr
* target_lang_mtld