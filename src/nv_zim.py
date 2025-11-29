"""Zim Desktop Wiki connection plugin for novelibre.

Requires Python 3.7+
Copyright (c) 2025 Peter Triesberger
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
from pathlib import Path
from tkinter import ttk
import webbrowser

from nvlib.controller.plugin.plugin_base import PluginBase
from nvzim.nvzim_locale import _
from nvzim.wiki_manager import WikiManager
import tkinter as tk


class Plugin(PluginBase):
    """Plugin class for the Zim connector."""
    VERSION = '@release'
    API_VERSION = '5.44'
    DESCRIPTION = 'Zim Desktop Wiki connection'
    URL = 'https://github.com/peter88213/nv_zim'

    FEATURE = 'Zim Desktop Wiki'
    HELP_URL = f'{_("https://peter88213.github.io/nvhelp-en")}/nv_zim'

    def install(self, model, view, controller):
        """Install the plugin.
        
        Positional arguments:
            model -- reference to the novelibre main model instance.
            view -- reference to the novelibre main view instance.
            controller -- reference to the novelibre main controller instance.

        Extends the superclass method.
        """
        super().install(model, view, controller)
        self.wikiManager = WikiManager(
            model,
            view,
            controller,
            self.FEATURE
        )
        self._icon = self._get_icon('zim.png')

        #--- Configure the main menu.
        self._disableOnLock = []

        # Add an entry to the Help menu.
        label = _('Zim connection Online help')
        self._ui.helpMenu.add_command(
            label=label,
            image=self._icon,
            compound='left',
            command=self.open_help,
        )

        # Create a "Zim wiki" submenu.
        self.zimMenu = tk.Menu(tearoff=0)

        label = _('Open project wiki')
        self.zimMenu.add_command(
            label=label,
            command=self.open_project_wiki,
        )

        label = _('Create project wiki')
        self.zimMenu.add_separator()
        self.zimMenu.add_command(
            label=label,
            command=self.create_project_wiki,
        )
        self._disableOnLock.append(label)

        self.zimMenu.add_separator()

        # Create a "Remove wiki links" submenu.
        self.removeLinksMenu = tk.Menu(self.zimMenu, tearoff=0)

        label = _('Selected pages')
        self.removeLinksMenu.add_command(
            label=label,
            command=self.remove_selected_page_links,
        )

        label = _('All')
        self.removeLinksMenu.add_command(
            label=label,
            command=self.remove_all_wiki_links,
        )

        label = _('Remove wiki links')
        self.zimMenu.add_cascade(
            label=label,
            menu=self.removeLinksMenu,
        )
        self._disableOnLock.append(label)

        # Add the "Zim wiki" submenu to the Tools menu.
        label = _('Zim Desktop Wiki')
        self._ui.toolsMenu.add_cascade(
            label=label,
            image=self._icon,
            compound='left',
            menu=self.zimMenu,
        )
        self._ui.toolsMenu.disableOnClose.append(label)

        #--- Register the link opener.
        self._ctrl.linkProcessor.add_opener(self.open_link)

        self._add_buttons()
        self._ui.root.bind('<<RebuildPropertiesView>>', self._add_buttons)

        #--- Configure the toolbar.
        self._ui.toolbar.add_separator(),

        # Put a button on the toolbar.
        self._ui.toolbar.new_button(
            text=self.FEATURE,
            image=self._icon,
            command=self.open_project_wiki,
            disableOnLock=False,
        ).pack(side='left')

    def create_project_wiki(self, event=None):
        self.wikiManager.create_project_wiki()

    def lock(self):
        for label in self._disableOnLock:
            self.zimMenu.entryconfig(label, state='disabled')

    def on_close(self):
        self.wikiManager.on_close()

    def open_element_page(self, event=None):
        self.wikiManager.open_element_page()

    def open_help(self, event=None):
        webbrowser.open(self.HELP_URL)

    def open_link(self, filePath):
        return self.wikiManager.open_page_file(filePath)

    def open_page_file(self, event=None):
        self.wikiManager.open_page_file()

    def open_project_wiki(self, event=None):
        self.wikiManager.open_project_wiki()

    def remove_all_wiki_links(self, event=None):
        self.wikiManager.remove_all_links()

    def remove_page_link(self, event=None):
        self.wikiManager.remove_page_link_after_asking()

    def remove_selected_page_links(self, event=None):
        self.wikiManager.remove_selected_page_links()

    def unlock(self):
        for label in self._disableOnLock:
            self.zimMenu.entryconfig(label, state='normal')

    def _add_buttons(self, event=None):
        """Add "Open wiki page" Buttons."""
        enableHovertips = self._ctrl.get_preferences()['enable_hovertips']
        Hovertip = self._mdl.nvService.new_hovertip
        views = [
            self._ui.propertiesView.characterView,
            self._ui.propertiesView.locationView,
            self._ui.propertiesView.itemView,
            self._ui.propertiesView.projectView,
        ]
        for view in views:
            zimButton = ttk.Button(
                view.linksWindow.titleBar,
                text=_('Wiki page'),
                image=self._icon,
                command=self.open_element_page,
            )
            zimButton.pack(side='right')
            zimButton.bind("<Alt-Button-1>", self.remove_page_link)

            if enableHovertips:
                Hovertip(zimButton, zimButton['text'])

    def _get_icon(self, fileName):
        # Return the icon for the main view.
        if self._ctrl.get_preferences().get('large_icons', False):
            size = 24
        else:
            size = 16
        try:
            homeDir = str(Path.home()).replace('\\', '/')
            iconPath = f'{homeDir}/.novx/icons/{size}'
            icon = tk.PhotoImage(file=f'{iconPath}/{fileName}')
        except:
            icon = None
        return icon
