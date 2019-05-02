# Spell-checker evaluation on etTenTen documents

---

## Resources and scripts

 * `[ettenten-valik]` -- a subset of the [etTenTen 2013 corpus](https://metashare.ut.ee/repository/browse/ettenten-korpus-toortekst/b564ca760de111e6a6e4005056b4002419cacec839ad4b7a93c3f7c45a97c55f) in which documents have been analysed morphologically + syntactically and later been manually corrected. Documents are in _cg_ format.
 
	Documents of the corpus are available in the repository [https://github.com/EstSyntax/EDT/tree/master/ettenten-valik](https://github.com/EstSyntax/EDT/tree/master/ettenten-valik).

* `norm_corpus.py` -- script that takes files in _cg_ format from a folder  `[ettenten-valik]` and as a output saves the files in a new _tsv_ format with added information into an existing folder `[ettenten-valik_tsv]`.
	
	The _tsv_ files created have got three columns:
		
	- 1st column: Words from original texts are listed along the first column. 
	- 2nd column: Every word from original texts is analysed -- whether the word has correct spelling or not. Based on the analysis, word is normalized or not. If spelling is incorrect and it is possible to automatically give it a normalized form, the new normalized form is added to the second column of a word. If word is correct or for some reason normalized form is not given, the original form of the word is added to the second column.
	- 3rd column: Every word has a tag. This way words are categorized and can be checked separately in evaluation process, if needed.
		
		- There are 15 different tags. 
					
			- _Emo_ -- emoticons
			- _Name_ -- proper names (cannot consist numbers)
			- _Abbrev_ -- abbreviations (cannot consist numbers)
			- _Abbrev\_Num_ -- proper names and abbreviations that consist numbers
			- _Ok_ -- correct word, that isn't name; emoticon; abbreviation
			- _Word\_w\_Punct_ -- words that consist of _-_; _:_; _/_
			- _Spell\_Missing\_Diacritics_ -- words where letters [äöõü] are missing or replaced with something else
			- _Spell\_Changed\_Diacritics_ -- words where any of the letters [äöõü] are replaced with another letter from this group
			- _Spell\_Missing\_Space_ -- words that shouldn't be written together (note: only a few manually added analyses)
			- _Spell\_ED\_1_ -- words where edit distance between the original and correct form is 1
			- _Spell\_ED>1_ -- words where edit distance between the original and correct form is bigger than 1
			- _Spell\_Unknown\_Gen_ -- words in genitive where synthesized word form could be wrong
			- _Spell\_Unknown\_Part_ -- words in partitive where synthesized word form could be wrong
			- _Spell\_Unknown_ -- all other problematic words, that were left without a normalized form
			- _Punct_ -- punctuation
			

	- Command line: `python norm_corpus.py`. Folder named `ettenten-valik` with _cg_ files in it is required; folder named `ettenten-valik_tsv` has to be created before running the script. `python-levenshtein` extension has to be installed (`pip install python-Levenshtein`).

- `norm_corpus_jupyter.ipynb` -- previous code in jupyter notebook with source code of CG3AnnotationParser (in case there are problems with importing the parser). `python-levenshtein` extension has to be installed (`pip install python-Levenshtein`)

- `testing_evaluation.py` -- evaluation of spell-checker on created corpus (how well are mistakes found and suggestions given).
		
	- Command line: `python testing_evaluation.py`. The output of script `norm_corpus.py` is required -- folder named `ettenten-valik_tsv`.
	

Corpus of _tsv_ files is created automatically, meaning it may contain several mistakes regarding the normalized forms or given tags. The original morphological analysis of words didn't include normalized forms, thus many of these forms where automatically synthesized based on the given morphological information. These new normalized forms were not manually checked. 
	
Although there are 15 different tags used in this corpus, these shouldn't really be used for gathering information about the number of occurrences in different categories. Several words may suit to more than one category, thus the given number of occurrences in one category doesn't often contain all of such cases. But in evaluation tags are still good to use in terms of how spell-checker works with different type of words in general.
