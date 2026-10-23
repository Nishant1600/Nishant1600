"""A cowboy that hunts down your GitHub contribution graph with a revolver.

Fetches the last year of contributions (GitHub GraphQL) and writes one animated,
seamlessly looping SVG in the profile's "General Store" paper style: a gunslinger
on a desert ridge swings his arm to each contributed day, fires, the bullet
crosses the board, the target is knocked out in a puff of dust and the square
turns to brass, while a hit counter and progress bar fill. Then it resets.

Usage:
    GITHUB_TOKEN=... python scripts/cowboy.py --user Nishant1600 --out dist
    python scripts/cowboy.py --demo --out dist        # synthetic data, no token
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

SERIF = "'Old Standard TT',Georgia,'Times New Roman',serif"

T = dict(
    paper=["#f6eed8", "#ecdfbd", "#e8c98f"], border="#1f1a14", text="#1f1a14", muted="#5a4d3e",
    panel="#ffffff", panel_op="0.42", empty="#dccfa8", target="#a1201a", red="#a1201a",
    body="#24160d", hat="#2c1b10", gold="#b8860b", brass="#d9a441", fire="#e0762b", dust="#9a7442",
    levels=["#e2b26e", "#c97a3a", "#a1201a", "#5a0f0b"],
    mesa=["#d9b87c", "#c49a5c"], mesa_op=["0.75", "0.95"], ground="#b9894c", sun="#e8883a")

CELL, STEP = 12, 15          # square size and pitch
GX, GY = 232, 74             # grid origin
MAX_SHOTS = 80               # busy years: one bullet drops several days
FLIGHT = 0.26                # seconds a bullet is in the air
HOLD = 3.4                   # seconds to admire the finished hunt
SPARKS = 5                   # spark particles per impact
PX, PY = 108, 118            # shoulder pivot of the shooting arm
MUZZLE = 54                  # pivot-to-muzzle distance


def fetch(login: str, token: str):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "cowboy-contribution-hunt"})
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


class Clock:
    """Turns seconds into keyTimes for one shared, looping timeline."""

    def __init__(self, total: float):
        self.total = total
        self.dur = f'dur="{total:.2f}s" repeatCount="indefinite"'

    def k(self, *times: float) -> str:
        return ";".join(f"{min(max(t / self.total, 0.0), 1.0):.5f}" for t in times)


def scenery(width: int, height: int, rnd: random.Random) -> str:
    out = [f'''
  <circle cx="62" cy="54" r="62" fill="url(#halo)"/>
  <circle cx="62" cy="54" r="20" fill="{T["sun"]}"/>''']
    for li, (base, amp, step) in enumerate([(height - 62, 36, 90), (height - 36, 22, 64)]):
        pts, x = [f"M0 {height}", f"L0 {base}"], 0
        while x < width + step:
            x += step * rnd.uniform(0.35, 0.6)
            pts.append(f"L{x:.0f} {base - amp * rnd.uniform(0.7, 1):.0f}")
            x += step * rnd.uniform(0.25, 0.45)
            pts.append(f"L{x:.0f} {base - amp * rnd.uniform(0.7, 1):.0f}")
            x += step * rnd.uniform(0.3, 0.6)
            pts.append(f"L{x:.0f} {base + rnd.uniform(-2, 6):.0f}")
        pts.append(f"L{width} {height} Z")
        out.append(f'<path d="{" ".join(pts)}" fill="{T["mesa"][li]}" opacity="{T["mesa_op"][li]}"/>')
    # a few circling birds
    for i, (bx, by, dur) in enumerate([(150, 40, 26), (520, 30, 34), (800, 48, 30)]):
        out.append(f'<path class="bird" d="M0 0 q4 -5 8 0 q4 -5 8 0" fill="none" stroke="{T["body"]}" '
                   f'stroke-width="1.4" stroke-linecap="round" style="animation-duration:{dur}s;animation-delay:-{i * 7}s" '
                   f'transform="translate({bx} {by})"/>')
    return "".join(out)


def cowboy(ground: float, arm_anim: str, flash_anim: str) -> str:
    b, h = T["body"], T["hat"]
    return f'''
  <path d="M26 {ground + 46} L38 {ground + 6} Q70 {ground - 8} 118 {ground - 4} Q170 {ground - 2} 190 {ground + 8} L204 {ground + 46} Z" fill="{T["ground"]}"/>
  <path d="M38 {ground + 6} Q70 {ground - 8} 118 {ground - 4} Q170 {ground - 2} 190 {ground + 8}" fill="none" stroke="{T["border"]}" stroke-opacity="0.55" stroke-width="1.4"/>
  <g stroke="{b}" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <path d="M100 150 L93 172 L88 {ground}" stroke-width="8"/>
    <path d="M108 150 L117 172 L124 {ground}" stroke-width="8"/>
    <path d="M82 {ground} H96 M120 {ground} H136" stroke-width="5.5"/>
    <path d="M104 118 L104 152" stroke-width="15"/>
    <path d="M101 120 L98 142" stroke-width="5.2"/>
  </g>
  <rect x="96" y="146" width="17" height="4" fill="{T["gold"]}"/>
  <path d="M96 148 L90 164 L97 166 L102 150 Z" fill="#4a2c14"/>
  <path d="M97 104 L111 104 L104 116 Z" fill="{T["red"]}"/>
  <circle cx="106" cy="98" r="8.6" fill="{b}"/>
  <path d="M88 92 Q106 98 126 92 Q124 86 106 85 Q90 86 88 92 Z" fill="{h}"/>
  <path d="M95 90 Q95 72 106 72 Q117 72 117 90 Z" fill="{h}"/>
  <path d="M95 86 H117" stroke="{T["gold"]}" stroke-width="2.4"/>
  <circle cx="86" cy="{ground - 1}" r="1.8" fill="{T["gold"]}"/><circle cx="138" cy="{ground - 1}" r="1.8" fill="{T["gold"]}"/>
  <g>
    {arm_anim}
    <path d="M{PX} {PY} L{PX + 29} {PY}" stroke="{b}" stroke-width="5.6" stroke-linecap="round"/>
    <circle cx="{PX + 31}" cy="{PY}" r="3.4" fill="{b}"/>
    <path d="M{PX + 30} {PY - 1} l-2 11 l6 1.5 l3 -10 z" fill="#4a2c14"/>
    <rect x="{PX + 28}" y="{PY - 5.5}" width="12" height="7" rx="1.6" fill="#3a3a3a" stroke="{b}" stroke-width="0.8"/>
    <circle cx="{PX + 35}" cy="{PY - 2}" r="4.6" fill="#555" stroke="{b}" stroke-width="0.8"/>
    <rect x="{PX + 38}" y="{PY - 5}" width="{MUZZLE - 38}" height="3.6" fill="#3a3a3a" stroke="{b}" stroke-width="0.6"/>
    <path d="M{PX + 29} {PY - 5.5} l-3 -4 l5 1.5 z" fill="#3a3a3a"/>
    <g opacity="0">
      {flash_anim}
      <path d="M{PX + MUZZLE} {PY - 3} l9 -7 l-2 6 l11 -2 l-8 5 l9 4 l-12 -1 l3 6 l-9 -6 z" fill="{T["fire"]}"/>
      <circle cx="{PX + MUZZLE + 6}" cy="{PY - 3}" r="4" fill="#fff3c4"/>
    </g>
  </g>'''


def render(login: str, total: int, weeks: list) -> str:
    rnd = random.Random(1600)
    ncols = len(weeks)
    width = GX + ncols * STEP + 26
    height = 268
    ground = 196

    days = []
    for col, w in enumerate(weeks):
        for d in w["contributionDays"]:
            days.append((d["date"], col, d["weekday"], d["contributionCount"]))
    days.sort()
    hits = [d for d in days if d[3] > 0]
    counts = sorted(d[3] for d in hits)
    cuts = [counts[int(len(counts) * q)] for q in (0.25, 0.5, 0.75)] if counts else [1, 2, 3]

    chunk = max(1, math.ceil(len(hits) / MAX_SHOTS))
    groups = [hits[i:i + chunk] for i in range(0, len(hits), chunk)]
    n = len(groups)
    shot = min(0.45, max(0.22, 10.0 / max(n, 1)))
    start = 1.2
    launches = [start + i * shot for i in range(n)]
    impacts = [l + FLIGHT for l in launches]
    hunt_end = (impacts[-1] + 0.5) if n else 5.0
    reset = hunt_end + HOLD
    clk = Clock(reset + 0.9)
    D = clk.dur

    # month labels
    labels, last_month = [], None
    for col, w in enumerate(weeks):
        m = date.fromisoformat(w["contributionDays"][0]["date"]).strftime("%b")
        if m != last_month and col < ncols - 2:
            x, _ = cell_xy(col, 0)
            labels.append(f'<text x="{x}" y="{GY - 9}" font-size="11" fill="{T["muted"]}">{m}</text>')
            last_month = m

    # grid
    hit_time = {}
    for gi, g in enumerate(groups):
        for j, d in enumerate(reversed(g)):
            hit_time[d[0]] = impacts[gi] + j * 0.04
    cells, targets, overlays = [], [], []
    for ds, col, row, count in days:
        x, y = cell_xy(col, row)
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{T["empty"]}"/>')
        if count == 0:
            continue
        cx, cy = x + CELL / 2, y + CELL / 2
        h = hit_time[ds]
        targets.append(
            f'<g opacity="1"><circle cx="{cx}" cy="{cy}" r="3.8" fill="none" stroke="{T["target"]}" stroke-width="1.3"/>'
            f'<circle cx="{cx}" cy="{cy}" r="1.3" fill="{T["target"]}"/>'
            f'<animate attributeName="opacity" values="1;0;1" keyTimes="{clk.k(0, h, reset)}" calcMode="discrete" {D}/></g>')
        overlays.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{T["levels"][level_of(count, cuts)]}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="{clk.k(0, h, reset)}" calcMode="discrete" {D}/></rect>')

    # per-shot geometry: arm angle, muzzle position, bullet path
    shots = []
    for gi, g in enumerate(groups):
        _, col, row, _ = g[-1]
        x, y = cell_xy(col, row)
        cx, cy = x + CELL / 2, y + CELL / 2
        ang = math.degrees(math.atan2(cy - PY, cx - PX))
        mx = PX + MUZZLE * math.cos(math.radians(ang))
        my = PY + MUZZLE * math.sin(math.radians(ang))
        shots.append((ang, mx, my, cx, cy))

    # bullets, dust puffs and sparks
    bullets, puffs = [], []
    for gi, (ang, mx, my, cx, cy) in enumerate(shots):
        l, h = launches[gi], impacts[gi]
        path = f"M{mx:.1f} {my:.1f} L{cx:.1f} {cy:.1f}"
        bullets.append(f'''<g opacity="0">
      <path d="M-20 0 L-3 0" stroke="url(#trail)" stroke-width="2.4"/>
      <circle cx="0" cy="0" r="2.3" fill="{T["brass"]}" stroke="{T["body"]}" stroke-width="0.6"/>
      <animateMotion path="{path}" rotate="auto" keyPoints="0;0;1;1" keyTimes="{clk.k(0, l, h, clk.total)}" calcMode="linear" {D}/>
      <animate attributeName="opacity" values="0;1;0" keyTimes="{clk.k(0, l, h)}" calcMode="discrete" {D}/>
    </g>''')
        e = h + 0.5
        sparks = []
        for si in range(SPARKS):
            a = 2 * math.pi * si / SPARKS + rnd.uniform(-0.4, 0.4)
            dist = rnd.uniform(10, 18)
            sx, sy = math.cos(a) * dist, math.sin(a) * dist
            sparks.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.6" fill="{T["fire"]}" opacity="0">'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{sx:.1f} {sy:.1f};{sx:.1f} {sy:.1f}" keyTimes="{clk.k(0, h, e, clk.total)}" {D}/>'
                f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="{clk.k(0, h, h + 0.02, e, clk.total)}" {D}/></circle>')
        puffs.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8" fill="{T["brass"]}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.9;0;0" keyTimes="{clk.k(0, h, h + 0.02, h + 0.22, clk.total)}" {D}/></circle>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="0" fill="none" stroke="{T["dust"]}" stroke-width="2.2" opacity="0">'
            f'<animate attributeName="r" values="0;0;17;17" keyTimes="{clk.k(0, h, e, clk.total)}" {D}/>'
            f'<animate attributeName="opacity" values="0;0;0.8;0;0" keyTimes="{clk.k(0, h, h + 0.02, e, clk.total)}" {D}/></circle>'
            + "".join(sparks))

    # shooting arm: swing to each target, kick back on the shot, settle
    times, a_vals = [0.0], [f"0 {PX} {PY}"]
    for gi, (ang, *_rest) in enumerate(shots):
        l = launches[gi]
        for tt, aa in ((l - 0.12, ang), (l, ang - 7), (l + 0.1, ang)):
            if tt > times[-1]:
                times.append(tt)
                a_vals.append(f"{aa:.2f} {PX} {PY}")
    times.append(clk.total - 0.4)
    a_vals.append(f"0 {PX} {PY}")
    times.append(clk.total)
    a_vals.append(f"0 {PX} {PY}")
    arm_anim = (f'<animateTransform attributeName="transform" type="rotate" values="{";".join(a_vals)}" '
                f'keyTimes="{clk.k(*times)}" {D}/>')

    # muzzle flash on every launch
    f_times, f_vals = [0.0], ["0"]
    for l in launches:
        for tt, vv in ((l - 0.001, "0"), (l, "1"), (l + 0.07, "0")):
            if tt > f_times[-1]:
                f_times.append(tt)
                f_vals.append(vv)
    f_times.append(clk.total)
    f_vals.append("0")
    flash_anim = (f'<animate attributeName="opacity" values="{";".join(f_vals)}" '
                  f'keyTimes="{clk.k(*f_times)}" calcMode="discrete" {D}/>')

    # hit counter (cumulative contributions) and progress bar
    grid_right = GX + ncols * STEP - (STEP - CELL)
    counter, running = [], 0
    shown_until = [impacts[i + 1] if i + 1 < n else reset for i in range(n)]
    counter.append(f'<text x="{width - 28}" y="35" font-size="23" font-weight="700" fill="{T["red"]}" text-anchor="end">0'
                   f'<animate attributeName="opacity" values="1;0;1" keyTimes="{clk.k(0, impacts[0] if n else reset, reset)}" calcMode="discrete" {D}/></text>')
    for gi, g in enumerate(groups):
        running += sum(d[3] for d in g)
        counter.append(
            f'<text x="{width - 28}" y="35" font-size="23" font-weight="700" fill="{T["red"]}" text-anchor="end" opacity="0">{running}'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="{clk.k(0, impacts[gi], shown_until[gi])}" calcMode="discrete" {D}/></text>')
    bar_w = grid_right - GX
    first, last = (impacts[0], impacts[-1]) if n else (start, start + 1)
    progress = (f'<rect x="{GX}" y="{GY + 7 * STEP + 12}" width="{bar_w}" height="5" rx="2.5" fill="{T["empty"]}"/>'
                f'<rect x="{GX}" y="{GY + 7 * STEP + 12}" width="0" height="5" rx="2.5" fill="url(#bar)">'
                f'<animate attributeName="width" values="0;0;{bar_w};{bar_w};0" keyTimes="{clk.k(0, first, last, reset, clk.total)}" {D}/></rect>')

    caption = (f"{total} contribution{'s' if total != 1 else ''} hunted down in the last year"
               if hits else "Hunting season starts soon")
    legend_x = grid_right - 4 * STEP - 62
    legend = "".join(
        f'<rect x="{legend_x + 32 + i * STEP}" y="{height - 31}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
        for i, c in enumerate(T["levels"]))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{SERIF}">
  <title>A cowboy shooting down each square of Nishant Sharma's GitHub contribution graph</title>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{T["paper"][0]}"/><stop offset="0.55" stop-color="{T["paper"][1]}"/><stop offset="1" stop-color="{T["paper"][2]}"/>
    </linearGradient>
    <radialGradient id="halo"><stop offset="0" stop-color="{T["sun"]}" stop-opacity="0.35"/><stop offset="1" stop-color="{T["sun"]}" stop-opacity="0"/></radialGradient>
    <linearGradient id="trail" gradientUnits="userSpaceOnUse" x1="-20" y1="0" x2="-3" y2="0">
      <stop offset="0" stop-color="{T["fire"]}" stop-opacity="0"/><stop offset="1" stop-color="{T["brass"]}"/>
    </linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T["brass"]}"/><stop offset="1" stop-color="{T["red"]}"/></linearGradient>
    <clipPath id="frame"><rect width="{width}" height="{height}" rx="10"/></clipPath>
  </defs>
  <style>
    @keyframes fly {{ from {{ transform: translate(-40px, 0) }} to {{ transform: translate({width + 40}px, 6px) }} }}
    .bird {{ animation: fly 30s linear infinite }}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{width}" height="{height}" fill="url(#sky)"/>
    {scenery(width, height, rnd)}
  </g>
  <rect x="1.5" y="1.5" width="{width - 3}" height="{height - 3}" rx="9" fill="none" stroke="{T["border"]}" stroke-width="3"/>
  <rect x="8" y="8" width="{width - 16}" height="{height - 16}" rx="5" fill="none" stroke="{T["border"]}" stroke-opacity="0.45"/>

  <text x="{GX - 4}" y="35" font-size="14" font-weight="700" fill="{T["red"]}" letter-spacing="4">THE CONTRIBUTION HUNT</text>
  <text x="{width - 96}" y="33" font-size="10.5" font-weight="700" fill="{T["muted"]}" text-anchor="end" letter-spacing="2">@{esc(login).upper()} · HITS</text>
  {"".join(counter)}

  <rect x="{GX - 12}" y="{GY - 24}" width="{grid_right - GX + 24}" height="{7 * STEP + 44}" rx="6" fill="{T["panel"]}" fill-opacity="{T["panel_op"]}" stroke="{T["border"]}" stroke-opacity="0.5"/>
  {"".join(labels)}
  <g>{"".join(cells)}</g>
  <g>{"".join(targets)}</g>
  <g>{"".join(overlays)}</g>
  {progress}

  {cowboy(ground, arm_anim, flash_anim)}

  <g fill="none" stroke-linecap="round">{"".join(bullets)}</g>
  <g>{"".join(puffs)}</g>

  <text x="{GX - 4}" y="{height - 21}" font-size="14" font-weight="700" fill="{T["text"]}">{esc(caption)}</text>
  <text x="{legend_x}" y="{height - 21}" font-size="11" fill="{T["muted"]}">Less</text>
  {legend}
  <text x="{legend_x + 32 + 4 * STEP + 4}" y="{height - 21}" font-size="11" fill="{T["muted"]}">More</text>
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
    svg = render(args.user, total, weeks)
    (out / "cowboy.svg").write_text(svg, encoding="utf-8")
    print(f"cowboy.svg  {len(svg) / 1024:.0f} KB  ({total} contributions)")


if __name__ == "__main__":
    main()
