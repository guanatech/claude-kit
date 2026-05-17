"""Пресеты:
- BACKGROUND_PRESETS — стол + свет (для apply_phone_camera_effect)
- PAPER_PRESETS      — расчертка листа (клетка, красное поле)
"""

BACKGROUND_PRESETS = {
    "white_desk": {
        "desk_color": (235, 232, 228),
        "desk_variation": 8,
        "warm": (3, 2, -1),
        "vign_str": 0.30, "lamp_fall": 0.18, "shadow_str": 0.10, "diag_str": 0.05,
        "overall_mult": 0.96, "overall_add": 12, "noise_std": 4.0,
        "lamp_min": 0.78,
    },
    "wood": {
        "desk_color": (185, 165, 140),
        "desk_variation": 10,
        "warm": (8, 4, -10),
        "vign_str": 0.40, "lamp_fall": 0.25, "shadow_str": 0.15, "diag_str": 0.08,
        "overall_mult": 0.90, "overall_add": 10, "noise_std": 5.0,
        "lamp_min": 0.65,
    },
    "dark_wood": {
        "desk_color": (110, 85, 65),
        "desk_variation": 8,
        "warm": (6, 3, -8),
        "vign_str": 0.42, "lamp_fall": 0.26, "shadow_str": 0.16, "diag_str": 0.09,
        "overall_mult": 0.88, "overall_add": 8, "noise_std": 5.0,
        "lamp_min": 0.60,
    },
    "gray": {
        "desk_color": (160, 160, 162),
        "desk_variation": 6,
        "warm": (1, 1, 0),
        "vign_str": 0.32, "lamp_fall": 0.20, "shadow_str": 0.12, "diag_str": 0.06,
        "overall_mult": 0.95, "overall_add": 10, "noise_std": 4.0,
        "lamp_min": 0.75,
    },
    "beige": {
        "desk_color": (220, 210, 195),
        "desk_variation": 8,
        "warm": (5, 3, -4),
        "vign_str": 0.34, "lamp_fall": 0.22, "shadow_str": 0.12, "diag_str": 0.06,
        "overall_mult": 0.94, "overall_add": 11, "noise_std": 4.0,
        "lamp_min": 0.72,
    },
    "graph": {
        "desk_color": (230, 226, 220),
        "desk_variation": 6,
        "warm": (2, 1, -2),
        "vign_str": 0.12, "lamp_fall": 0.08, "shadow_str": 0.05, "diag_str": 0.03,
        "overall_mult": 0.97, "overall_add": 10, "noise_std": 2.5,
        "lamp_min": 0.82,
    },
}

DEFAULT_PRESET = "white_desk"


# ==================== ПРЕСЕТЫ БУМАГИ ====================

PAPER_PRESETS = {
    "notebook": {
        "grid": True, "red_margin": True,
        "base_color": (250, 248, 240), "edge_yellowing": True,
    },
    "grid": {
        "grid": True, "red_margin": False,
        "base_color": (250, 248, 240), "edge_yellowing": True,
    },
    "white_grid": {                                    # белая бумага в клетку, без полей и желтизны
        "grid": True, "red_margin": False,
        "base_color": (253, 253, 253), "edge_yellowing": False,
    },
    "white_plain": {                                   # совсем чистый белый лист
        "grid": False, "red_margin": False,
        "base_color": (253, 253, 253), "edge_yellowing": False,
    },
}

DEFAULT_PAPER = "notebook"
