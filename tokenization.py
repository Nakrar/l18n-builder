from typing import Dict

from bs4 import BeautifulSoup

from helpers import replace_text_in_soup, get_string_id


def process_html_to_tokens(html: str) -> (str, Dict[str, str]):
    soup = BeautifulSoup(html, features="html.parser")

    # TODO with current approach to sentence division we would have dot(.) as in original text (not localize)
    # For now one solution would be to add it to the localization list, but need to fix before production
    sentences = get_text_from_soup(soup)

    tokens = generate_tokens_for_sentences(sentences)
    string_key_pair = zip(tokens.values(), tokens.keys())
    # replace long strings (sentences) first, short strings (single words) next
    string_key_pair = sorted(string_key_pair, key=lambda pair: len(pair[0]), reverse=True)



    replace_text_in_soup(soup, string_key_pair)
    output_html = str(soup)
    return output_html, tokens


def generate_tokens_for_sentences(sentences):
    # same strings would result in the same token, so work on unique strings only
    sentences = set(sentences)
    # ignore empty or one-char str since is probably not an english word
    sentences = (sentence for sentence in sentences if len(sentence) > 1)

    return {get_string_id(sentence): sentence for sentence in sentences}


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
