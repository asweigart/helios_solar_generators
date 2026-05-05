#!/usr/bin/env python3
"""Generate About/Preview.png for the Helios Solar Generators mod.

Layout: 640x360, dark sky gradient with a sun in the upper-left, the four
tier panels lined up across the bottom, and the title "HELIOS" with subtitle
"SOLAR GENERATORS" above them. Reuses build_panel() from the texture script.

Run from the repo root:
    python3 scripts/gen_helios_preview.py
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from gen_helios_textures import build_panel  # noqa: E402

OUT = os.path.join(REPO_ROOT, "heliossolargenerators", "About", "Preview.png")
W, H = 640, 360


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        d.line([(0, y), (w, y)], fill=(r, g, b, 255))
    return img


def draw_sun(img, cx, cy, r):
    d = ImageDraw.Draw(img)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i, alpha in [(r * 3, 18), (int(r * 2.2), 32), (int(r * 1.6), 60)]:
        gd.ellipse((cx - i, cy - i, cx + i, cy + i), fill=(255, 220, 120, alpha))
    img.alpha_composite(glow)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 230, 140, 255))
    d.ellipse(
        (cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4),
        fill=(255, 245, 180, 255),
    )


def load_font(size, bold=True):
    paths = [
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_text_with_shadow(img, xy, text, font, fill, shadow=(0, 0, 0, 180), off=3):
    d = ImageDraw.Draw(img)
    d.text((xy[0] + off, xy[1] + off), text, font=font, fill=shadow)
    d.text(xy, text, font=font, fill=fill)


def main():
    bg = vertical_gradient((W, H), (18, 38, 78), (60, 90, 140))
    draw_sun(bg, 70, 70, 32)

    d = ImageDraw.Draw(bg)
    d.rectangle((0, H - 70, W, H), fill=(46, 54, 50, 255))
    d.line((0, H - 70, W, H - 70), fill=(70, 78, 70, 255), width=2)

    panel_size = 120
    spacing = 18
    total_w = panel_size * 4 + spacing * 3
    start_x = (W - total_w) // 2
    panel_y = H - 70 - panel_size + 18

    for i, tier in enumerate(range(1, 5)):
        panel = build_panel(panel_size, tier)
        shadow = Image.new("RGBA", (panel_size + 16, panel_size + 16), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle(
            (8, 12, panel_size + 8, panel_size + 12),
            radius=6,
            fill=(0, 0, 0, 110),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(4))
        sx = start_x + i * (panel_size + spacing) - 8
        sy = panel_y - 4
        bg.alpha_composite(shadow, (sx, sy))
        bg.alpha_composite(panel, (start_x + i * (panel_size + spacing), panel_y))

    title_font = load_font(86, bold=True)
    sub_font = load_font(28, bold=True)

    title = "HELIOS"
    sub = "SOLAR GENERATORS"

    draw = ImageDraw.Draw(bg)
    title_w = draw.textlength(title, font=title_font)
    sub_w = draw.textlength(sub, font=sub_font)

    title_xy = ((W - title_w) // 2, 24)
    sub_xy = ((W - sub_w) // 2, 24 + 86 + 4)

    draw_text_with_shadow(
        bg, title_xy, title, title_font,
        fill=(255, 220, 110, 255), shadow=(0, 0, 0, 200), off=4,
    )
    draw_text_with_shadow(
        bg, sub_xy, sub, sub_font,
        fill=(220, 230, 240, 255), shadow=(0, 0, 0, 180), off=2,
    )

    bg.convert("RGB").save(OUT, "PNG")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
