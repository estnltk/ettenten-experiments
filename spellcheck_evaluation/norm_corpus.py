# Creates a new corpus of tsv files 

import os
from estnltk import Text
from estnltk.taggers import VabamorfTagger
import re
from estnltk.vabamorf.morf import synthesize
from Levenshtein import distance
import sys
from estnltk.converters.cg3_annotation_parser import CG3AnnotationParser

morph_tagger = VabamorfTagger(guess=False,propername=False,disambiguate=False,phonetic=False)

cwd = os.getcwd()
path = os.path.join(cwd, "ettenten-valik") 
new_path = os.path.join("ettenten-valik_tsv",'') 

cases={"abes":"ab","adit":"adt","gen":"g","nom":"n","part":"p","term":"ter"}

manual_corrections={"süüa-juua":"süüa-juua"+"\t"+"süüa-juua"+"\t"+"Ok","L-S":"L-S"+"\t"+"L-S"+"\t"+"Name",
              "New Yorgist":"New Yorgist"+"\t"+"New Yorgist"+"\t"+"Name","20D/30D":"20D/30D"+"\t"+"20D/30D"+"\t"+"Abbrev_Num",
             "mp3-dega":"mp3-dega"+"\t"+"mp3-dega"+"\t"+"Abbrev_Num",
             "mp3-de":"mp3-de"+"\t"+"mp3-de"+"\t"+"Abbrev_Num",
             "S3-el":"S3-el"+"\t"+"S3-l"+"\t"+"Abbrev_Num","nr,`d":"nr,`d"+"\t"+"nr-d"+"\t"+"Abbrev",
              "}-ks":"}-ks"+"\t"+"}-ks"+"\t"+"Abbrev","jämedad/paksud":"jämedad/paksud"+"\t"+"jämedad/paksud"+"\t"+"Ok",
             "s.-tapead":"s.-tapead"+"\t"+"sitapead"+"\t"+"Spell_ED>1",
             "suhet-peret":"suhet-peret"+"\t"+"suhet-peret"+"\t"+"Ok",
             "sidemeid-tutvusi":"sidemeid-tutvusi"+"\t"+"sidemeid-tutvusi"+"\t"+"Ok",
             "6-megane":"6-megane"+"\t"+"6-megane"+"\t"+"Ok",
             "e-teenindusse":"e-teenindusse"+"\t"+"e-teenindusse"+"\t"+"Ok",
             "a-seadmetega":"a-seadmetega"+"\t"+"a-seadmetega"+"\t"+"Ok","15-ndal":"15-ndal"+"\t"+"15-ndal"+"\t"+"Ok",
              "5-ndale":"5-ndale"+"\t"+"5-ndale"+"\t"+"Ok","Võib-olla":"Võib-olla"+"\t"+"Võib-olla"+"\t"+"Ok",
              "30-aastaselt":"30-aastaselt"+"\t"+"30-aastaselt"+"\t"+"Ok",
              "-ah":"-ah"+"\t"+"ah"+"\t"+"Spell_ED_1","ja/või":"ja/või"+"\t"+"ja/või"+"\t"+"Ok",
              "kirelt":"kirelt"+"\t"+"kiirelt"+"\t"+"Spell_ED_1","Vaepeal":"Vaepeal"+"\t"+"Vahepeal"+"\t"+"Spell_ED_1",
              "Aitähh":"Aitähh"+"\t"+"Aitäh"+"\t"+"Spell_ED_1","aitähh":"aitähh"+"\t"+"aitäh"+"\t"+"Spell_ED_1",
              "ara":"ara"+"\t"+"ära"+"\t"+"Spell_Missing_Diacritics","miskiparast":"miskiparast"+"\t"+"miskipärast"+"\t"+"Spell_Missing_Diacritics",
              "A":"A"+"\t"+"A"+"\t"+"Ok","mai":"mai"+"\t"+"ma ei"+"\t"+"Spell_ED>1","Mai":"Mai"+"\t"+"ma ei"+"\t"+"Spell_ED>1",
              "väljavalitud":"väljavalitud"+"\t"+"välja valitud"+"\t"+"Spell_Missing_Space",
              "Me":"Me"+"\t"+"Me"+"\t"+"Name",
              "L-S":"L-S"+"\t"+"L-S"+"\t"+"Name","pealgi":"pealgi"+"\t"+"pealegi"+"\t"+"Spell_ED_1",
              "kiirest":"kiirest"+"\t"+"kiiresti"+"\t"+"Spell_ED_1",
              "alti":"alti"+"\t"+"alati"+"\t"+"Spell_ED_1","mittekeegi":"mittekeegi"+"\t"+"mitte keegi"+"\t"+"Spell_Missing_Space",
              "õppinud":"õppinud"+"\t"+"õppinud"+"\t"+"Ok","põhjendatud":"põhjendatud"+"\t"+"põhjendatud"+"\t"+"Ok",
              "syya":"syya"+"\t"+"süüa"+"\t"+"Spell_Missing_Diacritics","oller":"oller"+"\t"+"olles"+"\t"+"Spell_ED_1",
              "väljaminnes":"väljaminnes"+"\t"+"välja minnes"+"\t"+"Spell_Missing_Space",
              "poleksi":"poleksi"+"\t"+"polekski"+"\t"+"Spell_ED_1",
              "tia":"tia"+"\t"+"tea"+"\t"+"Spell_ED_1",
              "kmaksis":"kmaksis"+"\t"+"maksis"+"\t"+"Spell_ED_1","käisgi":"käisgi"+"\t"+"käiski"+"\t"+"Spell_ED_1",
              "vötta":"vötta"+"\t"+"võtta"+"\t"+"Spell_Changed_Diacritics","ple":"ple"+"\t"+"pole"+"\t"+"Spell_ED_1",
              "plee":"plee"+"\t"+"pole"+"\t"+"Spell_ED>1","SuperCruise":"SuperCruise"+"\t"+"SuperCruise"+"\t"+"Name",
              "Tamakasuga":"Tamakasuga"+"\t"+"Tamakasuga"+"\t"+"Name","mp3-d":"mp3-d"+"\t"+"mp3-d"+"\t"+"Abbrev_Num",
              "4s-il":"4s-il"+"\t"+"4s-il"+"\t"+"Abbrev_Num","mp3-l":"mp3-l"+"\t"+"mp3-l"+"\t"+"Abbrev_Num",
              "rummstain_DuHast_(LIVE).mp3-ga":"rummstain_DuHast_(LIVE).mp3-ga"+"\t"+"rummstain_DuHast_(LIVE).mp3-ga"+"\t"+"Abbrev_Num",
              "LV`se":"LV`se"+"\t"+"LV"+"\t"+"Abbrev","LV`sel":"LV`sel"+"\t"+"LV-l"+"\t"+"Abbrev",
              "msnnis":"msnnis"+"\t"+"msnis"+"\t"+"Abbrev","msnis":"msnis"+"\t"+"msnis"+"\t"+"Abbrev","CMOS-ga":"CMOS-ga"+"\t"+"CMOS-ga"+"\t"+"Abbrev",
              "SEO’st":"SEO’st"+"\t"+"SEO’st"+"\t"+"Abbrev","M-st":"M-st"+"\t"+"M-st"+"\t"+"Abbrev",       
             }


parser = CG3AnnotationParser()

def use_edit_distance(analysis, form, i, i2, mult_anal):
    if analysis["case"][0] in cases.keys():
        form=analysis["number"][0]+ " " + cases[analysis["case"][0]]
        new_word=synthesize(analysis["lemma"], form=form)
    else:
        form=analysis["number"][0] + " " + analysis["case"][0]
        new_word=synthesize(analysis["lemma"], form=form)
    if len(new_word)>0:
        if i.lower() in new_word:
            info=i+"\t"+i+"\t"+"Ok"
            lines_list.append(info)
        elif analysis["case"][0] =="gen" or analysis["case"][0] =="part":
            if new_word[-1][-1] in ["a","e","i","o","u","õ","ä","ö"] and new_word[-1][-1]!=i[-1]:
                if analysis["case"][0]=="gen":
                    info=i+"\t"+new_word[-1]+"\t"+"Spell_Unknown_Gen"
                    lines_list.append(info)
                else:
                    info=i+"\t"+new_word[-1]+"\t"+"Spell_Unknown_Part"
                    lines_list.append(info)
            elif len(re.findall("ä|Ä|ö|Ö|ü|Ü|Õ|õ", i)) < len(re.findall("ä|Ä|ö|Ö|ü|Ü|Õ|õ", new_word[-1])):
                info=i+"\t"+new_word[-1]+"\t"+"Spell_Missing_Diacritics"
                lines_list.append(info)
            else:
                ld=distance(i.lower(), new_word[-1].lower())
                if ld > 1:
                    new_form=analysis["ending"].replace("_","")
                    new_word2 = analysis["lemma"]+new_form
                    if new_word2.lower() == i.lower():
                        if i[0].isupper():
                            info=i+"\t"+new_word2.capitalize()+"\t"+"Ok"
                            lines_list.append(info)
                        else:
                            info=i+"\t"+new_word2+"\t"+"Ok"
                            lines_list.append(info)
                    else:
                        if i[0].isupper():
                            info=i+"\t"+new_word[-1].capitalize()+"\t"+"Spell_ED>1"
                            lines_list.append(info)
                        else:
                            info=i+"\t"+new_word[-1]+"\t"+"Spell_ED>1"
                            lines_list.append(info)
                elif ld == 1:
                    if i[0].isupper():
                        info=i+"\t"+new_word[-1].capitalize()+"\t"+"Spell_ED_1"
                        lines_list.append(info)
                    else:
                        info=i+"\t"+new_word[-1]+"\t"+"Spell_ED_1"
                        lines_list.append(info)
                elif ld == 0:
                    if i[0].isupper():
                        info=i+"\t"+new_word[-1].capitalize()+"\t"+"Ok"
                        lines_list.append(info)
                    else:
                        info=i+"\t"+new_word[-1]+"\t"+"Ok"
                        lines_list.append(info)                          
                            
        else:
            ld=distance(i.lower(), new_word[-1].lower())
            if len(re.findall("ä|Ä|ö|Ö|ü|Ü|Õ|õ", i)) < len(re.findall("ä|Ä|ö|Ö|ü|Ü|Õ|õ", new_word[-1])):
                info=i+"\t"+new_word[-1]+"\t"+"Spell_Missing_Diacritics"
                lines_list.append(info)  
            elif ld > 1:
                new_form=analysis["ending"].replace("_","")
                new_word2 = analysis["lemma"]+new_form
                if new_word2.lower() == i.lower():
                    if i[0].isupper():
                        info=i+"\t"+new_word2.capitalize()+"\t"+"Ok"
                        lines_list.append(info)
                    else:
                        info=i+"\t"+new_word2+"\t"+"Ok"
                        lines_list.append(info)
                else:
                    if i[0].isupper():
                        info=i+"\t"+new_word[-1].capitalize()+"\t"+"Spell_ED>1"
                        lines_list.append(info)
                    else:
                        info=i+"\t"+new_word[-1]+"\t"+"Spell_ED>1"
                        lines_list.append(info)
            elif ld == 1:
                if i[0].isupper():
                    info=i+"\t"+new_word[-1].capitalize()+"\t"+"Spell_ED_1"
                    lines_list.append(info)
                else:
                    info=i+"\t"+new_word[-1]+"\t"+"Spell_ED_1"
                    lines_list.append(info)
            elif ld == 0:
                if i[0].isupper():
                    info=i+"\t"+new_word[-1].capitalize()+"\t"+"Ok"
                    lines_list.append(info)
                else:
                    info=i+"\t"+new_word[-1]+"\t"+"Ok"
                    lines_list.append(info)
           
    else:
        if analysis["case"][0] in cases.keys():
            form=analysis["number"][0]+ " " + cases[analysis["case"][0]]
            new_word=synthesize(i2[0].lemma, form=form)
        else:
            form=analysis["number"][0]+ " " + analysis["case"][0]
            new_word=synthesize(i2[0].lemma, form=form)
        if len(new_word)>0 and i.lower() in new_word:
            info=i+"\t"+i+"\t"+"Ok"
            lines_list.append(info)
        else:
            if mult_anal==False:
                add_manual_correction_if_available(i)

def add_manual_correction_if_available(i): 
    if i in new_analyses.keys():
        info=new_analyses[i]
        lines_list.append(info)
    else:
        info=i+"\t"+"-"+"\t"+"Spell_Unknown"
        lines_list.append(info)


def synt(i,analysis,tag,mult_anal):
    if analysis["case"][0] in cases.keys():
        form=analysis["number"][0]+ " " + cases[analysis["case"][0]]
        new_word=synthesize(analysis["lemma"], form=form)
        if len(new_word)>0 and i.lower() in new_word:
            info=i+"\t"+i+"\t"+tag
            lines_list.append(info)
        else:
            if mult_anal==False:
                add_manual_correction_if_available(i)
    else:
        form=analysis["number"][0] + " " + analysis["case"][0]
        new_word=synthesize(analysis["lemma"], form=form)
        if len(new_word)>0 and i.lower() in new_word:
            info=i+"\t"+i+"\t"+tag
            lines_list.append(info)
        else:
            if mult_anal==False:
                add_manual_correction_if_available(i)


def verb_check(morph_root,analysis,tagged_i,i,mult_anal):
    if morph_root.lemma != None:
        morph_root.root=morph_root.root.replace("_","")
    if morph_root.lemma != None and analysis["lemma"]==morph_root.root:
        info=i+"\t"+tagged_i.text+"\t"+"Ok"
        lines_list.append(info)
    else:
        if len(re.findall("ä|Ä|ö|Ö|ü|Ü|Õ|õ", i)) < len(re.findall("ä|Ä|ö|Ö|ü|Ü|Õ|õ", analysis["lemma"])):
            if analysis["ending"]=="0" and "tense" in analysis.keys() and "polarity" in analysis.keys() and "pres" in analysis["tense"] and "neg" in analysis["polarity"]:
                new_word=synthesize(analysis["lemma"]+"ma", form="o")
            else:
                new_word=synthesize(analysis["lemma"]+"ma", form=analysis["ending"])
            if len(new_word)>0:
                if i.lower() in new_word:
                    info=i+"\t"+i+"\t"+"Spell_Missing_Diacritics"
                    lines_list.append(info)
                else:
                    if i[0].isupper():
                        info=i+"\t"+new_word[-1].capitalize()+"\t"+"Spell_Missing_Diacritics"
                        lines_list.append(info)
                    else:
                        info=i+"\t"+new_word[-1]+"\t"+"Spell_Missing_Diacritics"
                        lines_list.append(info)
            else:
                if mult_anal==False:
                    add_manual_correction_if_available(i)        
     
        else: 
            if analysis["ending"]=="0" and "tense" in analysis.keys() and "polarity" in analysis.keys() and "pres" in analysis["tense"] and "neg" in analysis["polarity"]:
                new_word=synthesize(analysis["lemma"]+"ma", form="o")
            else:
                new_word=synthesize(analysis["lemma"]+"ma", form=analysis["ending"])
            if len(new_word)>0:
                ld=distance(i.lower(), new_word[-1].lower())
                if i.lower() in new_word:
                    info=i+"\t"+i+"\t"+"Ok"
                    lines_list.append(info)
                elif ld > 1:
                    if i in new_analyses.keys():
                        info=new_analyses[i]
                        lines_list.append(info)
                    else:
                        if i[0].isupper():
                            info=i+"\t"+new_word[-1].capitalize()+"\t"+"Spell_ED>1"
                            lines_list.append(info)
                        else:
                            info=i+"\t"+new_word[-1]+"\t"+"Spell_ED>1"
                            lines_list.append(info)
                elif ld == 1:
                    if i[0].isupper():
                        info=i+"\t"+new_word[-1].capitalize()+"\t"+"Spell_ED_1"
                        lines_list.append(info)
                    else:
                        info=i+"\t"+new_word[-1]+"\t"+"Spell_ED_1"
                        lines_list.append(info)
                elif ld == 0:
                    if i[0].isupper():
                        info=i+"\t"+new_word[-1].capitalize()+"\t"+"Ok"
                        lines_list.append(info)
                    else:
                        info=i+"\t"+new_word[-1]+"\t"+"Ok"
                        lines_list.append(info)
                else:
                    if mult_anal==False:
                        add_manual_correction_if_available(i)        
            else:
                if mult_anal==False:
                    add_manual_correction_if_available(i)
                
            
def others_check(morph,analysis,tagged_i,i,mult_anal):
    if ("unknown_attribute" in analysis.keys() and "Emo" in analysis["unknown_attribute"]) or (analysis["partofspeech"] =="E"):
        info=i+"\t"+analysis["lemma"]+"\t"+"Emo"
        lines_list.append(info)
    elif analysis["partofspeech"]=="Z":
        info=i+"\t"+analysis["lemma"]+"\t"+"Punct"
        lines_list.append(info)                  
    else:
        if "subtype" in analysis.keys() and "prop" in analysis["subtype"] and not re.search("\d", analysis["lemma"]):
            if analysis["case"][0] in cases.keys():
                form=analysis["number"][0]+ " " + cases[analysis["case"][0]]
                new_word=synthesize(analysis["lemma"], form=form)
            else:
                form=analysis["number"][0] + " " + analysis["case"][0] 
                new_word=synthesize(analysis["lemma"], form=form)
            if len(new_word)>0:
                if i.lower() in new_word:
                    info=i+"\t"+i+"\t"+"Name"
                    lines_list.append(info) 
                elif analysis["case"][0] =="gen" or analysis["case"][0] =="part":
                    if new_word[-1][-1] in ["a","e","i","o","u","õ","ä","ö"] and new_word[-1][-1]!=i[-1]:
                        if analysis["case"][0]=="gen":
                            info=i+"\t"+new_word[-1]+"\t"+"Spell_Unknown_Gen"
                            lines_list.append(info) 
                        else:
                            info=i+"\t"+new_word[-1]+"\t"+"Spell_Unknown_Part"
                            lines_list.append(info) 
                    else:
                        info=i+"\t"+new_word[-1].capitalize()+"\t"+"Name"
                        lines_list.append(info) 
                else:
                    info=i+"\t"+new_word[-1].capitalize()+"\t"+"Name"
                    lines_list.append(info) 
            else:
                if mult_anal==False:
                    add_manual_correction_if_available(i)
             
        elif ("subtype" in analysis.keys() and "prop" in analysis["subtype"]) or ((analysis["partofspeech"]=="Y" or analysis["partofspeech"]=="S") and re.search("\d", analysis["lemma"])):
            if (("case" not in analysis.keys()) or ("case" in analysis.keys() and "nom" in analysis["case"]) and "sg" in analysis["number"]):
                if i in new_analyses.keys(): 
                    info=new_analyses[i]
                    lines_list.append(info)
                else:
                    info=i+"\t"+analysis["lemma"]+"\t"+"Abbrev_Num"
                    lines_list.append(info)         
            else: 
                if i.lower()==analysis["lemma"].lower():
                    info=i+"\t"+analysis["lemma"]+"\t"+"Abbrev_Num"
                    lines_list.append(info) 
                else:
                    if mult_anal==False:
                        add_manual_correction_if_available(i)               
        
        elif analysis["partofspeech"]=="Y" and not re.search("\d", analysis["lemma"]):
            if ("case" in analysis.keys() and "nom" in analysis["case"] and "sg" in analysis["number"]) or ("case" not in analysis.keys()):
                info=i+"\t"+analysis["lemma"]+"\t"+"Abbrev"
                lines_list.append(info)
            else: 
                if "case" in analysis.keys():
                    if analysis["case"][0] in cases.keys():
                        new_word=synthesize(analysis["lemma"], form=analysis["number"][0]+" "+cases[analysis["case"][0]])
                    else:
                        new_word=synthesize(analysis["lemma"], form=analysis["number"][0]+" "+analysis["case"][0])
                    if len(new_word)>0:
                        info=i+"\t"+new_word[-1]+"\t"+"Abbrev"
                        lines_list.append(info)
                    else:
                        if mult_anal==False:
                            add_manual_correction_if_available(i)                
                else:
                    if mult_anal==False:
                        add_manual_correction_if_available(i)        
                    
        else:
            if morph.lemma!=None and analysis["lemma"].lower() == morph.lemma.lower():
                info=i+"\t"+tagged_i.text+"\t"+"Ok"
                lines_list.append(info)
        
            elif ("-" in i or ":" in i or "/" in i):
                if i == analysis["lemma"]:
                    info=i+"\t"+analysis["lemma"]+"\t"+"Word_w_Punct"
                    lines_list.append(info)
                else:
                    if "case" in analysis.keys():
                        if mult_anal==False:
                            synt(i,analysis,"Word_w_Punct",mult_anal==False)
                        elif mult_anal==True:
                            synt(i,analysis,"Word_w_Punct",mult_anal==True)
                    else:
                        if "partofspeech" in analysis.keys() and (analysis["partofspeech"]=="J" or analysis["partofspeech"]=="K" or analysis["partofspeech"]=="D" or analysis["partofspeech"]=="B"):
                            if analysis["lemma"].lower()==i.lower():
                                info=i+"\t"+analysis["lemma"]+"\t"+"Ok"
                                lines_list.append(info)
                            else:
                                ld=distance(i.lower(),analysis["lemma"].lower())
                                if ld>1:
                                    if i[0].isupper():
                                        info=i+"\t"+analysis["lemma"].capitalize()+"\t"+"Spell_ED>1"
                                        lines_list.append(info)
                                    else:
                                        info=i+"\t"+analysis["lemma"]+"\t"+"Spell_ED>1"
                                        lines_list.append(info)
                                elif ld == 1:
                                    if i[0].isupper():
                                        info=i+"\t"+analysis["lemma"].capitalize()+"\t"+"Spell_ED_1"
                                        lines_list.append(info)
                                    else:
                                        info=i+"\t"+analysis["lemma"]+"\t"+"Spell_ED_1"
                                        lines_list.append(info)
                                else:
                                    if mult_anal==False:
                                        add_manual_correction_if_available(i)
                        else:
                            if mult_anal==False:
                                add_manual_correction_if_available(i)
                            
            else:
                if "partofspeech" in analysis.keys() and (analysis["partofspeech"]=="J" or analysis["partofspeech"]=="K" or analysis["partofspeech"]=="D" or analysis["partofspeech"]=="B"):
                    if analysis["lemma"].lower()==i.lower():
                        info=i+"\t"+analysis["lemma"]+"\t"+"Ok"
                        lines_list.append(info)
                    else:
                        if len(re.findall("ä|Ä|ö|Ö|ü|Ü|Õ|õ", i)) < len(re.findall("ä|Ä|ö|Ö|ü|Ü|Õ|õ", analysis["lemma"])):
                            if i[0].isupper():
                                info=i+"\t"+analysis["lemma"].capitalize()+"\t"+"Spell_Missing_Diacritics"
                                lines_list.append(info) 
                            else:
                                info=i+"\t"+analysis["lemma"]+"\t"+"Spell_Missing_Diacritics"
                                lines_list.append(info) 
                        else:
                            ld=distance(i.lower(),analysis["lemma"].lower())
                            if ld>1:
                                if i[0].isupper():
                                    info=i+"\t"+analysis["lemma"].capitalize()+"\t"+"Spell_ED>1"
                                    lines_list.append(info)
                                else:
                                    info=i+"\t"+analysis["lemma"]+"\t"+"Spell_ED>1"
                                    lines_list.append(info)
                            elif ld == 1:
                                if i[0].isupper():
                                    info=i+"\t"+analysis["lemma"].capitalize()+"\t"+"Spell_ED_1"
                                    lines_list.append(info)
                                else:
                                    info=i+"\t"+analysis["lemma"]+"\t"+"Spell_ED_1"
                                    lines_list.append(info)
                            else:
                                if mult_anal==False:
                                    add_manual_correction_if_available(i)
                    
                elif "case" in analysis.keys():
                    if analysis["case"][0] in cases.keys():
                        form=analysis["number"][0]+ " " + cases[analysis["case"][0]]
                    else:
                        form=analysis["number"][0] + " " + analysis["case"][0]
                    if mult_anal==False:
                        use_edit_distance(analysis,form, i, i2, mult_anal==False)
                    elif mult_anal==True:
                        use_edit_distance(analysis,form, i, i2, mult_anal==True)

                else:
                    if i.lower() == analysis["lemma"].lower():
                        info=i+"\t"+analysis["lemma"]+"\t"+"Ok"
                        lines_list.append(info)
                    else:
                        if mult_anal==False:
                            add_manual_correction_if_available(i)
                        
                            

for file in os.listdir(path):
    filename = os.path.join(path, file)
    if ".cg" in filename:
        print("******************FAILINIMI:",filename)
        with open (filename, 'r', encoding="utf8") as f:
            lines_list=[]
            new_filename=filename.split("\\")[-1]
            new_filename=new_filename.split(".")
            new_filename=new_filename[-2]
            new_row=[]
            text=[]
            analyses=[]
            row=f.read()
            row=row.split("\n")
            for i in row:
                if not i.startswith('"<s>"') and not i.startswith('"</s>"') and i != '' and not i.startswith('"<kiil>"') and not i.startswith('"</kiil>"') and not i.startswith('"<kindel_piir/>"') and not i.startswith('<kindel_piir/>"') and not "####" in i :
                    new_row.append(i)
            for i in range(1, len(new_row), 2):
                analyses.append(new_row[i])
            for i in range(0, len(new_row), 2):
                i=new_row[i].replace("<","")
                i=i.replace(">","")
                i=i[1:].strip()
                text.append(i[:-1])
            
            for i,analysis in zip(text,analyses):
                analysis = parser.parse(analysis)
                analysis["lemma"]=analysis["lemma"].replace("_","")
                analysis["lemma"]=analysis["lemma"].replace("=","")
                tagged_i=Text(i)
                tagged_i.tag_layer(['words','sentences'])
                morph_tagger.tag(tagged_i)
                morph_counter=0
                for i2 in tagged_i.morph_analysis:
                    morph_counter+=1
                    if morph_counter==1:
                        if i2[0].lemma != None: # if auto.morph analysis != None
                            i2[0].lemma=i2[0].lemma.replace("_","")
                            i2[0].lemma=i2[0].lemma.replace("=","")
                            if len(i2)==1: # one auto.morph analysis
                                if analysis["partofspeech"]=="V":
                                    verb_check(i2[0],analysis,tagged_i,i,mult_anal=False)
                                else:
                                    others_check(i2[0],analysis,tagged_i,i,mult_anal=False)
                            else: # more than one auto.morph analysis
                                if analysis["partofspeech"]=="V":
                                    length=len(lines_list)
                                    for listike in i2:
                                        if length==len(lines_list):
                                            verb_check(listike,analysis,tagged_i,i,mult_anal=True)
                                    if length==len(lines_list):
                                        add_manual_correction_if_available(i)
                                else:
                                    length=len(lines_list)
                                    for listike in i2:
                                        if length==len(lines_list):
                                            others_check(listike,analysis,tagged_i,i,mult_anal=True)
                                    if length==len(lines_list):
                                        add_manual_correction_if_available(i)
                        else: # if auto.morph analysis == None
                            if analysis["partofspeech"]=="V":
                                verb_check(i2[0],analysis,tagged_i,i,mult_anal=False)
                            else:
                                others_check(i2[0],analysis,tagged_i,i,mult_anal=False)
                            
                            
            with open(new_path + new_filename+".tsv","w",encoding="utf8") as f:
                for line in lines_list:
                    f.write(line+"\n")
