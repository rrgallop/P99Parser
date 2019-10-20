import os
import sys
import datetime
import json
from glob import glob
import config
import parserwindow
from PyQt5.QtCore import QFileSystemWatcher, pyqtSignal
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon


config_file = r'config.json'
config.load(config_file)

def strip_timestamp(line):
    """
    Strings EQ Timestamp from log entry.
    """
    return line[line.find("]") + 1:].strip()

class LogReader(QFileSystemWatcher):
    print("Sup")
    new_line = pyqtSignal(object)
    def __init__(self,dir):
        self.logfiles = glob(os.path.join(dir, 'eqlog*.txt'))
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
    def __init__(self,*args):
        super().__init__(*args)
        self.toggled = False
        self.log_reader = None
        self.load_parser()
        # Tray Icon
        self.system_tray = QSystemTrayIcon()




    def load_parser(self):
        parser_window = parserwindow.ParserWindow()
        g = config.data['spells']['geometry']
        if config.data['spells']['toggled']:
            parser_window.toggle()


class Spell:
    def __init__(self, **kwargs):
        self.id = 0
        self.name = ''
        self.effect_string_you = ''
        self.effect_string_other = ''
        self.effect_string_worn_off = ''
        self.aoe_range = 0
        self.max_targets = 1
        self.cast_time = 0
        self.resist_type = 0
        self.duration_formula = 0
        self.pvp_duration_formula = 0
        self.duration = 0
        self.pvp_duration = 0
        self.type = 0
        self.spell_icon = 0
        self.__dict__.update(kwargs)


def ParserWindow(QFrame):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.setObjectName('ParserWindow')
        self.setWindowOpacity(1)




def create_spell_book():
    """
    Spell information is stored locally in spells_us.txt
    This method will parse the spell file to extract spell information
    For use in detection string etc
    """
    spellbook = {}
    with open('spells_us.txt') as spellz:
        for line in spellz:
            values = line.strip().split('^')
            spellbook[values[1]] = Spell(
                id=int(values[0]),
                name=values[1].lower(),
                effect_on_you=values[6],
                effect_text_other=values[7],
                effect_text_worn_off=values[8],
                aoe_range=int(values[10]),
                max_targets=(6 if int(values[10]) > 0 else 1),
                cast_time=int(values[13]),
                resist_type=int(values[85]),
                duration_formula=int(values[16]),
                pvp_duration_formula=int(values[181]),
                duration=int(values[17]),
                pvp_duration=int(values[182]),
                type=int(values[83]),
                spell_icon=int(values[144])
            )
        return spellbook


APP = EQParser(sys.argv)
print(config.data)
