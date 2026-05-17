"""Примитивы рисования ручкой и подготовка листа под график."""
import math
import random
from PIL import ImageDraw

from .config import DEFAULT_FONT_PATH, IMG_W, IMG_H, PEN
from .paper import make_paper_texture, draw_grid
from .presets import DEFAULT_PAPER
from .text import draw_handwritten_text


def _pen_line(draw, points, color=PEN, width=2):
    for i in range(len(points)-1):
        x1, y1 = points[i]; x2, y2 = points[i+1]
        steps = max(2, int(math.hypot(x2-x1, y2-y1) / 8))
        for s in range(steps):
            t0, t1 = s/steps, (s+1)/steps
            draw.line([(x1+(x2-x1)*t0+random.uniform(-0.3,0.3), y1+(y2-y1)*t0+random.uniform(-0.3,0.3)),
                       (x1+(x2-x1)*t1+random.uniform(-0.3,0.3), y1+(y2-y1)*t1+random.uniform(-0.3,0.3))],
                      fill=color, width=width)


def _pen_arrow(draw, x1, y1, x2, y2, color=PEN, width=2):
    _pen_line(draw, [(x1,y1),(x2,y2)], color, width)
    angle = math.atan2(y2-y1, x2-x1)
    for da in [0.4, -0.4]:
        _pen_line(draw, [(x2,y2),(x2-12*math.cos(angle+da), y2-12*math.sin(angle+da))], color, width)


def _pen_circle(draw, cx, cy, r, color=PEN, filled=True, width=2):
    if filled:
        draw.ellipse([(cx-r,cy-r),(cx+r,cy+r)], fill=color)
    else:
        draw.ellipse([(cx-r,cy-r),(cx+r,cy+r)], outline=color, width=width)


def _pen_rect(draw, x, y, w, h, color=PEN, width=2):
    _pen_line(draw, [(x,y),(x+w,y)], color, width)
    _pen_line(draw, [(x+w,y),(x+w,y+h)], color, width)
    _pen_line(draw, [(x+w,y+h),(x,y+h)], color, width)
    _pen_line(draw, [(x,y+h),(x,y)], color, width)


def _pen_text(img, x, y, text, font, color=PEN):
    draw_handwritten_text(img, x, y, text, font, color)


def make_graph_page(font_path=None, paper=DEFAULT_PAPER):
    """Создаёт тетрадный лист для графика/схемы."""
    if font_path is None: font_path = DEFAULT_FONT_PATH
    page = make_paper_texture(IMG_W, IMG_H, paper=paper)
    d = ImageDraw.Draw(page)
    draw_grid(d, IMG_W, IMG_H, paper=paper)
    return page
