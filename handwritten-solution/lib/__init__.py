"""Публичный API пакета handwritten-solution.lib."""

from .config import (
    DEFAULT_FONT_PATH, FONTS_DIR, SKILL_DIR,
    IMG_W, IMG_H, MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT,
    CELL_SIZE, LINE_HEIGHT,
    FONT_SIZE, FONT_SIZE_SMALL, HEADER_FONT_SIZE,
    PEN, PEN_LIGHT,
)
from .presets import BACKGROUND_PRESETS, DEFAULT_PRESET, PAPER_PRESETS, DEFAULT_PAPER
from .paper import make_paper_texture, draw_grid
from .text import draw_handwritten_text
from .pages import create_page, render_solution_pages
from .camera import apply_phone_camera_effect
from .graphs import (
    make_graph_page,
    _pen_line, _pen_arrow, _pen_circle, _pen_rect, _pen_text,
)
from .generator import HandwrittenGenerator

__all__ = [
    "HandwrittenGenerator",
    "BACKGROUND_PRESETS", "DEFAULT_PRESET",
    "PAPER_PRESETS", "DEFAULT_PAPER",
    "DEFAULT_FONT_PATH", "FONTS_DIR", "SKILL_DIR",
    "IMG_W", "IMG_H", "MARGIN_LEFT", "MARGIN_TOP", "MARGIN_RIGHT",
    "CELL_SIZE", "LINE_HEIGHT",
    "FONT_SIZE", "FONT_SIZE_SMALL", "HEADER_FONT_SIZE",
    "PEN", "PEN_LIGHT",
    "make_paper_texture", "draw_grid",
    "draw_handwritten_text",
    "create_page", "render_solution_pages",
    "apply_phone_camera_effect",
    "make_graph_page",
    "_pen_line", "_pen_arrow", "_pen_circle", "_pen_rect", "_pen_text",
]
