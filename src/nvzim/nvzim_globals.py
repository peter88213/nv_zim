"""Provide global variables and functions.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import gettext
import locale
import os
import sys

# Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
try:
    CURRENT_LANGUAGE = locale.getlocale()[0][:2]
except:
    # Fallback for old Windows versions.
    CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('nv_zim', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message

ZIM_NOTEBOOK_ABS_TAG = 'zim-notebook-abs'
ZIM_NOTEBOOK_REL_TAG = 'zim-notebook-rel'
ZIM_PAGE_ABS_TAG = 'zim-page-abs'
ZIM_PAGE_REL_TAG = 'zim-page-rel'


class StopParsing(Exception):
    pass


def fix_file_name(fileName):
    """Return a string that can be used as a file name.
    
    Caution: Do not use this function on complete paths, 
    otherwise the dividers will be removed.
    """
    FORBIDDEN_CHARACTERS = ('\\', '/', ':', '*', '?', '"', '<', '>', '|')
    # set of characters that filenames cannot contain
    for c in FORBIDDEN_CHARACTERS:
        fileName = fileName.replace(c, '')
    return fileName.replace(' ', '_')

