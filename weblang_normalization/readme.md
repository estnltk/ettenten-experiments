# Experiments on normalizing web language

---

## Resources and scripts

* `NormalizeWordsRetagger.py` -- retagger for adding normalized word forms for words of non-standard varieties of Estonian (e.g. the Internet slang, or texts written in a dialect). Normalized forms are added under the attribute *normalized_form* of the words layer.

* ..

* `words_wo_diacritics.csv` -- csv-file used for testing and evaluation of words with missing or wrong diacritics (e.g. l2ks - läks; tuli - tüli). 
	- First column: lists of possible word pairs: e.g. ['OK-lõhki-lohki']. In every list first there is a tag (*OK*, *NAME*, *ENGLISH*) and then the possible correct form followed by the problematic form. With the use of tags possible proper names and English words are separated from others. 
	- Second column: exmaple sentences from where the problematic forms were found.
	- Third column: filenames of the files consisting the example sentences. 
 
 NB! All these possible word pairs have been created automatically, thus there may also be incorrect matches! (e.g. ['OK-mõni-msni'], ['OK-öine-nine'])

* ..
