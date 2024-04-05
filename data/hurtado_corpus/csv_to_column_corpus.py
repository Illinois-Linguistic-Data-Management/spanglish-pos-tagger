import csv

with open('hurtado.corpus', 'w') as out_file:
    with open ('POS_data.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        cur_sentence = None
        for row in csv_reader:
            if not cur_sentence:
                cur_sentence = row['Sentence']
            elif cur_sentence and row['Sentence'] != cur_sentence:
                out_file.write('\n')
                cur_sentence = row['Sentence']
            if row["upos"] == "CLAN":
                continue # skip these, they are not actually part of the standard UPOS tagset
            out_file.write(f'{row["token"]} {row["upos"]}\n')