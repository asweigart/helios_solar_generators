#!/usr/bin/env python3
"""Generate Helios solar generator textures.

Style imitates vanilla RimWorld's solar generator (dark navy cells in a
silver frame) but with a 3x3 cell arrangement appropriate for a 2x2 footprint
rather than a shrunken vanilla panel. Yellow circles in the lower-right
indicate tier (1, 2 stacked, 3 in a triangle, 4 in a 2x2).

Run from the repo root:
    python3 scripts/gen_helios_textures.py
"""

from PIL import Image, ImageDraw
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "heliossolargenerators", "Textures", "Things", "Building", "Power")

# Vanilla-matching palette
FRAME_LIGHT = (170, 172, 174, 255)   # outer silver
FRAME_MID   = (138, 140, 142, 255)   # frame face
FRAME_DARK  = (78, 80, 84, 255)      # inset shadow
PANEL_BG    = (10, 16, 30, 255)      # vanilla-style dark backing
CELL_BASE   = (56, 88, 109, 255)      # vanilla dark navy cell
CELL_HI     = (76, 108, 129, 255)     # cell highlight
CELL_LO     = (36, 68, 89, 255)      # cell shadow
GRID_LINE   = (8, 12, 22, 255)       # busbar/grid line
SCREW       = (60, 62, 66, 255)      # frame bolts
YELLOW_OUT  = (210, 160, 20, 255)    # circle outline
YELLOW_IN   = (255, 214, 64, 255)    # circle fill
YELLOW_HI   = (255, 240, 170, 255)   # circle highlight


def draw_cell(draw: ImageDraw.ImageDraw, box):
    """Draw a single photovoltaic cell with grid busbars and edge shading."""
    x0, y0, x1, y1 = box
    draw.rectangle((x0, y0, x1, y1), fill=CELL_BASE)
    w = x1 - x0
    h = y1 - y0
    draw.rectangle((x0, y0, x1, y0 + max(1, h // 14)), fill=CELL_HI)
    draw.rectangle((x0, y0, x0 + max(1, w // 14), y1), fill=CELL_HI)
    draw.rectangle((x0, y1 - max(1, h // 14), x1, y1), fill=CELL_LO)
    draw.rectangle((x1 - max(1, w // 14), y0, x1, y1), fill=CELL_LO)
    bb1 = y0 + h // 3
    bb2 = y0 + (2 * h) // 3
    draw.line((x0 + 2, bb1, x1 - 2, bb1), fill=GRID_LINE, width=1)
    draw.line((x0 + 2, bb2, x1 - 2, bb2), fill=GRID_LINE, width=1)
    cx = (x0 + x1) // 2
    draw.line((cx, y0 + 2, cx, y1 - 2), fill=GRID_LINE, width=1)


def draw_yellow_circle(img: Image.Image, cx, cy, r):
    """Draw a glossy yellow LED-style circle onto img."""
    draw = ImageDraw.Draw(img)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YELLOW_OUT)
    inset = max(1, r // 4)
    draw.ellipse(
        (cx - r + inset, cy - r + inset, cx + r - inset, cy + r - inset),
        fill=YELLOW_IN,
    )
    hr = max(1, r // 3)
    hx = cx - r // 3
    hy = cy - r // 3
    draw.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=YELLOW_HI)


def tier_circle_positions(tier: int, anchor_x: int, anchor_y: int, step: int):
    """Slot positions in a 2x2 grid anchored at (anchor_x, anchor_y).

    Tier 1: bottom-right only.
    Tier 2: right column (top-right + bottom-right), stacked vertically.
    Tier 3: top-right + bottom-left + bottom-right (triangle).
    Tier 4: all four slots filled.
    """
    slots = {
        (0, 0): (anchor_x + step // 2, anchor_y + step // 2),
        (0, 1): (anchor_x + step + step // 2, anchor_y + step // 2),
        (1, 0): (anchor_x + step // 2, anchor_y + step + step // 2),
        (1, 1): (anchor_x + step + step // 2, anchor_y + step + step // 2),
    }
    keys_by_tier = {
        1: [(1, 1)],
        2: [(0, 1), (1, 1)],
        3: [(0, 1), (1, 0), (1, 1)],
        4: [(0, 0), (0, 1), (1, 0), (1, 1)],
    }
    return [slots[k] for k in keys_by_tier.get(tier, [])]


def build_panel(size: int, tier: int) -> Image.Image:
    """Build a 2x2 solar panel texture at given pixel size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = max(2, size // 32)
    frame_thick = max(3, size // 18)

    draw.rectangle(
        (margin, margin, size - margin - 1, size - margin - 1),
        fill=FRAME_LIGHT,
    )
    inner1 = margin + max(1, frame_thick // 3)
    draw.rectangle(
        (inner1, inner1, size - inner1 - 1, size - inner1 - 1),
        fill=FRAME_MID,
    )
    inner2 = margin + frame_thick
    draw.rectangle(
        (inner2, inner2, size - inner2 - 1, size - inner2 - 1),
        fill=FRAME_DARK,
    )
    panel_pad = max(1, frame_thick // 5)
    panel_box = (
        inner2 + panel_pad,
        inner2 + panel_pad,
        size - inner2 - panel_pad - 1,
        size - inner2 - panel_pad - 1,
    )
    draw.rectangle(panel_box, fill=PANEL_BG)

    # 3x3 cell grid — intentionally different from vanilla's 4x4 so this
    # doesn't look like a shrunken copy.
    px0, py0, px1, py1 = panel_box
    pw = px1 - px0
    ph = py1 - py0
    cells = 3
    gap = max(1, size // 64)
    cell_w = (pw - gap * (cells + 1)) // cells
    cell_h = (ph - gap * (cells + 1)) // cells
    for r in range(cells):
        for c in range(cells):
            cx0 = px0 + gap + c * (cell_w + gap)
            cy0 = py0 + gap + r * (cell_h + gap)
            cx1 = cx0 + cell_w
            cy1 = cy0 + cell_h
            draw_cell(draw, (cx0, cy0, cx1, cy1))

    # Corner bolts
    screw_r = max(1, size // 64)
    screw_inset = margin + frame_thick // 2
    for sx, sy in [
        (screw_inset, screw_inset),
        (size - screw_inset - 1, screw_inset),
        (screw_inset, size - screw_inset - 1),
        (size - screw_inset - 1, size - screw_inset - 1),
    ]:
        draw.ellipse(
            (sx - screw_r, sy - screw_r, sx + screw_r, sy + screw_r),
            fill=SCREW,
        )

    # Yellow tier indicator circles in lower-right of the panel area
    circle_r = max(3, size // 22)
    step = circle_r * 2 + max(2, size // 64)
    pad = max(2, size // 40)
    anchor_x = px1 - 2 * step - pad
    anchor_y = py1 - 2 * step - pad
    for cx, cy in tier_circle_positions(tier, anchor_x, anchor_y, step):
        draw_yellow_circle(img, cx, cy, circle_r)

    return img


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for tier in range(1, 5):
        panel = build_panel(256, tier)
        panel.save(os.path.join(OUT_DIR, f"HeliosSolarL{tier}.png"))
        icon = build_panel(128, tier)
        icon.save(os.path.join(OUT_DIR, f"HeliosSolarL{tier}_MenuIcon.png"))
        print(f"Wrote tier {tier}")


if __name__ == "__main__":
    main()
