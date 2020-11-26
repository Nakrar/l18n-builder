import asyncio
import time
from typing import List

from tokenizer import get_string_id


async def api_call(target) -> List[str]:
    await asyncio.sleep(1)
    return ["にほんご"] * len(target)


class TranslationClient:
    per_request_limit_char = 30.000
    accumulative_limit_char = 100.000
    accumulative_cooldown_ms = 100 * 1000

    def __init__(self):
        if self.per_request_limit_char > self.accumulative_limit_char:
            raise ValueError("accumulative_limit_char should be more or equal to per_request_limit_char")

        self._request_log = []
        self._request_char_sum = 0
        self._cache = {}  # todo local from localization file, save to localization file
        self._insert_lock = asyncio.Lock()
        self._update_lock = asyncio.Lock()

    # todo add localization file that would double up as localization cache
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
                # wait for next record cooldown and update limits
                await asyncio.sleep(next_available_in_ms + 500 / 1000)
                await self._update_request_log()

            # block resources
            now_ms = int(time.time() * 1000)
            self._request_log.append((now_ms, quantity))
            self._request_char_sum += quantity

    async def _make_request_with_resource_block(self, target):
        """
        before making request to translation backend we want to make sure that we're within limits
        current implementation waits until requested resources are available
        """
        length_total = sum(map(len, target))

        if length_total > self.per_request_limit_char:
            raise ValueError(f"single request should be no more then {self.per_request_limit_char} chars long")

        await self._insert_request_log(length_total)

        return api_call(target)

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
        return request_groups

    def translate_request_groups(self, request_groups):
        tasks = (
            asyncio.create_task(self._make_request_with_resource_block(group))
            for group in request_groups
        )
        return asyncio.gather(tasks)

    def translate_strings(self, target: List[str]) -> List[str]:
        if not target:
            return []

        # we dont want to split string by ourself since it can change meaning of resulting translation
        # but we still want to be able to translate it if there is such entry in out localization file
        if any(string for string in target if
               len(string) > self.per_request_limit_char
               and self._read_from_cache(string) is None
               ):
            raise ValueError(f"Maximum length for single string is {self.per_request_limit_char}")

        # we want to keep order of input strings, so create array and pre fill it with cached results
        result = [self._read_from_cache(string) for string in target]

        # split request to groups that respect `per_request_limit_char`
        strings_to_translate = (string for index, string in enumerate(target) if result[index] is None)
        request_groups = self.split_to_request_groups(strings_to_translate)

        translated_groups = self.translate_request_groups(request_groups)

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

        # TODO maybe save cache to disk here
        return result
