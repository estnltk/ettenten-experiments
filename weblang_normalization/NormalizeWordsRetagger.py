from estnltk.taggers import Retagger
import regex as re
from estnltk.vabamorf import morf as vm
from estnltk import Text, Annotation
from estnltk.taggers.morph_analysis.morf_common import _get_word_text
from itertools import groupby
from estnltk.taggers.morph_analysis.proxy import MorphAnalyzedToken
import nltk

class NormalizeWordsRetagger(Retagger):
    """Retagger for adding normalized forms as attributes of words layer for words used in non-canonical texts."""
    
    conf_param = ["use_letter_reps", "use_diacritics_fixes", "use_diacritics_fixes_1", "use_diacritics_fixes_2", 
                 "use_diacritics_fixes_3"]
    
    
    def __init__(self,
                 words_layer='words',
                 use_letter_reps=True,
                 use_diacritics_fixes=True,
                 use_diacritics_fixes_1=True,
                 use_diacritics_fixes_2=True,
                 use_diacritics_fixes_3=True):

        self.use_letter_reps = use_letter_reps
        self.use_diacritics_fixes = use_diacritics_fixes
        self.use_diacritics_fixes_1 = use_diacritics_fixes_1
        self.use_diacritics_fixes_2 = use_diacritics_fixes_2
        self.use_diacritics_fixes_3 = use_diacritics_fixes_3
        output_attributes=()
        
        self.input_layers = [words_layer]
        self.output_layer = words_layer
        
        if use_letter_reps is True or use_diacritics_fixes is True:
            output_attributes=output_attributes

        self.output_attributes=output_attributes
        

    def _change_layer(self, text, layers, status):
      
        words=layers[self.output_layer]    
            
        words.attributes = words.attributes + self.output_attributes

        # normalizes letter repetitions (e.g. väääääga)
        if self.use_letter_reps == True:

            # checks if created normalized form should be changed or additional forms added
            def add_normalized_form(outcome, form_to_use, candidates, spelling_list):
                forms_to_add=[] # all the normalized forms will be added here
                dict_of_other_forms={"w":"www","x":"xxx","z":"zzz"}

                if type(outcome)==str:

                    # normalized form is changed if needed to match the original word (upper/lowercase, capital letter)
                    if form_to_use.isupper() and outcome.islower():
                        outcome=outcome.upper()
                    elif form_to_use.islower() and outcome.isupper():
                        outcome=outcome.lower()
                    elif form_to_use[0].isupper() and outcome[0].islower():
                        outcome=outcome.capitalize()
                    # normalized form is added if the original word contains more than 2 letter reps or repetitive chunks 
                    if re.search(r"([a-zšžõäöü])\1{2,}",  form_to_use.lower()) !=None or find_repeats(form_to_use.lower())!=None:
                        forms_to_add.append(outcome)

                        wo_repeats=without_recurrent_letters(outcome)
                        # finding and adding possible alternative forms
                        outcome_modif=[]
                        # e.g. "prrrr-ga" -- so that it will then be "prrrr"--"prr" and would get special alternative forms too ("pr")
                        if "-" in outcome and outcome.count("-")==1: 
                            splitted_outcome=outcome.split("-")
                            to_add=splitted_outcome[0],splitted_outcome[1] # word and the word ending etc
                            outcome_modif.append(to_add)
                            splitted_form_to_use=form_to_use.split("-")
                            form_to_use=splitted_form_to_use[0] # e.g. prr
                            outcome=splitted_outcome[0] # e.g. original prrr

                        if (len(set(without_recurrent_letters(outcome))) in [2,3]) or \
                        (len(set(without_recurrent_letters(outcome))) in [1,2,3] and outcome_modif!=0): # certain shorter forms get possible other alternatives
                            # if max 3 different letters in word: new alternative form: e.g. "ma" (orig: "maaaa", first norm_form: "maa") 
                            new_form=re.sub(r"([a-zšžõäöüA-ZÜÕÄÖŠŽ])\1{1,}", r"\1", form_to_use)
                            # if max 2 different letters in word: new alternative form: e.g. "krr" (orig: "krrrr", first norm_form: "kr")
                            new_form2=re.sub(r"([a-zšžõäöüA-ZÜÕÄÖŠŽ])\1{2,}", r"\1\1", form_to_use)
                            if len(outcome_modif)==0:
                                if len(outcome)==2 and len(new_form2)==len(outcome)+1: # e.g. krr
                                    forms_to_add.append(new_form2)
                                # max 5 letters or max 2 diff letters (e.g. maa - ma, ahhaa - aha)
                                if (len(outcome)<5 or len(set(without_recurrent_letters(outcome)))==2) \
                                and new_form!=outcome and len(new_form)<len(outcome): 
                                    forms_to_add.append(new_form)
                            
                            else: # words with "-", e.g. "prrrr-ga"
                                if (new_form!=outcome_modif[0][0] and len(new_form)<len(outcome_modif[0][0])) or \
                                    (len(set(without_recurrent_letters(outcome)))==1):
                                    if outcome not in dict_of_other_forms:
                                        forms_to_add.append(new_form+"-"+outcome_modif[0][1])
                                    else:
                                        # special alternative forms from dict, e.g. w - www-le
                                        forms_to_add.append(dict_of_other_forms[outcome]+"-"+outcome_modif[0][1])
                                        
                        # special alternative forms from dict, e.g. w - www
                        if len(outcome_modif)==0 and outcome in dict_of_other_forms: 
                            forms_to_add.append(dict_of_other_forms[outcome])

                        # roman numeral, e.g. "xii"/"Xii" get "XII" as an alternative
                        if (all(c in ["i","v","x","l","c","d","m"] for c in form_to_use)==True) or \
                        (all(c in ["i","v","x","l","c","d","m"] for c in form_to_use[1:])==True and form_to_use[0] in ["I","V","X","L","C","D","M"]):
                            if len(outcome_modif)==0:
                                forms_to_add.append(form_to_use.upper())
                            else: # if there is "-" 
                                forms_to_add.append(form_to_use.upper()+"-"+outcome_modif[0][1])

                        # if besides 3+x letter reps there are also double letters in word and it is not a word
                        # alternative form with 1x letters will be added, e.g. "uiijjjee - uiijee; uije"
                        if re.search(r"(\w)\1",outcome.lower()) and MorphAnalyzedToken(outcome).is_word==False \
                        and wo_repeats!=outcome.lower():
                            if not any(i.lower() == wo_repeats for i in candidates):
                                if form_to_use.isupper() and wo_repeats.islower():
                                    forms_to_add.append(wo_repeats.upper())
                                elif form_to_use[0].isupper() and outcome[0].islower():
                                    forms_to_add.append(wo_repeats.capitalize())
                                else:
                                    forms_to_add.append(wo_repeats)
                        # shorter words in uppercase get the original word as an alternative (e.g. EEEL)
                        if outcome.isupper() and len(form_to_use)<5 and outcome!=form_to_use:
                            if not any(i.lower() == form_to_use.lower() for i in candidates):
                                forms_to_add.append(form_to_use)
                                
                for form in forms_to_add:
                    candidates.append(form)
                    spelling_new_form=vm.spellcheck([form], suggestions=True)[0]["spelling"]
                    spelling_list.append(spelling_new_form)
                               
            # removes all letter reps, e.g. noonohhh -- nonoh
            def without_recurrent_letters(word):
                new_word=re.compile(r'(.)\1{1,}', re.IGNORECASE).sub(r'\1', word.lower())
                return new_word
            
            # compares word without letter reps 
            def compare_words_wo_repeating_letters(speller_sugg_list, new_form):
                for word in speller_sugg_list:
                    test=0 # to avoid forms where new letters are added, e.g. "urr" [1,2] -- "uur" [2,1] (no double "u" in our word)
                    count_letters1 = [(sum(1 for i in group)) for label, group in groupby(new_form.lower())]
                    count_letters2 = [(sum(1 for i in group)) for label, group in groupby(word.lower())]
                    # if any number in the list of the new word is bigger from the other word's list, then this new form is avoided 
                    for i, i2 in zip(count_letters1, count_letters2):
                        if i2>i:
                            test+=1
                    
                    if len(word.lower())>1 and without_recurrent_letters(new_form)==without_recurrent_letters(word) and \
                    test==0:
                        return word
                        break
            
            # finds if the word consists of repetitive chunks (e.g. blabla, kluklu, nununu)
            def find_repeats(word):
                rep_regex = re.compile(r"(.+?)\1+$") # e.g. lalala, blablablabla, midagigigi, muhahaha
                match1=re.sub(rep_regex,r'\1',word.lower())
                if MorphAnalyzedToken(match1).is_word==True and len(match1)>4: # e.g. midagigi - midagi vs. lala - lala
                    return match1
                else:
                    match2 = re.sub(rep_regex,r'\1\1',word.lower())
                    if match2!=word and match2!=without_recurrent_letters(word): # to not count e.g. programmmerija in here
                        return match2
                    elif match1+match1==word.lower(): # e.g. EIEI 
                        return match2
                    else:
                        return None
            
            # running spell_check
            def check_spelling(word_to_use):
                spell_check=vm.spellcheck([word_to_use], suggestions=True)
                for i in spell_check:
                    return i
            
            # checks the spelling and runs all the rules
            def use_rules(word_to_use, rule, form_to_use):
                speller_info=check_spelling(word_to_use)
                run_the_rules=compare(speller_info, rule, form_to_use)
                return run_the_rules                    
                                                                                               
            # rules; normalized form is found or not
            def compare(speller_info, rule, form_to_use):
                
                new_form=re.sub(r"([a-zšžõäöüA-ZÜÕÄÖŠŽ])\1{2,}", r"\1", form_to_use.lower())
                abbrev_w_other_char=re.match(r'^[A-ZÜÕÄÖŠŽ]{1,4}[\.\-][a-züõäöšž]+$',speller_info["text"]) 
                two_letters = re.sub(r"([a-zšžõäöüA-ZÜÕÄÖŠŽ])\1{2,}", r"\1\1", form_to_use)
                
                # avoid abbrevs with endings, e.g. XXXX-le
                if abbrev_w_other_char!=None: 
                    return None
                # words like Mmm, Ooo, Eee etc to lowercase
                if len(speller_info["text"])>1 and len(set(without_recurrent_letters(speller_info["text"]))) == 1 \
                and speller_info["text"][0].isupper() and speller_info["text"][1:].islower(): 
                    speller_info["text"]=speller_info["text"].lower()

                # if SPELLING==TRUE
                if speller_info["spelling"]==True:

                    if not speller_info["text"].isupper() and not speller_info["text"].islower():
                        if len(re.findall(r'[A-ZÜÕÄÖŠŽ]',speller_info["text"]))>1: # e.g. MMMnjaah -- mmmnjaah
                            speller_info["text"]=speller_info["text"].lower()

                        # e.g. Aaagaa - change to lowercase to avoid counting only as a proper name 
                        if len(check_spelling(without_recurrent_letters(speller_info["text"]))["suggestions"])!=0 or \
                        check_spelling(without_recurrent_letters(speller_info["text"]))["spelling"]==True:
                            speller_info["text"]=speller_info["text"].lower()
                            
                    # if word is uppercase + is a word with reps changed to either 2x or 1x         
                    if rule!="nr 2" and speller_info["text"].isupper() and \
                    (MorphAnalyzedToken(without_recurrent_letters(speller_info["text"])).is_word==True or \
                     MorphAnalyzedToken(two_letters).is_word==True or len(speller_info["text"])>5) \
                    and all(c in ["I","V","X","L","C","D","M"] for c in speller_info["text"])==False: 
                        # e.g. JAAAA, SEEEEE have to be changed, but roman numerals kept the same
                        return speller_info # goes to next round
                    
                    elif rule=="analysis OK":
                        return None
                    else: 
                        if MorphAnalyzedToken(speller_info["text"]).is_word==True: # e.g. NII, EEL
                            return speller_info["text"]
                        elif MorphAnalyzedToken(without_recurrent_letters(speller_info["text"])).is_word==True: # e.g. AAAHHH
                            speller_info["text"]=speller_info["text"].lower()
                            return without_recurrent_letters(speller_info["text"])
                        else:
                            return form_to_use 

                else:
                    if len(speller_info["suggestions"])==1: # if spelling==False, but 1 suggestion
                        w1=without_recurrent_letters(speller_info["text"])
                        w2=without_recurrent_letters(speller_info["suggestions"][0])
                        # lists - e.g. "urr" - [1, 2]
                        count_letters1 = [(sum(1 for i in group)) for label, group in groupby(speller_info["text"])]
                        count_letters2 = [(sum(1 for i in group)) for label, group in groupby(speller_info["suggestions"][0])]
                        rep_word=find_repeats(w1)
                        test=0 # e.g. "Urr" -- "uur"
                        for i, i2 in zip(count_letters1,count_letters2):
                            if i2>i:
                                test+=1
                        # not in [1,2,3] - to avoid unnecessary suggestions by speller
                        if w1==w2 and ((test==0) or (test!=0 and len(set(w1)) not in [1,2,3])) :
                            return speller_info["suggestions"][0]
                        elif rep_word!=None: 
                            return rep_word
                        # proper names
                        elif len(speller_info["suggestions"][0])>1 and (speller_info["suggestions"][0][0].isupper() \
                             and speller_info["suggestions"][0][1].islower()) and rule=="nr 2":
                            return speller_info["text"]
                        else:
                            if rule=="nr 2":
                                return new_form
                            else:
                                return speller_info

                    elif len(speller_info["suggestions"])>1:
                        speller_info["suggestions"].sort(key=len) # e.g. vitamiine vs vitamiinne
                        func_compare_words=compare_words_wo_repeating_letters(speller_info["suggestions"],speller_info["text"])
                        if func_compare_words:
                            return func_compare_words
                        
                        elif rule=="nr 2":
                            speller_try=check_spelling(new_form)
                            if len(speller_try["suggestions"])==1:
                                func_compare_words=compare_words_wo_repeating_letters(speller_try["suggestions"],speller_info["text"])
                                if func_compare_words:
                                    return func_compare_words
                                else:
                                    return new_form 
                            else:
                                rep_word=find_repeats(without_recurrent_letters(new_form))
                                if rep_word!=None:
                                    return rep_word
                                else:
                                    return new_form                     
                        else:
                            return speller_info

                    elif len(speller_info["suggestions"])==0 and rule=="nr 2":
                        
                        w1=without_recurrent_letters(new_form)
                        rep_word=find_repeats(w1)
                        if rep_word!=None:
                            new_form=rep_word
                        speller_try=check_spelling(new_form)
                        if speller_try["spelling"]==True :
                            return new_form
                        elif len(speller_try["suggestions"])==1 or len(speller_try["suggestions"])>1:
                            speller_try["suggestions"].sort(key=len)
                            func_compare_words=compare_words_wo_repeating_letters(speller_try["suggestions"], new_form)
                            if func_compare_words:
                                return func_compare_words
                            else:
                                return new_form 
                        else:
                            # goes as an abbrev, e.g. CCCPis
                            if rep_word==None and (form_to_use.isupper()) or (not form_to_use.isupper() and not form_to_use.islower() and form_to_use[0:2].isupper()):
                                return None
                            elif rep_word==None and speller_info["text"][0].isupper():
                                return speller_info["text"]
                            else:
                                return new_form          
                    else:
                        return speller_info 

        # words without diacritics, eg voimalus-võimalus
        if self.use_diacritics_fixes == True:
            
            # checks, whether word is corrected, if only one of the letters is changed
            def check_changes_separately(how_many, form_to_use, k, v, dict_nr):
                check=0
                for i in range (how_many):
                    form_to_use_rep=form_to_use.replace(k, v, i+1)
                    if MorphAnalyzedToken(form_to_use_rep).is_word==True and re.search(r'[^0-9]+', form_to_use_rep):
                        return form_to_use_rep
                    else:
                        check+=1
                if check==how_many and dict_nr!="dict 3":
                    return True
                elif check==how_many and dict_nr=="dict 3":
                    return None
            
            # makes changes
            def find_diacritics(form_to_use, k, v, dict_nr, new_form_to_use):
                alternatives=[]
                if dict_nr=="dict 1":
                    new_form_to_use=form_to_use
                else:
                    new_form_to_use=new_form_to_use
                check_letters=0
                how_many=form_to_use.lower().count(k)
                if k in form_to_use.lower():
                    if len(v)==1:
                        form_to_use_rep=form_to_use.replace(k, v)
                        new_form_to_use=new_form_to_use.replace(k, v)

                        if MorphAnalyzedToken(form_to_use_rep).is_word==True and re.search(r'[^0-9]+', form_to_use_rep):
                            alternatives.append(form_to_use_rep)
                        else:
                            if MorphAnalyzedToken(new_form_to_use).is_word==True and re.search(r'[^0-9]+', new_form_to_use):
                                alternatives.append(new_form_to_use)
                            else:
                                if k+k in form_to_use.lower():
                                    form_to_use_rep=form_to_use.replace(k+k, v+v)
                                    if MorphAnalyzedToken(form_to_use_rep).is_word==True and re.search(r'[^0-9]+', form_to_use_rep):
                                        alternatives.append(form_to_use_rep)
                                    else:
                                        check=check_changes_separately(how_many, form_to_use, k, v, dict_nr)
                                        if type(check)==str:
                                            alternatives.append(check)
                                        elif check==True:
                                            return True, new_form_to_use
                                else: 
                                    check=check_changes_separately(how_many, form_to_use, k, v, dict_nr)
                                    if type(check)==str:
                                        alternatives.append(check)
                                    elif check==True:
                                        return True, new_form_to_use

                    else:
                        for letter in v:
                            form_to_use_rep=form_to_use.replace(k, letter)
                            new_form_to_use=new_form_to_use.replace(k, letter)

                            if MorphAnalyzedToken(form_to_use_rep).is_word==True and re.search(r'[^0-9]+', form_to_use_rep):
                                alternatives.append(form_to_use_rep)
                            else:
                                if MorphAnalyzedToken(new_form_to_use).is_word==True and re.search(r'[^0-9]+', new_form_to_use):
                                    alternatives.append(new_form_to_use)
                                else:
                                    if k+k in form_to_use.lower():
                                        form_to_use_rep=form_to_use.replace(k+k, letter+letter)
                                        if MorphAnalyzedToken(form_to_use_rep).is_word==True and re.search(r'[^0-9]+', form_to_use_rep):
                                            alternatives.append(form_to_use_rep)
                                        else:
                                            check=check_changes_separately(how_many, form_to_use, k, letter, dict_nr)
                                            if type(check)==str:
                                                alternatives.append(check)
                                            else:
                                                check_letters+=1
                                    else: 
                                        check=check_changes_separately(how_many, form_to_use, k, letter, dict_nr)
                                        if type(check)==str:
                                            alternatives.append(check)
                                        else:
                                            check_letters+=1

                if len(alternatives)!=0:
                    return alternatives
                elif check_letters==len(v) and dict_nr!="dict 3":
                    return True, new_form_to_use
                elif check_letters==len(v) and dict_nr=="dict 3":
                    return None

            # new form is found 
            def use_diacritics_rules(form_to_use):
                
                dict_of_alterns_1={"y":"ü","6":"õ","2":"ä","å":"ä","ô":"õ","ó":"õ","ō":"õ","û":"ü","ú":"ü"}
                dict_of_alterns_2={"a":"ä","o":["õ","ö"],"u":"ü"}
                dict_of_alterns_3={"ö":["ü","õ","ö","ä"],"õ":["ü","õ","ö","ä"],"ü":["ü","õ","ö","ä"], 
                                   "ä":["ü","õ","ö","ä"], "e":["ä","ö","õ"],"?":["ü","õ","ö","ä"]}
                
                if_no_result=False 
                new_form_to_use=""
                
                # dict_of_alterns_1
                if self.use_diacritics_fixes_1==True:
                    for k,v in dict_of_alterns_1.items():
                        find_dict1=find_diacritics(form_to_use, k, v, "dict 1", "")
                        if type(find_dict1) is list:
                            return find_dict1
                        elif find_dict1==True:
                            if_no_result=True
                        elif find_dict1 is not None and len(find_dict1)==2:
                            if_no_result=True
                            new_form_to_use=find_dict1[1]
                    
                # dict_of_alterns_2               
                if self.use_diacritics_fixes_2==True:
                    if if_no_result == True or [l for l in form_to_use.lower() if l in dict_of_alterns_1]==[]:
                        for k,v in dict_of_alterns_2.items():
                            find_dict2=find_diacritics(form_to_use, k, v, "dict 2", new_form_to_use)
                            if type(find_dict2) is list:
                                return find_dict2
                            elif find_dict2==True:
                                if_no_result=True
                            elif find_dict2 is not None and len(find_dict2)==2:
                                if_no_result=True
                                new_form_to_use=find_dict2[1]

                # dict_of_alterns_3
                if self.use_diacritics_fixes_3==True:
                    if if_no_result==True or [l for l in form_to_use.lower() if l in dict_of_alterns_2]==[] or \
                    [l for l in form_to_use.lower() if l in dict_of_alterns_1]==[]:
                        for k,v in dict_of_alterns_3.items():
                            find_dict3=find_diacritics(form_to_use, k, v, "dict 3", new_form_to_use)
                            if type(find_dict3) is list:
                                return find_dict3
                                                                          
            
        for word_id, w in enumerate(words):
            form_to_use = _get_word_text(w)
            candidates = [ form_to_use ]
            spelling_results = [ vm.spellcheck([form_to_use], suggestions=True)[0]["spelling"] ]

            if self.use_letter_reps == True: # normalizes letter repetitions (e.g. väääääga)

                new_candidates=[] 
                for candidate, spelling in zip(candidates, spelling_results):
                    if spelling==False:
                        first_try = use_rules(candidate,"analysis OK", candidate)
                        if type(first_try)==str:
                            new_candidates.append(first_try)
                        elif first_try!=None:
                            rule_1 =  re.sub(r"([a-zšžõäöüA-ZÜÕÄÖŠŽ])\1{2,}", r"\1\1\1", first_try["text"]) # nr 1 - 3 reps
                            second_try = use_rules(rule_1,"nr 1",form_to_use)
                            if type(second_try)==str:
                                new_candidates.append(second_try)
                            elif second_try!=None:
                                rule_2 = re.sub(r"([a-zšžõäöüA-ZÜÕÄÖŠŽ])\1{2,}", r"\1\1", second_try["text"]) # nr 2 - 2 reps
                                third_try = use_rules(rule_2,"nr 2",form_to_use)
                                if type(third_try)==str:
                                    new_candidates.append(third_try)
                
                for new_c in new_candidates:
                    add_normalized_form(new_c, form_to_use, candidates, spelling_results)

            if self.use_diacritics_fixes == True: 
                english_words = set(nltk.corpus.words.words())
                new_candidates=[]
                for candidate, spelling in zip(candidates, spelling_results):
                    if spelling==False:
                        prev_word=""
                        next_word=""
                        if word_id-1>-1:
                            prev_word=words[word_id-1]
                        if len(words)-1>word_id:
                            next_word=words[word_id+1]
                        if (candidate[0].isupper() and (w.start>2 and words.text[w.start-2:w.start-1] in ["!","?","."])) \
                        or (candidate in english_words and ((not type(prev_word) is str and prev_word.text in english_words) \
                                                            or (not type(next_word) is str and next_word.text in english_words))) \
                        or (MorphAnalyzedToken(candidate.capitalize()).is_word==True):
                            continue
                        else:
                            first_try=use_diacritics_rules(candidate)
                            if type(first_try) is list:
                                for i in first_try:
                                    if i not in new_candidates:
                                        new_candidates.append(i)
                            
                for new_c in new_candidates:
                    candidates.append(new_c)
                    spelling_new_form=vm.spellcheck([new_c], suggestions=True)[0]["spelling"]
                    spelling_results.append(spelling_new_form)
                            
            # remove if first in the list is the original incorrect word
            if w.text == candidates[0] :
                candidates.pop(0)
                spelling_results.pop(0)

            if candidates:
                w.clear_annotations()
                for candidate in candidates:
                    w.add_annotation(Annotation(w, normalized_form=candidate) )
