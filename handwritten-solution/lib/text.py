"""Рукописный текст с имитацией нажима ручки."""
import random
from PIL import Image, ImageDraw


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
