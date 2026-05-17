"""Константы и пути."""
import os

_LIB_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(_LIB_DIR)
FONTS_DIR = os.path.join(SKILL_DIR, "fonts")

DEFAULT_FONT_PATH = os.path.join(FONTS_DIR, "lorenco_font.ttf")
if not os.path.exists(DEFAULT_FONT_PATH):
    DEFAULT_FONT_PATH = os.path.join(FONTS_DIR, "abram_font.ttf")
if not os.path.exists(DEFAULT_FONT_PATH):
    DEFAULT_FONT_PATH = os.path.expanduser("~/Library/Fonts/BadScript-Regular.ttf")

IMG_W = 1748
IMG_H = 2480
MARGIN_LEFT = 130
MARGIN_TOP = 60
MARGIN_RIGHT = 80
CELL_SIZE = 30
LINE_HEIGHT = CELL_SIZE * 2
FONT_SIZE = 40
FONT_SIZE_SMALL = 34
HEADER_FONT_SIZE = 30

PEN = (15, 30, 120)
PEN_LIGHT = (40, 60, 145)
