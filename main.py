import os
import sys
import datetime
import json
from glob import glob
import config
import spellParser
from PyQt5.QtCore import QFileSystemWatcher, pyqtSignal
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon


config_file = r'config.json'
config.load(config_file)

def strip_timestamp(line):
    """
    Strings EQ Timestamp from log entry.
    """
    return line[line.find("]") + 1:].strip()

# class LogReader(QFileSystemWatcher):
#     print("dawg")
#     new_line = pyqtSignal(object)
#     def __init__(self,dir):
#         self.logfiles = glob(os.path.join(dir, 'eqlog*.txt'))
#         self.filesys_watcher = QFileSystemWatcher(self.logfiles)
#         self.filesys_watcher.fileChanged.connect(self.file_changed)
#
#         self.stats = {
#             'log_file': '',
#             'last_read': 0
#         }
#
#     def file_changed(self, changed_file):
#         with open(changed_file) as log:
#
#             if changed_file != self.stats['log_file']:
#                 self.stats['log_file'] = changed_file
#                 log.seek(0, os.SEEK_END)
#                 self.stats['last_read'] = log.tell()
#             try:
#                 log.seek(self.stats['last_read'], os.SEEK_SET)
#                 lines = log.readlines()
#                 self.stats['last_read'] = log.tell()
#                 for line in lines:
#                     self.new_line.emit((
#                         datetime.datetime.now(),
#                         strip_timestamp(line)
#
#                     ))
#             except Exception:
#                 log.seek(0, os.SEEK_END)
#                 self.stats['last_read'] = log.tell()


class EQParser(QApplication):
    def __init__(self,*args):
        super().__init__(*args)
        self.toggled = False
        self.log_reader = None
        self.load_parser()

        self.toggle_parser()



    def load_parser(self):
        parser_window = spellParser.ParserWindow()
        g = config.data['spells']['geometry']

        if config.data['spells']['toggled']:
            parser_window.toggle()

    def toggle_parser(self):
        pass
        #if not self.toggled:
            #self.log_reader = LogReader(config.data['general']['eq_log_dir'])





def ParserWindow(QFrame):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.setObjectName('ParserWindow')
        self.setWindowOpacity(1)







APP = EQParser(sys.argv)
print(config.data)
