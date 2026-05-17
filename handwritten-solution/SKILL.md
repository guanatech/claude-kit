---
name: handwritten-solution
description: Use when user asks to create a handwritten solution, рукописное решение, написать от руки, имитация рукописного текста, сфотографированное решение, тетрадный лист с решением. Generates realistic notebook-paper images with pen handwriting and phone camera effects.
---

# Handwritten Solution Generator

## Overview

Generates realistic images of handwritten solutions on notebook paper (A5, grid/checkered), with blue ballpoint pen text and phone camera photo effects. Output: PNG images + optional DOCX/PDF assembly.

## When to Use

- User asks for "рукописное решение", "написать от руки", "имитация почерка"
- User wants a solution that looks like a photo of a handwritten notebook page
- Any homework, контрольная, задание that needs to look hand-written

## Architecture

1. **Paper texture** — A5 grid paper with cellulose grain, color variation, yellowed edges
2. **Grid lines** — blue checkered lines with micro-jitter
3. **Red margin** — left margin line, slightly wobbly
4. **Handwritten text** — per-character rendering with pressure simulation
5. **Graphs/diagrams** — drawn with PIL directly on notebook paper using pen color (NOT matplotlib)
6. **Phone camera effect** — desk texture, shadows, vignetting, noise, chromatic aberration

## Font

Lives in `fonts/`. Primary: `fonts/lorenco_font.ttf`. Fallbacks: `fonts/abram_font.ttf`, `~/Library/Fonts/BadScript-Regular.ttf`.

## Source layout

Code is split into `lib/` for clarity; `handwritten_generator.py` re-exports the public API for backward compat.

- `lib/config.py` — image dims, margins, font sizes, `PEN` colors, `DEFAULT_FONT_PATH`
- `lib/presets.py` — `BACKGROUND_PRESETS`, `DEFAULT_PRESET`
- `lib/paper.py` — paper texture + grid
- `lib/text.py` — handwritten char rendering
- `lib/pages.py` — `create_page`, `render_solution_pages`
- `lib/camera.py` — `apply_phone_camera_effect`
- `lib/graphs.py` — pen primitives, `make_graph_page`
- `lib/generator.py` — `HandwrittenGenerator` class

## Background presets

`apply_phone_camera_effect(img, preset=...)` and `HandwrittenGenerator.generate(..., preset=...)` accept:

| Preset       | Desk          | Light          |
|--------------|---------------|----------------|
| `white_desk` | off-white     | neutral/daylight (default) |
| `wood`       | warm wood     | mildly warm    |
| `dark_wood`  | dark wood     | mildly warm    |
| `gray`       | neutral gray  | white          |
| `beige`      | light beige   | slightly warm  |
| `graph`      | off-white     | very soft (for graphs, alias of `light=True`) |

Default is `white_desk` — white LED / daylight rather than incandescent. Override per-call: `gen.generate(header, lines, preset="wood")`.

## Paper presets

`HandwrittenGenerator.generate(..., paper=...)` and `draw_grid(..., paper=...)` accept:

| Paper      | Grid | Red margin |
|------------|------|------------|
| `notebook` | yes  | yes (default) |
| `grid`     | yes  | no         |

Example: `gen.generate(header, lines, paper="grid", preset="white_desk")`.

## Line Format

```python
lines = [
    ("Задача 1", "blue"),        # accent color
    ("", "skip"),                  # empty line
    ("Формула: x = 2", "normal"), # regular pen
    ("подставим", "indent"),       # indented
    ("Ответ: x = 2", "blue"),    # accent for answers
    ("мелкий текст", "small"),    # smaller font
]
```

## Drawing Graphs

Use PIL helper functions from `handwritten_generator.py` — NOT matplotlib:

```python
from handwritten_generator import make_graph_page, _pen_arrow, _pen_line, _pen_circle, _pen_text, _pen_rect, apply_phone_camera_effect, PEN

page = make_graph_page()
draw = ImageDraw.Draw(page)
font = ImageFont.truetype(FONT_PATH, 42)

# Axes with arrows
_pen_arrow(draw, x1, y1, x2, y2)
# Lines with hand-jitter
_pen_line(draw, [(x1,y1), (x2,y2)])
# Circles (filled/open for step functions)
_pen_circle(draw, cx, cy, r, PEN, filled=True)
# Rectangles (for circuit diagrams)
_pen_rect(draw, x, y, w, h)
# Labels in handwriting font
_pen_text(page, x, y, "F(x)", font, PEN)

# Apply camera effect and save
page = apply_phone_camera_effect(page)
page.save("graph.png")
```

## Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `FONT_SIZE` | 40 | Main text |
| `FONT_SIZE_SMALL` | 34 | Small text |
| `HEADER_FONT_SIZE` | 30 | Header |
| Graph labels | 42 (title), 34 (axis) | Graph text |
| `PEN` | (15, 30, 120) | Pen color |
| `IMG_W x IMG_H` | 1748 x 2480 | A5 at ~300dpi |
| `CELL_SIZE` | 30 | Grid cell (~5mm) |

## Dependencies

```
pip install Pillow numpy python-docx
```

For PDF: `brew install --cask libreoffice` (soffice --headless --convert-to pdf).

## Workflow

1. Solve the task, structure as line tuples
2. Generate pages with `HandwrittenGenerator`
3. For graphs — draw with PIL on `make_graph_page()`, apply camera effect
4. Assemble DOCX with python-docx, convert to PDF with LibreOffice
5. Graphs inserted as-is (camera effect already baked in)
