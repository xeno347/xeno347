#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG.

A title bar, then colored key/value rows. Keep the *story* here - the
numbers live in the contribution graph. Each line fades and slides in on a
short stagger so the panel looks like it is printing next to the portrait.

    python scripts/make_info_card.py            # animated
    STATIC=1 python scripts/make_info_card.py   # frozen frame for Quick Look
"""
import html
import os

OUT = "info-card.svg"

# --- edit your story here --------------------------------------------------
NAME = "xeno347@github"
ROWS = [
    ("Now",        "Building AI + web products"),
    ("Prev",       "Full-stack apps & landing pages"),
    ("Stack",      "TypeScript / React / Node / Python"),
    ("Highlights", "notelab.ai / Zenithra / FarmConnect"),
]
# ---------------------------------------------------------------------------

KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
BG = "#0d1117"
BAR = "#161b22"
STATIC = os.environ.get("STATIC") == "1"

W = 490
PAD = 20
LINE_H = 30
TITLE_H = 36
KEY_X = PAD
VAL_X = PAD + 118
H = TITLE_H + PAD + LINE_H * len(ROWS) + PAD - 6


def main():
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" '
        f"font-family=\"'SF Mono','Cascadia Code',Consolas,monospace\">"
    ]

    if not STATIC:
        delays = "".join(
            f".r{i}{{animation-delay:{0.15 + i * 0.13:.2f}s;}}"
            for i in range(len(ROWS))
        )
        p.append(
            "<style>"
            ".row{opacity:0;animation:slidein .45s ease forwards;}"
            + delays
            + "@keyframes slidein{from{opacity:0;transform:translateX(-10px);}"
            "to{opacity:1;transform:translateX(0);}}"
            "</style>"
        )

    p.append(f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>')
    p.append(f'<path d="M0 10 a10 10 0 0 1 10 -10 h{W - 20} a10 10 0 0 1 10 10 '
             f'v{TITLE_H - 10} h-{W} z" fill="{BAR}"/>')
    for j, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{20 + j * 18}" cy="{TITLE_H / 2}" r="6" fill="{c}"/>')
    p.append(
        f'<text x="{W / 2}" y="{TITLE_H / 2 + 4}" text-anchor="middle" '
        f'font-size="12" fill="#8b949e">{html.escape(NAME)} — neofetch</text>'
    )

    y0 = TITLE_H + PAD + 12
    for i, (k, v) in enumerate(ROWS):
        y = y0 + i * LINE_H
        cls = "" if STATIC else f' class="row r{i}"'
        p.append(f"<g{cls}>")
        p.append(
            f'<text x="{KEY_X}" y="{y}" font-size="14" fill="{KEY_COLOR}" '
            f'font-weight="bold">{html.escape(k)}</text>'
        )
        p.append(
            f'<text x="{VAL_X}" y="{y}" font-size="14" fill="{VAL_COLOR}">'
            f"{html.escape(v)}</text>"
        )
        p.append("</g>")

    p.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(p))
    print(f"wrote {OUT}{' (static)' if STATIC else ''}")


if __name__ == "__main__":
    main()
