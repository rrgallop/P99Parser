from PyQt5.QtCore import Qt, QRect, pyqtSignal, QObject, QTimer, QEvent
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QLabel, QProgressBar,
                             QPushButton, QVBoxLayout, QWidget, QScrollArea, QSpinBox, QListView)
import config
import datetime
import math
import string


class SpellParser():
    """
    Manages top-level gui object. Parent of all other widgets defined below.
    """
    def __init__(self):
        super().__init__()
        global gui
        gui = QFrame()
        self.layout = QVBoxLayout(gui)
        self.menu = QWidget(gui)
        self.menu_content = QHBoxLayout(gui)
        self.scroll_area = QScrollArea(gui)
        self.title = QLabel(gui)
        self.lvlspinner = QSpinBox(gui)
        self.spell_countdown = SpellContainerWidget()
        self.toggled = False
        self.name = 'Spell Parser'
        gui.setWindowTitle(self.name)
        self.setup_ui()
        self.spell_book = create_spell_book()
        self.triggered_spell_holder = None  # will hold created TriggeredSpell objects defined below

    def setup_ui(self):
        """
        Set up GUI elements defined above. Listed here for reference.
        layout = QVBoxLayout()
        menu = QWidget()
        menu_content = QHBoxLayout()
        title = QLabel()
        scroll_area = QScrollArea()
        lvlspinner = QSpinBox()
        spell_countdown = SpellCountdownContainer() defined below
        :return:
        """
        gui.setMinimumWidth(200)
        gui.setLayout(self.layout)
        self.menu.setLayout(self.menu_content)
        self.menu_content.setSpacing(5)
        self.layout.addWidget(self.menu, 0)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.spell_countdown)
        self.scroll_area.setObjectName('SpellScrollArea')
        self.layout.addWidget(self.scroll_area, 1)
        self.lvlspinner.setRange(1, 60)
        self.lvlspinner.setPrefix('level: ')
        self.layout.addWidget(self.lvlspinner)

        gui.show()

    def reset_spell_trigger(self):
        self.triggered_spell_holder = None

    def triggered_spell_handler(self):
        """
        Triggered once spell casting is complete to handle next steps
        :return:
        """
        print("Heard the signal, now reset the parser...")
        for target in self.triggered_spell_holder.spell_targets:
            print(target)
            self.spell_countdown.add_spell(self.triggered_spell_holder.spell, target[0], target[1])
        self.reset_spell_trigger()
        print("success")

    def parse(self, timestamp, text):

        # spell is triggered, waiting for casting to complete
        if self.triggered_spell_holder is not None:
            self.triggered_spell_holder.parse(timestamp, text)

        # player starts casting, we set up the spell trigger
        if text[:17] == 'You begin casting':
            spell = self.spell_book.get(text[18:-1], None)
            if spell is not None and spell.duration_formula != 0:  # only buffs/debuffs/DoTs
                triggered_spell = TriggeredSpell(
                    spell=spell,
                    timestamp=timestamp
                )
                triggered_spell.triggered_spell_signal.connect(self.triggered_spell_handler)
                self.triggered_spell_holder = triggered_spell
                print("Casting "+triggered_spell.spell.name)

        elif (self.triggered_spell_holder and
              text[:26] == 'Your spell is interrupted.' or
              text[:20] == 'Your target resisted' or
              text[:29] == 'Your spell did not take hold.' or
              text[:26] == 'You try to cast a spell on'):
            self.reset_spell_trigger()
            print("**Failed cast**")


class SpellContainerWidget(QFrame):
    """
    GUI Element that stores active spells, organized by spell target
    """
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout(gui))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setObjectName('CountdownElement')

    def add_spell(self, spell, timestamp, target):
        spell_target = None
        new = False
        print('Adding spell for '+target)
        for st in self.findChildren(SpellTargetWidget):
            print(st)
            if st.title == target:
                spell_target = st
                self.layout().addWidget(spell_target, 0)
        if not spell_target:
            new = True
            spell_target = SpellTargetWidget(target=target)
            self.layout().addWidget(spell_target, 0)
        spell_target.add_spell(spell, timestamp)


class SpellTargetWidget(QFrame):
    """
    Child element of SpellGUIContainer. Displays the name of the spell's target.
    """

    def __init__(self, target='yourself'):
        super().__init__()
        self.title = target
        self.setObjectName('SpellTarget')
        self.target_label = QLabel(self.title.title())
        self.setup_ui()

    def setup_ui(self):
        self.setLayout(QVBoxLayout(gui))
        self.target_label.setObjectName('SpellTargetLabel')
        self.setFixedHeight(80)
        self.layout().addWidget(self.target_label, 1)

    def add_spell(self, spell, timestamp):
        """
        Identify the cast spell and add it to the GUI after calculating the timestamp
        :param spell: Spell object representing the detected spell that was cast
        :param timestamp: Datetime object used to calculate spell duration.
        """
        recast = False
        # cycle through active spells to detect recasts
        for _ in self.findChildren(SpellCountdownWidget):
            if _.spell.name == spell.name:
                recast = True
                _.calculate(timestamp)  # recalculate spell duration
        if not recast:
            self.layout().addWidget(SpellCountdownWidget(spell, timestamp))

    def childEvent(self, event):
        """
        Signal is emitted when child widget is removed.
        If signal is detected by parent, and no children remain, delete the GUI element.
        :param event:
        """
        if event.type() == QEvent.ChildRemoved:
            if type(event.child()) == SpellCountdownWidget:
                if not self.findChildren(SpellCountdownWidget):
                    self.setParent(None)
                    self.deleteLater()
        event.accept()


class SpellCountdownWidget(QFrame):
    """
    Child element of SpellTargetWidget. Shows the name of the spell,
    and tracks its duration
    """

    def __init__(self, spell, timestamp):
        super().__init__()
        self.setObjectName('SpellCountdownWidget')
        self.spell = spell
        self.progress = QProgressBar(gui)
        self.progress.setMinimumHeight(30)
        self.calculate(timestamp)
        self.setup_ui()
        self.setProperty('Warning', False)

    def setup_ui(self):

        layout = QHBoxLayout(gui)
        self.setLayout(layout)
        progress_layout = QHBoxLayout(self.progress)
        self.name_label = QLabel(self.spell.name, self.progress)
        self.name_label.setObjectName('CountdownNameLabel')
        progress_layout.addWidget(self.name_label)
        self.time_label = QLabel('', self.progress)
        self.time_label.setObjectName('CountdownTimeLabel')
        progress_layout.addWidget(self.time_label)
        layout.addWidget(self.progress, 0)
        self.update()

    def calculate(self, timestamp):
        """
        Calculates spell duration in seconds.
        :param timestamp: Datetime object representing when spell was cast
        :return:
        """
        self.ticks_remaining = get_spell_duration(self.spell)
        self.seconds_remaining = (int(self.ticks_remaining * 6))
        self.end_time = timestamp + datetime.timedelta(seconds=self.seconds_remaining)
        print(self.end_time)
        self.progress.setMaximum(self.seconds_remaining)

    def update(self):
        """
        Updates progress bar with new time remaining
        """
        time_remaining = self.end_time - datetime.datetime.now()
        remaining_seconds = time_remaining.total_seconds()
        self.progress.setValue(time_remaining.seconds)
        self.progress.update()
        if remaining_seconds <= 0:
            # Remove
            self.setParent(None)
            self.deleteLater()
        QTimer.singleShot(1000, self.update)


def get_spell_duration(spell, level=7):
    """
    Method used to parse raw duration into spell ticks, with each tick being roughly 6 seconds.
    :param spell: The Spell object representing the spell being cast.
    :param level: Your character's level.
    :return: spell's duration in ticks
    """
    formula = spell.duration_formula
    duration = spell.duration

    spell_ticks = 0
    if formula == 0:
        pass
    elif formula == 1:
        spell_ticks = int(math.ceil(level / float(2.0)))
        if spell_ticks > duration:
            spell_ticks = duration
    elif formula == 2:
        spell_ticks = int(math.ceil(level / float(5.0)*3))
    elif formula == 3:
        spell_ticks = int(level*30)
        if spell_ticks > duration:
            spell_ticks = duration
    elif formula == 4:
        if duration == 0:
            spell_ticks = 50
    elif formula == 5:
        spell_ticks = duration
        if spell_ticks == 0:
            spell_ticks = 3
    elif formula == 6:
        spell_ticks = int(math.ceil(level / float(2.0)))
        if spell_ticks > duration:
            spell_ticks = duration
    elif formula == 7:
        spell_ticks = level
        if spell_ticks > duration:
            spell_ticks = duration
    elif formula == 8:
        spell_ticks = level + 10
        if spell_ticks > duration:
            spell_ticks = duration
    elif formula == 9:
        spell_ticks = int((level * 2) + 10)
        if spell_ticks > duration:
            spell_ticks = duration
    elif formula == 10:
        spell_ticks = int(level * 3 + 10)
        if spell_ticks > duration:
            spell_ticks = duration
    elif formula == 11:
        spell_ticks = duration
    elif formula == 12:
        spell_ticks = duration
    elif formula == 15:
        spell_ticks = duration
    elif formula == 50:
        spell_ticks = 72000
    elif formula == 3600:
        if duration == 0:
            spell_ticks = 3600
        else:
            spell_ticks = duration

    print('Spell ticks calculated to be: ' +str(spell_ticks))
    return spell_ticks


class Spell:
    """
    Parsed spell data from spells_us.txt is stored as a Spell object.
    This serves as my internal representation of a spell.
    """
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


class TriggeredSpell(QObject):

    """
    Here I store the spell information along with the time it was cast together in the same object.
    Then this object's parse function will use the attached spell and datetime to determine buff timers

    """

    # signals spell is active to the parser
    triggered_spell_signal = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__()
        self.datetime = None
        self.spell = None
        self.spell_targets = []
        self.active = False
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
            target = text[:len(text) - len(self.spell.effect_text_other)].strip()
            self.spell_targets.append((timestamp, target))

        if self.spell_targets:
            print("Spell active! Ready to parse. Targets:")
            print(self.spell_targets)
            self.triggered_spell_signal.emit()

    def set_as_expired(self):
        self.effect_expired = True


def create_spell_book():
    """
    Spell information is stored locally in spells_us.txt
    This method will parse the spell file to extract spell information
    The spell file contains all information describing the spells in the game.
    Information parsed then can be used to determine what spell is being cast,
    and then calculate its duration.
    Spells that are read in are stored as a Spell object, defined above.
    :returns: spellbook, a dictionary of spells, organized by spell name.
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
