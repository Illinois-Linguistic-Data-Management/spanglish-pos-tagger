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

These dataframes provide more detailed data on the lexical choices for each narrative,
listing all of the words used as well as the number of times each of those words was used to tell the narrative.
These dataframes contain the following features:
* word: The surface form of the word found in the narrative transcript.
* category: The lexical category of the word.
* participant_id: The rest of the columns correspond to a participant id, the value for that column describes how many times that participant used the word.