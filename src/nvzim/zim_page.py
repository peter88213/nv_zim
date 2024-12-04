"""Provide a class for a Zim Wiki page representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvzim.nvzim_globals import StopParsing
from nvzim.nvzim_globals import _


class ZimPage:

    DESCRIPTION = _('Zim page')
    EXTENSION = '.txt'

    PAGE_HEADER = '''Content-Type: text/x-zim-wiki
Wiki-Format: zim 0.4
'''
    REPLACEMENTS = {
        '//':'',
        '**': '',
    }

    def __init__(self, filePath, element):
        self.filePath = filePath
        self.element = element
        self.page_names = [self.element.title]

    def body(self, text):
        """Parser callback method for a note's body text line."""
        pass

    def fill_page(self, lines):
        """Add page content to the lines."""
        # To be overridden by subclasses.
        pass

    def from_wiki(self, text):
        """Return text with Zim-specific formatting removed."""
        for tag in self.REPLACEMENTS:
            text = text.replace(tag, self.REPLACEMENTS[tag])
        return text

    def get_h1(self, text):
        """Return text, formatted as first level heading."""
        return f'====== {text} ======'

    def get_h2(self, text):
        """Return text, formatted as second level heading."""
        return f'===== {text} ====='

    def get_h3(self, text):
        """Return text, formatted as third level heading."""
        return f'==== {text} ===='

    def h1(self, heading):
        """Parser callback method for a note's first level heading."""
        if self.element.title is None:
            self.element.title = heading

    def h2(self, heading):
        """Parser callback method for a note's second level heading."""
        pass

    def h3(self, heading):
        """Parser callback method for a note's third level heading."""
        pass

    def new_page_name(self):
        """Return the name for a new page."""
        # Override this if another name is required.
        for name in self.page_names:
            if name is not None:
                return name

    def parse_line(self, line):
        """An event-driven line parser."""
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
        """Modify the element with data read from the note file."""
        with open (self.filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
        for line in lines:
            try:
                self.parse_line(line)
            except StopParsing:
                return

    def write(self):
        """Write the note.
        
        Page content:
        - The Zim note header 
        - A first level heading with the note title as specified by the new_page_name() method.
        - Note text as specified by the fill_page() method.
        
        Overwrite existing note.
        """
        lines = [
            self.PAGE_HEADER,
            f'{self.get_h1(self.new_page_name())}\n\n',
        ]
        self.fill_page(lines)
        text = '\n'.join(lines)
        with open (self.filePath, 'w', encoding='utf-8') as f:
            f.write(text)
