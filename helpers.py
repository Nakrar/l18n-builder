import hashlib
import re


def replace_text_in_soup(soup, before_after_pairs):
    for (before, after) in set(before_after_pairs):
        search_regexp = re.compile(re.escape(before), re.IGNORECASE)

        node_matches = soup.find_all(text=search_regexp)
        for node in node_matches:
            node.replace_with(search_regexp.sub(after, node))


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
