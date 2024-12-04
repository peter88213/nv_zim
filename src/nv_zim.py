"""Zim Desktop Wiki connection plugin for novelibre.

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
import webbrowser

from nvlib.controller.plugin.plugin_base import PluginBase
from nvzim.nvzim_locale import _
from nvzim.wiki_manager import WikiManager


class Plugin(PluginBase):
    """Template plugin class."""
    VERSION = '@release'
    API_VERSION = '5.0'
    DESCRIPTION = 'Zim Desktop Wiki connection'
    URL = 'https://github.com/peter88213/nv_zim'

    FEATURE = 'Zim Desktop Wiki'
    HELP_URL = 'https://github.com/peter88213/nv_zim/tree/main/docs/nv_zim'

    def disable_menu(self):
        """Disable UI widgets, e.g. when no project is open."""
        self._ui.toolsMenu.entryconfig(_('Open project wiki'), state='disabled')

    def enable_menu(self):
        """Enable UI widgets, e.g. when a project is opened."""
        self._ui.toolsMenu.entryconfig(_('Open project wiki'), state='normal')

    def install(self, model, view, controller):
        """Install the plugin.
        
        Positional arguments:
            model -- reference to the main model instance of the application.
            view -- reference to the main view instance of the application.
            controller -- reference to the main controller instance of the application.

        Extends the superclass method.
        """
        super().install(model, view, controller)
        self.wikiManager = WikiManager(model, view, controller, self.FEATURE)

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(label=_('Zim connection Online help'), command=self.open_help_page)
        self._ui.toolsMenu.add_command(label=_('Open project wiki'), command=self.open_project_wiki)

        # Register the link opener.
        self._ctrl.linkProcessor.add_opener(self.open_page_file)

        # Add "Open wiki page" Buttons.
        self.wikiPageButton = ttk.Button(
            self._ui.propertiesView.characterView.linksWindow.titleBar,
            text=_('Wiki page'),
            command=self.open_element_page
            )
        self.wikiPageButton.pack(side='right')

    def open_element_page(self):
        self.wikiManager.open_element_page()

    def open_help_page(self):
        webbrowser.open(self.HELP_URL)

    def open_page_file(self):
        self.wikiManager.open_page_file()

    def open_project_wiki(self):
        self.wikiManager.open_project_wiki()
