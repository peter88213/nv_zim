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
from tkinter import filedialog

from nvlib.controller.plugin.plugin_base import PluginBase
from nvlib.model.file.doc_open import open_document
from nvzimlib.nvzim_globals import _
from nvzimlib.nvzim_globals import norm_path
from nvzimlib.nvzim_globals import open_help
from nvzimlib.zim_wiki_page import ZimWikiPage
from tkinter import ttk


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
        self._ui.toolsMenu.add_command(label=_('Open project wiki'), command=self.open_project_wiki)

        # Register the link opener.
        self._ctrl.linkProcessor.add_opener(self.open_zim_page)

        # Add "Open wiki page" Buttons.
        ttk.Button(
            self._ui.propertiesView.characterView.linksWindow,
            text=_('Wiki page'),
            command=self.open_element_page
            ).pack(anchor='w')

        self._fileTypes = [('Zim Wiki', '.zim')]
        self.prjWiki = None

    def create_wiki_page(self, element):
        """Create a wiki page and open it."""
        wikiPath = os.path.split(self.prjWiki)[0]
        filePath = f'{wikiPath}/Home/{element.title}{self.ZIM_NOTE_EXTENSION}'
        newPage = ZimWikiPage(filePath, element)
        newPage.write()
        newPage.create_link()
        return filePath

    def get_project_wiki(self):
        if self._mdl.prjFile is None:
            return

        prjWikiPath = self._mdl.novel.fields.get('zim-wiki', '')
        if os.path.isfile(prjWikiPath):
            return prjWikiPath

        prjWikiPath = filedialog.askopenfilename(
            filetypes=self._fileTypes,
            defaultextension=self._fileTypes[0][1],
            initialdir=os.path.split(self._mdl.prjFile.filePath)[0]
            )
        if prjWikiPath:
            fields = self._mdl.novel.fields
            fields['zim-wiki'] = prjWikiPath
            self._mdl.novel.fields = fields
            return prjWikiPath

    def get_zim_installation(self):
        self.zimInstallPaths = [
            'C:/Program Files/Zim Desktop Wiki/zim.exe',
            'C:/Program Files (x86)/Zim Desktop Wiki/zim.exe',
            ]
        for zimPath in self.zimInstallPaths:
            if os.path.isfile(zimPath):
                return zimPath

        if not self._ui.ask_ok_cancel(_('Zim installation not found. Select now?')):
            return

    def on_close(self):
        self.prjWiki = None

    def open_element_page(self, event=None):
        element = self._ui.propertiesView.activeView.element

        self.set_project_wiki()

        filePath = element.fields.get('wiki-page', None)
        if filePath is None:
            filePath = self.create_wiki_page(element)

        if not os.path.isfile(filePath):
            # Repair broken link or open file picker.
            filePath = self.create_wiki_page(element)

        if self.open_zim_page(filePath):
            return

    def set_project_wiki(self):
        if self.prjWiki is None:
            prjWikiPath = self.get_project_wiki()
            if prjWikiPath is None:
                raise ValueError

            self.prjWiki = prjWikiPath

    def open_project_wiki(self):
        open_document(self.prjWiki)

    def open_zim_page(self, filePath):
        root, extension = os.path.splitext(filePath)
        if extension != self.ZIM_NOTE_EXTENSION:
            return False

        launcher = self._ctrl.launchers.get('.zim', '')
        if not os.path.isfile(launcher):
            return False

        pagePath = root.split('/')
        zimPages = []
        # this is for the page path in Zim notation

        # Search backwards through the file branch.
        # If the page is a child of a Zim Wiki, start a subprocess to open it.
        while pagePath:
            zimPages.insert(0, pagePath.pop())
            zimPath = '/'.join(pagePath)
            zimNotebook = glob.glob(norm_path(f'{zimPath}/*.zim'))
            if zimNotebook:
                # the link path belongs to a Zim wiki
                subprocess.Popen([launcher, zimNotebook[0], ":".join(zimPages)])
                return True

        return False

