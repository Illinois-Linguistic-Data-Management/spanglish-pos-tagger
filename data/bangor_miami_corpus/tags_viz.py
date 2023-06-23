import os, csv
from matplotlib import pyplot as plt

data = {}
words = 0
for file in os.listdir('data/bangor_miami_corpus/'):
    if file.split(".")[-1] == "tsv":
        with open ('data/bangor_miami_corpus/' + file, 'r') as tsv:
            reader = csv.DictReader(tsv, delimiter='\t')
            for row in reader:
                try:
                    word = row["surface"]
                    tag = row["auto"].split(".")[1]
                    print(tag, word)
                    if tag not in data:
                        data[tag] = 1
                    else:
                        data[tag] += 1
                    words += 1
                except:
                    pass

data = {k: v for k, v in reversed(sorted(data.items(), key=lambda item: item[1])) }

common = {}
uncommon = {}
for d in data:
    if data[d] > 50:
        common[d] = data[d]
    else:
        uncommon[d] = data[d]

print(common, len(common), sum(common.values()), common.keys(), len(common.keys()))
print(uncommon, len(uncommon), sum(uncommon.values()))
print(data, len(data), sum(data.values()))
print(words)

plt.rc('font', size=6)
plt.bar([x for x in common.keys()], [y for y in common.values()])
plt.show()

plt.rc('font', size=5)
plt.bar([x for x in uncommon.keys()], [y for y in uncommon.values()])
plt.show()

plt.rc('font', size=16)
fig, ax = plt.subplots()
slice_sizes = [sum(common.values()) /  sum(data.values()), sum(uncommon.values()) / sum(data.values())]
ax.pie(slice_sizes, labels=['common', 'uncommon'], autopct='%1.1f%%')
plt.show()