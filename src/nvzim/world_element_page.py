"""Provide a class for a Zim Wiki page representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvzim.zim_page import ZimPage


class WorldElementPage(ZimPage):

    def __init__(self, filePath, element):
        super().__init__(filePath, element)
        self.page_names = [self.element.title]

    def fill_page(self, lines):
        """Add page content to the lines.
        
        Overrides the superclass method.
        """
        if self.element.aka:
            lines.append(self.element.aka)
            lines.append('\n')

        if self.element.tags:
            for tag in self.element.tags:
                lines.append(f"@{tag.replace(' ', '_')}")
            lines.append('\n')

        if self.element.desc:
            lines.append(self.element.desc)
            lines.append('\n')
