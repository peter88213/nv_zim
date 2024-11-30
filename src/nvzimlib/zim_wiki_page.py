"""Provide a class for a Zim Wiki page representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvzimlib.nvzim_globals import StopParsing


class ZimWikiPage:

    ZIM_PAGE_HEADER = '''Content-Type: text/x-zim-wiki
Wiki-Format: zim 0.4
'''
    REPLACEMENTS = {
        '//':'',
        '**': '',
    }

    def __init__(self, filePath, element):
        self.filePath = filePath
        self.element = element

    def body(self, text):
        pass

    def create_link(self):
        fields = self.element.fields
        fields['wiki-page'] = self.filePath
        self.element.fields = fields

    def fill_page(self, lines):
        pass

    def from_wiki(self, text):
        for tag in self.REPLACEMENTS:
            text = text.replace(tag, self.REPLACEMENTS[tag])
        return text

    def h1(self, heading):
        if self.element.title is None:
            self.element.title = heading

    def h2(self, heading):
        pass

    def h3(self, heading):
        pass

    def parse_line(self, line):
        if line.startswith('====== '):
            heading = line.strip('= ')
            self.h1(heading)

        if line.startswith('===== '):
            heading = line.strip('= ')
            self.h2(heading)

        if line.startswith('==== '):
            heading = line.strip('= ')
            self.h3(heading)

        elif not line.startswith('='):
            self.body(line)

    def read(self):
        with open (self.filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
        for line in lines:
            try:
                self.parse_line(line)
            except StopParsing:
                return

    def write(self):
        lines = [
            self.ZIM_PAGE_HEADER,
            f'====== {self.element.title} ======\n\n',
        ]
        self.fill_page(lines)
        text = '\n'.join(lines)
        with open (self.filePath, 'w', encoding='utf-8') as f:
            f.write(text)
