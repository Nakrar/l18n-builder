import asyncio
import unittest
from functools import reduce

from tokenization import process_html_to_tokens
from translation import TranslationClient, process_html_tokens_to_translation


async def mock_translation_api_request(target, source_lang='en', target_lang='jp'):
    mapping = {
        # proper japanese translation
        "A": "ア", "B": "ビ", "C": "シ", "D": "ディ", "E": "イ", "F": "フ", "G": "ジ", "H": "チ", "I": "イ", "J": "ジェ",
        "K": "ケ", "L": "ル", "M": "ム", "N": "ン", "O": "オ", "P": "ピ", "Q": "キュ", "R": "ラ", "S": "ス", "T": "ティ",
        "U": "ユ", "V": "ビ", "W": "ビ", "X": "", "Y": "", "Z": "ゼ"
    }

    result = [
        reduce(lambda s, kv: s.replace(kv[0], kv[1]), mapping.items(), string.upper())
        for string in target
    ]
    return result


class TestTokenization(unittest.TestCase):

    def test_tokenization(self):
        # setup
        html = INPUT_HTML

        # run tokenization service
        tokenized_html, tokens = process_html_to_tokens(html)

        # test output
        self.assertEqual(tokens, EXPECTED_OUTPUT_TOKENIZATION_TOKENS, "Tokenized tokens not as expected")
        self.assertEqual(tokenized_html, EXPECTED_OUTPUT_TOKENIZATION_HTML, "Tokenized HTML not as expected")


class TestTranslation(unittest.TestCase):

    def test_translation(self):
        # setup
        tokens = EXPECTED_OUTPUT_TOKENIZATION_TOKENS
        tokenized_html = EXPECTED_OUTPUT_TOKENIZATION_HTML
        translation_client = TranslationClient(translation_api_call=mock_translation_api_request)

        # run translation service
        translated_html, translated_tokens = asyncio.run(
            process_html_tokens_to_translation(
                tokenized_html=tokenized_html,
                tokens=tokens,
                translation_client=translation_client
            ))

        # test output
        self.assertEqual(translated_tokens, EXPECTED_OUTPUT_TRANSLATION_TOKENS, "Translated tokens not as expected")
        self.assertEqual(translated_html, EXPECTED_OUTPUT_TRANSLATION_HTML, "Translated HTML not as expected")


INPUT_HTML = """
<section class="relative bg-black antialiased text-white overflow-hidden">
    <div class="dark-overlay"></div>
    <div class="absolute pin-t pin-l w-full h-full">
        <img class="background-cover lazyload fade-in faded"
             src="data:image/jpeg;base64,%2F9j%2F4AAQSkZJRgABAQAASABIAAD%2F2wBDABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2P%2F2wBDARESEhgVGC8aGi9jQjhCY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2P%2FwAARCAAIABADASIAAhEBAxEB%2F8QAFgABAQEAAAAAAAAAAAAAAAAAAAQG%2F8QAHxAAAQQCAgMAAAAAAAAAAAAAAQIDBBEAEgUhIjGh%2F8QAFAEBAAAAAAAAAAAAAAAAAAAAAf%2FEABkRAAIDAQAAAAAAAAAAAAAAAAABAhEhMf%2FaAAwDAQACEQMRAD8AzTbkNaygRoqQs13sft3lL8Xj4qqdjMihsfJZPoGqB6xjC%2BAo6z%2F%2F2Q%3D%3D"
             alt="Image of Foc Cover Future Commerce Retail" title="Foc Cover Future Commerce Retail" />
    </div>
    <div class="container container-x relative z-20">
        <div class="flex-column-wrap">
            <div class="flex-column w-full xl:w-5/6 pt-32 mb-16">
                <p class="text-sm font-bold"><span class="mr-16">Blog posts</span><span class="text-grey">February 28, 2019</span></p>
                <h1>16 Retail &amp; Logistics Experts Weigh In on the Future of Commerce</h1>
                <p class="text-lg">In our latest collection, retail and supply chain leaders tell us what the future of retail has in store (and online).</p>
            </div>
        </div>
    </div>
</section>
"""

EXPECTED_OUTPUT_TOKENIZATION_TOKENS = {
    "0baef8d15e567c": "February 28, 2019",
    "661cc3f8a53846": "16 Retail & Logistics Experts Weigh In on the Future of Commerce",
    "0c81832420e7bd": "In our latest collection, retail and supply chain leaders tell us what the future of retail has in store (and online).",
    "23f61d90ab8bc8": "Blog posts"
}
EXPECTED_OUTPUT_TOKENIZATION_HTML = """
<section class="relative bg-black antialiased text-white overflow-hidden">
<div class="dark-overlay"></div>
<div class="absolute pin-t pin-l w-full h-full">
<img alt="Image of Foc Cover Future Commerce Retail" class="background-cover lazyload fade-in faded" src="data:image/jpeg;base64,%2F9j%2F4AAQSkZJRgABAQAASABIAAD%2F2wBDABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2P%2F2wBDARESEhgVGC8aGi9jQjhCY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2P%2FwAARCAAIABADASIAAhEBAxEB%2F8QAFgABAQEAAAAAAAAAAAAAAAAAAAQG%2F8QAHxAAAQQCAgMAAAAAAAAAAAAAAQIDBBEAEgUhIjGh%2F8QAFAEBAAAAAAAAAAAAAAAAAAAAAf%2FEABkRAAIDAQAAAAAAAAAAAAAAAAABAhEhMf%2FaAAwDAQACEQMRAD8AzTbkNaygRoqQs13sft3lL8Xj4qqdjMihsfJZPoGqB6xjC%2BAo6z%2F%2F2Q%3D%3D" title="Foc Cover Future Commerce Retail"/>
</div>
<div class="container container-x relative z-20">
<div class="flex-column-wrap">
<div class="flex-column w-full xl:w-5/6 pt-32 mb-16">
<p class="text-sm font-bold"><span class="mr-16">23f61d90ab8bc8</span><span class="text-grey">0baef8d15e567c</span></p>
<h1>661cc3f8a53846</h1>
<p class="text-lg">0c81832420e7bd</p>
</div>
</div>
</div>
</section>
"""

EXPECTED_OUTPUT_TRANSLATION_TOKENS = {
    "0baef8d15e567c": {
        "en": "February 28, 2019",
        "jp": "フイビラユアラ 28, 2019"
    },
    "661cc3f8a53846": {
        "en": "16 Retail & Logistics Experts Weigh In on the Future of Commerce",
        "jp": "16 ライティアイル & ルオジイスティイシス イピイラティス ビイイジチ イン オン ティチイ フユティユライ オフ シオムムイラシイ"
    },
    "0c81832420e7bd": {
        "en": "In our latest collection, retail and supply chain leaders tell us what the future of retail has in store (and online).",
        "jp": "イン オユラ ルアティイスティ シオルルイシティイオン, ライティアイル アンディ スユピピル シチアイン ルイアディイラス ティイルル ユス ビチアティ ティチイ フユティユライ オフ ライティアイル チアス イン スティオライ (アンディ オンルインイ)."
    },
    "23f61d90ab8bc8": {
        "en": "Blog posts",
        "jp": "ビルオジ ピオスティス"
    }
}

EXPECTED_OUTPUT_TRANSLATION_HTML = """
<section class="relative bg-black antialiased text-white overflow-hidden">
<div class="dark-overlay"></div>
<div class="absolute pin-t pin-l w-full h-full">
<img alt="Image of Foc Cover Future Commerce Retail" class="background-cover lazyload fade-in faded" src="data:image/jpeg;base64,%2F9j%2F4AAQSkZJRgABAQAASABIAAD%2F2wBDABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2P%2F2wBDARESEhgVGC8aGi9jQjhCY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2P%2FwAARCAAIABADASIAAhEBAxEB%2F8QAFgABAQEAAAAAAAAAAAAAAAAAAAQG%2F8QAHxAAAQQCAgMAAAAAAAAAAAAAAQIDBBEAEgUhIjGh%2F8QAFAEBAAAAAAAAAAAAAAAAAAAAAf%2FEABkRAAIDAQAAAAAAAAAAAAAAAAABAhEhMf%2FaAAwDAQACEQMRAD8AzTbkNaygRoqQs13sft3lL8Xj4qqdjMihsfJZPoGqB6xjC%2BAo6z%2F%2F2Q%3D%3D" title="Foc Cover Future Commerce Retail"/>
</div>
<div class="container container-x relative z-20">
<div class="flex-column-wrap">
<div class="flex-column w-full xl:w-5/6 pt-32 mb-16">
<p class="text-sm font-bold"><span class="mr-16">ビルオジ ピオスティス</span><span class="text-grey">フイビラユアラ 28, 2019</span></p>
<h1>16 ライティアイル &amp; ルオジイスティイシス イピイラティス ビイイジチ イン オン ティチイ フユティユライ オフ シオムムイラシイ</h1>
<p class="text-lg">イン オユラ ルアティイスティ シオルルイシティイオン, ライティアイル アンディ スユピピル シチアイン ルイアディイラス ティイルル ユス ビチアティ ティチイ フユティユライ オフ ライティアイル チアス イン スティオライ (アンディ オンルインイ).</p>
</div>
</div>
</div>
</section>
"""
