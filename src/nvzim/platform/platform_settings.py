"""Provide platform specific key definitions for the nv_zim plugin.

Copyright (c) Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import platform

from nvzim.platform.generic_mouse import GenericMouse
from nvzim.platform.mac_mouse import MacMouse

if platform.system() == 'Windows':
    PLATFORM = 'win'
    MOUSE = GenericMouse()
elif platform.system() in ('Linux', 'FreeBSD'):
    PLATFORM = 'ix'
    MOUSE = GenericMouse()
elif platform.system() == 'Darwin':
    PLATFORM = 'mac'
    MOUSE = MacMouse()
else:
    PLATFORM = ''
    MOUSE = GenericMouse()

