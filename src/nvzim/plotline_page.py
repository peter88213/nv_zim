"""Provide a class for a Zim Wiki page representation.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""

from nvzim.zim_page import ZimPage


class PlotlinePage(ZimPage):

    def fill_page(self, lines):
        """Add page content to the lines.
        
        Overrides the superclass method.
        """
        if self.element.desc:
            lines.append(self.element.desc)
            lines.append('\n')
