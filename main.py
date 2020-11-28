"""
goal:

Input of html files/ fragments

Output of translated html file,


"""
import asyncio
import json
import os

from tokenizer import process_html_to_tokens, process_tokenized_to_translated_html
from translation import TranslationClient

ENGLISH = "en"
JAPANESE = "jp"


def save_file(directory, file_name, content):
    if not os.path.isdir(directory):
        os.mkdir(directory)
    with open(os.path.join(directory, file_name), "w") as file:
        file.write(content)


async def main():
    input_folder = "./input"
    output_tokenizer_folder = "./output_tokenizer"
    output_translation_folder = "./output_translation"

    translation_client = TranslationClient()

    # read file
    if os.path.exists(input_folder):
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".html"):
                # run tokenizer
                input_file_path = os.path.join(input_folder, file_name)
                tokenized_html, tokens = process_html_to_tokens(input_file_path)

                # save tokenizer output
                save_file(output_tokenizer_folder, file_name, tokenized_html)
                serialized_tokens = json.dumps(tokens)
                save_file(output_tokenizer_folder, file_name.replace("html", "json"), serialized_tokens)

                # run translation service
                # TODO run asynchronously for several files
                translated_strings = await translation_client.translate_strings(list(tokens.values()))
                # for now assume that original language is English, translation is Japanese
                # create dict with {key: LocalizationString}
                translated_tokens = {
                    k: {ENGLISH: en, JAPANESE: jp}
                    for k, en, jp
                    in zip(tokens.keys(), tokens.values(), translated_strings)
                }
                token_translation_pairs = ((k, v[JAPANESE]) for k, v in translated_tokens.items())
                translated_html = process_tokenized_to_translated_html(tokenized_html, token_translation_pairs)

                # save translation output
                save_file(output_translation_folder, file_name, translated_html)
                serialized_translated_tokens = json.dumps(translated_tokens)
                save_file(output_translation_folder, file_name.replace("html", "json"), serialized_translated_tokens)

    return


if __name__ == "__main__":
    asyncio.run(main())
