# Experiments on detecting web language

---

## Resources and scripts

 * `[kirjak_vs_mittekirjak_ettenten]` -- a subset of the [etTenTen 2013 corpus](https://metashare.ut.ee/repository/browse/ettenten-korpus-toortekst/b564ca760de111e6a6e4005056b4002419cacec839ad4b7a93c3f7c45a97c55f) in which documents have been manually classified into two categories: canonical language texts (_kirjak_) and non-canonical language texts (_mittekirjak_). All documents are in _json_ format, and the files can be loaded / imported as EstNLTK v1.6 Text objects.
 
    The origins of the corpus: see the article by [Vaik and Muischnek (2018)](http://arhiiv.rakenduslingvistika.ee/ajakirjad/index.php/aastaraamat/article/view/ERYa14.13); documents of the corpus are available in the repository [https://github.com/kristiinavaik/veebikorpuse-klassifitseerimine](https://github.com/kristiinavaik/veebikorpuse-klassifitseerimine) ;

* `paragraphweblanguagescoreretagger.py` -- retagger for detecting web language features in text. Web language features will be marked as attributes of the paragraphs layer.

* `paragraphweblanguagescoreretagger_tutorial` -- tutorial on how to use paragraphweblanguagescoreretagger.

* `process_and_save_results.py` -- script that takes json-files from a folder and adds to them layers required by paragraphweblanguagescoreretagger. Output is a folder with tagged json-files.
	- Command line: `python process_and_save_results.py kirjak_vs_mittekirjak_ettenten kirjak_vs_mittekirjak_ettenten_tagged`
	- Arguments: first argument is a folder of json-files that need to be tagged (`kirjak_vs_mittekirjak_ettenten`); second argument is an empty folder for tagged output files (`kirjak_vs_mittekirjak_ettenten_tagged`).

* `retagger_results_kirjak_vs_mittekirjak_to_csv.py` -- creates a csv-file `weblang_scores.csv`. In there all files with the total number of detected features are presented.
	- Command line: `python retagger_results_kirjak_vs_mittekirjak_to_csv.py`
	- Retagger `paragraphweblanguagescoreretagger.py` has to be accessible.
	- The output of script `process_and_save_results.py` is required -- folder named `kirjak_vs_mittekirjak_ettenten_tagged`.
	
* `retagger_average_score_kirjak_vs_mittekirjak.py` -- script gives an overview of how many features of web language there are on average in two different categories.
	- Command line: `python retagger_average_score_kirjak_vs_mittekirjak.py`
	- The output of script `retagger_results_kirjak_vs_mittekirjak_to_csv.py` is required -- file named `weblang_scores.csv`.

* `testing_kirjak_vs_mittekirjak_whole_text_score.py` -- for testing purposes to find a threshold value - when files, based on their calculated whole text score, can automatically be labelled as *mittekirjak*.
	- Command line: `python testing_kirjak_vs_mittekirjak_whole_text_score.py`
	- The output of script `retagger_results_kirjak_vs_mittekirjak_to_csv.py` is required -- file named `weblang_scores.csv`.
	- If a variable *only_docs_agreement_3* is set to True in script, file named `agreement_scores_kirjak_mittekirjak.csv` is required. If True, only files that were given the same label by 3 persons (*kirjak* vs *mittekirjak*) are used.
	- Currently threshold value 0.04 seems to give the best outcome.

* `testing_kirjak_vs_mittekirjak_KNN.py` -- for testing purposes to find a k-value for categorizing files as *kirjak/mittekirjak* by cosine / euclidean distance and KNN algorithm.
	- Command line: `python testing_kirjak_vs_mittekirjak_KNN.py`
	- The output of script `retagger_results_kirjak_vs_mittekirjak_to_csv.py` is required -- file named `weblang_scores.csv`.
	- If a variable *only_docs_agreement_3* is set to True in script, file named `agreement_scores_kirjak_mittekirjak.csv` is required. If True, only files that were given the same label by 3 persons (*kirjak* vs *mittekirjak*) are used.
	- Currently cosine distance seems to work better (with k-values of 3 or 5 and all features + word_count aswell).



