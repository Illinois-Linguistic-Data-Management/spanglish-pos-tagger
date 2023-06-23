import os, re, sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import f_oneway
from util import extract_occurances_and_times_from_cha, convert_milliseconds_to_seconds, count_target_word_occurences

def mins_to_secs(mins: str):
    minutes = mins.split(":")[0]
    seconds = mins.split(":")[1]
    return (int(minutes)*60) + int(seconds)

def count_usage(group, words):
    dir = f'../transcriptions/Tagged Transcriptions (group {str(group)})'
    data = {}
    for file in os.listdir(dir):
        if ".cha" in file:
            participant_num = re.search(r'\d+', file).group(0)
            extracted = extract_occurances_and_times_from_cha(f'{dir}/{file}', words, ['PRON'])
            for d in extracted:
                if participant_num not in data:
                    data[participant_num] = d[0]
                else:
                    data[participant_num] += d[0]
    return data

def graph_usage_by_group(group, words):
    data = count_usage(group, words)
    plt.bar([x for x in data.keys()], [y for y in data.values()])
    plt.show()

def graph_direct_obj_pronouns():
    graph_usage_by_group(100, ['lo', 'la'])
    graph_usage_by_group(200, ['lo', 'la'])
    #graph_usage_by_group(300)
    #graph_usage_by_group(400)
    graph_usage_by_group(500, ['lo', 'la'])
    graph_usage_by_group(600, ['lo', 'la'])
    graph_usage_by_group(700, ['lo', 'la'])

def graph_subj_pronouns():
    graph_usage_by_group(100, ['él', 'ella'])
    graph_usage_by_group(200, ['él', 'ella'])
    #graph_usage_by_group(300)
    #graph_usage_by_group(400)
    graph_usage_by_group(500, ['él', 'ella'])
    graph_usage_by_group(600, ['él', 'ella'])
    graph_usage_by_group(700, ['él', 'ella'])

def count_3rd_person_pronoun_usages(group):
    obj = count_usage(group, ['lo', 'la'])
    subj = count_usage(group, ['él', 'ella'])

    combined = {}
    for participant in obj:
        if participant not in combined:
            if participant in obj and participant in subj:
                combined[participant] = [subj[participant], obj[participant]]
            elif participant in obj and participant not in subj:
                combined[participant] = [0, obj[participant]]
            elif participant not in obj and participant in subj:
                combined[participant] = [subj[participant], 0]
    return combined

def pronoun_anova():
    print(list(count_3rd_person_pronoun_usages(500).values()))
    return f_oneway(
        [x[1] for x in list(count_3rd_person_pronoun_usages(100).values())],
        [x[1] for x in list(count_3rd_person_pronoun_usages(200).values())],
        [x[1] for x in list(count_3rd_person_pronoun_usages(500).values())],
        [x[1] for x in list(count_3rd_person_pronoun_usages(600).values())],
        [x[1] for x in list(count_3rd_person_pronoun_usages(700).values())]
    )

def graph_combined(group):
    combined = count_3rd_person_pronoun_usages(group)
    X = [x for x in combined.keys()]
    Ysubj = [y[0] for y in combined.values()]
    Yobj = [y[1] for y in combined.values()]
    
    X_axis = np.arange(len(X))
    
    plt.bar(X_axis - 0.2, Ysubj, 0.4, label = '3rd Person Subj Pron')
    plt.bar(X_axis + 0.2, Yobj, 0.4, label = '3rd Person Obj Pron')
    
    plt.xticks(X_axis, X)
    plt.xlabel("Participant")
    plt.ylabel("Number of Usages")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    
    graph_direct_obj_pronouns()
    
    print(pronoun_anova())