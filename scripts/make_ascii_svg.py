#!/usr/bin/env python3
"""Convert source-prepped.png into a self-typing monochrome ASCII-art SVG.

Design choices that keep it clean instead of noisy:
  * Monochrome - one light-gray fill. Per-character rainbow coloring is
    exactly what makes most ASCII portraits look like static.
  * High contrast - a busy background washes out to the space glyph, so
    only the subject prints.

Each row is wrapped in a horizontal clip that wipes left-to-right (a small
block "cursor" rides the wipe edge), staggered top to bottom. The whole
portrait prints once and freezes - no looping. It is SMIL inside the SVG,
so GitHub plays it.

    python scripts/make_ascii_svg.py   # writes avi-ascii.svg
"""
import html

from PIL import Image

SRC = "source-prepped.png"
OUT = "avi-ascii.svg"

COLS = 100
RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
#        ^ leading space clears the background to nothing

FILL = "#b9c0c7"          # one light-gray fill color
BG = "#0d1117"            # github dark canvas
CHAR_W = 6.0
LINE_H = 11.0
FONT_SIZE = 11
STAGGER = 0.022           # seconds between row wipes
WIPE_DUR = 0.42


def load_grid():
    img = Image.open(SRC).convert("L")
    w, h = img.size
    # monospace glyphs are ~2x taller than wide -> squash vertically
    rows = max(1, int(COLS * (h / w) * 0.5))
    img = img.resize((COLS, rows))
    px = img.load()
    grid = []
    for y in range(rows):
        line = []
        for x in range(COLS):
            v = px[x, y]
            idx = int((255 - v) / 255 * (len(RAMP) - 1) + 0.5)
            line.append(RAMP[idx])
        grid.append("".join(line).rstrip() or " ")
    return grid


def main():
    grid = load_grid()
    rows = len(grid)
    width = int(COLS * CHAR_W)
    height = int(rows * LINE_H) + 8

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f"font-family=\"'SF Mono','Cascadia Code',Consolas,monospace\">",
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        f"<style>text{{font-size:{FONT_SIZE}px;fill:{FILL};}}</style>",
    ]

    for i, line in enumerate(grid):
        begin = f"{i * STAGGER:.3f}s"
        baseline = (i + 1) * LINE_H
        top = baseline - LINE_H
        clip_id = f"c{i}"
        p.append(
            f'<clipPath id="{clip_id}"><rect x="0" y="{top:.1f}" width="0" '
            f'height="{LINE_H:.1f}">'
            f'<animate attributeName="width" from="0" to="{width}" '
            f'begin="{begin}" dur="{WIPE_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        safe = html.escape(line)
        p.append(
            f'<text x="0" y="{baseline:.1f}" clip-path="url(#{clip_id})" '
            f'xml:space="preserve">{safe}</text>'
        )
        # cursor block riding the wipe edge
        p.append(
            f'<rect x="0" y="{top + 1.5:.1f}" width="{CHAR_W:.1f}" '
            f'height="{LINE_H - 2:.1f}" fill="{FILL}" opacity="0">'
            f'<animate attributeName="x" from="0" to="{width - CHAR_W:.1f}" '
            f'begin="{begin}" dur="{WIPE_DUR}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;0.85;0.85;0" '
            f'keyTimes="0;0.05;0.9;1" begin="{begin}" dur="{WIPE_DUR}s" '
            f'fill="freeze"/></rect>'
        )

    p.append("</svg>")
    with open(OUT, "w") as f:
        f.write("\n".join(p))
    print(f"wrote {OUT} ({COLS}x{rows})")


if __name__ == "__main__":
    main()
