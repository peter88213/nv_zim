"""Provide a class for a Zim Wiki representation.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_zim
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from configparser import ConfigParser
import glob
import os
import subprocess

from nvzim.nvzim_locale import _
from nvzim.zim_page import ZimPage


class ZimNotebook:

    DESCRIPTION = _('Zim notebook')
    EXTENSION = '.zim'

    NOTEBOOK = 'Notebook'
    HOME = 'Home'

    def __init__(self, zimApp, dirPath='', filePath='', wikiName=None):
        self.zimApp = zimApp

        # Specify either directory or file path.
        if wikiName is None:
            wikiName = self.NOTEBOOK
        self.settings = dict(
            version='0.4',
            name=wikiName,
            interwiki='',
            home=self.HOME,
            icon='',
            document_root='',
            shared='True',
            endofline='dos',
            disable_trash='False',
            profile='',
        )
        if os.path.isfile(filePath):
            self.filePath = filePath
            self.dirPath, __ = os.path.split(filePath)
            self.filePath = filePath
            self.read_settings()
            self.homeDir = f"{self.dirPath}/{self.settings['home']}"
        elif os.path.isdir(dirPath):
            self.dirPath = dirPath
            self.filePath = f'{dirPath}/{self.NOTEBOOK}.zim'
            self.homeDir = f'{self.dirPath}/{self.HOME}'
            self.write()
            self.update_index()
        else:
            raise AttributeError

    def open(self, initialPage=None):
        if not os.path.isfile(self.filePath):
            return
        if initialPage is None:
            initialPage = self.settings['home']

        subprocess.Popen([
            self.zimApp,
            self.filePath,
            initialPage,
            ])

    def read_settings(self):
        """Read the settings, updating the instance variable."""
        notebook = ConfigParser()
        notebook.read(self.filePath, encoding='utf-8')
        for tag in self.settings:
            self.settings[tag] = notebook.get(self.NOTEBOOK, tag)

    def update_index(self):
        if not os.path.isfile(self.filePath):
            return

        subprocess.Popen([
            self.zimApp,
            '--index',
            self.filePath,
            ])

    def write(self):
        """Write the notebook, overwriting existing one."""
        notebook = ConfigParser()
        notebook.add_section(self.NOTEBOOK)
        for tag in self.settings:
            notebook.set(self.NOTEBOOK, tag, self.settings[tag])
        with open(self.filePath, 'w', encoding='utf-8') as f:
            notebook.write(f)
        os.makedirs(self.homeDir, exist_ok=True)

    def get_page_path_by_name(self, pageName):
        """Return the path of a note specified by page name."""
        foundFiles = glob.glob(
            f"**/{pageName.replace(' ', '_')}{ZimPage.EXTENSION}",
            root_dir=self.homeDir,
            recursive=True,
            )
        if foundFiles:
            foundFile = foundFiles[0].replace('\\', '/')
            return f'{self.homeDir}/{foundFile}'

