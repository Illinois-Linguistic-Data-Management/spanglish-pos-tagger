# [Bangor Miami Corpus](http://bangortalk.org.uk/speakers.php?c=miami)

This corpus contains transcripts of recorded conversations between L1 Spanish L2 English speakers in Miami, Florida. Their conversations often feature code switching, making it an ideal training set for our bilingual models.

## Data preparation and preprocessing

I've chosen to work with the herring sub corpus, specifically the tab-separated-values formatted files. TSV is a convenient format because tabs, unlike commas, are generally not meaningful in transcriptions of dialog while using a format like CSV would be confusing because not all commas we would want to use as a delimiter.

The biggest challenge of working with this dataset was that the corpus uses a different tagset than the [universal dependencies tagset](https://universaldependencies.org/u/pos/). To convert the Bangor Miami tags to Universal Dependency POS tags I used a simple set of rules to translate the most frequent tags in the Bangor Miami corpus. Tags found less than 40 times in the corpus were converted to `X` for unknown. The code for this can be found in `convert_to_UD.py`