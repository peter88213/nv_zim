"""Provide a class for a Zim Wiki representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from configparser import ConfigParser
import glob
import os

from nvzimlib.nvzim_globals import ZIM_NOTEBOOK_TAG
from nvzimlib.nvzim_globals import ZIM_NOTE_EXTENSION


class ZimNotebook:

    NOTEBOOK = 'Notebook'
    HOME = 'Home'

    def __init__(self, novel, dirPath='', filePath=''):
        # Specify either directory or file path.
        self.settings = dict(
            version='0.4',
            name=self.NOTEBOOK,
            interwiki='',
            home=self.HOME,
            icon='',
            document_root='',
            shared='True',
            endofline='dos',
            disable_trash='False',
            profile='',
        )
        self._novel = novel
        if os.path.isfile(filePath):
            self.filePath = filePath
            self.dirPath, __ = os.path.split(filePath)
            self.filePath = filePath
            self.read_settings()
            self.homeDir = f'{self.dirPath}/{self.settings["home"]}'
        elif os.path.isdir(dirPath):
            self.dirPath = dirPath
            self.filePath = f'{dirPath}/{self.NOTEBOOK}.zim'
            self.homeDir = f'{self.dirPath}/{self.HOME}'
            self.write()
        else:
            raise AttributeError

    def create_link(self):
        """Add or replace the novel's Zim notebook link."""
        fields = self.novel.fields
        fields[ZIM_NOTEBOOK_TAG] = self.dirPath
        self._novel.fields = fields

    def read_settings(self):
        """Read the settings, updating the instance variable."""
        notebook = ConfigParser()
        notebook.read(self.filePath, encoding='utf-8')
        for tag in self.settings:
            self.settings[tag] = notebook.get(self.NOTEBOOK, tag)

    def write(self):
        """Write the notebook, overwriting existing one."""
        notebook = ConfigParser()
        notebook.add_section()
        for tag in self.settings:
            notebook.set(self.NOTEBOOK, tag, self.settings[tag])
        with open(self.filePath, 'w', encoding='utf-8') as f:
            notebook.write(f)
        os.makedirs(self.homeDir, exist_ok=True)

    def get_note(self, title):
        """Return the path of a note specified by title."""
        foundFiles = glob.glob(
            f'**/{title}{ZIM_NOTE_EXTENSION}',
            root_dir=self.homeDir,
            recursive=True,
            )
        if foundFiles:
            foundFile = foundFiles[0].replace('\\', '/')
            return f'{self.homeDir}/{foundFile}'

