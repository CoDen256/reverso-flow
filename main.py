# -*- coding: utf-8 -*-

import sys,os
parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'lib'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))


import reverso_api
from flowlauncher import FlowLauncher
import webbrowser


class HelloWorld(FlowLauncher):

    path = "Images/app.png"

    def query(self, query):
        if (len(query) < 5): return []

        return list(map(lambda src_trg: self.query_entry(src_trg[0], src_trg[1]), self.reverse_limit(query, "de", "en", 5)))
    
    def query_entry(self, title, subtitle): 
        return {
                "Title": title,
                "SubTitle": subtitle,
                "IcoPath": HelloWorld.path,
                "JsonRPCAction": {
                    "method": "open_url",
                    "parameters": ["https://github.com/Flow-Launcher/Flow.Launcher"]
                }
            }

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

    def reverse_limit(self, input, src_lang, trg_lang, limit):
        out = self.reverse(input, src_lang, trg_lang)
        return list([next(out) for _ in range(limit) ])

    def reverse(self, input, src_lang, trg_lang):
        for (source, target) in reverso_api.context.ReversoContextAPI(input, "", src_lang, trg_lang).get_examples():
            yield (highlight_example(source.text, source.highlighted), highlight_example(target.text, source.highlighted))



def highlight_example(text, highlighted):
    """'Highlights' ALL the highlighted parts of the word usage example with * characters.

    Args:
        text: The text of the example
        highlighted: Indexes of the highlighted parts' indexes

    Returns:
        The highlighted word usage example

    """

    def insert_char(string, index, char):
        """Inserts the given character into a string.

        Example:
            string = "abc"
            index = 1
            char = "+"
            Returns: "a+bc"

        Args:
            string: Given string
            index: Index where to insert
            char: Which char to insert

        Return:
            String string with character char inserted at index index.
        """

        return string[:index] + char + string[index:]

    def highlight_once(string, start, end, shift):
        """'Highlights' ONE highlighted part of the word usage example with two * characters.

        Example:
            string = "This is a sample string"
            start = 0
            end = 4
            shift = 0
            Returns: "*This* is a sample string"

        Args:
            string: The string to be highlighted
            start: The start index of the highlighted part
            end: The end index of the highlighted part
            shift: How many highlighting chars were already inserted (to get right indexes)

        Returns:
            The highlighted string.

        """

        s = insert_char(string, start + shift, "*")
        s = insert_char(s, end + shift + 1, "*")
        return s

    shift = 0
    for start, end in highlighted:
        text = highlight_once(text, start, end, shift)
        shift += 2
    return text

if __name__ == "__main__":
    h = HelloWorld()