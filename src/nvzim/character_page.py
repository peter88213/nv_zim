"""Provide a class for a Zim Wiki page representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvzim.world_element_page import WorldElementPage


class CharacterPage(WorldElementPage):

    def __init__(self, filePath, element):
        super().__init__(filePath, element)
        self.page_names = [self.element.fullName, self.element.title, self.element.aka]

