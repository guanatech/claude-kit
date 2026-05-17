"""Высокоуровневый интерфейс генератора."""
import os

from .camera import apply_phone_camera_effect
from .config import DEFAULT_FONT_PATH
from .pages import render_solution_pages
from .presets import DEFAULT_PRESET, DEFAULT_PAPER


class HandwrittenGenerator:
    def __init__(self, output_dir="./handwritten_output", font_path=None):
        self.output_dir = output_dir
        self.font_path = font_path or DEFAULT_FONT_PATH
        os.makedirs(output_dir, exist_ok=True)

    def render_pages(self, header_text, solution_lines, apply_camera=True,
                     preset=DEFAULT_PRESET, paper=DEFAULT_PAPER):
        pages = render_solution_pages(solution_lines, header_text, self.font_path, paper=paper)
        if apply_camera:
            pages = [apply_phone_camera_effect(p, preset=preset) for p in pages]
        return pages

    def save_pages(self, pages, prefix="page"):
        paths = []
        for i, page in enumerate(pages):
            path = os.path.join(self.output_dir, f"{prefix}_{i+1}.png")
            page.save(path, 'PNG')
            paths.append(path)
        return paths

    def generate(self, header_text, solution_lines, prefix="page", apply_camera=True,
                 preset=DEFAULT_PRESET, paper=DEFAULT_PAPER):
        pages = self.render_pages(header_text, solution_lines, apply_camera,
                                  preset=preset, paper=paper)
        return self.save_pages(pages, prefix)
