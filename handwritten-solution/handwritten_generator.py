"""Совместимый фасад: импортирует публичный API из lib/.

Существующий код вида
    from handwritten_generator import HandwrittenGenerator
продолжает работать."""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from lib import *  # noqa: F401,F403,E402
from lib import __all__  # noqa: E402


if __name__ == '__main__':
    from lib import HandwrittenGenerator
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
    for p in gen.generate("Демо стр.1", demo_lines):
        print(f"Сохранено: {p}")
