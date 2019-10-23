from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QLabel,
                             QPushButton, QVBoxLayout, QWidget, QScrollArea, QSpinBox, QListView)
import config


class SpellParser():
    def __init__(self):
        super().__init__()
        global gui
        gui = QFrame()
        self.fucked = True
        self.toggled = False
        self.name = 'Spell Parser'
        gui.setWindowTitle(self.name)
        gui.resize(300, 420)
        self.setup_ui()
        self.spell_book = create_spell_book()

    def setup_ui(self):
        listview = QListView(gui)
        listview.setGeometry(QRect(20, 20, 260, 330))
        listview.setObjectName('Spell Info')
        spinbox = QSpinBox(gui)
        spinbox.setGeometry(222, 370, 60, 30)
        spinbox.setMinimum(1)
        spinbox.setMaximum(60)
        spinbox.setPrefix('lvl: ')
        spinbox.setObjectName('lvl')




        menu_content = QHBoxLayout()
        menu_content.setSpacing(5)
        menu_content.setContentsMargins(3,0,0,0)
        # layout.addWidget(menu_content)

        gui.show()

    def parse(self, timestamp, text):
        if text[:17] == 'You begin casting':
            print("We got one boys!")

    def toggle(self):
        pass


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
