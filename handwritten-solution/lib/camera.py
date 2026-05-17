"""Эффект фотографии на телефон: стол, перспектива, свет, шум."""
import math
import random
import numpy as np
from PIL import Image, ImageFilter

from .presets import BACKGROUND_PRESETS, DEFAULT_PRESET


def _find_perspective_coeffs(source, target):
    matrix = []
    for s, t in zip(target, source):
        matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
        matrix.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])
    A = np.array(matrix, dtype=np.float64)
    B = np.array([s for pair in source for s in pair], dtype=np.float64)
    return tuple(np.linalg.solve(A, B).tolist())


def apply_phone_camera_effect(img, preset=DEFAULT_PRESET, light=False):
    """Имитация фото на телефон.

    preset — ключ из BACKGROUND_PRESETS (white_desk, wood, dark_wood, gray, beige, graph).
    light=True — алиас для пресета 'graph' (мягче, для графиков)."""
    if light:
        preset = "graph"
    if preset not in BACKGROUND_PRESETS:
        raise ValueError(f"Unknown preset: {preset!r}. Available: {list(BACKGROUND_PRESETS)}")
    cfg = BACKGROUND_PRESETS[preset]

    w, h = img.size

    dpx = random.randint(80, 140)
    dpt = random.randint(60, 120)
    dpb = random.randint(80, 150)
    nw, nh = w + dpx*2, h + dpt + dpb
    dv = cfg["desk_variation"]
    base = cfg["desk_color"]
    db = (max(0, min(255, base[0]+random.randint(-dv, dv))),
          max(0, min(255, base[1]+random.randint(-dv, dv))),
          max(0, min(255, base[2]+random.randint(-dv, dv))))
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

    warm_r, warm_g, warm_b = cfg["warm"]
    vign_str = cfg["vign_str"]
    lamp_fall = cfg["lamp_fall"]
    shadow_str = cfg["shadow_str"]
    diag_str = cfg["diag_str"]
    overall_mult = cfg["overall_mult"]
    overall_add = cfg["overall_add"]
    noise_std = cfg["noise_std"]
    lamp_min = cfg["lamp_min"]

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
