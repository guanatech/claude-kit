"""Сборка страницы из строк и постраничная разбивка."""
import random
from PIL import ImageDraw, ImageFont

from .config import (
    IMG_W, IMG_H, MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT,
    CELL_SIZE, LINE_HEIGHT, FONT_SIZE, FONT_SIZE_SMALL, HEADER_FONT_SIZE,
    DEFAULT_FONT_PATH,
)
from .paper import make_paper_texture, draw_grid
from .presets import DEFAULT_PAPER
from .text import draw_handwritten_text


def create_page(header_text, lines, font_path=None, paper=DEFAULT_PAPER):
    if font_path is None: font_path = DEFAULT_FONT_PATH
    img = make_paper_texture(IMG_W, IMG_H, paper=paper)
    draw = ImageDraw.Draw(img)
    draw_grid(draw, IMG_W, IMG_H, paper=paper)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(font_path, FONT_SIZE)
    font_small = ImageFont.truetype(font_path, FONT_SIZE_SMALL)
    font_header = ImageFont.truetype(font_path, HEADER_FONT_SIZE)

    if header_text:
        bbox = draw.textbbox((0, 0), header_text, font=font_header)
        tw = bbox[2] - bbox[0]
        draw_handwritten_text(img, IMG_W - MARGIN_RIGHT - tw, 30, header_text, font_header, (25, 50, 150))

    y_start = MARGIN_TOP + 60
    y = (y_start // CELL_SIZE) * CELL_SIZE + CELL_SIZE

    for line in lines:
        if isinstance(line, tuple):
            text, style = line
        else:
            text, style = line, 'normal'

        r_var = random.randint(-5, 5)
        pen_color = (25+r_var, 50+r_var, 150+r_var)
        pen_accent = (15+r_var, 35+r_var, 130+r_var)

        if style in ('bold', 'title', 'blue'):
            f, color = font, pen_accent
        elif style == 'small':
            f, color = font_small, pen_color
        else:
            f, color = font, pen_color

        if style == 'skip':
            y += LINE_HEIGHT
            y = round(y / CELL_SIZE) * CELL_SIZE
            continue

        x = MARGIN_LEFT + (60 if style == 'indent' else 0)
        max_w = IMG_W - x - MARGIN_RIGHT
        words = text.split(' ')
        current_line = ''
        for word in words:
            test = current_line + (' ' if current_line else '') + word
            bbox = draw.textbbox((0, 0), test, font=f)
            if bbox[2] - bbox[0] > max_w and current_line:
                jy = random.uniform(-2, 2)
                draw_handwritten_text(img, x, y + jy, current_line, f, color)
                y += LINE_HEIGHT
                y = round(y / CELL_SIZE) * CELL_SIZE
                current_line = word
                if y > IMG_H - 100: break
            else:
                current_line = test
        if current_line and y <= IMG_H - 100:
            jy = random.uniform(-2, 2)
            draw_handwritten_text(img, x, y + jy, current_line, f, color)
            y += LINE_HEIGHT
            y = round(y / CELL_SIZE) * CELL_SIZE

    return img


def render_solution_pages(solution_lines, header_text="", font_path=None, paper=DEFAULT_PAPER):
    if font_path is None: font_path = DEFAULT_FONT_PATH
    pages, page_lines = [], []
    y_estimate = MARGIN_TOP + 60
    font_test = ImageFont.truetype(font_path, FONT_SIZE)
    font_test_small = ImageFont.truetype(font_path, FONT_SIZE_SMALL)

    for line in solution_lines:
        text = line[0] if isinstance(line, tuple) else line
        style = line[1] if isinstance(line, tuple) else 'normal'
        f = font_test_small if style == 'small' else font_test
        x = MARGIN_LEFT + (60 if style == 'indent' else 0)
        max_w = IMG_W - x - MARGIN_RIGHT
        words, current, line_count = text.split(' '), '', 1
        for word in words:
            test = current + (' ' if current else '') + word
            bbox_test = f.getbbox(test)
            if bbox_test and (bbox_test[2] - bbox_test[0]) > max_w and current:
                line_count += 1; current = word
            else:
                current = test
        needed = LINE_HEIGHT * line_count
        if y_estimate + needed > IMG_H - 100:
            pages.append(create_page(header_text, page_lines, font_path, paper=paper))
            page_lines, y_estimate = [], MARGIN_TOP + 60
        page_lines.append(line)
        y_estimate += needed

    if page_lines:
        pages.append(create_page(header_text, page_lines, font_path, paper=paper))
    return pages
