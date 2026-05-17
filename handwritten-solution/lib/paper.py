"""Текстура бумаги, клетка и красное поле."""
import random
import numpy as np
from PIL import Image

from .config import CELL_SIZE, MARGIN_LEFT
from .presets import PAPER_PRESETS, DEFAULT_PAPER


def make_paper_texture(w, h, paper=DEFAULT_PAPER):
    if paper not in PAPER_PRESETS:
        raise ValueError(f"Unknown paper preset: {paper!r}. Available: {list(PAPER_PRESETS)}")
    cfg = PAPER_PRESETS[paper]
    base_r, base_g, base_b = cfg.get("base_color", (250, 248, 240))
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

    if cfg.get("edge_yellowing", True):
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


def draw_grid(draw, w, h, paper=DEFAULT_PAPER):
    """Рисует расчертку листа согласно выбранному пресету бумаги.

    paper — ключ из PAPER_PRESETS: 'notebook' (клетка + красное поле),
    'grid' (только клетка)."""
    if paper not in PAPER_PRESETS:
        raise ValueError(f"Unknown paper preset: {paper!r}. Available: {list(PAPER_PRESETS)}")
    cfg = PAPER_PRESETS[paper]

    if cfg.get("grid"):
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

    if cfg.get("red_margin"):
        margin_x = MARGIN_LEFT - 15
        for sy in range(0, h, 30):
            j1, j2 = random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4)
            rc = (215+random.randint(-5,5), 75+random.randint(-5,5), 75)
            draw.line([(margin_x+j1, sy), (margin_x+j2, min(sy+30, h))], fill=rc, width=2)
            draw.line([(margin_x-4+j1, sy), (margin_x-4+j2, min(sy+30, h))], fill=rc, width=1)
