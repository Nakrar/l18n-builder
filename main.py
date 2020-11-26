"""
goal:

Input of html files/ fragments

Output of translated html file,


"""
import hashlib
import os
import re
from typing import List, Dict, Set
from bs4 import BeautifulSoup

from selectolax.parser import HTMLParser

INPUT_FOLDER = "./input"

File = any

JAPANESE = "jp"
ENGLISH = "en"

global_key_storage = {
    "==hello==": {JAPANESE: "konichiva", ENGLISH: "hello"},
}

""":return unique strings from  the html"""


def process_html_to_tokens(html: str):
    # TODO occasionally misses strings, need to take a deeper look
    # eg "https://www.mitsubishi-motors.com/en/index.html": "Announcement regarding Grant of Stock Options as Equity-linked Compensation(274KB)"
    soup = BeautifulSoup(html, features="html.parser")

    text = get_text_from_soup(soup)
    tokens = replace_text_in_soup(soup, text)

    return str(soup), tokens


def replace_text_in_soup(soup, text):
    tokens = {}

    for string in text:
        # ignore empty or one-char str since is probably not an english word
        if len(string) > 1:
            id = get_string_id(string)
            tokens[id] = string

            node_matches = soup.find_all(text=re.compile(f".*{string}.*"))
            for node in node_matches:
                node.replace_with(node.replace(string, id))

    return tokens


def get_text_from_soup(soup):
    # get text
    text = soup.get_text(separator="\n")
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = list(chunk for chunk in chunks if chunk)
    # replace long strings first
    text.sort(key=len, reverse=True)
    return text


def get_string_id(s: str) -> str:
    # using hash function we would get same key for the same input each time
    normalized_str = s.strip().lower()
    return hashlib.sha1(normalized_str.encode("UTF-8")).hexdigest()[:14]


def process_doc(file_name):
    with open(os.path.join(INPUT_FOLDER, file_name), "r") as file:
        html = file.read()
        if "<body" not in html:
            html = "<body>" + html + "</body>"

        text = process_html_to_tokens(html)

        for string in text:
            # ignore empty or one-char str since is probably not an english word
            if len(string) > 1:
                id = get_string_id(string)
                html = html.replace(string, id)

    return html


def main():
    # read file
    if os.path.exists(INPUT_FOLDER):
        for file_name in os.listdir(INPUT_FOLDER):
            if file_name.endswith(".html"):
                process_doc(file_name)
    # word/sentence key should be a hash. it would allow us to get consistent keys for the same input
    # write translation and l18n fiels

    return


# def parse_html(html_file: File, keys_storage: Dict[str, str]) -> List[str]:
#     sentence_key = keys_storage.get(sentence)
#
#     pass


if __name__ == "__main__":
    main()
