"""Provide global variables and functions.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from datetime import date

ZIM_NOTEBOOK_ABS_TAG = 'zim-notebook-abs'
ZIM_NOTEBOOK_REL_TAG = 'zim-notebook-rel'
ZIM_PAGE_ABS_TAG = 'zim-page-abs'
ZIM_PAGE_REL_TAG = 'zim-page-rel'


class StopParsing(Exception):
    pass


def locale_date(isoDate):
    try:
        newDate = date.fromisoformat(isoDate)
        return newDate.strftime('%x')

    except:
        return isoDate

