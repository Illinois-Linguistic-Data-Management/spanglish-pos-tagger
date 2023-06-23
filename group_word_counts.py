import os, sys, csv

dir = f'/Users/ben/Documents/school/spanglish-tagger-new/lexical_analysis_data_frames/word_counts_{sys.argv[1]}'
data = {}
for filename in os.listdir(dir):
    if filename.split(".")[-1] == "csv":
        with open(f'{dir}/{filename}', 'r') as file:
            reader = csv.DictReader(file, delimiter=',')
            for row in reader:
                if row['word'] not in data:
                    data[row['word']] = (int(row['frequency']), row['language'])
                else:
                    data[row['word']] = (int(data[row['word']][0]) + int(row['frequency']), row['language'])

with open(f'{dir}/group_word_frequencies.csv', 'w') as file:
    file.write(f'word,frequency,language\n')
    for x in data:
        file.write(f'{x},{data[x][0]},{data[x][1]}\n')