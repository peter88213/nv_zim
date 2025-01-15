"""Provide a class for a Zim Wiki page representation.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
from nvlib.novx_globals import CHARACTER_PREFIX
from nvlib.novx_globals import ITEM_PREFIX
from nvlib.novx_globals import LOCATION_PREFIX
from nvzim.character_page import CharacterPage
from nvzim.nvzim_locale import _
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
            self._add_links(self.element.characters, _('Characters'), lines)
            self._add_links(self.element.locations, _('Locations'), lines)
            self._add_links(self.element.items, _('Items'), lines)

    def _add_links(self, elements, heading, lines):
        """Add links to existent pages to the lines."""
        linkLines = []
        homeDir = os.path.dirname(self.filePath)
        for elemId in elements:
            elemPage = self._new_zim_page(elements[elemId], elemId)
            pageName = elemPage.new_page_name()
            filePath = f"{homeDir}/{pageName.replace(' ', '_')}{elemPage.EXTENSION}"
            if os.path.isfile(filePath):
                linkLines.append(f'[[{pageName}]]')
        if linkLines:
            lines.append(self.get_h2(heading))
            lines.extend(sorted(linkLines))
            lines.append('\n')

    def _new_zim_page(self, element, elemId):
        """Return the reference to a new ZimPage subclass instance."""

        # WikiFactory cannot be used here due to circular import.

        if elemId.startswith(CHARACTER_PREFIX):
            return CharacterPage(None, element)

        if elemId.startswith(LOCATION_PREFIX):
            return WorldElementPage(None, element)

        if elemId.startswith(ITEM_PREFIX):
            return WorldElementPage(None, element)
