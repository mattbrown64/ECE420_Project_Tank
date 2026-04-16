import RPi.GPIO as GPIO
from RPLCD.gpio import CharLCD


GPIO.setmode(GPIO.BCM)

lcd = CharLCD(
    numbering_mode=GPIO.BCM,
    cols=20, rows=4,
    pin_rs=7,
    pin_e=8,
    pins_data=[25, 24, 23, 18],
    auto_linebreaks=True,
)

SMILEY = [
    0b00000,
    0b01010,
    0b01010,
    0b00000,
    0b10001,
    0b01110,
    0b00000,
    0b00000,
]

SMILEY = [
    0b00000,
    0b01010,
    0b01010,
    0b00000,
    0b10001,
    0b10001,
    0b01110,
    0b00000,
 ]

ANGRY = [
    0b00000,
    0b11011,
    0b10101,
    0b00000,
    0b01110,
    0b10001,
    0b00000,
    0b00000,
]

HEART_EYES = [
    0b00000,
    0b01010,
    0b11111,
    0b11111,
    0b01010,
    0b10001,
    0b01110,
    0b00000,
]


def setup_emoticons():
    lcd.create_char(0, SMILEY)
    lcd.create_char(1, ANGRY)
    lcd.create_char(2, HEART_EYES)


def clear_display():
    lcd.clear()


def show_emotion(char_index, text=None, text_row=2, emotion_row=1, emotion_col=8):
    clear_display()
    lcd.cursor_pos = (emotion_row, emotion_col)
    lcd.write_string(chr(char_index))

    if text:
        lcd.cursor_pos = (text_row, 0)
        lcd.write_string(text)


def show_smiley():
    show_emotion(0, text='Happy!', text_row=2, emotion_row=1, emotion_col=7)


def show_angry():
    show_emotion(1, text='Angry!', text_row=2, emotion_row=1, emotion_col=8)


def show_heart_eyes():
    show_emotion(2, text='Love it!', text_row=2, emotion_row=1, emotion_col=6)


setup_emoticons()

if __name__ == '__main__':
    show_smiley()
    input('Press Enter for angry face...')
    clear_display()
    show_angry()
    input('Press Enter for heart-eyes face...')
    clear_display()
    show_heart_eyes()