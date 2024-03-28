# -*- coding: utf-8 -*-

import sys
import time
import os

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'lib'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))
sys.path.append(os.path.join(parent_folder_path, 'lib/lxml'))

import requests
import re
import reverso_api
from flowlauncher import FlowLauncher
import webbrowser
from collections import defaultdict


class ReversoFlow(FlowLauncher):
    path = "Images/app.png"

    const = {
        "en": "english",
        "de": "german",
        "ru": "russian"
    }

    def_src = "de"
    def_trg = "en"

    lang_resolver = defaultdict(lambda: "english")
    lang_rev_resolver = defaultdict(lambda: "en")

    russian_alpha = re.compile("[а-яА-Я]")
    german_alpha = re.compile("[äÄüÜöÖß]")

    # ru -> en + de (exact translation)
    # ru -> de (exact translation)

    # en -> ru (exact translation)
    # en -> de (spelling context, translation for en)

    # de -> en (spelling, context, translation for de)
    # de -> ru (exact translation)

    # rd ->
    # r + russian ->

    def __init__(self):
        super().__init__()
        for (k, v) in self.const.items():
            self.lang_resolver[k] = v
            self.lang_rev_resolver[v] = k

    def get_lang(self, query):
        # if self.is_russian(query): return

        return [self.def_src], [self.def_trg]


    def query(self, param: str = '') -> list:
        if len(param) < 2: return []
        if len(param) < 5: time.sleep(1)

        for (src, trg) in self.get_langs(param):

        return list(self.generate_results(param, sr))


    def get_target_lang(self, query):
        if (query.startswith("re ")):
            return

    def is_german(self, query):
        return bool(self.german_alpha.search(query))

    def is_russian(self, query):
        return bool(self.russian_alpha.search(query))

    def generate_results(self, query, src, trg):

        url = self.link(query, src_lang, trg_lang)
        if not url: return []
        max_contexts = 10
        max_translations = 5
        for (source, target) in self.get_reverse(query, src_lang, trg_lang, max_contexts, max_translations):
            yield self.query_entry(source, target, url)

    def query_entry(self, title, subtitle, link):
        return {
            "Title": title,
            "SubTitle": subtitle,
            "IcoPath": ReversoFlow.path,
            "JsonRPCAction": {
                "method": "open_url",
                "parameters": [link]
            }
        }

    def link(self, src_lang, trg_lang, query):
        return f"https://context.reverso.net/translation/{self.lang_resolver[src_lang]}-{self.lang_resolver[trg_lang]}/{query}"

    def context_menu(self, data):
        return [
            {
                "Title": "Hello <b>World Python's Contessxt menu</b>",
                "SubTitle": "Press enter to open Flow the plugin's repo in GitHub",
                "IcoPath": "Images/app.png",
                "JsonRPCAction": {
                    "method": "open_url",
                    "parameters": ["https://github.com/Flow-Launcher/Flow.Launcher.Plugin.HelloWorldPython"]
                }
            }
        ]

    def open_url(self, url):
        webbrowser.open(url)

    def get_reverse(self, input, src_lang, trg_lang, max_contexts, max_translations):
        api = reverso_api.context.ReversoContextAPI(input, "", src_lang, trg_lang)

        translations = []
        for translation in api.get_translations():
            if len(translations) >= max_translations: break
            translations.append(translation.translation)
        yield " | ".join(translations), ""

        contexts = 0
        for (source, target) in api.get_examples():
            if contexts >= max_contexts: break
            yield source.text, target.text
            contexts += 1

    def highlight_example(self, text, highlighted):
        def insert_char(string, index, char):
            return string[:index] + char + string[index:]

        def highlight_once(string, start, end, shift):
            s = insert_char(string, start + shift, "*")
            s = insert_char(s, end + shift + 1, "*")
            return s

        shift = 0
        for start, end in highlighted:
            text = highlight_once(text, start, end, shift)
            shift += 2
        return text


if __name__ == "__main__":
    h = ReversoFlow()
    # print(h.get_url_and_lang("what is it"))
    # print(h.query("was soll das"))
