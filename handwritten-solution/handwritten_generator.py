#!/usr/bin/env python3
"""
Универсальный генератор рукописных решений на тетрадном листе.
Создаёт реалистичные изображения с имитацией:
- тетрадного листа A5 в клетку с текстурой бумаги
- почерка синей шариковой ручкой (с вариацией нажима)
- фотографии на телефон при плохом освещении
- графиков и схем, нарисованных ручкой

Использование:
    from handwritten_generator import HandwrittenGenerator

    gen = HandwrittenGenerator(output_dir="/path/to/output")
    pages = gen.render_pages("Заголовок", [
        ("Задача 1", "blue"),
        ("Решение:", "normal"),
        ("x = 2 + 3 = 5", "indent"),
        ("", "skip"),
        ("Ответ: x = 5", "blue"),
    ])
"""

import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ==================== НАСТРОЙКИ ====================

DEFAULT_FONT_PATH = os.path.expanduser(
    "~/Downloads/fd059b0992a48a29deca57bc6ea325c1/fonts/abram_font4you.ttf")
# Фоллбэк
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

# Цвета ручки
PEN = (15, 30, 120)
PEN_LIGHT = (40, 60, 145)


# ==================== ТЕКСТУРА БУМАГИ ====================

def make_paper_texture(w, h):
    base_r, base_g, base_b = 250, 248, 240
    arr = np.zeros((h, w, 3), dtype=np.float32)
    arr[:, :, 0] = base_r; arr[:, :, 1] = base_g; arr[:, :, 2] = base_b

    coarse = np.random.normal(0, 3.0, (h // 4, w // 4))
    coarse = np.kron(coarse, np.ones((4, 4)))[:h, :w]
    for c in range(3): arr[:, :, c] += coarse

    fine = np.random.normal(0, 1.8, (h, w))
    for c in range(3): arr[:, :, c] += fine

    for _ in range(5):
        cx, cy = random.randint(0, w), random.randint(0, h)
        radius = random.randint(200, 600)
        intensity = random.uniform(-3, 3)
        yy, xx = np.mgrid[0:h, 0:w]
        spot = intensity * np.exp(-((xx-cx)**2 + (yy-cy)**2) / (radius**2))
        for c in range(3): arr[:, :, c] += spot

    yy, xx = np.mgrid[0:h, 0:w]
    edge_dist = np.minimum(np.minimum(xx, w-1-xx), np.minimum(yy, h-1-yy)).astype(np.float32)
    edge_factor = np.clip(1.0 - edge_dist / 300, 0, 1) * 4
    arr[:, :, 0] += edge_factor * 2; arr[:, :, 1] += edge_factor; arr[:, :, 2] -= edge_factor * 3

    for y in range(0, h, random.randint(3, 7)):
        if random.random() < 0.3:
            sv = random.uniform(-1.5, 1.5)
            t = random.randint(1, 3)
            for c in range(3): arr[y:min(y+t, h), :, c] += sv

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ==================== КЛЕТКА И ПОЛЯ ====================

def draw_grid(draw, w, h):
    for x in range(0, w, CELL_SIZE):
        b = random.randint(-8, 8)
        color = (180+b, 208+b, 232+b)
        pts = [(x + random.uniform(-0.3, 0.3), y) for y in range(0, h, 40)]
        for i in range(len(pts)-1): draw.line([pts[i], pts[i+1]], fill=color, width=1)

    for y in range(0, h, CELL_SIZE):
        b = random.randint(-8, 8)
        color = (180+b, 208+b, 232+b)
        pts = [(x, y + random.uniform(-0.3, 0.3)) for x in range(0, w, 40)]
        for i in range(len(pts)-1): draw.line([pts[i], pts[i+1]], fill=color, width=1)

    margin_x = MARGIN_LEFT - 15
    for sy in range(0, h, 30):
        j1, j2 = random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4)
        rc = (215+random.randint(-5,5), 75+random.randint(-5,5), 75)
        draw.line([(margin_x+j1, sy), (margin_x+j2, min(sy+30, h))], fill=rc, width=2)
        draw.line([(margin_x-4+j1, sy), (margin_x-4+j2, min(sy+30, h))], fill=rc, width=1)


# ==================== РУКОПИСНЫЙ ТЕКСТ С НАЖИМОМ ====================

def _render_char_image(ch, font, color, pressure):
    pad = 20
    bbox = font.getbbox(ch)
    ch_w = bbox[2] - bbox[0] + pad * 2
    ch_h = bbox[3] - bbox[1] + pad * 2

    char_img = Image.new('RGBA', (ch_w, ch_h), (0, 0, 0, 0))
    char_draw = ImageDraw.Draw(char_img)
    char_draw.text((pad - bbox[0], pad - bbox[1]), ch, fill=color + (255,), font=font)

    if pressure > 1.1:
        overlay_color = (max(5, color[0]-10), max(10, color[1]-10), max(60, color[2]-15), 180)
        char_draw.text((pad - bbox[0] + 1, pad - bbox[1]), ch, fill=overlay_color, font=font)

    # Микро-трансформации
    angle = random.uniform(-0.3, 0.3)
    char_img = char_img.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(0,0,0,0))
    sx = random.uniform(0.995, 1.005)
    sy = random.uniform(0.995, 1.005)
    char_img = char_img.resize((max(1, int(char_img.width*sx)), max(1, int(char_img.height*sy))), Image.BICUBIC)

    return char_img


def draw_handwritten_text(img, x, y, text, font, base_color):
    pressure = random.uniform(0.85, 1.15)
    pressure_drift = random.uniform(-0.003, 0.003)
    cur_x = x

    for ch in text:
        pressure += pressure_drift + random.uniform(-0.015, 0.015)
        pressure = max(0.6, min(1.3, pressure))

        if ch == ' ':
            pressure += random.uniform(-0.1, 0.1)
            pressure = max(0.6, min(1.3, pressure))
            bbox = font.getbbox(' ')
            cur_x += (bbox[2] - bbox[0]) + random.uniform(-1, 2)
            continue

        r = int(base_color[0] + (1.0 - pressure) * 40)
        g = int(base_color[1] + (1.0 - pressure) * 35)
        b = int(base_color[2] + (1.0 - pressure) * 25)
        char_color = (max(5, min(80, r)), max(15, min(100, g)), max(80, min(200, b)))

        char_img = _render_char_image(ch, font, char_color, pressure)
        paste_y = int(y + random.uniform(-2, 2) - char_img.height // 2 + font.size // 2)
        paste_x = int(cur_x + random.uniform(-0.5, 0.5))
        img.paste(char_img, (paste_x, paste_y), char_img)

        bbox = font.getbbox(ch)
        cur_x += (bbox[2] - bbox[0]) + random.uniform(-0.5, 1.0)

    return cur_x


# ==================== СОЗДАНИЕ СТРАНИЦЫ ====================

def create_page(header_text, lines, font_path=None):
    if font_path is None: font_path = DEFAULT_FONT_PATH
    img = make_paper_texture(IMG_W, IMG_H)
    draw = ImageDraw.Draw(img)
    draw_grid(draw, IMG_W, IMG_H)
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


# ==================== ПАГИНАЦИЯ ====================

def render_solution_pages(solution_lines, header_text="", font_path=None):
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
            pages.append(create_page(header_text, page_lines, font_path))
            page_lines, y_estimate = [], MARGIN_TOP + 60
        page_lines.append(line)
        y_estimate += needed

    if page_lines:
        pages.append(create_page(header_text, page_lines, font_path))
    return pages


# ==================== ЭФФЕКТ ФОТО НА ТЕЛЕФОН ====================

def _find_perspective_coeffs(source, target):
    matrix = []
    for s, t in zip(target, source):
        matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
        matrix.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])
    A = np.array(matrix, dtype=np.float64)
    B = np.array([s for pair in source for s in pair], dtype=np.float64)
    return tuple(np.linalg.solve(A, B).tolist())


def apply_phone_camera_effect(img, light=False):
    """Имитация фото на телефон. light=True — мягче для графиков."""
    w, h = img.size

    # Стол
    dpx = random.randint(80, 140)
    dpt = random.randint(60, 120)
    dpb = random.randint(80, 150)
    nw, nh = w + dpx*2, h + dpt + dpb
    db = (185+random.randint(-10,10), 165+random.randint(-10,10), 140+random.randint(-10,10))
    desk = Image.new('RGB', (nw, nh), db)
    da = np.array(desk, dtype=np.float32)

    phase = random.uniform(0, 6.28)
    f1, f2 = random.uniform(0.03, 0.06), random.uniform(0.1, 0.2)
    for y in range(nh):
        wave = 5*math.sin(y*f1+phase) + 2.5*math.sin(y*f2+phase*2) + 1.5*math.sin(y*0.4+phase*0.5)
        da[y,:,0] += wave*1.1; da[y,:,1] += wave*0.9; da[y,:,2] += wave*0.6

    for _ in range(random.randint(3, 7)):
        yc, bw = random.randint(0, nh), random.randint(15, 50)
        intensity = random.uniform(-12, 8)
        for dy in range(-bw, bw):
            yy = yc + dy
            if 0 <= yy < nh:
                fade = 1.0 - abs(dy)/bw
                da[yy,:,0] += intensity*fade; da[yy,:,1] += intensity*0.85*fade; da[yy,:,2] += intensity*0.6*fade

    da += np.random.normal(0, 3.5, da.shape)
    for _ in range(random.randint(1, 3)):
        sx, sy, sr = random.randint(0, nw), random.randint(0, nh), random.randint(8, 25)
        yy, xx = np.mgrid[0:nh, 0:nw]
        for c in range(3): da[:,:,c] += -15 * np.exp(-((xx-sx)**2 + (yy-sy)**2) / sr**2)

    da = np.clip(da, 0, 255)
    desk = Image.fromarray(da.astype(np.uint8))

    shadow_rgb = Image.new('RGB', (w+8, h+8), (max(db[0]-30,0), max(db[1]-30,0), max(db[2]-30,0)))
    desk.paste(shadow_rgb, (dpx+4, dpt+5))
    desk.paste(img, (dpx, dpt))
    img = desk
    w, h = img.size

    angle = random.uniform(-1.5, 1.5)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=db)

    margin = 25
    coeffs = _find_perspective_coeffs(
        [(0,0),(w,0),(w,h),(0,h)],
        [(random.randint(0,margin), random.randint(0,margin)),
         (w-random.randint(0,margin), random.randint(0,margin)),
         (w-random.randint(0,margin//2), h-random.randint(0,margin)),
         (random.randint(0,margin//2), h-random.randint(0,margin))])
    img = img.transform((w,h), Image.PERSPECTIVE, coeffs, Image.BICUBIC, fillcolor=db)

    arr = np.array(img, dtype=np.float32)

    if light:
        warm_r, warm_g, warm_b = 6, 3, -8
        vign_str, lamp_fall, shadow_str, diag_str = 0.12, 0.08, 0.05, 0.03
        overall_mult, overall_add, noise_std = 0.96, 8, 2.5
        lamp_min = 0.75
    else:
        warm_r, warm_g, warm_b = 18, 8, -22
        vign_str, lamp_fall, shadow_str, diag_str = 0.45, 0.3, 0.18, 0.10
        overall_mult, overall_add, noise_std = 0.82, 10, 5.5
        lamp_min = 0.55

    brightness = np.mean(arr, axis=2)
    warm_mask = (brightness > 100).astype(np.float32)
    arr[:,:,0] = np.clip(arr[:,:,0] + warm_mask*warm_r, 0, 255)
    arr[:,:,1] = np.clip(arr[:,:,1] + warm_mask*warm_g, 0, 255)
    arr[:,:,2] = np.clip(arr[:,:,2] + warm_mask*warm_b, 0, 255)

    yg, xg = np.mgrid[0:h, 0:w]
    cx, cy = w/2, h/2
    dist = np.sqrt((xg-cx)**2 + (yg-cy)**2)
    md = np.sqrt(cx**2 + cy**2)
    vignette = 1.0 - vign_str * (dist/md)**1.5
    for c in range(3): arr[:,:,c] *= vignette

    lx, ly = random.randint(-w//6, w//3), random.randint(-h//6, h//6)
    ld = np.sqrt((xg-lx)**2 + (yg-ly)**2)
    lm = np.sqrt(w**2 + h**2)
    ll = 1.05 * np.exp(-0.8*(ld/lm)**1.5)
    lf = 1.0 - lamp_fall*(ld/lm)**1.0
    lc = np.clip(lf + ll - 1.0, lamp_min, 1.1)
    for c in range(3): arr[:,:,c] *= lc

    scx, scy = w*random.uniform(0.65,0.9), h*random.uniform(0.7,0.95)
    sd = np.sqrt((xg-scx)**2 + (yg-scy)**2)
    sr = random.uniform(0.35, 0.55)*max(w,h)
    shadow = 1.0 - shadow_str * np.clip(1.0-sd/sr, 0, 1)**0.6
    for c in range(3): arr[:,:,c] *= shadow

    da2 = random.uniform(0.3, 0.7)
    do2 = random.uniform(0.6, 0.85)*h
    dl = da2*xg + yg
    ds = 1.0 - diag_str * np.clip((dl-do2)/(0.3*h), 0, 1)
    for c in range(3): arr[:,:,c] *= ds

    arr = arr * overall_mult + overall_add
    arr += np.random.normal(0, noise_std, arr.shape)

    arr_s = arr.copy()
    arr_s[1:,:,0] = arr[:-1,:,0]
    arr_s[:,:-1,2] = arr[:,1:,2]
    arr = arr*0.7 + arr_s*0.3

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    return img


# ==================== ГРАФИКИ РУЧКОЙ (PIL) ====================

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


def make_graph_page(font_path=None):
    """Создаёт тетрадный лист для графика/схемы"""
    if font_path is None: font_path = DEFAULT_FONT_PATH
    page = make_paper_texture(IMG_W, IMG_H)
    d = ImageDraw.Draw(page)
    draw_grid(d, IMG_W, IMG_H)
    return page


# ==================== ВЫСОКОУРОВНЕВЫЙ ИНТЕРФЕЙС ====================

class HandwrittenGenerator:
    def __init__(self, output_dir="./handwritten_output", font_path=None):
        self.output_dir = output_dir
        self.font_path = font_path or DEFAULT_FONT_PATH
        os.makedirs(output_dir, exist_ok=True)

    def render_pages(self, header_text, solution_lines, apply_camera=True):
        pages = render_solution_pages(solution_lines, header_text, self.font_path)
        if apply_camera:
            pages = [apply_phone_camera_effect(p) for p in pages]
        return pages

    def save_pages(self, pages, prefix="page"):
        paths = []
        for i, page in enumerate(pages):
            path = os.path.join(self.output_dir, f"{prefix}_{i+1}.png")
            page.save(path, 'PNG')
            paths.append(path)
        return paths

    def generate(self, header_text, solution_lines, prefix="page", apply_camera=True):
        pages = self.render_pages(header_text, solution_lines, apply_camera)
        return self.save_pages(pages, prefix)


if __name__ == '__main__':
    demo_lines = [
        ("Задача 1", "blue"),
        ("", "skip"),
        ("Дано: x + 3 = 7", "normal"),
        ("Найти: x", "normal"),
        ("", "skip"),
        ("Решение:", "blue"),
        ("x + 3 = 7", "indent"),
        ("x = 7 - 3", "indent"),
        ("x = 4", "indent"),
        ("", "skip"),
        ("Ответ: x = 4", "blue"),
    ]
    gen = HandwrittenGenerator(output_dir="/tmp/handwritten_demo")
    paths = gen.generate("Демо стр.1", demo_lines)
    for p in paths:
        print(f"Сохранено: {p}")
