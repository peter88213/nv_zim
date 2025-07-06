"""Zim Desktop Wiki connection plugin for novelibre.

Requires Python 3.6+
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

from nvzim.nvzim_locale import _
from nvlib.controller.plugin.plugin_base import PluginBase
from nvzim.wiki_manager import WikiManager
import tkinter as tk


class Plugin(PluginBase):
    """Plugin class for the Zim connector."""
    VERSION = '@release'
    API_VERSION = '5.17'
    DESCRIPTION = 'Zim Desktop Wiki connection'
    URL = 'https://github.com/peter88213/nv_zim'

    FEATURE = 'Zim Desktop Wiki'
    HELP_URL = f'{_("https://peter88213.github.io/nvhelp-en")}/nv_zim'

    def disable_menu(self):
        """Disable UI widgets, e.g. when no project is open."""
        self._ui.toolsMenu.entryconfig(_('Zim Desktop Wiki'), state='disabled')
        self.zimButton.config(state='disabled')

    def enable_menu(self):
        """Enable UI widgets, e.g. when a project is opened."""
        self._ui.toolsMenu.entryconfig(_('Zim Desktop Wiki'), state='normal')
        self.zimButton.config(state='normal')

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

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(
            label=_('Zim connection Online help'),
            image=self._icon,
            compound='left',
            command=self.open_help,
        )

        # Create a "Zim wiki" submenu.
        self.zimMenu = tk.Menu(self._ui.toolsMenu, tearoff=0)
        self.zimMenu.add_command(
            label=_('Open project wiki'),
            command=self.open_project_wiki,
        )
        self.zimMenu.add_separator()
        self.zimMenu.add_command(
            label=_('Create project wiki'),
            command=self.create_project_wiki,
        )
        self.zimMenu.add_separator()

        # Create a "Remove wiki links" submenu.
        self.removeLinksMenu = tk.Menu(self.zimMenu, tearoff=0)
        self.removeLinksMenu.add_command(
            label=_('Selected pages'),
            command=self.remove_selected_page_links,
        )
        self.removeLinksMenu.add_command(
            label=_('All'),
            command=self.remove_all_wiki_links,
        )
        self.zimMenu.add_cascade(
            label=_('Remove wiki links'),
            menu=self.removeLinksMenu,
        )

        self._ui.toolsMenu.add_cascade(
            label=_('Zim Desktop Wiki'),
            image=self._icon,
            compound='left',
            menu=self.zimMenu,
        )

        # Register the link opener.
        self._ctrl.linkProcessor.add_opener(self.open_link)

        self._add_buttons()
        self._ui.root.bind('<<RebuildPropertiesView>>', self._add_buttons)

        #--- Configure the toolbar.
        self._configure_toolbar()

    def create_project_wiki(self, event=None):
        self.wikiManager.create_project_wiki()

    def lock(self):
        self.zimMenu.entryconfig(
            _('Create project wiki'),
            state='disabled',
        )
        self.zimMenu.entryconfig(
            _('Remove wiki links'),
            state='disabled',
        )

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

    def remove_selected_page_links(self, event=None):
        self.wikiManager.remove_selected_page_links()

    def unlock(self):
        self.zimMenu.entryconfig(_('Create project wiki'), state='normal')
        self.zimMenu.entryconfig(_('Remove wiki links'), state='normal')

    def _add_buttons(self, event=None):
        """Add "Open wiki page" Buttons."""
        views = [
            self._ui.propertiesView.characterView,
            self._ui.propertiesView.locationView,
            self._ui.propertiesView.itemView,
            self._ui.propertiesView.projectView,
        ]
        for view in views:
            ttk.Button(
                view.linksWindow.titleBar,
                text=_('Wiki page'),
                command=self.open_element_page,
            ).pack(side='right')

    def _configure_toolbar(self):

        # Put a Separator on the toolbar.
        tk.Frame(
            self._ui.toolbar.buttonBar,
            bg='light gray', width=1,
        ).pack(side='left', fill='y', padx=4)

        # Put a button on the toolbar.
        self.zimButton = ttk.Button(
            self._ui.toolbar.buttonBar,
            text=self.FEATURE,
            image=self._icon,
            command=self.open_project_wiki,
        )
        self.zimButton.pack(side='left')
        self.zimButton.image = self._icon

        # Initialize tooltip.
        if not self._ctrl.get_preferences()['enable_hovertips']:
            return

        try:
            from idlelib.tooltip import Hovertip
        except ModuleNotFoundError:
            return

        Hovertip(self.zimButton, self.zimButton['text'])

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
