import importlib
import sys
from types import ModuleType


class DummyLCD:
    def __init__(self):
        self.events = []
        self._cursor = (0, 0)

    def create_char(self, location, pattern):
        self.events.append(("create_char", location, pattern))

    def clear(self):
        self.events.append(("clear",))

    @property
    def cursor_pos(self):
        return self._cursor

    @cursor_pos.setter
    def cursor_pos(self, value):
        self._cursor = value
        self.events.append(("cursor_pos", value))

    def write_string(self, text):
        self.events.append(("write_string", text))


# Provide fake Pi GPIO and RPLCD modules so Emotions.py imports cleanly on non-Raspberry Pi systems.
mock_rpi = ModuleType("RPi")
mock_rpi_gpio = ModuleType("RPi.GPIO")
mock_rpi_gpio.BCM = 0
mock_rpi_gpio.OUT = 0
mock_rpi_gpio.IN = 0
mock_rpi_gpio.setmode = lambda mode: None
mock_rpi_gpio.setup = lambda *args, **kwargs: None
mock_rpi_gpio.output = lambda *args, **kwargs: None
mock_rpi_gpio.input = lambda *args, **kwargs: 0
mock_rpi_gpio.cleanup = lambda: None
mock_rpi_gpio.gpio_function = lambda pin: None

mock_rplcd = ModuleType("RPLCD")
mock_rplcd_gpio = ModuleType("RPLCD.gpio")
mock_rplcd_gpio.CharLCD = lambda *args, **kwargs: DummyLCD()
mock_rplcd_gpio.CharLCD.__module__ = "RPLCD.gpio"

sys.modules["RPi"] = mock_rpi
sys.modules["RPi.GPIO"] = mock_rpi_gpio
sys.modules["RPLCD"] = mock_rplcd
sys.modules["RPLCD.gpio"] = mock_rplcd_gpio

import Emotions
importlib.reload(Emotions)

# Inject a dummy LCD instance for the display logic.
dummy = DummyLCD()
Emotions.lcd = dummy
Emotions.setup_emoticons()
Emotions.show_smiley()
Emotions.show_angry()
Emotions.show_heart_eyes()

print(dummy.events)