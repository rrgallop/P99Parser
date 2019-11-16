import os
import sys
import datetime
import json
from glob import glob
import config
import spellParser

from PyQt5.QtCore import QFileSystemWatcher, pyqtSignal, Qt
from PyQt5.QtGui import QCursor, QFontDatabase, QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QLabel, QWidget, QPushButton, QVBoxLayout


config_file = r'config.json'
config.load(config_file)

def strip_timestamp(line):
    return line[line.find("]") + 1:].strip()

class LogReader(QFileSystemWatcher):
    """
    Monitors the logfiles in the given directory, detecting any changes that occur to the files.
    """
    new_line = pyqtSignal(object)

    def __init__(self,dir):
        super().__init__()
        self.logfiles = glob(os.path.join(dir, 'eqlog*.txt'))
        print(self.logfiles)
        self.filesys_watcher = QFileSystemWatcher(self.logfiles)

        # fileChanged signal is emitted when a file is changed, triggering connected function
        self.filesys_watcher.fileChanged.connect(self.file_changed)
        self.stats = {
            'log_file': '',
            'last_read': 0
        }

    def file_changed(self, changed_file):
        """
        Triggered when a change is detected in a file.
        Reads the line of the file and extracts it for further parsing.
        :param changed_file: location of the changed file
        """
        with open(changed_file) as log:

            if changed_file != self.stats['log_file']:
                self.stats['log_file'] = changed_file
                log.seek(0, os.SEEK_END)
                self.stats['last_read'] = log.tell()
            try:
                log.seek(self.stats['last_read'], os.SEEK_SET)
                lines = log.readlines()
                self.stats['last_read'] = log.tell()
                for line in lines:
                    self.new_line.emit((
                        datetime.datetime.now(),
                        strip_timestamp(line)

                    ))
            except Exception:
                log.seek(0, os.SEEK_END)
                self.stats['last_read'] = log.tell()


class EQParser(QApplication):
    """
    Parent application of parser windows
    (currently only SpellParser)
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.toggled = False
        self.log_reader = None
        self.parser_window = spellParser.SpellParser()
        self.toggle_parser()

    def toggle_parser(self):
        """
        Activates, and eventually, deactivates the LogReader as necessary
        """
        self.log_reader = LogReader(config.data['general']['eq_log_dir'])
        self.log_reader.new_line.connect(self.parse)

    def parse(self, new_line):
        if new_line:
            timestamp, text = new_line
            self.parser_window.parse(timestamp, text)


APP = EQParser(sys.argv)
APP.setQuitOnLastWindowClosed(True)
APP.setAttribute(Qt.AA_EnableHighDpiScaling)

APP.exec_()
