# This script is for testing purposes. 
# Helps to find a threshold value where files with a score above that value can be categorized as "mittekirjak"

import csv
from sklearn import metrics
from sklearn.metrics import precision_score
from collections import defaultdict

all_summaries=[]
true_category=[]

only_docs_agreement_3 = True # False - use all files; True - use files that were labelled exactly the same by 3 people

def get_info(reader):
    attr_sum=0
    for i in row[3:]:
        number=int(i)
        attr_sum+=number
    summary=attr_sum/int(row[2])
    true_category.append(row[1])
    all_summaries.append(summary)

with open('weblang_scores.csv', newline='') as f:
    reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
    headers=next(reader)
    if only_docs_agreement_3==False:
        for row in reader:
            get_info(row)
            
    if only_docs_agreement_3==True:
        all_agreed=[]
        with open('agreement_scores_kirjak_mittekirjak.csv', newline='') as f:
            reader2 = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
            headers2=next(reader2)
            for row2 in reader2:
                if row2[1]=="3":
                    all_agreed.append(row2[0])
        for row in reader:
            if row[0] in all_agreed:
                get_info(row)
                            

threshold=[0.038,0.04,0.001,0.025]

print("Files with a summary above threshold are labelled as \"mittekirjak\".\n")

for i in threshold:
    pred_category=[]
    for summary in all_summaries:
        if summary > i:
            pred_category.append("mittekirjak")
        else: 
            pred_category.append("kirjak")
            
    print("Threshold: ",i)
    print("Precision: ",precision_score(true_category, pred_category, labels=['kirjak', 'mittekirjak'], average='binary', pos_label='mittekirjak'))
    print("Recall: ",metrics.recall_score(true_category, pred_category, labels=['kirjak', 'mittekirjak'], average='binary', pos_label='mittekirjak'))
    print("F1: ",metrics.f1_score(true_category, pred_category, labels=['kirjak', 'mittekirjak'], average='binary', pos_label='mittekirjak'))
    print("-----------------")
