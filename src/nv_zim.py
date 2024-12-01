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
from tkinter import ttk

from nvlib.controller.plugin.plugin_base import PluginBase
from nvlib.gui.widgets.nv_simpledialog import SimpleDialog
from nvzimlib.nvzim_globals import ZIM_NOTEBOOK_TAG
from nvzimlib.nvzim_globals import ZIM_NOTE_EXTENSION
from nvzimlib.nvzim_globals import ZIM_NOTE_TAG
from nvzimlib.nvzim_globals import _
from nvzimlib.nvzim_globals import norm_path
from nvzimlib.nvzim_globals import open_help
from nvzimlib.zim_note import ZimNote
from nvzimlib.zim_notebook import ZimNotebook


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

        Optional arguments:
            prefs -- deprecated. Please use controller.get_preferences() instead.
        
        Extends the superclass method.
        """
        super().install(model, view, controller)

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(label=_('nv_zim Online help'), command=open_help)
        self._ui.toolsMenu.add_command(label=_('Open project wiki'), command=self.open_project_wiki)

        # Register the link opener.
        self._ctrl.linkProcessor.add_opener(self.open_note_file)

        # Add "Open wiki page" Buttons.
        ttk.Button(
            self._ui.propertiesView.characterView.linksWindow.titleBar,
            text=_('Wiki page'),
            command=self.open_element_note
            ).pack(side='right')

        self._ZimNotebookType = [('Zim Wiki', '.zim')]
        self._ZimNoteType = [('Zim Note', '.txt')]
        self.prjWiki = None
        self.launchers = self._ctrl.get_launchers()
        self.zimApp = self.launchers.get('.zim', '')

    def create_wiki_page(self, element):
        """Create a wiki page and open it."""
        wikiPath = os.path.split(self.prjWiki.filePath)[0]
        filePath = f'{wikiPath}/Home/{element.title}{ZIM_NOTE_EXTENSION}'
        newPage = ZimNote(filePath, element)
        newPage.write()
        newPage.create_link()
        return filePath

    def get_project_wiki_path(self):
        """Return the project's wiki path, if any."""
        if self._mdl.prjFile is None:
            return

        prjWikiPath = self._mdl.novel.fields.get(ZIM_NOTEBOOK_TAG, '')
        if os.path.isfile(prjWikiPath):
            return prjWikiPath

    def on_close(self):
        self.prjWiki = None

    def open_element_note(self, event=None):
        self._ui.restore_status()
        element = self._ui.propertiesView.activeView.element
        self.set_project_wiki()
        filePath = element.fields.get(ZIM_NOTE_TAG, None)
        initialFilePath = filePath
        if filePath is None:
            filePath = self.create_wiki_page(element)
            self._ui.set_status(_('Wiki page created'))

        elif not os.path.isfile(filePath) or not filePath.endswith(ZIM_NOTE_EXTENSION):
            if self.prjWiki is not None:
                filePath = self.prjWiki.get_note(element.title)
            else:
                filePath = None
            if filePath is None:
                answer = SimpleDialog(
                    None,
                    text=_('Open an existing page, or create a new one?'),
                    buttons=[_('Browse'), _('Create'), _('Cancel')],
                    default=0,
                    cancel=2,
                    title=_('Wiki page not found')
                    ).go()
                if answer == 2:
                    return

                if answer == 0:
                    filePath = filedialog.askopenfilename(
                        filetypes=self._ZimNoteType,
                        defaultextension=self._ZimNoteType[0][1],
                        initialdir=os.path.split(self._mdl.prjFile.filePath)[0]
                        )
                else:
                    filePath = self.create_wiki_page(element)
                    self._ui.set_status(_('Wiki page created'))
                    initialFilePath = filePath
            if filePath is None:
                return

            # Update link.
            fields = element.fields
            fields[ZIM_NOTE_TAG] = filePath
            element.fields = fields
            if initialFilePath and filePath and filePath != initialFilePath:
                self._ui.set_status(f"#{_('Broken link fixed')}")
        self.open_note_file(filePath)

    def open_project_wiki(self):
        if not self.zim_is_installed():
            self._ui.set_status(f'!{_("Zim installation not found")}.')
            return

        self.set_project_wiki()
        if self.prjWiki is not None:
            subprocess.Popen([self.zimApp, self.prjWiki.filePath, 'Home'])

    def open_note_file(self, filePath):
        if not self.zim_is_installed():
            self._ui.set_status(f'!{_("Zim installation not found")}.')
            return

        root, extension = os.path.splitext(filePath)
        if extension != ZIM_NOTE_EXTENSION:
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
                subprocess.Popen([self.zimApp, zimNotebook[0], ":".join(zimPages)])
                return True

        return False

    def set_project_wiki(self):
        if self.prjWiki is not None:
            return

        prjWikiPath = self.get_project_wiki_path()
        if prjWikiPath is not None:
            self.prjWiki = ZimNotebook(self._mdl.novel, filePath=prjWikiPath)
            return

        answer = SimpleDialog(
            None,
            text=_('Open an existing wiki, or create a new one?'),
            buttons=[_('Browse'), _('Create'), _('Cancel')],
            default=0,
            cancel=2,
            title=_('Project wiki not found')
            ).go()
        if answer == 2:
            return

        if answer == 0:
            prjWikiPath = filedialog.askopenfilename(
                filetypes=self._ZimNotebookType,
                defaultextension=self._ZimNotebookType[0][1],
                initialdir=os.path.split(self._mdl.prjFile.filePath)[0]
                )
            if prjWikiPath is None:
                return

            fields = self._mdl.novel.fields
            fields[ZIM_NOTEBOOK_TAG] = prjWikiPath
            self._mdl.novel.fields = fields
            self.prjWiki = ZimNotebook(self._mdl.novel, filePath=prjWikiPath)
        else:
            prjDir, prjFile = os.path.split(self._mdl.prjFile.filePath)
            prjFileBase = os.path.splitext(prjFile)[0]
            prjWikiDir = f'{prjDir}/{prjFileBase}_zim'
            os.makedirs(prjWikiDir, exist_ok=True)
            self.prjWiki = ZimNotebook(self._mdl.novel, dirPath=prjWikiDir)
            self._ui.set_status(f'{_("Wiki created")}: "{norm_path(self.prjWiki.filePath)}"')

    def zim_is_installed(self):
        """Return True if Zim seems to be installed."""
        if os.path.isfile(self.zimApp):
            self.launchers['.zim'] = self.zimApp
            return True

        self.zimInstallPaths = [
            'C:/Program Files/Zim Desktop Wiki/zim.exe',
            'C:/Program Files (x86)/Zim Desktop Wiki/zim.exe',
            ]
        self.zimInstallPaths.clear()
        for zimPath in self.zimInstallPaths:
            if os.path.isfile(zimPath):
                self.zimApp = zimPath
                self.launchers['.zim'] = self.zimApp
                return True

        if not self._ui.ask_yes_no(_('Zim installation not found. Select now?')):
            return

        zimPath = filedialog.askopenfilename()
        if not zimPath:
            return

        self.zimApp = zimPath
        self.launchers['.zim'] = self.zimApp
        return True

