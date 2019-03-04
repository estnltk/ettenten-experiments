# Output is a csv-file where all files with the total number of detected attributes are presented.

from estnltk import Text
import os
from paragraphweblanguagescoreretagger import ParagraphWebLanguageScoreRetagger
from estnltk.converters import json_to_text
import csv
from collections import defaultdict

cwd = os.getcwd()
path = os.path.join(cwd, "kirjak_vs_mittekirjak_ettenten_tagged") 

weblang_tagger=ParagraphWebLanguageScoreRetagger()

info_all=[] # all texts and their total scores of attributes 

for file in os.listdir(path):
    file_location = os.path.join(path, file)
    if "json" in file_location:
        info_files=defaultdict(list) # scores of attributes of paragraphs
        filename=file_location.split("\\")[-1]
        info_files["filename"]=[filename]
        text = json_to_text(file=file_location)
        weblang_tagger.retag(text)
        
        if "mittekirjak" in filename:
            info_files["doc_category"].append("mittekirjak")
        else:
            info_files["doc_category"].append("kirjak")
            
        for i in text.paragraphs.attributes:
            info_files[i].append(sum(text.paragraphs[i]))
        info_all.append(info_files)
        
with open ("weblang_scores_csv.csv","w") as csvfile:
    fieldnames=['filename', "doc_category"]
    for i in text.paragraphs.attributes:
        fieldnames.append(i)
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for i in info_all:
        for k,v in i.items():
            i[k] = v[0]
        writer.writerow(i)
