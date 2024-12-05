"""Provide a class for a Zim Wiki page representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvlib.novx_globals import CHARACTER_PREFIX
from nvlib.novx_globals import ITEM_PREFIX
from nvlib.novx_globals import LOCATION_PREFIX
from nvzim.character_page import CharacterPage
from nvzim.nvzim_globals import _
from nvzim.world_element_page import WorldElementPage
from nvzim.zim_page import ZimPage


class BookPage(ZimPage):

    def fill_page(self, lines):
        """Add page content to the lines.
        
        Overrides the superclass method.
        """
        if self.element.desc:
            lines.append(self.element.desc)
            lines.append('\n')

        if self.element.characters:
            lines.append(self.get_h2(_('Characters')))
            self._add_links(self.element.characters, lines)

        if self.element.locations:
            lines.append(self.get_h2(_('Locations')))
            self._add_links(self.element.locations, lines)

        if self.element.items:
            lines.append(self.get_h2(_('Items')))
            self._add_links(self.element.items, lines)

    def _add_links(self, elements, lines):
        for elemId in elements:
            elemPage = self._new_wiki_page(elements[elemId], elemId)
            pageName = elemPage.new_page_name()
            lines.append(f'[[{pageName}]]')
        lines.append('\n')

    def _new_wiki_page(self, element, elemId):
        """Return the reference to a new WikiPage subclass instance.
        
        WikiFactory cannot be used here due to circular import.
        """
        if elemId.startswith(CHARACTER_PREFIX):
            return CharacterPage(None, element)

        if elemId.startswith(LOCATION_PREFIX):
            return WorldElementPage(None, element)

        if elemId.startswith(ITEM_PREFIX):
            return WorldElementPage(None, element)
