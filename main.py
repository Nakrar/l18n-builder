"""
goal:

Input of html files/ fragments

Output of translated html file,


"""
import hashlib
import os
import re
from typing import Dict

from bs4 import BeautifulSoup

INPUT_FOLDER = "./input"
OUTPUT_FOLDER = "./output"

JAPANESE = "jp"
ENGLISH = "en"

global_key_storage = {
    "==hello==": {JAPANESE: "konichiva", ENGLISH: "hello"},
}


def process_html_to_tokens(file_name: str) -> (str, Dict[str, str]):
    # TODO occasionally misses strings, need to take a deeper look
    # eg "https://www.mitsubishi-motors.com/en/index.html": "Announcement regarding Grant of Stock Options as Equity-linked Compensation(274KB)"
    with open(os.path.join(INPUT_FOLDER, file_name), "r") as file:
        html = file.read()

    soup = BeautifulSoup(html, features="html.parser")

    # TODO with current approach to sentence division we would have dot(.) as in original text (not localize)
    # For now one solution would be to add it to the localization list, but need to fix before production
    sentences = get_text_from_soup(soup)

    tokens = replace_text_in_soup(soup, sentences)

    return str(soup), tokens


def replace_text_in_soup(soup, strings):
    tokens = {}

    # replace sentences first, separate words later
    strings.sort(key=len, reverse=True)

    for string in set(strings):
        # ignore empty or one-char str since is probably not an english word
        if len(string) > 1:
            id = get_string_id(string)
            tokens[id] = string

            # TODO for some reason soup wouldn't find string if there is a parenthesis in it
            search_regexp = re.compile(f".*{string[:string.find('(') or string.find(')')]}.*")

            node_matches = soup.find_all(text=search_regexp)
            for node in node_matches:
                node.replace_with(node.replace(string, id))

    return tokens


def get_text_from_soup(soup):
    """:return sentences from the html"""
    # get text
    text = soup.get_text(separator="\n")
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines, split text by sentences
    sentences_list = (chunk.split(". ") for chunk in chunks if chunk)
    # flatten list out and return
    return [sentence for sentences in sentences_list for sentence in sentences]


def get_string_id(target: str) -> str:
    """
    in order to generate token for a word/sentence we're
    - first normalizing target string,
        it would allow us to get the same hash for the same strings having different letter case
    - next we using hash function and cutting it to 14 chars,
        which would be still unique but would take a little bit less space

    While designing tokenization system I've decided to tokenize text on by-sentence basis.
    It would increase granularity of the localization which would allow us to invalidate less,
    text on updates to original document.

    :param target: target string
    :return: key for the target
    """
    normalized_str = target.strip().lower()
    return hashlib.sha1(normalized_str.encode("UTF-8")).hexdigest()[:14]


def main():
    # read file
    if os.path.exists(INPUT_FOLDER):
        for file_name in os.listdir(INPUT_FOLDER):
            if file_name.endswith(".html"):
                tokenized_html, tokens = process_html_to_tokens(file_name)


    # word/sentence key should be a hash. it would allow us to get consistent keys for the same input
    # write translation and l18n fiels

    return


if __name__ == "__main__":
    main()
