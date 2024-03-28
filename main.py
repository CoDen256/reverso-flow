# -*- coding: utf-8 -*-

import sys, os
import time
import os

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'lib'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))
sys.path.append(os.path.join(parent_folder_path, 'lib/lxml'))

from lxml import etree
import requests
from bs4 import BeautifulSoup
import reverso_api
from flowlauncher import FlowLauncher
import webbrowser
from collections import defaultdict

with open("modules", "a") as f:
    f.writelines("\nRUNNING\n")
    f.writelines(",".join(sys.modules.keys()))
    f.writelines(["\n"])
    f.writelines([parent_folder_path, "\n", __file__, "\n", str(sys.argv), "\n", os.__file__, "\n"])


# source = BeautifulSoup(requests.get("https://google.com").text, features="lxml")
# help('modules')

class ReversoFlow(FlowLauncher):
    path = "Images/app.png"

    const = {
        "en": "english",
        "de": "german",
        "ru": "russian"
    }

    lang_resolver = defaultdict(lambda: "english")

    def __init__(self):
        super().__init__()
        for (k, v) in self.const.items():
            self.lang_resolver[k] = v

    def query(self, param: str = '') -> list:
        return list(self.generate_results(param))

    def generate_results(self, query):
        if len(query) < 2:
            return []

        if len(query) < 5:
            time.sleep(1)

        src_lang = "de"
        trg_lang = "en"
        lang = 10
        for (source, target) in self.get_reverse_limit(query, src_lang, trg_lang, lang):
            yield self.query_entry(source, target, self.link(source, target, query))

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

    def get_reverse_limit(self, input, src_lang, trg_lang, limit):
        count = 0
        for item in self.get_reverse(input, src_lang, trg_lang):
            if count <= limit:
                yield item
            else:
                return
            count += 1

    def get_reverse(self, input, src_lang, trg_lang):
        for (source, target) in reverso_api.context.ReversoContextAPI(input, "", src_lang, trg_lang).get_examples():
            yield source.text, target.text

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
    # print(h.query("hallo"))
    # for i in h.get_reverse("Hallo", "de", "en"):
    #     print(i)
    # source = BeautifulSoup(requests.get("https://google.com").text, features="lxml")
