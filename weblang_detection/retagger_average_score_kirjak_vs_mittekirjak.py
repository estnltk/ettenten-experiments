# Script gives an overview of how many features of web language there are on average in two different categories (kirjak vs mittekirjak) 

from estnltk import Text
import os
from paragraphweblanguagescoreretagger import ParagraphWebLanguageScoreRetagger
from estnltk.converters import json_to_text
from collections import defaultdict

cwd = os.getcwd()
path = os.path.join(cwd, "kirjak_vs_mittekirjak_ettenten_tagged")

weblang_tagger=ParagraphWebLanguageScoreRetagger(use_punct_reps=True)

info_kirjak=defaultdict(int) # features in kirjak-files
info_mittekirjak=defaultdict(int) # features in mittekirjak-files

for file in os.listdir(path):
    file_location = os.path.join(path, file)
    if "json" in file_location:
        filename=file_location.split("\\")[-1]
        text = json_to_text(file=file_location)
        weblang_tagger.retag(text)        
        for i in text.paragraphs.attributes:
            if "mittekirjak" in filename:
                info_mittekirjak["files"]+=1
                info_mittekirjak[i]=info_mittekirjak[i]+sum(text.paragraphs[i])
            else:
                info_kirjak["files"]+=1
                info_kirjak[i]=info_kirjak[i]+sum(text.paragraphs[i])       

for info_k,info_mk in zip(info_kirjak.items(),info_mittekirjak.items()):
    if (info_k[0] != "files" and info_k[0] != "word_count") and (info_mk[0] != "files" and info_mk[0] != "word_count"):
        outcome_k=round(info_k[1]/info_kirjak["files"],2)
        print("KIRJ: The average occurrence of attribute -",info_k[0],"- in a file:",outcome_k,". A total of",info_k[1],"occurrences in the corpus.")
        outcome_mk=round(info_mk[1]/info_mittekirjak["files"],2)
        print("MITTEKIRJ: The average occurrence of attribute -",info_mk[0],"- in a file:",outcome_mk,". A total of",info_mk[1],"occurrences in the corpus.")
        print("-------------")
