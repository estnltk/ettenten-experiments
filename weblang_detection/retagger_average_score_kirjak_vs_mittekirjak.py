# Script gives an overview of how many features of web language there are on average in two different categories (kirjak vs mittekirjak) 

import csv
from collections import defaultdict

info_kirjak=defaultdict(int) # features in kirjak-files
info_mittekirjak=defaultdict(int) # features in mittekirjak-files

with open('weblang_scores.csv', newline='') as f:
    reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
    headers=next(reader)
    for row in reader:
        for attr, header in zip(row[2:],headers[2:]):
            if "mittekirjak" in row[1]:
                info_mittekirjak["files"]+=1
                info_mittekirjak[header]=info_mittekirjak[header]+int(attr)
            else:
                info_kirjak["files"]+=1
                info_kirjak[header]=info_kirjak[header]+int(attr)
            
                
for info_k,info_mk in zip(info_kirjak.items(),info_mittekirjak.items()):
    if (info_k[0] != "files" and info_k[0] != "word_count") and (info_mk[0] != "files" and info_mk[0] != "word_count"):
        outcome_k=round(info_k[1]/info_kirjak["files"],2)
        print("KIRJ: The average occurrence of feature -",info_k[0],"- in a file:",outcome_k,". A total of",info_k[1],"occurrences in the corpus.")
        outcome_mk=round(info_mk[1]/info_mittekirjak["files"],2)
        print("MITTEKIRJ: The average occurrence of feature -",info_mk[0],"- in a file:",outcome_mk,". A total of",info_mk[1],"occurrences in the corpus.")
        print("-------------")          
