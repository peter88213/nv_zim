"""Provide a class with mouse operation definitions for the Mac OS.

Copyright (c) Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvzim.platform.generic_mouse import GenericMouse


class MacMouse(GenericMouse):

    REMOVE_PAGE_LINK = '<Option-Button-1>'
