import re
from utils.util import get_cha_files_in_dir

def get_data(path, data, participants):
    for file in get_cha_files_in_dir(path):
        participant_id = None # reset each time to be sure we dont assign the wrong id ever
        with open (file, 'r') as cha_file:
            for line in cha_file:
                if re.search(r'@Participants:', line):
                    participant_id = re.search(r'[0-9]+', line).group(0) # then assume this will always come before the actual words
                    if participant_id not in participants:
                        participants.append(participant_id)
                if "%pos:" in line:
                    tokens = [x.strip("\n") for x in line.split(" ") if x.strip("\n").replace('.', '').isalpha()]
                    for token in tokens:
                        if token.split(".")[-1] in ['SYM', 'X', 'PUNCT'] or token.split(".")[0] in ['xxx']:
                            continue # ignore non word tokens
                        if token not in data:
                            data[token] = {participant_id: 1}
                        elif participant_id not in data[token]:
                            data[token][participant_id] = 1
                        else:
                            data[token][participant_id] += 1

def write_frame(output_path, data, participants):
    with open(output_path, 'w') as outFile:
            # write header
            outFile.write('word,category')
            for participant_id in participants:
                outFile.write(f',{participant_id}')
            outFile.write('\n')
            # write the rest
            for token in data.keys():
                word = token.split(".")[0]
                category = token.split(".")[1]
                outFile.write(f'{word},{category}')
                for participant_id in participants:
                    if participant_id in data[token]:
                        outFile.write(f',{data[token][participant_id]}')
                    else:
                        outFile.write(',0')
                outFile.write('\n')

def gen_all_frame():
    data = {}
    participants = []
    get_data('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Tagged Transcriptions (group 100)', data, participants)
    get_data('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Tagged Transcriptions (group 200)', data, participants)
    get_data('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Tagged Transcriptions (group 300)', data, participants)
    get_data('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Tagged Transcriptions (group 400)', data, participants)
    get_data('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Tagged Transcriptions (group 500)', data, participants)
    get_data('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Tagged Transcriptions (group 600)', data, participants)
    get_data('/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Tagged Transcriptions (group 700)', data, participants)
    write_frame('word_counts_all.csv', data, participants)

def gen_group_frame(group):
    path = f'/Users/ben/Documents/school/spanglish-tagger-new/transcriptions/Tagged Transcriptions (group {str(group)})'
    output_path = f'word_counts_{group}.csv'
    data = {}
    participants = []
    get_data(path, data, participants)            
    write_frame(output_path, data, participants)

def gen_group_frames():
    gen_group_frame(100)
    gen_group_frame(200)
    gen_group_frame(300)
    gen_group_frame(400)
    gen_group_frame(500)
    gen_group_frame(600)
    gen_group_frame(700)
                
if __name__ == "__main__":
    gen_all_frame()