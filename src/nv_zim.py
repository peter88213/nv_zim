"""Plugin template for novelibre.

Requires Python 3.6+
Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import glob
import os
import subprocess

from nvlib.controller.plugin.plugin_base import PluginBase
from nvzimlib.nvzim_globals import _
from nvzimlib.nvzim_globals import open_help
from nvzimlib.nvzim_globals import norm_path


class Plugin(PluginBase):
    """Template plugin class."""
    VERSION = '@release'
    API_VERSION = '5.0'
    DESCRIPTION = 'Zim Desktop Wiki connector'
    URL = 'https://github.com/peter88213/nv_zim'

    FEATURE = 'Zim Desktop Wiki'
    ZIM_NOTE_EXTENSION = '.txt'

    def install(self, model, view, controller):
        """Install the plugin.
        
        Positional arguments:
            model -- reference to the main model instance of the application.
            view -- reference to the main view instance of the application.
            controller -- reference to the main controller instance of the application.

        Optional arguments:
            prefs -- deprecated. Please use controller.get_preferences() instead.
        
        Extends the superclass method.
        """
        super().install(model, view, controller)

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(label=_('nv_zim Online help'), command=open_help)

        # Register the link opener.
        self._ctrl.linkProcessor.add_special_opener(self.open_zim_page)

    def open_zim_page(self, filePath, extension):
        if extension != self.ZIM_NOTE_EXTENSION:
            return False

        launcher = self._ctrl.launchers.get('.zim', '')
        if not os.path.isfile(launcher):
            return False

        pagePath = filePath.split('/')
        zimPages = []
        # this is for the page path in Zim notation

        # Search backwards through the file branch.
        while pagePath:
            zimPages.insert(0, pagePath.pop())
            zimPath = '/'.join(pagePath)
            zimNotebook = glob.glob(norm_path(f'{zimPath}/*.zim'))
            if zimNotebook:
                # the link path belongs to a Zim wiki
                subprocess.Popen([launcher, zimNotebook[0], ":".join(zimPages)])
                return True

        return False

