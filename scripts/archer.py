"""Neon archer that hunts down your GitHub contribution graph.

Fetches the last year of contributions (GitHub GraphQL) and writes an animated,
seamlessly looping SVG in dark and light versions: an archer shoots arrows at
each contributed day, and the square bursts and lights up gold when hit.

Usage:
    GITHUB_TOKEN=... python scripts/archer.py --user Nishant1600 --out dist
    python scripts/archer.py --demo --out dist        # synthetic data, no token
Standard library only.
"""
import argparse
import json
import math
import os
import random
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape as esc

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}"""

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

THEMES = {
    "dark": dict(bg1="#070b18", bg2="#121030", border="#283044", text="#e6edf3", muted="#8b949e",
                 empty="#161b22", target="#22d3ee", neon="#22d3ee", head="#fbbf24",
                 levels=["#7a5410", "#b7791f", "#f59e0b", "#fde68a"], glow=2.4),
    "light": dict(bg1="#ffffff", bg2="#f3f4ff", border="#d0d7de", text="#1f2328", muted="#57606a",
                  empty="#ebedf0", target="#0891b2", neon="#0891b2", head="#d97706",
                  levels=["#fde68a", "#fbbf24", "#f59e0b", "#b45309"], glow=1.2),
}

CELL, STEP = 12, 15          # square size and pitch
GX, GY = 200, 52             # grid origin
MAX_ARROWS = 70              # busy years: one arrow pierces several days
FLIGHT = 0.55                # seconds an arrow is in the air
HOLD = 3.0                   # seconds to admire the finished hunt


def fetch(login: str, token: str):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "archer-contribution-hunt"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if data.get("errors"):
        raise SystemExit(f"GraphQL error: {data['errors']}")
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def demo_weeks(seed: int = 7):
    rnd = random.Random(seed)
    end = date.today()
    start = end - timedelta(days=364 + (end.weekday() + 1) % 7)
    weeks, cur, week = [], start, []
    while cur <= end:
        wd = (cur.weekday() + 1) % 7
        busy = 0.35 + 0.3 * math.sin(cur.toordinal() / 40)
        count = rnd.choice([0, 0, 1, 2, 3, 5, 8]) if rnd.random() < busy else 0
        week.append({"date": cur.isoformat(), "contributionCount": count, "weekday": wd})
        if wd == 6:
            weeks.append({"contributionDays": week})
            week = []
        cur += timedelta(days=1)
    if week:
        weeks.append({"contributionDays": week})
    total = sum(d["contributionCount"] for w in weeks for d in w["contributionDays"])
    return total, weeks


def cell_xy(col: int, row: int):
    return GX + col * STEP, GY + row * STEP


def level_of(count: int, cuts):
    for i, c in enumerate(cuts):
        if count <= c:
            return i
    return 3


def kt(t: float, total: float) -> str:
    return f"{min(max(t / total, 0.0), 1.0):.5f}"


def archer_figure(t: dict, ax: float, ay: float, string_anim: str, arm_anim: str) -> str:
    bx, by = ax + 30, ay - 6
    return f'''
  <g filter="url(#glow)" stroke="{t["neon"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <circle cx="{ax - 8}" cy="{ay - 40}" r="9"/>
    <path d="M{ax - 8} {ay - 30} L{ax - 12} {ay + 12}"/>
    <path d="M{ax - 12} {ay + 12} L{ax - 28} {ay + 48} M{ax - 12} {ay + 12} L{ax + 4} {ay + 48}"/>
    <path d="M{ax - 8} {ay - 22} L{bx} {by}"/>
    <path d="M{bx - 6} {by - 40} Q{bx + 22} {by} {bx - 6} {by + 40}" stroke-width="3"/>
    <path d="M{ax - 8} {ay - 22} L{ax + 4} {by + 2} L{bx - 6} {by}" stroke-width="2.2">{arm_anim}</path>
    <path d="M{bx - 6} {by - 40} L{bx - 6} {by} L{bx - 6} {by + 40}" stroke-width="1.2" stroke-opacity="0.9">{string_anim}</path>
    <path d="M{ax - 26} {ay - 34} L{ax - 18} {ay - 2}" stroke-width="5" stroke-opacity="0.45"/>
    <path d="M{ax - 27} {ay - 38} l-3 -7 M{ax - 23} {ay - 38} l0 -8 M{ax - 19} {ay - 37} l3 -7" stroke-width="1.6"/>
  </g>'''


def render(theme: str, login: str, total: int, weeks: list) -> str:
    t = THEMES[theme]
    ncols = len(weeks)
    width = GX + ncols * STEP + 28
    height = GY + 7 * STEP + 58
    ax, ay = 92, GY + 3 * STEP + 6
    bx, by = ax + 30, ay - 6
    nock_rest, nock_drawn = (bx - 6, by), (bx - 26, by)

    days = []
    for col, w in enumerate(weeks):
        for d in w["contributionDays"]:
            days.append((d["date"], col, d["weekday"], d["contributionCount"]))
    days.sort()
    hits = [d for d in days if d[3] > 0]
    counts = sorted(d[3] for d in hits)
    cuts = [counts[int(len(counts) * q)] for q in (0.25, 0.5, 0.75)] if counts else [1, 2, 3]

    chunk = max(1, math.ceil(len(hits) / MAX_ARROWS))
    groups = [hits[i:i + chunk] for i in range(0, len(hits), chunk)]
    n = len(groups)
    shot = min(0.45, max(0.13, 9.0 / max(n, 1)))
    start = 0.9
    launches = [start + i * shot for i in range(n)]
    hunt_end = (launches[-1] + FLIGHT + 0.4) if n else 4.0
    reset = hunt_end + HOLD
    T = reset + 0.8

    # month labels
    labels, last_month = [], None
    for col, w in enumerate(weeks):
        m = date.fromisoformat(w["contributionDays"][0]["date"]).strftime("%b")
        if m != last_month and col < ncols - 2:
            x, _ = cell_xy(col, 0)
            labels.append(f'<text x="{x}" y="{GY - 8}" font-size="11" fill="{t["muted"]}">{m}</text>')
            last_month = m

    # grid: base squares + gold overlays that light up on impact
    hit_time = {}
    for gi, g in enumerate(groups):
        h = launches[gi] + FLIGHT
        for j, d in enumerate(reversed(g)):
            hit_time[d[0]] = h + j * 0.035
    cells, overlays = [], []
    for ds, col, row, count in days:
        x, y = cell_xy(col, row)
        if count == 0:
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{t["empty"]}"/>')
            continue
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{t["empty"]}" '
                     f'stroke="{t["target"]}" stroke-opacity="0.55" stroke-width="1"/>')
        h = hit_time[ds]
        color = t["levels"][level_of(count, cuts)]
        overlays.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{kt(h, T)};{kt(reset, T)}" '
            f'calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite"/></rect>')

    # arrows + impact bursts
    arrows, bursts = [], []
    tip0 = (bx + 6, by)
    for gi, g in enumerate(groups):
        _, col, row, _ = g[-1]
        x, y = cell_xy(col, row)
        cx, cy = x + CELL / 2, y + CELL / 2
        dx = cx - tip0[0]
        mx, my = (tip0[0] + cx) / 2, min(tip0[1], cy) - (18 + 0.11 * dx)
        path = f"M{tip0[0]} {tip0[1]} Q{mx:.1f} {my:.1f} {cx:.1f} {cy:.1f}"
        l, h = launches[gi], launches[gi] + FLIGHT
        arrows.append(f'''<g opacity="0">
      <path d="M-24 0 H-3" stroke="{t["neon"]}" stroke-width="2"/>
      <path d="M0 0 L-8 -3.6 L-8 3.6 Z" fill="{t["head"]}" stroke="none"/>
      <path d="M-24 0 l-5 -4 M-24 0 l-5 4 M-20 0 l-5 -4 M-20 0 l-5 4" stroke="{t["neon"]}" stroke-width="1.4"/>
      <animateMotion path="{path}" rotate="auto" keyPoints="0;0;1;1" keyTimes="0;{kt(l, T)};{kt(h, T)};1" calcMode="linear" dur="{T:.2f}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;1;0" keyTimes="0;{kt(l, T)};{kt(h, T)}" calcMode="discrete" dur="{T:.2f}s" repeatCount="indefinite"/>
    </g>''')
        e = h + 0.45
        bursts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="0" fill="none" stroke="{t["head"]}" stroke-width="2" opacity="0">'
            f'<animate attributeName="r" values="0;0;16;16" keyTimes="0;{kt(h, T)};{kt(e, T)};1" dur="{T:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0;0.95;0;0" keyTimes="0;{kt(h, T)};{kt(h + 0.02, T)};{kt(e, T)};1" dur="{T:.2f}s" repeatCount="indefinite"/>'
            f'</circle>')

    # bowstring + drawing arm, synced to every shot
    def string_d(nx):
        return f"M{bx - 6} {by - 40} L{nx} {by} L{bx - 6} {by + 40}"

    def arm_d(nx):
        return f"M{ax - 8} {ay - 22} L{(ax - 8 + nx) / 2 + 2:.1f} {by + 6} L{nx} {by}"

    times, s_vals, a_vals = [0.0], [string_d(nock_rest[0])], [arm_d(nock_rest[0])]
    draw = min(0.32, shot * 0.7)
    for l in launches:
        for tt, nx in ((l - draw, nock_rest[0]), (l - 0.01, nock_drawn[0]), (l, nock_rest[0])):
            if tt > times[-1]:
                times.append(tt)
                s_vals.append(string_d(nx))
                a_vals.append(arm_d(nx))
    times.append(T)
    s_vals.append(string_d(nock_rest[0]))
    a_vals.append(arm_d(nock_rest[0]))
    key = ";".join(kt(tt, T) for tt in times)
    string_anim = f'<animate attributeName="d" values="{";".join(s_vals)}" keyTimes="{key}" dur="{T:.2f}s" repeatCount="indefinite"/>'
    arm_anim = f'<animate attributeName="d" values="{";".join(a_vals)}" keyTimes="{key}" dur="{T:.2f}s" repeatCount="indefinite"/>'

    caption = (f"{total} contribution{'s' if total != 1 else ''} hunted in the last year"
               if hits else "Hunting season starts soon")
    legend_x = width - 28 - 4 * STEP - 70
    legend = "".join(
        f'<rect x="{legend_x + 34 + i * STEP}" y="{height - 30}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(t["levels"]))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{SANS}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="{t["glow"]}" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="18" fill="url(#bg)" stroke="{t["border"]}"/>
  <text x="28" y="30" font-size="12" font-weight="800" fill="{t["neon"]}" letter-spacing="2.5">CONTRIBUTION HUNT</text>
  <text x="{width - 28}" y="30" font-size="12" fill="{t["muted"]}" text-anchor="end">@{esc(login)}</text>
  {"".join(labels)}
  <line x1="40" y1="{ay + 49}" x2="{GX - 30}" y2="{ay + 49}" stroke="{t["neon"]}" stroke-opacity="0.35"/>
  {archer_figure(t, ax, ay, string_anim, arm_anim)}
  <g>{"".join(cells)}</g>
  <g>{"".join(overlays)}</g>
  <g filter="url(#glow)" fill="none" stroke-linecap="round">{"".join(arrows)}</g>
  <g>{"".join(bursts)}</g>
  <text x="28" y="{height - 20}" font-size="14" font-weight="700" fill="{t["text"]}">{esc(caption)}</text>
  <text x="{legend_x}" y="{height - 20}" font-size="11" fill="{t["muted"]}">Less</text>
  {legend}
  <text x="{legend_x + 34 + 4 * STEP + 4}" y="{height - 20}" font-size="11" fill="{t["muted"]}">More</text>
</svg>
'''


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "Nishant1600"))
    ap.add_argument("--out", default="dist")
    ap.add_argument("--demo", action="store_true", help="use synthetic data instead of the API")
    args = ap.parse_args()

    if args.demo:
        total, weeks = demo_weeks()
    else:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            raise SystemExit("Set GITHUB_TOKEN (or use --demo).")
        total, weeks = fetch(args.user, token)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        svg = render(theme, args.user, total, weeks)
        (out / f"archer-{theme}.svg").write_text(svg, encoding="utf-8")
        print(f"archer-{theme}.svg  {len(svg) / 1024:.0f} KB  ({total} contributions)")


if __name__ == "__main__":
    main()
