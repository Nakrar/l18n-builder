"""
goal:

Input of html files/ fragments

Output of translated html file,


"""
import asyncio
import json
import os

from tokenizer import process_html_to_tokens

JAPANESE = "jp"
ENGLISH = "en"

global_key_storage = {
    "==hello==": {JAPANESE: "konichiva", ENGLISH: "hello"},
}


def save_file(directory, file_name, content):
    if not os.path.isdir(directory):
        os.mkdir(directory)
    with open(os.path.join(directory, file_name), "w") as file:
        file.write(content)


async def main():
    input_folder = "./input"
    output_folder = "./output"
    _lock = asyncio.Lock()

    async with _lock:
        print(1)
        async with _lock:
            print(2)
        print(3)

    # read file
    if os.path.exists(input_folder):
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".html"):
                # run tokenizer
                input_file_path = os.path.join(input_folder, file_name)
                tokenized_html, tokens = process_html_to_tokens(input_file_path)

                # save tokenizer output
                save_file(output_folder, file_name, tokenized_html)
                serialized_tokens = json.dumps(tokens)
                save_file(output_folder, file_name.replace("html", "json"), serialized_tokens)

                # run translation service
    # word/sentence key should be a hash. it would allow us to get consistent keys for the same input
    # write translation and l18n fiels

    return


if __name__ == "__main__":
    asyncio.run(main())
