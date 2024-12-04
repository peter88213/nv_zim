"""Zim Desktop Wiki connector plugin for novelibre.

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
from tkinter import ttk

from nvlib.controller.plugin.plugin_base import PluginBase
from nvzim.nvzim_help import NvzimHelp
from nvzim.nvzim_locale import _
from nvzim.zim_connector import ZimConnector


class Plugin(PluginBase):
    """Template plugin class."""
    VERSION = '@release'
    API_VERSION = '5.0'
    DESCRIPTION = 'Zim Desktop Wiki connector'
    URL = 'https://github.com/peter88213/nv_zim'

    FEATURE = 'Zim Desktop Wiki'

    def install(self, model, view, controller):
        """Install the plugin.
        
        Positional arguments:
            model -- reference to the main model instance of the application.
            view -- reference to the main view instance of the application.
            controller -- reference to the main controller instance of the application.

        Extends the superclass method.
        """
        super().install(model, view, controller)
        self.zimConnector = ZimConnector(model, view, controller)

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(label=_('nv_zim Online help'), command=NvzimHelp.open_help_page)
        self._ui.toolsMenu.add_command(label=_('Open project wiki'), command=self.zimConnector.open_project_wiki)

        # Register the link opener.
        self._ctrl.linkProcessor.add_opener(self.zimConnector.open_page_file)

        # Add "Open wiki page" Buttons.
        ttk.Button(
            self._ui.propertiesView.characterView.linksWindow.titleBar,
            text=_('Wiki page'),
            command=self.zimConnector.open_element_note
            ).pack(side='right')

