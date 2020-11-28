import hashlib
import re
from typing import Dict

from bs4 import BeautifulSoup


def process_tokenized_to_translated_html(html, token_translation_pairs) -> (str):
    soup = BeautifulSoup(html, features="html.parser")

    replace_text_in_soup(soup, token_translation_pairs)

    return str(soup)


def process_html_to_tokens(file_path: str) -> (str, Dict[str, str]):
    with open(file_path, "r") as file:
        html = file.read()

    soup = BeautifulSoup(html, features="html.parser")

    # TODO with current approach to sentence division we would have dot(.) as in original text (not localize)
    # For now one solution would be to add it to the localization list, but need to fix before production
    sentences = get_text_from_soup(soup)

    tokens = generate_tokens_for_sentences(sentences)
    string_key_pair = zip(tokens.values(), tokens.keys())
    # replace long strings (sentences) first, short strings (single words) next
    string_key_pair = sorted(string_key_pair, key=lambda pair: len(pair[0]), reverse=True)

    replace_text_in_soup(soup, string_key_pair)

    return str(soup), tokens


def generate_tokens_for_sentences(sentences):
    # same strings would result in the same token, so work on unique strings only
    sentences = set(sentences)
    # ignore empty or one-char str since is probably not an english word
    sentences = (sentence for sentence in sentences if len(sentence) > 1)

    return {get_string_id(sentence): sentence for sentence in sentences}


def replace_text_in_soup(soup, before_after_pairs):
    for (before, after) in set(before_after_pairs):
        search_regexp = re.compile(re.escape(before), re.IGNORECASE)

        node_matches = soup.find_all(text=search_regexp)
        for node in node_matches:
            node.replace_with(search_regexp.sub(after, node))


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
