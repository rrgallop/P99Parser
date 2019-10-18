import os
import sys
import json
from glob import glob

from PyQt5.QeCore import QFileSystemWatcher, pyqtSignal

eq_directory = r'C:\Users\User\Desktop\school\stuff\EverQuest\Logs'

class EQParser:

    def __init__(self,*args):
        super().__init__(*args)
        self.log_reader = LogReader(eq_directory)

class LogReader:
    def __init__(self,dir):
        super().__init__()
        self.logfiles = glob(os.path.join(dir, 'eqlog*.txt'))
        self.filesys_watcher = QFileSystemWatcher(self.logfiles)

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


create_spell_book()
