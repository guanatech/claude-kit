#!/usr/bin/env python3
"""Добавить недостающие математические глифы в lorenco.ttf.

В исходном lorenco.ttf нет глифов для:
  · (U+00B7)  · (U+22C5)  − (U+2212)  ² (U+00B2)  ³ (U+00B3)
Скрипт идемпотентный — берёт шрифт из бэкапа `lorenco_original.ttf`
(если есть) либо из текущего lorenco.ttf и пересохраняет поверх.

Источники:
  ·  — нарисован с нуля (маленький круг), потому что `period` в этом
       рукописном шрифте имеет хвостик и выглядит как запятая.
  −  — алиас на `hyphen`.
  ²,³ — `two`, `three`, уменьшенные до 0.62 и поднятые на надстрочную позицию.
"""
import os
import shutil
from copy import deepcopy

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import RecordingPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(HERE, "..", "fonts")
FONT_PATH = os.path.normpath(os.path.join(FONTS_DIR, "lorenco.ttf"))
BACKUP   = os.path.normpath(os.path.join(FONTS_DIR, "lorenco_original.ttf"))

# Если есть бэкап — патчим из него, иначе делаем бэкап перед патчем.
if os.path.exists(BACKUP):
    src_path = BACKUP
else:
    shutil.copy(FONT_PATH, BACKUP)
    src_path = BACKUP
    print(f"  → создан бэкап: {BACKUP}")

font = TTFont(src_path)
glyf = font['glyf']
hmtx = font['hmtx']


def transform_glyph(src_name, new_name, scale=1.0, dy=0, dx=0, advance_scale=None):
    src = glyf[src_name]
    new = deepcopy(src)
    if new.numberOfContours > 0:
        coords = new.coordinates
        for i in range(len(coords)):
            x, y = coords[i]
            coords[i] = (int(x * scale + dx), int(y * scale + dy))
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        new.xMin, new.xMax = min(xs), max(xs)
        new.yMin, new.yMax = min(ys), max(ys)
    glyf[new_name] = new
    adv, lsb = hmtx[src_name]
    if advance_scale is None:
        advance_scale = scale
    hmtx[new_name] = (max(1, int(adv * advance_scale)), int(lsb * scale + dx))


def make_dot_glyph(cx, cy, r, advance):
    """Создать глиф-кружок: 8 точек (4 on-curve + 4 off-curve), квадратичная аппроксимация."""
    pen = TTGlyphPen(None)
    # квадратичная аппроксимация окружности через 4 сегмента
    pen.moveTo((cx + r, cy))
    pen.qCurveTo((cx + r, cy + r), (cx, cy + r))
    pen.qCurveTo((cx - r, cy + r), (cx - r, cy))
    pen.qCurveTo((cx - r, cy - r), (cx, cy - r))
    pen.qCurveTo((cx + r, cy - r), (cx + r, cy))
    pen.closePath()
    return pen.glyph()


# ---------- 1. periodcentered (·): свежий маленький круг ----------
# unitsPerEm = 1000; x-height ≈ 440, cap height ≈ 683.
# Точку умножения ставим чуть ниже math-midline, чтобы она была
# на уровне центра цифр.
DOT_CX = 80
DOT_CY = 180       # настройте по вкусу; 220 = строго в центре x-height, 180 — заметно ниже
DOT_R  = 55        # радиус
DOT_ADV = 220      # ширина места под точку с боковыми отступами

dot = make_dot_glyph(DOT_CX, DOT_CY, DOT_R, DOT_ADV)
glyf['periodcentered'] = dot
hmtx['periodcentered'] = (DOT_ADV, 0)

# ---------- 2. supercripts ² ³ ----------
transform_glyph('two',   'twosuperior',   scale=0.62, dy=340, advance_scale=0.62)
transform_glyph('three', 'threesuperior', scale=0.62, dy=340, advance_scale=0.62)

# ---------- 3. cmap ----------
new_mappings = {
    0x00B7: 'periodcentered',  # ·
    0x22C5: 'periodcentered',  # ⋅ (dot operator) — то же изображение
    0x2212: 'hyphen',           # − (minus sign, алиас на hyphen)
    0x00B2: 'twosuperior',      # ²
    0x00B3: 'threesuperior',    # ³
}
for table in font['cmap'].tables:
    if table.isUnicode():
        for cp, gname in new_mappings.items():
            table.cmap[cp] = gname

# ---------- 4. glyph order, maxp ----------
glyph_order = font.getGlyphOrder()
for name in ('periodcentered', 'twosuperior', 'threesuperior'):
    if name not in glyph_order:
        glyph_order.append(name)
font.setGlyphOrder(glyph_order)
font['maxp'].numGlyphs = len(glyph_order)

font.save(FONT_PATH)
print(f"  → сохранено: {FONT_PATH}")
print(f"  numGlyphs: {font['maxp'].numGlyphs}")
