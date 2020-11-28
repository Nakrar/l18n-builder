import asyncio
import json
import os

from settings import OUTPUT_TOKENIZATION_FOLDER, INPUT_FOLDER, OUTPUT_TRANSLATION_JP_FOLDER
from tokenization import process_html_to_tokens, process_tokenized_to_translated_html
from translation import TranslationClient

ENGLISH = "en"
JAPANESE = "jp"


def save_file(directory: str, file_name: str, content: str):
    if not os.path.isdir(directory):
        os.mkdir(directory)
    with open(os.path.join(directory, file_name), 'wb') as file:
        file.write(content.encode('utf8'))


async def do_translate(file_name, translation_client, tokens=None):
    # load tokenized html and tokens
    tokenized_html_path = os.path.join(OUTPUT_TOKENIZATION_FOLDER, file_name)
    tokenized_tokens_path = os.path.join(OUTPUT_TOKENIZATION_FOLDER, file_name.replace('html', 'json'))
    with open(tokenized_html_path, "r") as file:
        tokenized_html = file.read()
    # according to the task, we need to be able to pass tokens directly
    # "Please provide code that will accept our associated array of texts indexed by unique IDs"
    if tokens is None:
        with open(tokenized_tokens_path, "r") as file:
            tokens = json.loads(file.read())

    # run translation service
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
    save_file(OUTPUT_TRANSLATION_JP_FOLDER, file_name, translated_html)
    serialized_translated_tokens = json.dumps(translated_tokens, ensure_ascii=False, indent=4)
    save_file(OUTPUT_TRANSLATION_JP_FOLDER, file_name.replace("html", "json"), serialized_translated_tokens)


def do_tokenize(file_name):
    # run tokenization
    input_file_path = os.path.join(INPUT_FOLDER, file_name)
    tokenized_html, tokens = process_html_to_tokens(input_file_path)
    # save tokenization output
    save_file(OUTPUT_TOKENIZATION_FOLDER, file_name, tokenized_html)
    serialized_tokens = json.dumps(tokens, ensure_ascii=False, indent=4)
    save_file(OUTPUT_TOKENIZATION_FOLDER, file_name.replace("html", "json"), serialized_tokens)
    return tokenized_html, tokens


async def main():
    translation_client = TranslationClient()

    # for each HTML file in INPUT_FOLDER, tokenize and translate
    if os.path.exists(INPUT_FOLDER):
        all_html_files = [file_name for file_name in os.listdir(INPUT_FOLDER) if file_name.endswith(".html")]
        for i, file_name in enumerate(all_html_files):
            print(f'\nwork on [{i}/{len(all_html_files)}] "{file_name}"')
            # TODO run asynchronously
            do_tokenize(file_name)
            await do_translate(file_name, translation_client)

    return


if __name__ == "__main__":
    asyncio.run(main())
