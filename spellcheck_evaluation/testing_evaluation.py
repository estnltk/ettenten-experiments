# Evaluation of spell-checker

import os
from estnltk.vabamorf import morf as vm
from sklearn import metrics
from sklearn.metrics import precision_score
from collections import defaultdict


cwd = os.getcwd()
path = os.path.join("ettenten-valik_tsv",'')

true=[]
pred=[]

spell_true=[]
spell_pred=[]

dict_sugg_correct=defaultdict(int)
dict_sugg_wrong=defaultdict(int)
dict_sugg_none=defaultdict(int)
dict_problematic=defaultdict(int)
dict_correct=defaultdict(int)
dict_ok_correct=defaultdict(int)
dict_ok_problematic=defaultdict(int)


for file in os.listdir(path):
    filename = os.path.join(path, file)
    if ".tsv" in filename:
        with open (filename, 'r',encoding="utf8") as f:
            row=f.read()
            row=row.split("\n")
            for i in row:
                i=i.split("\t")
                if len(i)!=0 and len(i)!=1:
                    if i[-1]!="Punct":
                        spell_check=vm.spellcheck([i[0]], suggestions=True)
                        if i[-1]!="Ok": # you can add here other tags to be left out from evaluation (to see how metrics change)
                            for item in spell_check:
                                # TESTING HOW WELL SPELLER RECOGNIZES MISTAKES
                                # If spelling is OK according to speller:
                                # OK
                                if item["spelling"]==True and item["text"].lower()==i[1].lower():
                                    true.append("correct")
                                    pred.append("correct")
                                    dict_correct[i[-1]]+=1
                                # Speller counts word as correct, but in corpus it has been normalized
                                elif item["spelling"]==True and item["text"].lower()!=i[1].lower():  
                                    true.append("wrong")
                                    pred.append("correct")
                                    dict_problematic[i[-1]]+=1
                                else:
                                    # If spelling is wrong according to speller:
                                    if item["spelling"]!=True:
                                        # Speller counts word as wrong, but in corpus it hasn't been normalized
                                        if item["text"].lower()==i[1].lower():
                                            true.append("correct")
                                            pred.append("wrong")
                                        else:
                                            # Speller counts word as wrong and in corpus it has been normalized
                                            true.append("wrong")
                                            pred.append("wrong")
                                        
                                        # TESTING HOW SUGGESTIONS ARE GIVEN BY SPELLER
                                        # If word is incorrect, but no suggestions is given
                                        if len(item["suggestions"])==0 and item["text"].lower()!=i[1].lower():
                                            spell_true.append("correct")
                                            spell_pred.append("wrong")
                                            dict_sugg_none[i[-1]]+=1
                                        else:
                                            find=0
                                            for sugg in item["suggestions"]:
                                                if find==0:
                                                    if sugg.lower() == i[1].lower():
                                                        find+=1
                                                        break
                                            # If suggestion matches with a normalized word
                                            if find > 0 and item["text"].lower()!=i[1].lower():
                                                spell_true.append("correct")
                                                spell_pred.append("correct")
                                                dict_sugg_correct[i[-1]]+=1
                                            # If suggestion doesn't match with a normalized word
                                            elif find==0 and item["text"].lower()!=i[1].lower():
                                                spell_true.append("correct")
                                                spell_pred.append("wrong")
                                                dict_sugg_wrong[i[-1]]+=1
                         
                        else:
                            if i[-1]=="Ok":
                                # POSSIBLE MISTAKES IN WORDS OF "OK"-GROUP
                                for item in spell_check:
                                    # If spelling is OK according to speller
                                    if item["spelling"]==True and item["text"].lower()==i[1].lower():
                                        true.append("correct")
                                        pred.append("correct")
                                        dict_ok_correct[i[-1]]+=1
                                    # If spelling is not OK according to speller, but word hasn't been normalized
                                    elif item["spelling"]==False and item["text"].lower()==i[1].lower():
                                        true.append("correct")
                                        pred.append("wrong")
                                        dict_ok_problematic[i[-1]]+=1
                                        
                                        
print("How well are problematic words found by speller?")
print("Precision: ",precision_score(true, pred, labels=['correct', 'wrong'], average='binary', pos_label='wrong'))
print("Recall: ",metrics.recall_score(true, pred, labels=['correct', 'wrong'], average='binary', pos_label='wrong'))
print("F1: ",metrics.f1_score(true, pred, labels=['correct', 'wrong'], average='binary', pos_label='wrong'))
print("-------------------")
print("How well can speller give correct suggestions (in conditions, where a word has been normalized and speller says spelling of the original word is wrong)?")
print("Accuracy score: ",metrics.accuracy_score(spell_true, spell_pred))

print("---------------------------------")
     
print("***","Speller: word correct; Corpus: word normalized:",sum(dict_problematic.values()),"\n",dict_problematic,"\n")
print("***","Speller: word correct; Corpus: word correct:",sum(dict_correct.values()),"\n",dict_correct,"\n")
print("***","Given suggestion == normalized word:",sum(dict_sugg_correct.values()),"\n",dict_sugg_correct,"\n")
print("***","Given suggestion != normalized word:",sum(dict_sugg_wrong.values()),"\n",dict_sugg_wrong,"\n")
print("***","Spelling is wrong, but no suggestions is given:",sum(dict_sugg_none.values()),"\n",dict_sugg_none,"\n")
print("***","Words of OK-group: speller says spelling is OK:",sum(dict_ok_correct.values()),"\n",dict_ok_correct,"\n")
print("***","Words of OK-group: speller says spelling is WRONG:",sum(dict_ok_problematic.values()),"\n",dict_ok_problematic,"\n")
                       