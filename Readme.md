# i18n Builder

Tokenization and translation modules for the future system.

### Usage
Tool would process `.html` files in `./input` folder. Outputs tokens and processed HTML files to `./output_tokenization` and `./output_translation_jp` for tokenization and translation modules respectively.  

You can change folder structure as well as translation service restrictions in `settings.py`.

### How to run

Requires python 3.7+

From the application folder:

1. create new venv `virtualenv .env`
1. activate venv `source .env/bin/python`
1. install dependencies `pip install -r requirements.txt`
1. run main.py `python main.py`

### Possible improvements
1. Add more tests.
1. Depending on usage, add CLI arguments.
1. Run translation service asynchronously for different files.
    - For now, translations would run asynchronously for a single file. Running translation asynchronously for different files would cut on the time used to wait for translation service. (Wouldn't be beneficial if translation service restrictions would be the bottleneck)
1. Add global localization file and use it as TranslationService cache:
    - Would add the ability to adjust translations not only page-by-page basis but for the whole application;
    - Would cut on API requests for re-runs of the translation tool.
1. Investigate on HTML parsing method. The current implementation has relatively poor performance.
    - Try a different parser for BeautifulSoup.
    - Run parsing in separate threads (since parsing is an expensive operation we wouldn't benefit from running several parsing tasks asynchronously on one thread, we need a different thread).
1. Add an ability to specify the desired language in a command line. 


### How should we create the unique IDs? What properties should they have?

To generate a token for a word/sentence we're:
1. Normalizing target string. It would allow us to get the same hash for the same strings, even if two strings would be in a different case.
1. Run hash function and truncating result to 14 chars. The truncated result should be unique enough but would allow us to save some space and make HTML and token files more readable.

While designing the tokenization system I've decided to split text on a by-sentence basis.
It would increase the granularity of the localization.
Also, it would allow us to save time on review in case of an update to the original document.
We would be required to review just the updated sentences.

The downside of using hash as a key for the strings:
We cannot get strings in the order of appearance in the original text, just from simple sort by key. Could be solved by writing tokens to token file according to the order of appearance in HTML.    
