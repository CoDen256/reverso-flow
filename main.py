# -*- coding: utf-8 -*-
import itertools
import pprint
import sys
import time
import os

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'lib'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))
sys.path.append(os.path.join(parent_folder_path, 'lib/lxml'))

import requests
import ctypes
import re
import reverso_api
from flowlauncher import FlowLauncher
import webbrowser
from collections import defaultdict


class ReversoFlow(FlowLauncher):
    path = "Images/app.png"

    const = {
        "en": ("english", "e"),
        "de": ("german", "d"),
        "ru": ("russian", "r"),
    }

    def_src = "de"
    def_trg = "en"

    lang_resolver = defaultdict(lambda: "english")
    lang_rev_resolver = defaultdict(lambda: "en")
    action_resolver = defaultdict(lambda: "en")

    russian_alpha = re.compile("[а-яА-Я]")
    german_alpha = re.compile("[äÄüÜöÖß]")
    max_contexts = 10
    max_translations = 10

    for (k, full_action) in const.items():
        full, action = full_action
        lang_resolver[k] = full
        lang_rev_resolver[full] = k
        action_resolver[action] = k

    # [<russian>]          ru -> en + de (exact translation)
    # [<keyboard-layout>]  de -> en (spelling, context, translation)
    #                           en -> de (spelling context, translation)

    # [<input> :en]        en ->

    # :er                 <src> -> en+ru  (exact translation) (0)
    # :e                  <src> -> en      for en) (2)

    # :d                  <src> -> de     (spelling, context, translation for de) (3)
    # :dr                 <src> -> de+ru  (exact translation) (1)

    # :drn                <src> -> de + ru + en

    def get_help_message(self):
        link = "https://context.reverso.net/translation/"
        return [
            self.query_entry(":n ", ":n <any lang> -> english ", link),
            self.query_entry(":d ", ":d <any lang> -> deutsch ", link),
            self.query_entry(":r ", ":r <any lang> -> russian ", link),
            self.query_entry("<text> :en", "<english text> -> deutsch", link),
            self.query_entry("<text> :de", "<german text> -> english", link),
            self.query_entry("<text> :ru", "<russian text> -> english + deutsch", link),
            self.query_entry(":<target>* [keyboard-lang]", "<keyboard-lang> -> <target>*", link),
            self.query_entry(":<target>* <text> <src>", "<src> -> <targets>*", link),

        ]

    def get_override(self, query):
        src = query.split(":")
        if len(src) == 1: return None
        override = src[-1]
        if override in self.const.keys():
            return override
        else:
            return None

    def get_langs(self, query):
        if self.is_russian(query): return [("ru", "en"), ("ru", "de")]

        src = self.get_src_lang(query)
        targets = self.get_target_langs(query)

        if targets: return [(src,t) for t in targets]

        # re <src:de> or re <src:en>
        if (src == "de"):
            return [("de", "en")]
        if (src == "en"):
            return [("en", "de")]
        if (src == "ru"):
            return [("ru", "en"), ("ru", "de")]
        return [("en", "de"), ("de", "en"), ("ru", "en")]

    def get_target_langs(self, query):
        if not query.startswith(":"): return []
        actions = query.split(" ", 1)[0][1:]
        return set(map(lambda x: self.action_resolver[x], list(actions)))

    def get_src_lang(self, query):
        if self.is_german(query):
            return "de"
        elif override := self.get_override(query):
            return override

        layout = get_layout()
        return layout

    def query(self, param: str = '') -> list:
        query = self.clean_query(param)
        if len(query) < 3: return self.get_help_message()
        if len(query) < 5: time.sleep(1)

        out = []
        langs = self.get_langs(param)

        for (src, trg) in langs:
            if (src == trg): continue
            out.append(
                list(self.generate_results(query, src, trg, self.max_contexts // len(langs), self.max_translations)))

        result = []
        for mul in itertools.zip_longest(*out):
            for i in mul:
                if i: result.append(i)
        return result

    def is_german(self, query):
        return bool(self.german_alpha.search(query))

    def is_russian(self, query):
        return bool(self.russian_alpha.search(query))

    def generate_results(self, query, src, trg, max_contexts, max_translations):
        url = self.link(src, trg, query)
        if not url: return []
        yield self.query_entry(f"{src}->{trg} [c:{max_contexts}|t:{max_translations}]", query+"\n"+url, url)
        for (source, target) in self.get_reverse(query, src, trg, max_contexts, max_translations):
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
        if translations:
            yield " | ".join(translations), ""

        contexts = 0
        for (source, target) in api.get_examples():
            if contexts >= max_contexts: break
            if (src_lang == "ru"):
                yield target.text, source.text
            else:
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

    def clean_query(self, param):
        return re.sub(":\\w\\w$|^:\\w{,3}\s?", "", param.strip())


def get_layout():
    lid_hex = get_layout_hex()
    mapping = {
        "0x407": "de",
        "0x409": "en",
        "0x419": "ru"
    }
    if (lid_hex not in mapping): return "en"
    return mapping[lid_hex]


def get_layout_hex():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
    klid = user32.GetKeyboardLayout(thread_id)
    lid = klid & (2 ** 16 - 1)
    lid_hex = hex(lid)
    return lid_hex


if __name__ == "__main__":
    h = ReversoFlow()
    # print(h.clean_query(":ndr Auto"))
    # print(h.get_langs(":dre auto :ru"))
    # print(h.get_url_and_lang("what is it"))
    # pprint.pprint(h.query("Auto"))
