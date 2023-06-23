"""
This is a script for generating graphs for the visualization of the usage of a specific word, filtered by lexical class.

It takes as input a file path to a .cha file that has %pos annotation tiers
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from util import extract_occurances_and_times_from_cha, convert_milliseconds_to_seconds, count_target_word_occurences

if __name__ == "__main__":
    # Example usage: python3 time_distribution_graph.py 107_spanish.cha la/DET/PRON la/DET la/PRON
    cha_file = sys.argv[1]
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