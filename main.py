import asyncio
import json
import os

from settings import OUTPUT_TOKENIZATION_FOLDER, INPUT_FOLDER, OUTPUT_TRANSLATION_JP_FOLDER
from tokenization import process_html_to_tokens
from translation import TranslationClient, process_html_tokens_to_translation


def save_file(directory: str, file_name: str, content: str):
    if not os.path.isdir(directory):
        os.mkdir(directory)
    with open(os.path.join(directory, file_name), 'wb') as file:
        file.write(content.encode('utf8'))


async def do_translate(file_name, translation_client):
    # load tokenized HTML and tokens
    tokenized_html_path = os.path.join(OUTPUT_TOKENIZATION_FOLDER, file_name)
    tokenized_tokens_path = os.path.join(OUTPUT_TOKENIZATION_FOLDER, file_name.replace('html', 'json'))
    with open(tokenized_html_path, "r") as file:
        tokenized_html = file.read()
    with open(tokenized_tokens_path, "r") as file:
        tokens = json.loads(file.read())

    # run translation service
    translated_html, translated_tokens = await process_html_tokens_to_translation(
        tokenized_html=tokenized_html,
        tokens=tokens,
        translation_client=translation_client
    )

    # save translation output
    save_file(OUTPUT_TRANSLATION_JP_FOLDER, file_name, translated_html)
    serialized_translated_tokens = json.dumps(translated_tokens, ensure_ascii=False, indent=4)
    save_file(OUTPUT_TRANSLATION_JP_FOLDER, file_name.replace("html", "json"), serialized_translated_tokens)

    return translated_html, translated_tokens

def do_tokenize(file_name):
    # load input HTML
    input_file_path = os.path.join(INPUT_FOLDER, file_name)
    with open(input_file_path, "r") as file:
        html = file.read()

    # run tokenization
    tokenized_html, tokens = process_html_to_tokens(html)

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
