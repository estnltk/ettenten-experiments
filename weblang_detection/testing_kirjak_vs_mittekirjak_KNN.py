# This script is for testing purposes. 
# Helps to find if it is possible to categorize files as "kirjak"/"mittekirjak" by cosine / euclidean distance and KNN algorithm

import csv
from collections import defaultdict
import numpy as np
from nltk.cluster.util import cosine_distance, euclidean_distance
from sklearn.model_selection import KFold
from random import shuffle
from sklearn.metrics import precision_score
from sklearn import metrics

av_prec=[]
av_rec=[]
av_f1=[]

vectors=[]

with open('weblang_scores_csv.csv','r') as f:
    data=f.readlines()
header, rest=data[0], data[1:]
shuffle(rest)

for i in rest:
    i=i.strip()
    i=i.split(";")
    vectors.append(i[1:]) # results of 1 file
    
vectors=np.array(vectors)

kfold_number=4
k=3 #KNN
method=cosine_distance
#method=euclidean_distance

X_train_sets=[] # 4 trainingsets - finding similarities
X_test_sets=[] # 4 testsets

print("------------------------")
print("Corpus is divided into",kfold_number,"testgroups.")
print("Method:",method)
print("Value of k in KNN algorithm:",k,"\n")    

kf = KFold(n_splits=kfold_number)
KFold(n_splits=kfold_number, random_state=None, shuffle=False) # korpus jagatakse tükkideks
for train, test in kf.split(vectors):
    X_train, X_test = vectors[train], vectors[test]
    X_train_sets.append(X_train)
    X_test_sets.append(X_test)   

for testgroup,traingroup in zip(X_test_sets,X_train_sets):
    true=[] # results of all files
    pred=[]
    for i,i2 in zip(testgroup,enumerate(testgroup)):
        distances = []
        without_cat_test=np.array(i[1:],dtype=float) # only numerical attributes (without category of text)
        for t,t2 in zip(traingroup,enumerate(traingroup)):
            without_cat_train=np.array(t[1:],dtype=float)
            similarity=method(without_cat_test,without_cat_train) # finding similarity
            distances.append([similarity, t2[0], t[0], i2[0], i[0]])
        distances.sort()
        
        list_pred=[] # predicted categories of trainset texts
        list_true=[] # categories of testset texts (kirjak or mittekirjak)

        for i in distances[:k]:
            list_pred.append(i[2])
        list_true.append(i[4])

        true.append(list_true)
        pred.append(list_pred)

    true_y=[]    
    pred_y=[]

    for i,i2 in zip(true,pred): # finding the final prediction from k predicted categories
        true_y.append(i) # the actual category 
        if i2.count("mittekirjak") > i2.count("kirjak"):
            pred_y.append("mittekirjak")
        if i2.count("mittekirjak") < i2.count("kirjak"):
            pred_y.append("kirjak")
        
    flat_true=[item for sublist in true_y for item in sublist]
    
    prec=precision_score(flat_true, pred_y, labels=['kirjak', 'mittekirjak'], average='binary', pos_label='mittekirjak')
    print("Precision:",prec)
    av_prec.append(prec)
    rec=metrics.recall_score(flat_true, pred_y, labels=['kirjak', 'mittekirjak'], average='binary', pos_label='mittekirjak')
    print("Recall:",rec)
    av_rec.append(rec)
    f1=metrics.f1_score(flat_true, pred_y, labels=['kirjak', 'mittekirjak'], average='binary', pos_label='mittekirjak')
    print("F1:",f1)
    av_f1.append(f1)
    print("-----------")

print("Average precision:",sum(av_prec) / 4)
print("Average recall:",sum(av_rec) / 4)
print("Average F1:",sum(av_f1) / 4)
print("------------------------")

