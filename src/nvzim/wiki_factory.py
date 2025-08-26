"""Provide a factory class for Zim wiki pages.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvlib.novx_globals import CHARACTER_PREFIX
from nvlib.novx_globals import CH_ROOT
from nvlib.novx_globals import ITEM_PREFIX
from nvlib.novx_globals import LOCATION_PREFIX
from nvlib.novx_globals import PLOT_LINE_PREFIX
from nvzim.book_page import BookPage
from nvzim.character_page import CharacterPage
from nvzim.plotline_page import PlotlinePage
from nvzim.world_element_page import WorldElementPage


class WikiFactory:

    def __init__(self, model):
        self._mdl = model

    def new_wiki_page(self, element, elemId, filePath):
        """Return the reference to a new ZimPage subclass instance."""
        if elemId == CH_ROOT:
            return BookPage(filePath, element)

        if elemId.startswith(CHARACTER_PREFIX):
            return CharacterPage(
                filePath,
                element,
                field1Name=self._mdl.novel.crField1,
                field2Name=self._mdl.novel.crField2,
            )

        if elemId.startswith(LOCATION_PREFIX):
            return WorldElementPage(filePath, element)

        if elemId.startswith(ITEM_PREFIX):
            return WorldElementPage(filePath, element)

        if elemId.startswith(PLOT_LINE_PREFIX):
            return PlotlinePage(filePath, element)

