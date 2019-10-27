from PyQt5.QtCore import Qt, QRect, pyqtSignal, QObject, QTimer
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QLabel,
                             QPushButton, QVBoxLayout, QWidget, QScrollArea, QSpinBox, QListView)
import config


class SpellParser():
    def __init__(self):
        super().__init__()
        global gui
        gui = QFrame()
        self.toggled = False
        self.name = 'Spell Parser'

        self.setup_ui()
        self.spell_book = create_spell_book()
        self.triggered_spell_holder = None  # will hold created TriggeredSpell objects defined below

    def setup_ui(self):
        gui.setWindowTitle(self.name)
        gui.resize(300, 420)
        listview = QListView(gui)
        listview.setGeometry(QRect(20, 20, 260, 330))
        listview.setObjectName('Spell Info')
        spinbox = QSpinBox(gui)
        spinbox.setGeometry(222, 370, 60, 30)
        spinbox.setMinimum(1)
        spinbox.setMaximum(60)
        spinbox.setPrefix('lvl: ')
        spinbox.setObjectName('lvl')

        gui.show()

    def reset_spell_trigger(self):
        self.triggered_spell_holder = None

    def parse(self, timestamp, text):

        # spell is triggered, waiting for casting to complete
        if self.triggered_spell_holder is not None:
            self.triggered_spell_holder.parse(timestamp, text)
            self.reset_spell_trigger()  # set triggered_spell back to None

        # player starts casting, we set up the spell trigger
        if text[:17] == 'You begin casting':
            spell = self.spell_book.get(text[18:-1], None)
            if spell is not None and spell.duration_formula != 0:
                triggered_spell = TriggeredSpell(
                    spell=spell,
                    timestamp=timestamp
                )
                self.triggered_spell_holder = triggered_spell
                print("Casting "+triggered_spell.spell.name)


    # def spell_triggered_handler(self):
    #     if self.triggered_spell_holder:
    #         self.

    def toggle(self):
        pass


class Spell:
    def __init__(self, **kwargs):
        self.id = 0
        self.name = ''
        self.effect_text_you = ''
        self.effect_text_other = ''
        self.effect_text_worn_off = ''
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


class TriggeredSpell():

    """
    Here I store the spell information along with the time it was cast together in the same object.
    Then this object's parse function will use the attached spell and datetime to determine buff timers

    """

    # signal used to notify handler function when changes have occured to this spell
    # such as duration, spell expired, spell refreshed, whatever else I can think of...
    #  triggered_spell_signal = pyqtSignal()

    def __init__(self, **kwargs):
        self.datetime = None
        self.spell = None
        self.spell_targets = None
        self.effect_expired = False
        self.__dict__.update(kwargs)

        # set up timer countdown here
        self.active_buff_timer = QTimer()
        self.active_buff_timer.setSingleShot(True)  # timer will not repeat unless triggered
        self.active_buff_timer.timeout.connect(self.set_as_expired)

    def parse(self, timestamp, text):
        """
        Reaching this point signifies successful spell casting completion.
        At this point, we wnt to determine the effect of the spell, which we will do
        by parsing the logfile. Once the effect of the spell is determined,
        we will set up the GUI accordingly.
        :param text: The line of text received from the logfile.
        :return: None
        """
        if self.spell.effect_text_you == text[:len(self.spell.effect_text_you)]:
            print("You cast it on yourself")
            self.spell_targets.append((timestamp, 'yourself'))
        elif self.spell.effect_text_other == text[(len(text) - len(self.spell.effect_text_other)):]:
            print("You cast it on someone else")

        if self.targets is not None:
            pass

    def set_as_expired(self):
        self.effect_expired = True

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
                effect_text_you=values[6],
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
