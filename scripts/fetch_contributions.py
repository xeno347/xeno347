#!/usr/bin/env python3
"""Scrape the public GitHub contributions calendar - no token required.

GitHub serves the calendar as public HTML at
    https://github.com/users/<username>/contributions
(the same fragment the profile page uses). We fetch it with requests, parse
the day cells with BeautifulSoup, and write data/contributions.json with the
raw days plus derived stats.

    python scripts/fetch_contributions.py
"""
import json
import os
import re
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "xeno347")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = os.path.join("data", "contributions.json")

_COUNT_RE = re.compile(r"^\s*([\d,]+|No)\s+contribution", re.IGNORECASE)


def fetch_html() -> str:
    resp = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (profile-art fetcher)"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.text


def _tooltip_counts(soup: BeautifulSoup) -> dict:
    counts = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for")
        if not target:
            continue
        m = _COUNT_RE.match(tip.get_text(strip=True))
        if not m:
            continue
        raw = m.group(1)
        counts[target] = 0 if raw.lower() == "no" else int(raw.replace(",", ""))
    return counts


def parse(html_text: str) -> list:
    soup = BeautifulSoup(html_text, "html.parser")
    counts = _tooltip_counts(soup)
    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        date = cell.get("data-date")
        level = int(cell.get("data-level") or 0)
        cid = cell.get("id")
        # prefer explicit count from the tooltip; fall back to data-count
        count = counts.get(cid)
        if count is None:
            count = int(cell.get("data-count") or 0)
        days.append({"date": date, "level": level, "count": count})
    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list) -> dict:
    total = sum(d["count"] for d in days)

    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    # current streak: walk back from the end, allowing today (last cell) to
    # still be zero without breaking an otherwise-live streak.
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["count"] > 0:
            current += 1
        elif i == 0:
            continue
        else:
            break

    best = max(days, key=lambda d: d["count"], default=None)

    monthly: dict = {}
    for d in days:
        ym = d["date"][:7]
        monthly[ym] = monthly.get(ym, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": ({"date": best["date"], "count": best["count"]}
                     if best else None),
        "monthly": monthly,
    }


def main() -> None:
    days = parse(fetch_html())
    if not days:
        print("warning: parsed 0 contribution cells (markup change?)",
              file=sys.stderr)
    stats = compute_stats(days)
    os.makedirs("data", exist_ok=True)
    payload = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {OUT}: {len(days)} days, {stats['total']} contributions, "
          f"current streak {stats['current_streak']}d")


if __name__ == "__main__":
    main()
