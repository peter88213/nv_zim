"""Provide a class for a Zim Wiki page representation.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvzim.nvzim_globals import locale_date
from nvzim.nvzim_locale import _
from nvzim.world_element_page import WorldElementPage


class CharacterPage(WorldElementPage):

    def __init__(
        self,
        filePath,
        element,
        field1Name=f'{_("Field")} 1',
        field2Name=f'{_("Field")} 2',
    ):
        super().__init__(filePath, element)
        self.field1Name = field1Name
        self.field2Name = field2Name
        self.page_names = [
            self.element.fullName,
            self.element.title,
            self.element.aka,
        ]

    def fill_page(self, lines):
        """Add page content to the lines.
        
        Extends the superclass method.
        """
        super().fill_page(lines)

        if self.element.bio:
            lines.append(self.get_h2(self.field1Name))
            self._write_life_dates(lines)
            lines.append(self.element.bio)
            lines.append('\n')
        else:
            self._write_life_dates(lines)
            lines.append('\n')

        if self.element.goals:
            lines.append(self.get_h2(self.field2Name))
            lines.append(self.element.goals)
            lines.append('\n')

    def _write_life_dates(self, lines):
        showDate = False
        if self.element.birthDate:
            startDate = locale_date(self.element.birthDate)
            showDate = True
        else:
            startDate = '?'
        if self.element.deathDate:
            endDate = locale_date(self.element.deathDate)
            showDate = True
        else:
            endDate = '?'
        if showDate:
            lines.append(f'{startDate}—{endDate}\n')

