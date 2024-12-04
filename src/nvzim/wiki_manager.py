"""Provide a service class for a Zim Desktop Wiki connection manager.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import glob
import os
import subprocess
from tkinter import filedialog

from mvclib.controller.service_base import ServiceBase
from nvlib.gui.widgets.nv_simpledialog import SimpleDialog
from nvlib.novx_globals import norm_path
from nvzim.nvzim_globals import ZIM_NOTEBOOK_ABS_TAG
from nvzim.nvzim_globals import ZIM_NOTEBOOK_REL_TAG
from nvzim.nvzim_globals import ZIM_PAGE_ABS_TAG
from nvzim.nvzim_globals import ZIM_PAGE_REL_TAG
from nvzim.nvzim_locale import _
from nvzim.zim_notebook import ZimNotebook
from nvzim.zim_page import ZimPage


class WikiManager(ServiceBase):

    def __init__(self, model, view, controller, windowTitle):
        super().__init__(model, view, controller)
        self.prjWiki = None
        self.launchers = self._ctrl.get_launchers()
        self.zimApp = self.launchers.get(ZimNotebook.EXTENSION, '')
        self.windowTitle = windowTitle

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
        self.set_page_links(element, newPage.filePath)
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

    def open_element_page(self, event=None):
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
                    title=self.windowTitle
                    ).go()
                if answer == 2:
                    return

                if answer == 0:
                    filePath = filedialog.askopenfilename(
                        filetypes=[(ZimPage.DESCRIPTION, ZimPage.EXTENSION)],
                        defaultextension=ZimPage.EXTENSION,
                        initialdir=os.path.split(self._mdl.prjFile.filePath)[0]
                        )
                elif not self._ctrl.check_lock():
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
            zimNotebook = glob.glob(norm_path(f'{zimPath}/*{ZimNotebook.EXTENSION}'))
            if zimNotebook:
                # the link path belongs to a Zim wiki
                subprocess.Popen([self.zimApp, zimNotebook[0], ":".join(zimPages)])
                return True

        return False

    def set_notebook_links(self, prjWikiPath):
        self._ui.restore_status()
        if self._ctrl.isLocked:
            return

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
        if self._ctrl.isLocked:
            return

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
            title=self.windowTitle
            ).go()
        if answer == 2:
            return

        if answer == 0:
            # Select existing notebook.
            prjWikiPath = filedialog.askopenfilename(
                filetypes=[(ZimNotebook.DESCRIPTION, ZimNotebook.EXTENSION)],
                defaultextension=ZimNotebook.EXTENSION,
                initialdir=os.path.split(self._mdl.prjFile.filePath)[0]
                )
            if not prjWikiPath:
                return

            self.prjWiki = ZimNotebook(filePath=prjWikiPath)
            self.set_notebook_links(self.prjWiki.filePath)
        elif not self._ctrl.check_lock():
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

