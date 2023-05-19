"""
This is a script for generating graphs for the visualization of the usage of a specific word, filtered by lexical class.

It takes as input a file path to a .cha file that has %pos annotation tiers
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

def count_target_word_occurences(line:str, target_word:str, target_lexical_classes:str=None):
    """
    Inputs:
        - line: %pos tier line from a .cha file, the whole raw string
        - target_word: the word to look for
        - target_lexical_class: (optional) the word must also belong to this lexical class
    Outputs:
        The number of times the targe word appears in the input string
    """
    tokens = line.split(" ") # split up tokens by white space
    if tokens[0] != "%pos:":
        raise ValueError("count_target_word_occurences expects a %pos tier as input")
    del tokens[0] # now we can ignore that

    # now actually count occurances
    occurances = 0
    for token in tokens:
        word = token.split(".")[0]
        lexical_class = token.split(".")[1]
        if word == target_word and lexical_class in target_lexical_classes:
            occurances += 1
    return occurances

def convert_milliseconds_to_seconds(timestamp: str):
    # first filter out any "weird" characters
    milliseconds = ""
    for char in timestamp:
        if char.isalnum():
            milliseconds += char
    # Convert milliseconds to seconds and round to nearest integer
    total_seconds = round(float(milliseconds) / 1000.0)
    # Calculate minutes and seconds
    minutes, seconds = divmod(total_seconds, 60)
    # Return formatted string
    return f"{minutes}:{str(seconds).zfill(2)}"

def extract_occurances_and_times_from_cha(filepath: str, target_word:str, target_lexical_classes:list=None):
    """
    Inputs:
        - filepath: A path to a .cha file that has been annotated with %pos annotation tiers.
    Outputs:
        A list of tuples of the format (word_occurances, utterance_end_timestamp)
    """
    result = []
    with open(filepath, 'r', encoding='utf-8') as cha_file:
        timestamp = 0
        for line in cha_file:
            if "%pos" in line[0:5]:
                result.append((count_target_word_occurences(line, target_word, target_lexical_classes), convert_milliseconds_to_seconds(timestamp)))
            elif "PAR:" in line[0:5]:
                timestamp = (line.split(" ")[-1]).split("_")[-1] # the timestamp is at the very end of the line
    return result

if __name__ == "__main__":
    # Example usage: python3 time_distribution_graph.py 107_spanish.cha la/DET/PRON la/DET la/PRON
    cha_file = sys.argv[1]
    print(sys.argv)
    argc = 0
    for arg in sys.argv:
        argc += 1
        if argc <= 2:
            continue # ignore the file name argument

        word = arg.split("/")[0]
        lexical_classes = arg.split("/")
        print(lexical_classes)

        data = extract_occurances_and_times_from_cha(cha_file, word, lexical_classes)
        Ys = [datapoint[0] for datapoint in data] # the counts will be the heights or "Ys" for the chart
        Xs = [datapoint[1] for datapoint in data] # the timestamp will be the "Xs" for the chart

        fig, ax = plt.subplots()
        bars = ax.bar(Xs, Ys)

        bar_locations = np.arange(len(Xs))
        num_ticks = 8
        min_val = min(bar_locations)
        max_val = max(bar_locations)

        # generate num_ticks evenly spaced numbers between min_val and max_val
        ticks = np.linspace(min_val, max_val, num_ticks)

        # Assign these to the x-ticks
        ax.set_xticks(ticks)

        ax.set_yticks(np.arange(min(Ys), max(Ys)+1, 1))
        plt.show()