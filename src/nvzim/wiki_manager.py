"""Provide a service class for a Zim Desktop Wiki connection manager.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import glob
import os
import subprocess
from tkinter import filedialog

from mvclib.controller.sub_controller import SubController
from nvlib.gui.widgets.nv_simpledialog import SimpleDialog
from nvlib.novx_globals import CHARACTER_PREFIX
from nvlib.novx_globals import CH_ROOT
from nvlib.novx_globals import CR_ROOT
from nvlib.novx_globals import ITEM_PREFIX
from nvlib.novx_globals import IT_ROOT
from nvlib.novx_globals import LC_ROOT
from nvlib.novx_globals import LOCATION_PREFIX
from nvlib.novx_globals import norm_path
from nvzim.nvzim_globals import ZIM_NOTEBOOK_ABS_TAG
from nvzim.nvzim_globals import ZIM_NOTEBOOK_REL_TAG
from nvzim.nvzim_globals import ZIM_PAGE_ABS_TAG
from nvzim.nvzim_globals import ZIM_PAGE_REL_TAG
from nvzim.nvzim_locale import _
from nvzim.wiki_factory import WikiFactory
from nvzim.zim_notebook import ZimNotebook
from nvzim.zim_page import ZimPage


class WikiManager(SubController):

    def __init__(self, model, view, controller, windowTitle):
        super().initialize_controller(model, view, controller)
        self.prjWiki = None
        self.launchers = self._ctrl.get_launchers()
        self.zimApp = self.launchers.get(ZimNotebook.EXTENSION, '')
        self.windowTitle = windowTitle

    def check_home_dir(self):
        """Create the project wiki's home directory, if missing."""
        if self.prjWiki is None:
            return

        if not os.path.isdir(self.prjWiki.homeDir):
            os.makedirs(self.prjWiki.homeDir)

    def create_blank_prj_notebook(self, prjWikiDir):
        os.makedirs(prjWikiDir, exist_ok=True)
        self.prjWiki = ZimNotebook(
            self.zimApp,
            dirPath=prjWikiDir,
            wikiName=self._mdl.novel.title
            )
        self.set_notebook_links(self.prjWiki.filePath)
        self._ui.set_status(f'{_("Wiki created")}: "{norm_path(self.prjWiki.filePath)}"')

    def create_project_wiki(self):
        if self._mdl.prjFile is None:
            return

        prjWikiDir = self.get_project_wiki_dir()
        if os.path.isdir(prjWikiDir):
            text = f"{_('This will back up the existing wiki and create a new one containing all pages.')}"
            if not self._ui.ask_ok_cancel(text, title=self.windowTitle):
                return

            # Back up the existing wiki.
            backupWikiDir = f'{prjWikiDir}.bak'
            while os.path.isdir(backupWikiDir):
                backupWikiDir = f'{backupWikiDir}_'
            os.rename(prjWikiDir, backupWikiDir)

        self.create_blank_prj_notebook(prjWikiDir)
        sources = [
            self._mdl.novel.characters,
            self._mdl.novel.locations,
            self._mdl.novel.items,
        ]
        for source in sources:
            for elemId in source:
                self.create_wiki_page(source[elemId], elemId)
            bookPageName = self.create_wiki_page(self._mdl.novel, CH_ROOT)

        self.prjWiki.update_index()
        self._ui.set_status(f'{_("Wiki created")}: "{norm_path(self.prjWiki.filePath)}"')
        self.prjWiki.open(initialPage=f'{self.prjWiki.HOME}:{bookPageName}')

    def create_wiki_page(self, element, elemId):
        newPage = WikiFactory.new_wiki_page(element, elemId, None)
        newPageName = newPage.new_page_name()
        newPage.filePath = f"{self.prjWiki.homeDir}/{newPageName.replace(' ', '_')}{newPage.EXTENSION}"
        newPage.write()
        self.set_page_links(element, newPage.filePath)
        return newPageName

    def get_element(self, elemId):
        """Return the element specified by elemId, or the novel reference."""
        if elemId.startswith(CHARACTER_PREFIX):
            return self._mdl.novel.characters[elemId]

        if elemId.startswith(LOCATION_PREFIX):
            return self._mdl.novel.locations[elemId]

        if elemId.startswith(ITEM_PREFIX):
            return self._mdl.novel.items[elemId]

        if elemId == CH_ROOT:
            return self._mdl.novel

    def get_project_wiki_dir(self):
        prjDir, prjFile = os.path.split(self._mdl.prjFile.filePath)
        prjFileBase = os.path.splitext(prjFile)[0]
        return f'{prjDir}/{prjFileBase}_zim'

    def get_project_wiki_link(self):
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

    def get_wiki_page_link(self, element):
        """Return the element's wiki page path, if any."""
        wikiPagePath = element.fields.get(ZIM_PAGE_ABS_TAG, None)
        if wikiPagePath is None:
            wikiPagePath = element.fields.get(ZIM_PAGE_REL_TAG, None)
            if wikiPagePath is None:
                return

            wikiPagePath = self._ctrl.linkProcessor.expand_path(wikiPagePath)

        if not wikiPagePath.endswith(ZimPage.EXTENSION):
            return

        if os.path.isfile(wikiPagePath):
            return wikiPagePath

    def on_close(self):
        self.prjWiki = None

    def open_page_by_id(self, elemId):
        self._ui.restore_status()
        element = self.get_element(elemId)

        # First of all, try the element's wiki page link.
        filePath = self.get_wiki_page_link(element)
        pageCreated = False

        if filePath is None:

            # Try to find an existing project wiki page.
            wikiPage = WikiFactory.new_wiki_page(element, elemId, None)
            self.set_project_wiki()
            if self.prjWiki is not None:
                for pageName in wikiPage.page_names:
                    if not pageName:
                        continue

                    filePath = self.prjWiki.get_page_path_by_name(pageName)
                    if filePath is not None:
                        break

        if filePath is None:

            # Ask whether to browse or to create.
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
                # "Cancel" button clicked
                return

            if answer == 0:

                # Browse the file system for an existing wiki page.
                if self.prjWiki is not None:
                    initialDir = self.prjWiki.homeDir
                else:
                    initialDir = os.path.split(self._mdl.prjFile.filePath)[0]
                filePath = filedialog.askopenfilename(
                    filetypes=[(ZimPage.DESCRIPTION, ZimPage.EXTENSION)],
                    defaultextension=ZimPage.EXTENSION,
                    initialdir=initialDir
                    )
                if not filePath:
                    # file picker closed without selection
                    return

            else:
                # "Create" button clicked
                if self.prjWiki is None:
                    return

                # Create a new page in the project wiki.
                self.check_home_dir()
                fileName = wikiPage.new_page_name().replace(' ', '_')
                filePath = f'{self.prjWiki.homeDir}/{fileName}{wikiPage.EXTENSION}'
                wikiPage.filePath = filePath
                wikiPage.write()
                pageCreated = True

        self.set_page_links(element, filePath)
        if pageCreated:
            self._ui.set_status(_('Wiki page created'))
            # overwriting the "wiki link" message.
            self.prjWiki.update_index()
        self.open_page_file(filePath)

    def open_project_wiki(self):
        if self._mdl.prjFile is None:
            return

        self._ui.restore_status()
        self._ui.propertiesView.apply_changes()
        if not self.zim_is_installed():
            self._ui.set_status(f'!{_("Zim installation not found")}.')
            return

        self.set_project_wiki()
        self.check_home_dir()
        if self.prjWiki is not None:
            self.prjWiki.open()

    def open_page_file(self, filePath):
        """Return True if the file specified by filepath is opened with Zim."""
        if not self.zim_is_installed():
            self._ui.set_status(f'!{_("Zim installation not found")}.')
            return False

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
                subprocess.Popen([
                    self.zimApp,
                    zimNotebook[0],
                    ":".join(zimPages)
                    ])
                return True

        return False

    def open_element_page(self):
        self.open_page_by_id(self._ui.propertiesView.activeView.elementId)

    def remove_all_links(self):
        self._ui.restore_status()
        if self._mdl.prjFile is None:
            return

        if self._ctrl.check_lock():
            return

        if not self._ui.ask_ok_cancel(
            _('This will remove all Zim wiki links'),
            title=self.windowTitle,
            ):
            return

        removed = False
        if self.remove_notebook_links():
            self.prjWiki = None
            removed = True
        if self.remove_page_links(self._mdl.novel):
            removed = True
        for elemId in self._mdl.novel.characters:
            if self.remove_page_links(self._mdl.novel.characters[elemId]):
                removed = True
        for elemId in self._mdl.novel.locations:
            if self.remove_page_links(self._mdl.novel.locations[elemId]):
                removed = True
        for elemId in self._mdl.novel.items:
            if self.remove_page_links(self._mdl.novel.items[elemId]):
                removed = True
        self.set_removal_status(removed)

    def remove_notebook_links(self):
        removed = False
        fields = self._mdl.novel.fields
        try:
            del(fields[ZIM_NOTEBOOK_ABS_TAG])
            removed = True
        except KeyError:
            pass
        try:
            del(fields[ZIM_NOTEBOOK_REL_TAG])
            removed = True
        except KeyError:
            pass
        self._mdl.novel.fields = fields
        return removed

    def remove_page_links(self, element):
        removed = False
        fields = element.fields
        try:
            del (fields[ZIM_PAGE_ABS_TAG])
            removed = True
        except KeyError:
            pass
        try:
            del (fields[ZIM_PAGE_REL_TAG])
            removed = True
        except KeyError:
            pass
        element.fields = fields
        return removed

    def remove_selected_page_links(self):
        self._ui.restore_status()
        if self._mdl.prjFile is None:
            return

        if self._ctrl.check_lock():
            return

        for elemId in self._ui.selectedNodes:
            element = self.get_element(elemId)
            if elemId[:2] in (CHARACTER_PREFIX, LOCATION_PREFIX, ITEM_PREFIX) or elemId in (CH_ROOT, CR_ROOT, LC_ROOT, IT_ROOT):
                if self._ui.ask_ok_cancel(
                    _('This will remove the Zim wiki links of the selected elements'),
                    title=self.windowTitle,
                    ):
                    break
                else:
                    return

        removed = False
        for elemId in self._ui.selectedNodes:
            element = self.get_element(elemId)
            if element is not None:
                if self.remove_page_links(element):
                    removed = True
            else:
                if elemId == CR_ROOT:
                    for elemId in self._mdl.novel.characters:
                        if self.remove_page_links(self._mdl.novel.characters[elemId]):
                            removed = True
                    continue

                if elemId == LC_ROOT:
                    for elemId in self._mdl.novel.locations:
                        if self.remove_page_links(self._mdl.novel.locations[elemId]):
                            removed = True
                    continue

                if elemId == IT_ROOT:
                    for elemId in self._mdl.novel.items:
                        if self.remove_page_links(self._mdl.novel.items[elemId]):
                            removed = True
                    continue
        self.set_removal_status(removed)

    def set_removal_status(self, removed):
        if removed:
            self._ui.set_status(_('Wiki link(s) removed.'))
        else:
            self._ui.set_status(f"#{_('No Wiki link found.')}")

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

        prjWikiPath = self.get_project_wiki_link()
        if prjWikiPath is not None and os.path.isfile(prjWikiPath):

            # Open an existing notebook.
            self.prjWiki = ZimNotebook(self.zimApp, filePath=prjWikiPath)
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

            # Select an existing notebook.
            prjWikiPath = filedialog.askopenfilename(
                filetypes=[(ZimNotebook.DESCRIPTION, ZimNotebook.EXTENSION)],
                defaultextension=ZimNotebook.EXTENSION,
                initialdir=os.path.split(self._mdl.prjFile.filePath)[0]
                )
            if not prjWikiPath:
                return

            self.prjWiki = ZimNotebook(self.zimApp, filePath=prjWikiPath)
            self.set_notebook_links(self.prjWiki.filePath)
        else:
            self.create_blank_prj_notebook(self.get_project_wiki_dir())

    def zim_is_installed(self):
        """Return True if Zim seems to be installed."""
        if os.path.isfile(self.zimApp):
            self.launchers[ZimNotebook.EXTENSION] = self.zimApp
            return True

        self.zimInstallPaths = [
            'C:/Program Files/Zim Desktop Wiki/zim.exe',
            'C:/Program Files (x86)/Zim Desktop Wiki/zim.exe',
            ]
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
        if self.prjWiki is not None:
            self.prjWiki.zimApp = self.zimApp
        return True

