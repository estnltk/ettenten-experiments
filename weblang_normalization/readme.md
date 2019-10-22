# Experiments on normalizing web language

---

## Resources and scripts

* `NormalizeWordsRetagger.py` -- retagger for adding normalized word forms for words of Estonian Internet language, particularly the language characteristic to etTenTen. Normalized forms are added under an attribute *normalized_form* of the words layer.

* `words_letter_reps.csv` -- csv-file used for testing and evaluation of words containing letter repetitions (e.g. tereeeee - tere; midaaaagiii - midagi).
	- 1st column *word*: word containing letter repetitions, e.g. *äkkkki*, *vääääga*, *jjjuuuu*. 
	- 2nd column *filename*: filename of the file consisting the problematic word.
	- 3rd column *index*: position index of the problematic word in the file.
	- 4th column *context*: some context before and after the problematic word is given.

* `words_wo_diacritics.csv` -- csv-file used for testing and evaluation of words with missing or wrong diacritics (e.g. l2ks - läks; tuli - tüli). 
	- 1st column *words*: lists of possible word pairs, e.g. ['OK-lõhki-lohki']. In every list first there is a tag (*OK*, *NAME*, *ENGLISH*) and then the possible correct form followed by the problematic form. With the use of tags possible proper names and English words are separated from others. 
	- 2nd column *sentence*: example sentences from where the problematic forms were found.
	- 3rd column *filename*: filenames of the files consisting the example sentences. 
 
 	NB! All word pairs in `words_wo_diacritics.csv` have been mined automatically from the etTenTen corpus, and because heuristics were used, there can also be incorrect matches (e.g. ['OK-mõni-msni'], ['OK-öine-nine'])! Words in `words_letter_reps.csv` were also mined heuristically from a subset of the etTenTen corpus. 

* `particles_userdict.csv` -- csv-file that gives correct morphological analyses for particles (e.g. *vä*, *lol*, *hihi*) with the help of UserDictTagger. File consists of particles and their new correct analyses (POS-tag - B).

* `NormalizeWordsRetagger_tutorial.ipynb` -- tutorial on how to use NormalizeWordsRetagger.
    - File named `particles_userdict.csv` is required for running the third example in the notebook.
