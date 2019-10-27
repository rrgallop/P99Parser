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
    new_line = pyqtSignal(object)

    def __init__(self,dir):
        super().__init__()
        self.logfiles = glob(os.path.join(dir, 'eqlog*.txt'))
        print(self.logfiles)
        self.filesys_watcher = QFileSystemWatcher(self.logfiles)
        self.filesys_watcher.fileChanged.connect(self.file_changed)
        self.stats = {
            'log_file': '',
            'last_read': 0
        }

    def file_changed(self, changed_file):
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
    def __init__(self, *args):
        super().__init__(*args)
        self.toggled = False
        self.log_reader = None
        self.parser_window = spellParser.SpellParser()
        self.toggle_parser()

    def toggle_parser(self):

        self.log_reader = LogReader(config.data['general']['eq_log_dir'])
        self.log_reader.new_line.connect(self.parse)

    def parse(self, new_line):
        if new_line:
            timestamp, text = new_line
            self.parser_window.parse(timestamp, text)


def ParserWindow(QFrame):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.setObjectName('ParserWindow')
        self.setWindowOpacity(1)







APP = EQParser(sys.argv)
APP.setStyleSheet(open('_.css').read())
APP.setWindowIcon(QIcon('data/ui/icon.png'))
APP.setQuitOnLastWindowClosed(True)
APP.setAttribute(Qt.AA_EnableHighDpiScaling)
QFontDatabase.addApplicationFont('NotoSans-Regular.ttf')
QFontDatabase.addApplicationFont('NotoSans-Bold.ttf')
APP.exec_()
