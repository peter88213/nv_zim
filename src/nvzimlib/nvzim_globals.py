"""Provide global variables and functions.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import gettext
import locale
import os
import sys
import webbrowser

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

HELP_URL = 'https://github.com/peter88213/nv_zim/tree/main/docs/nv_zim'

ZIM_NOTEBOOK_ABS_TAG = 'zim-notebook-abs'
ZIM_NOTEBOOK_REL_TAG = 'zim-notebook-rel'
ZIM_PAGE_ABS_TAG = 'zim-page-abs'
ZIM_PAGE_REL_TAG = 'zim-page-rel'


class StopParsing(Exception):
    pass


def norm_path(path):
    if path is None:
        path = ''
    return os.path.normpath(path)


def open_help(event=None):
    """Show the online help page specified by HELP_URL."""
    webbrowser.open(HELP_URL)
