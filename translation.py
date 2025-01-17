import asyncio
import time
from functools import reduce
from typing import List

from bs4 import BeautifulSoup

from helpers import replace_text_in_soup, get_string_id
from settings import ENGLISH, JAPANESE, PER_REQUEST_LIMIT_CHAR, ACCUMULATIVE_LIMIT_CHAR, ACCUMULATIVE_COOLDOWN_MS

mapping = {
    # proper japanese translation
    "A": "ア", "B": "ビ", "C": "シ", "D": "ディ", "E": "イ", "F": "フ", "G": "ジ", "H": "チ", "I": "イ", "J": "ジェ",
    "K": "ケ", "L": "ル", "M": "ム", "N": "ン", "O": "オ", "P": "ピ", "Q": "キュ", "R": "ラ", "S": "ス", "T": "ティ",
    "U": "ユ", "V": "ビ", "W": "ビ", "X": "", "Y": "", "Z": "ゼ"
}


async def translation_api_request(target: List[str], source_lang='en', target_lang='jp') -> List[str]:
    await asyncio.sleep(1)
    result = [
        reduce(lambda s, kv: s.replace(kv[0], kv[1]), mapping.items(), string.upper())
        for string in target
    ]
    return result


async def process_html_tokens_to_translation(tokenized_html, tokens, translation_client):
    # translate tokens and create new tokens, containing original and translated string
    strings_to_translate = list(tokens.values())
    translated_strings = await translation_client.translate_strings(strings_to_translate)
    translated_tokens = {
        k: {ENGLISH: en, JAPANESE: jp}
        for k, en, jp
        in zip(tokens.keys(), tokens.values(), translated_strings)
    }

    # replace tokens with translation
    token_translation_pairs = ((k, v[JAPANESE]) for k, v in translated_tokens.items())
    soup = BeautifulSoup(tokenized_html, features="html.parser")
    replace_text_in_soup(soup, token_translation_pairs)
    translated_html = str(soup)

    return translated_html, translated_tokens


class TranslationClient:
    per_request_limit_char = PER_REQUEST_LIMIT_CHAR
    accumulative_limit_char = ACCUMULATIVE_LIMIT_CHAR
    accumulative_cooldown_ms = ACCUMULATIVE_COOLDOWN_MS

    def __init__(self, translation_api_call=translation_api_request):
        if self.per_request_limit_char > self.accumulative_limit_char:
            raise ValueError("accumulative_limit_char should be more or equal to per_request_limit_char")

        self._translation_api_call = translation_api_call
        self._request_log = []
        self._request_char_sum = 0
        self._cache = {}  # todo local from localization file, save to localization file
        self._insert_lock = asyncio.Lock()
        self._update_lock = asyncio.Lock()

    # todo add global localization file that would double up as localization cache
    def _read_from_cache(self, string):
        return self._cache.get(get_string_id(string))

    def _write_to_cache(self, string, translation):
        self._cache[get_string_id(string)] = translation

    async def _update_request_log(self):
        """
        clear _request_log from old records
        """
        async with self._update_lock:
            now_ms = int(time.time() * 1000)
            while self._request_log:
                (block_time_ms, _) = self._request_log[0]
                cooldown_on_ms = block_time_ms + self.accumulative_cooldown_ms
                if now_ms > cooldown_on_ms:
                    (_, quantity) = self._request_log.pop(0)
                    self._request_char_sum -= quantity
                else:
                    return

    async def _insert_request_log(self, quantity):
        """
        Insert new log entry and increment how many characters was used so far.
        Wait for resources to become available if limit is reached

        Note: we assume that translation server would assert out request limit
        and keep track of when cooldown ends based on request start time, not on request resolve time.
        """
        async with self._insert_lock:
            # wait for resources to become available
            while quantity + self._request_char_sum > self.accumulative_limit_char:
                if not self._request_log:
                    raise AssertionError("Log is empty but resources unavailable")

                now_ms = int(time.time() * 1000)
                (block_time_ms, _) = self._request_log[0]
                cooldown_on_ms = block_time_ms + self.accumulative_cooldown_ms
                next_available_in_ms = cooldown_on_ms - now_ms
                if next_available_in_ms > 0:
                    next_available_in_s = next_available_in_ms / 1000
                    # wait for next record cooldown and update limits
                    print(f"\tfailed to block {quantity}chr. waiting {next_available_in_s}s.; "
                          f"used [{self._request_char_sum}/{self.accumulative_limit_char}]")
                    await asyncio.sleep(next_available_in_s)
                await self._update_request_log()

            # block resources
            now_ms = int(time.time() * 1000)
            self._request_log.append((now_ms, quantity))
            self._request_char_sum += quantity
            print(f"\tblocked {quantity}chr.; "
                  f"used [{self._request_char_sum}/{self.accumulative_limit_char}]")

    async def _make_request_with_resource_block(self, target):
        """
        before making request to translation backend we want to make sure that we're within limits
        current implementation waits until requested resources are available
        """
        length_total = sum(map(len, target))

        if length_total > self.per_request_limit_char:
            raise ValueError(f"single request should be no more then {self.per_request_limit_char} chars long")

        await self._insert_request_log(length_total)

        return await self._translation_api_call(target)

    def split_to_request_groups(self, target):
        # split request to groups that respect `per_request_limit_char`
        length_sum = 0
        request_groups = [[]]
        for index, string in enumerate(target):
            # check can we add current string to existing request
            length_sum += len(string)
            if length_sum > self.per_request_limit_char:
                # if existing request would be overflown by our string, create new request batch
                length_sum = len(string)
                request_groups.append([])
            # add string to active request
            request_groups[-1].append(string)
        return [group for group in request_groups if group]

    async def translate_request_groups(self, request_groups):
        tasks = (
            asyncio.create_task(self._make_request_with_resource_block(group))
            for group in request_groups
        )
        return await asyncio.gather(*tasks)

    async def translate_strings(self, target: List[str]) -> List[str]:
        if not target:
            return []
        start_ms = int(time.time() * 1000)

        # we dont want to split string by ourself since it can change meaning of resulting translation
        # but we still want to be able to translate it if there is such entry in out localization file
        if any(string for string in target if
               len(string) > self.per_request_limit_char
               and self._read_from_cache(string) is None
               ):
            raise ValueError(f"Maximum length of a single string is {self.per_request_limit_char}")

        # we want to keep order of input strings, so create array and pre fill it with cached results
        result = [self._read_from_cache(string) for string in target]

        # split request to groups that respect `per_request_limit_char`
        strings_to_translate = [string for index, string in enumerate(target) if result[index] is None]
        request_groups = self.split_to_request_groups(strings_to_translate)

        translated_groups = await self.translate_request_groups(request_groups)

        translation_list = (translation for group in translated_groups for translation in group)

        # insert new translations to result and cache, skipping already populated indexes
        offset = 0
        for i_, translation in enumerate(translation_list):
            index = offset + i_
            # find next index that had no cached value
            while result[index] is not None:
                offset += 1
                index = offset + i_
            # insert to the index
            result[index] = translation
            original = target[index]
            self._write_to_cache(original, translation)

        print(f"\ttranslated {sum(map(len, target))}ch. in {int(time.time() * 1000) - start_ms}ms. "
              f"with {sum(map(len, target)) - sum(map(len, strings_to_translate))}ch. from cache")
        # TODO save cache to global localization file here
        return result
