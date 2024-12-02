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
from nvzimlib.nvzim_globals import ZIM_NOTEBOOK_ABS_TAG
from nvzimlib.nvzim_globals import ZIM_NOTEBOOK_REL_TAG
from nvzimlib.nvzim_globals import ZIM_PAGE_ABS_TAG
from nvzimlib.nvzim_globals import ZIM_PAGE_REL_TAG
from nvzimlib.nvzim_globals import _
from nvzimlib.nvzim_globals import norm_path
from nvzimlib.nvzim_globals import open_help
from nvzimlib.zim_notebook import ZimNotebook
from nvzimlib.zim_page import ZimPage


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
        self._ctrl.linkProcessor.add_opener(self.open_page_file)

        # Add "Open wiki page" Buttons.
        ttk.Button(
            self._ui.propertiesView.characterView.linksWindow.titleBar,
            text=_('Wiki page'),
            command=self.open_element_note
            ).pack(side='right')

        self._ZimNotebookType = [(ZimNotebook.DESCRIPTION, ZimNotebook.EXTENSION)]
        self._ZimNoteType = [('Zim Note', '.txt')]
        self.prjWiki = None
        self.launchers = self._ctrl.get_launchers()
        self.zimApp = self.launchers.get(ZimNotebook.EXTENSION, '')

    def check_home_dir(self):
        """Chreate the project wiki's home directory, if missing."""
        if self.prjWiki is None:
            return

        if not os.path.isdir(self.prjWiki.homeDir):
            os.makedirs(self.prjWiki.homeDir)

    def create_wiki_page(self, element):
        """Create a wiki page and open it."""
        self.check_home_dir()
        wikiPath = os.path.split(self.prjWiki.filePath)[0]
        filePath = f'{wikiPath}/Home/{element.title}{ZimPage.EXTENSION}'
        newPage = ZimPage(filePath, element)
        newPage.write()

        # Create link.
        fields = element.fields
        fields[ZIM_PAGE_ABS_TAG] = newPage.filePath
        fields[ZIM_PAGE_REL_TAG] = self._ctrl.linkProcessor.shorten_path(newPage.filePath)
        element.fields = fields
        return filePath

    def get_project_wiki_path(self):
        """Return the project's wiki path, if any."""
        if self._mdl.prjFile is None:
            return

        prjWikiPath = self._mdl.novel.fields.get(ZIM_NOTEBOOK_ABS_TAG, None)
        if prjWikiPath is None:
            prjWikiPath = self._mdl.novel.fields.get(ZIM_NOTEBOOK_REL_TAG, None)
            if prjWikiPath is None:
                return

            prjWikiPath = self._ctrl.linkProcessor.expand_path(prjWikiPath)

        if not prjWikiPath.endswith(ZimNotebook.EXTENSION):
            return

        if os.path.isfile(prjWikiPath):
            return prjWikiPath

    def on_close(self):
        self.prjWiki = None

    def open_element_note(self, event=None):
        self._ui.restore_status()
        element = self._ui.propertiesView.activeView.element
        self.set_project_wiki()
        filePath = element.fields.get(ZIM_PAGE_ABS_TAG, None)
        if filePath is None or os.path.isfile(filePath) or not filePath.endswith(ZimPage.EXTENSION):
            pageCreated = False
            if self.prjWiki is not None:
                filePath = self.prjWiki.get_note(element.title)
            else:
                filePath = None
            if filePath is None:
                text = f"{_('Wiki page not found')}\n\n{_('Open an existing page, or create a new one?')}"
                answer = SimpleDialog(
                    None,
                    text=text,
                    buttons=[_('Browse'), _('Create'), _('Cancel')],
                    default=0,
                    cancel=2,
                    title=self.FEATURE
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
                    pageCreated = True
            if not filePath:
                return

            self.set_page_links(element, filePath)
            if pageCreated:
                self._ui.set_status(_('Wiki page created'))
                # overwriting the "wiki link" message
        self.open_page_file(filePath)

    def open_project_wiki(self):
        self._ui.restore_status()
        self._ui.propertiesView.apply_changes()
        if not self.zim_is_installed():
            self._ui.set_status(f'!{_("Zim installation not found")}.')
            return

        self.set_project_wiki()
        self.check_home_dir()
        if self.prjWiki is not None:
            subprocess.Popen([self.zimApp, self.prjWiki.filePath, 'Home'])

    def open_page_file(self, filePath):
        if not self.zim_is_installed():
            self._ui.set_status(f'!{_("Zim installation not found")}.')
            return

        root, extension = os.path.splitext(filePath)
        if extension != ZimPage.EXTENSION:
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

    def set_notebook_links(self, prjWikiPath):
        self._ui.restore_status()
        fields = self._mdl.novel.fields
        initialAbsPath = fields.get(ZIM_NOTEBOOK_ABS_TAG, None)
        initialRelPath = fields.get(ZIM_NOTEBOOK_REL_TAG, None)
        fields[ZIM_NOTEBOOK_ABS_TAG] = prjWikiPath
        relPath = self._ctrl.linkProcessor.shorten_path(prjWikiPath)
        fields[ZIM_NOTEBOOK_REL_TAG] = relPath
        self._mdl.novel.fields = fields
        message = None
        if initialAbsPath is None or initialRelPath is None:
            message = f"#{_('Wiki link created')}"
        elif initialAbsPath != prjWikiPath  or initialRelPath != relPath:
            message = f"#{_('Broken link fixed')}"
        if message is not None:
            self._ui.set_status(message)

    def set_page_links(self, element, wikiPagePath):
        self._ui.restore_status()
        fields = element.fields
        initialAbsPath = fields.get(ZIM_PAGE_ABS_TAG, None)
        initialRelPath = fields.get(ZIM_PAGE_REL_TAG, None)
        fields[ZIM_PAGE_ABS_TAG] = wikiPagePath
        relPath = self._ctrl.linkProcessor.shorten_path(wikiPagePath)
        fields[ZIM_PAGE_REL_TAG] = relPath
        element.fields = fields
        message = None
        if initialAbsPath is None or initialRelPath is None:
            message = f"#{_('Wiki link created')}"
        elif initialAbsPath != wikiPagePath  or initialRelPath != relPath:
            message = f"#{_('Broken link fixed')}"
        if message is not None:
            self._ui.set_status(message)

    def set_project_wiki(self):
        if self.prjWiki is not None:
            return

        prjWikiPath = self.get_project_wiki_path()
        if prjWikiPath is not None and os.path.isfile(prjWikiPath):

            # Open existing notebook.
            self.prjWiki = ZimNotebook(filePath=prjWikiPath)
            self.set_notebook_links(self.prjWiki.filePath)
            return

        text = f"{_('Project wiki not found')}\n\n{_('Open an existing wiki, or create a new one?')}"
        answer = SimpleDialog(
            None,
            text=text,
            buttons=[_('Browse'), _('Create'), _('Cancel')],
            default=0,
            cancel=2,
            title=self.FEATURE
            ).go()
        if answer == 2:
            return

        if answer == 0:
            # Select existing notebook.
            prjWikiPath = filedialog.askopenfilename(
                filetypes=self._ZimNotebookType,
                defaultextension=self._ZimNotebookType[0][1],
                initialdir=os.path.split(self._mdl.prjFile.filePath)[0]
                )
            if not prjWikiPath:
                return

            self.prjWiki = ZimNotebook(filePath=prjWikiPath)
            self.set_notebook_links(self.prjWiki.filePath)
        else:
            # Create new notebook.
            prjDir, prjFile = os.path.split(self._mdl.prjFile.filePath)
            prjFileBase = os.path.splitext(prjFile)[0]
            prjWikiDir = f'{prjDir}/{prjFileBase}_zim'
            os.makedirs(prjWikiDir, exist_ok=True)
            self.prjWiki = ZimNotebook(dirPath=prjWikiDir, wikiName=self._mdl.novel.title)
            self.set_notebook_links(self.prjWiki.filePath)
            self._ui.set_status(f'{_("Wiki created")}: "{norm_path(self.prjWiki.filePath)}"')

    def zim_is_installed(self):
        """Return True if Zim seems to be installed."""
        if os.path.isfile(self.zimApp):
            self.launchers[ZimNotebook.EXTENSION] = self.zimApp
            return True

        self.zimInstallPaths = [
            'C:/Program Files/Zim Desktop Wiki/zim.exe',
            'C:/Program Files (x86)/Zim Desktop Wiki/zim.exe',
            ]
        self.zimInstallPaths.clear()
        for zimPath in self.zimInstallPaths:
            if os.path.isfile(zimPath):
                self.zimApp = zimPath
                self.launchers[ZimNotebook.EXTENSION] = self.zimApp
                return True

        if not self._ui.ask_yes_no(_('Zim installation not found. Select now?')):
            return

        zimPath = filedialog.askopenfilename()
        if not zimPath:
            return

        self.zimApp = zimPath
        self.launchers[ZimNotebook.EXTENSION] = self.zimApp
        return True

