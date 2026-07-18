#!/usr/bin/env python3
"""Render data/contributions.json as the classic 53-week x 7-day calendar.

Rounded, colored boxes on a GitHub-ish green ramp. The grid reveals once with
a diagonal, line-after-line slide-down (CSS keyframes that play on load, then
freeze - no looping glow), plus a Less->More legend and a stats footer.

    python scripts/render_heatmap_svg.py   # writes contrib-heatmap.svg
"""
import json
import os
from datetime import datetime

IN = os.path.join("data", "contributions.json")
OUT = "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 is a neon top end)

CELL = 13
GAP = 3
PAD = 20
TOP = 40
BG = "#0d1117"
STEP = CELL + GAP


def build_weeks(days: list) -> list:
    """Group day dicts into week-columns; index 0 = Sunday."""
    weeks: list = []
    col: list = []
    for d in days:
        wd = (datetime.strptime(d["date"], "%Y-%m-%d").weekday() + 1) % 7  # Sun=0
        if wd == 0 and col:
            weeks.append(col)
            col = []
        if not weeks and not col and wd != 0:
            col = [None] * wd  # pad the very first partial week
        col.append(d)
    if col:
        weeks.append(col)
    return weeks


def main() -> None:
    with open(IN) as f:
        data = json.load(f)
    days = data["days"]
    stats = data.get("stats", {})

    weeks = build_weeks(days)
    n_cols = len(weeks)
    width = PAD * 2 + n_cols * STEP
    height = TOP + 7 * STEP + 46

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" '
        f"font-family=\"'SF Mono',Consolas,monospace\">",
        "<style>"
        ".c{opacity:0;animation:pop .4s ease forwards;}"
        "@keyframes pop{from{opacity:0;transform:translateY(-6px);}"
        "to{opacity:1;transform:translateY(0);}}"
        "</style>",
        f'<rect width="{width}" height="{height}" rx="8" fill="{BG}"/>',
    ]

    total = stats.get("total", sum(d["count"] for d in days))
    p.append(
        f'<text x="{PAD}" y="26" font-size="14" fill="#c9d1d9">'
        f"{total:,} contributions in the last year</text>"
    )

    for ci, col in enumerate(weeks):
        for ri, d in enumerate(col):
            if d is None:
                continue
            x = PAD + ci * STEP
            y = TOP + ri * STEP
            color = PALETTE[min(int(d["level"]), len(PALETTE) - 1)]
            delay = (ci + ri) * 0.012  # diagonal wave
            p.append(
                f'<rect class="c" x="{x}" y="{y}" width="{CELL}" '
                f'height="{CELL}" rx="3" fill="{color}" '
                f'style="animation-delay:{delay:.3f}s"/>'
            )

    ly = TOP + 7 * STEP + 16
    legend_w = len(PALETTE) * STEP
    lx = width - PAD - legend_w - 40
    p.append(
        f'<text x="{lx - 34}" y="{ly + CELL - 3}" font-size="11" '
        f'fill="#8b949e">Less</text>'
    )
    for i, c in enumerate(PALETTE):
        p.append(
            f'<rect x="{lx + i * STEP}" y="{ly}" width="{CELL}" '
            f'height="{CELL}" rx="3" fill="{c}"/>'
        )
    p.append(
        f'<text x="{lx + legend_w + 4}" y="{ly + CELL - 3}" font-size="11" '
        f'fill="#8b949e">More</text>'
    )

    cs = stats.get("current_streak", 0)
    ls = stats.get("longest_streak", 0)
    best = stats.get("best_day") or {}
    footer = f"Current streak: {cs}d · Longest: {ls}d"
    if best.get("count"):
        footer += f" · Best day: {best['count']} on {best['date']}"
    p.append(
        f'<text x="{PAD}" y="{ly + CELL - 3}" font-size="11" '
        f'fill="#8b949e">{footer}</text>'
    )

    p.append("</svg>")
    with open(OUT, "w") as f:
        f.write("\n".join(p))
    print(f"wrote {OUT}: {n_cols} weeks")


if __name__ == "__main__":
    main()
