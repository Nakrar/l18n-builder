# i18n Builder

Tokenization and translation modules for future system.

Would process `.html` files in `./input` folder. Outputs tokens and processed HTML files to `./output_tokenization` and `./output_translation_jp` for tokenization and translation modules respectevly.  

You can change folder structure as well as translation service restrictions in `settings.py`.

### How to run

Assuming you have python 3.8. From the application folder: 

1. create new venv `virtualenv .env`
1. activate venv `source .env/bin/python`
1. install dependencies `pip install -r requirements.txt`
1. run main.py `python main.py`

### Possible improvements

1. Add tests
1. Run translation service asynchronously for different files.
    - For now translations would run asynchronously for single file. Running translation asynchronously for different files would cut on time used to wait for translation service. (Wouldn't be beneficial if translation service restrictions would be the bottleneck.)
1. Add global localization file and use it as TranslationService cache:
    - Would add ability to adjust translations not only page-by-page basis but for whole application;
    - Would cut on API requests for re-runs of the translation tool.
1. Investigate on HTML parsing method. Current implementation has relatively poor performance.
    - Try different parser for BeautifulSoup.
    - Run parsing in separate threads (since parsing is expensive operation we wouldn't benefit from running several parsing tasks asynchronously on one thread, we need a different threads).
1. Add ability to specify desired language in a command line. 


### How should we create the unique IDs? What properties should they have?

In order to generate token for a word/sentence we're:
1. Normalizing target string. It would allow us to get the same hash for the same strings, even if they have different case.
1. Run hash function and truncating result to 14 chars. Truncated result should be unique enough, but would allow us to save some space and make HTML and token files more readable.

While designing tokenization system I've decided to split text on by-sentence basis.
It would increase granularity of the localization.
Also, it would allow us to save time on review in case of update to original document.
We would be required do review just the updated sentences, not whole paragraphs.

Downside of using hash as a key for the strings:
We cannot get strings in the order of appearance in the original text, just from simple sort by key. Could be solved by writing tokens to token file according to order of apperance in HTML.    
