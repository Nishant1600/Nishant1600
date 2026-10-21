"""Cinematic archer that hunts down your GitHub contribution graph.

Fetches the last year of contributions (GitHub GraphQL) and writes an animated,
seamlessly looping SVG in dark (night) and light (dawn) versions: a hooded
archer on a cliff fires flaming arrows at each contributed day, the square
explodes in sparks and lights up gold, and a hit counter and progress bar fill.

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
    "dark": dict(
        sky=["#050816", "#0b1030", "#1d1245"], border="#283044", text="#e6edf3", muted="#8b949e",
        panel="#ffffff", panel_op="0.035", empty="#161b22", target="#22d3ee", rim="#22d3ee",
        body="#060a18", bow="#67e8f9", string="#e0f2fe", gold="#fbbf24", fire="#fb923c",
        levels=["#8a5a0c", "#c2850f", "#f59e0b", "#fde68a"],
        mountains=["#2a1f5c", "#160f38"], mountain_op=["0.55", "0.9"], rock="#0d1328",
        night=True),
    "light": dict(
        sky=["#dbeafe", "#eef2ff", "#fde7c7"], border="#d0d7de", text="#1f2328", muted="#57606a",
        panel="#ffffff", panel_op="0.55", empty="#e5e7eb", target="#0891b2", rim="#0891b2",
        body="#1e293b", bow="#0e7490", string="#334155", gold="#d97706", fire="#ea580c",
        levels=["#fcd34d", "#f59e0b", "#d97706", "#92400e"],
        mountains=["#a5b4fc", "#818cf8"], mountain_op=["0.35", "0.45"], rock="#475569",
        night=False),
}

CELL, STEP = 12, 15          # square size and pitch
GX, GY = 232, 74             # grid origin
MAX_ARROWS = 70              # busy years: one arrow pierces several days
FLIGHT = 0.6                 # seconds an arrow is in the air
HOLD = 3.2                   # seconds to admire the finished hunt
SPARKS = 5                   # spark particles per impact


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


class Clock:
    """Turns seconds into keyTimes for one shared, looping timeline."""

    def __init__(self, total: float):
        self.total = total
        self.dur = f'dur="{total:.2f}s" repeatCount="indefinite"'

    def k(self, *times: float) -> str:
        return ";".join(f"{min(max(t / self.total, 0.0), 1.0):.5f}" for t in times)


def sky_layer(t: dict, width: int, height: int, rnd: random.Random) -> str:
    out = []
    if t["night"]:
        for _ in range(90):
            x, y = rnd.uniform(6, width - 6), rnd.uniform(6, height * 0.62)
            r = rnd.choice([0.6, 0.8, 0.8, 1.1, 1.4])
            cls = rnd.choice(["s1", "s2", "s3"])
            out.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#ffffff" '
                       f'style="animation-delay:-{rnd.uniform(0, 6):.2f}s"/>')
        # moon with halo and craters
        out.append('''
  <circle cx="62" cy="50" r="64" fill="url(#halo)"/>
  <circle cx="62" cy="50" r="19" fill="#fef3c7"/>
  <circle cx="69" cy="45" r="19" fill="url(#moonShade)"/>
  <circle cx="55" cy="47" r="3.2" fill="#f5deb3" opacity="0.7"/>
  <circle cx="60" cy="58" r="2.2" fill="#f5deb3" opacity="0.6"/>
  <line class="shoot" x1="0" y1="0" x2="46" y2="16" stroke="url(#shootGrad)" stroke-width="1.6" stroke-linecap="round"/>''')
    else:
        rays = "".join(
            f'<line x1="0" y1="-30" x2="0" y2="-40" transform="rotate({a})" stroke="#f59e0b" stroke-width="2.2" stroke-linecap="round" opacity="0.7"/>'
            for a in range(0, 360, 30))
        out.append(f'''
  <circle cx="62" cy="52" r="70" fill="url(#halo)"/>
  <g transform="translate(62 52)"><g>{rays}<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="40s" repeatCount="indefinite"/></g></g>
  <circle cx="62" cy="52" r="20" fill="#fbbf24"/>''')
    return "".join(out)


def mountains(t: dict, width: int, height: int, rnd: random.Random) -> str:
    layers = []
    for li, (base, amp, step) in enumerate([(height - 64, 34, 70), (height - 34, 22, 52)]):
        pts, x = [f"M0 {height}", f"L0 {base}"], 0
        while x < width + step:
            x += step * rnd.uniform(0.7, 1.3)
            pts.append(f"L{x:.0f} {base - rnd.uniform(0.3, 1) * amp:.0f}")
            x += step * rnd.uniform(0.5, 1.0)
            pts.append(f"L{x:.0f} {base + rnd.uniform(-4, 8):.0f}")
        pts.append(f"L{width} {height} Z")
        layers.append(f'<path d="{" ".join(pts)}" fill="{t["mountains"][li]}" opacity="{t["mountain_op"][li]}"/>')
    return "".join(layers)


def archer(t: dict, ground: float, string_anim: str, arm_anim: str, cape_anim: str) -> str:
    b = t["body"]
    return f'''
  <path d="M28 {ground + 46} L36 {ground + 4} Q60 {ground - 10} 112 {ground - 6} Q170 {ground - 4} 192 {ground + 8} L204 {ground + 46} Z" fill="{t["rock"]}"/>
  <path d="M36 {ground + 4} Q60 {ground - 10} 112 {ground - 6} Q170 {ground - 4} 192 {ground + 8}" fill="none" stroke="{t["rim"]}" stroke-opacity="0.35"/>
  <g filter="url(#rim)">
    <path fill="{b}" d="M102 112 C84 124 72 152 62 186 L86 180 C90 156 96 136 108 120 Z">{cape_anim}</path>
    <path d="M90 100 L99 97 L108 138 L99 141 Z" fill="{b}"/>
    <g stroke="{b}" stroke-linecap="round" stroke-linejoin="round" fill="none">
      <path d="M103 114 L101 152" stroke-width="13"/>
      <path d="M100 150 L90 172 L80 {ground}" stroke-width="8"/>
      <path d="M104 150 L121 171 L131 {ground}" stroke-width="8"/>
      <path d="M76 {ground} H88 M128 {ground} H140" stroke-width="5"/>
      <path d="M107 116 L150 124" stroke-width="6"/>
      <path stroke-width="5.5" d="M101 116 L124 128 L146 124">{arm_anim}</path>
    </g>
    <circle cx="105" cy="98" r="9.5" fill="{b}"/>
    <path d="M94 102 Q93 82 107 82 Q118 84 116 97 L111 92 Q104 89 99 104 Z" fill="{b}"/>
  </g>
  <g stroke-linecap="round">
    <path d="M91 98 l-4 -10 M95 97 l-1 -11 M99 96 l3 -10" stroke="{t["gold"]}" stroke-width="1.8"/>
    <path d="M146 82 Q138 86 145 94 Q170 124 145 154 Q138 162 146 166" fill="none" stroke="{t["bow"]}" stroke-width="3.4" filter="url(#glow)"/>
    <rect x="147" y="118" width="6" height="12" rx="2" fill="{t["gold"]}"/>
    <path d="M146 82 L146 124 L146 166" fill="none" stroke="{t["string"]}" stroke-width="1.1" opacity="0.9">{string_anim}</path>
  </g>'''


def render(theme: str, login: str, total: int, weeks: list) -> str:
    t = THEMES[theme]
    rnd = random.Random(1600)
    ncols = len(weeks)
    width = GX + ncols * STEP + 26
    height = 268
    ground = 196
    nock_rest, nock_drawn, by = 146, 118, 124
    tip0 = (160, by)

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
    shot = min(0.5, max(0.14, 10.0 / max(n, 1)))
    start = 1.0
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
            labels.append(f'<text x="{x}" y="{GY - 9}" font-size="11" fill="{t["muted"]}">{m}</text>')
            last_month = m

    # grid
    hit_time = {}
    for gi, g in enumerate(groups):
        for j, d in enumerate(reversed(g)):
            hit_time[d[0]] = impacts[gi] + j * 0.04
    cells, targets, overlays = [], [], []
    for ds, col, row, count in days:
        x, y = cell_xy(col, row)
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{t["empty"]}"/>')
        if count == 0:
            continue
        cx, cy = x + CELL / 2, y + CELL / 2
        h = hit_time[ds]
        targets.append(
            f'<g opacity="1"><circle cx="{cx}" cy="{cy}" r="3.6" fill="none" stroke="{t["target"]}" stroke-width="1.2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="1.2" fill="{t["target"]}"/>'
            f'<animate attributeName="opacity" values="1;0;1" keyTimes="{clk.k(0, h, reset)}" calcMode="discrete" {D}/></g>')
        overlays.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{t["levels"][level_of(count, cuts)]}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="{clk.k(0, h, reset)}" calcMode="discrete" {D}/></rect>')

    # flaming arrows, impact flashes and sparks
    arrows, impacts_svg = [], []
    for gi, g in enumerate(groups):
        _, col, row, _ = g[-1]
        x, y = cell_xy(col, row)
        cx, cy = x + CELL / 2, y + CELL / 2
        dx = cx - tip0[0]
        mx, my = (tip0[0] + cx) / 2, min(tip0[1], cy) - (26 + 0.13 * dx)
        path = f"M{tip0[0]} {tip0[1]} Q{mx:.1f} {my:.1f} {cx:.1f} {cy:.1f}"
        l, h = launches[gi], impacts[gi]
        arrows.append(f'''<g opacity="0">
      <path d="M-74 0 L-24 0" stroke="url(#trail)" stroke-width="3.2"/>
      <path d="M-28 0 H-5" stroke="{t["string"]}" stroke-width="1.8"/>
      <path d="M-28 0 l-6 -4.5 M-28 0 l-6 4.5 M-23 0 l-6 -4.5 M-23 0 l-6 4.5" stroke="{t["rim"]}" stroke-width="1.4"/>
      <path d="M2 0 L-8 -4.4 L-5.5 0 L-8 4.4 Z" fill="{t["gold"]}"/>
      <circle class="flame" cx="-1" cy="0" r="4.2" fill="{t["fire"]}"/>
      <animateMotion path="{path}" rotate="auto" keyPoints="0;0;1;1" keyTimes="{clk.k(0, l, h, clk.total)}" calcMode="linear" {D}/>
      <animate attributeName="opacity" values="0;1;0" keyTimes="{clk.k(0, l, h)}" calcMode="discrete" {D}/>
    </g>''')
        e = h + 0.5
        sparks = []
        for si in range(SPARKS):
            ang = 2 * math.pi * si / SPARKS + rnd.uniform(-0.4, 0.4)
            dist = rnd.uniform(11, 19)
            sx, sy = math.cos(ang) * dist, math.sin(ang) * dist
            sparks.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.6" fill="{t["gold"]}" opacity="0">'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{sx:.1f} {sy:.1f};{sx:.1f} {sy:.1f}" keyTimes="{clk.k(0, h, e, clk.total)}" {D}/>'
                f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="{clk.k(0, h, h + 0.02, e, clk.total)}" {D}/></circle>')
        impacts_svg.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="{t["gold"]}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.85;0;0" keyTimes="{clk.k(0, h, h + 0.02, h + 0.25, clk.total)}" {D}/></circle>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="0" fill="none" stroke="{t["fire"]}" stroke-width="1.6" opacity="0">'
            f'<animate attributeName="r" values="0;0;18;18" keyTimes="{clk.k(0, h, e, clk.total)}" {D}/>'
            f'<animate attributeName="opacity" values="0;0;0.9;0;0" keyTimes="{clk.k(0, h, h + 0.02, e, clk.total)}" {D}/></circle>'
            + "".join(sparks))

    # bowstring, drawing arm and cape
    def string_d(nx):
        return f"M146 82 L{nx} {by} L146 166"

    def arm_d(nx):
        return f"M101 116 L{(101 + nx) / 2 + 2:.1f} {by + 5} L{nx} {by}"

    times, s_vals, a_vals = [0.0], [string_d(nock_rest)], [arm_d(nock_rest)]
    draw = min(0.34, shot * 0.7)
    for l in launches:
        for tt, nx in ((l - draw, nock_rest), (l - 0.01, nock_drawn), (l, nock_rest)):
            if tt > times[-1]:
                times.append(tt)
                s_vals.append(string_d(nx))
                a_vals.append(arm_d(nx))
    times.append(clk.total)
    s_vals.append(string_d(nock_rest))
    a_vals.append(arm_d(nock_rest))
    key = clk.k(*times)
    string_anim = f'<animate attributeName="d" values="{";".join(s_vals)}" keyTimes="{key}" {D}/>'
    arm_anim = f'<animate attributeName="d" values="{";".join(a_vals)}" keyTimes="{key}" {D}/>'
    cape_anim = ('<animate attributeName="d" dur="3.2s" repeatCount="indefinite" values="'
                 'M102 112 C84 124 72 152 62 186 L86 180 C90 156 96 136 108 120 Z;'
                 'M102 112 C80 128 64 150 52 180 L80 182 C88 158 96 138 108 120 Z;'
                 'M102 112 C84 124 72 152 62 186 L86 180 C90 156 96 136 108 120 Z"/>')

    # hit counter (cumulative contributions) and progress bar
    grid_right = GX + ncols * STEP - (STEP - CELL)
    counter, running = [], 0
    shown_until = [impacts[i + 1] if i + 1 < n else reset for i in range(n)]
    counter.append(f'<text x="{width - 26}" y="34" font-size="22" font-weight="800" fill="{t["gold"]}" text-anchor="end">0'
                   f'<animate attributeName="opacity" values="1;0;1" keyTimes="{clk.k(0, impacts[0] if n else reset, reset)}" calcMode="discrete" {D}/></text>')
    for gi, g in enumerate(groups):
        running += sum(d[3] for d in g)
        counter.append(
            f'<text x="{width - 26}" y="34" font-size="22" font-weight="800" fill="{t["gold"]}" text-anchor="end" opacity="0">{running}'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="{clk.k(0, impacts[gi], shown_until[gi])}" calcMode="discrete" {D}/></text>')
    bar_w = grid_right - GX
    first, last = (impacts[0], impacts[-1]) if n else (start, start + 1)
    progress = (f'<rect x="{GX}" y="{GY + 7 * STEP + 12}" width="{bar_w}" height="5" rx="2.5" fill="{t["empty"]}"/>'
                f'<rect x="{GX}" y="{GY + 7 * STEP + 12}" width="0" height="5" rx="2.5" fill="url(#bar)">'
                f'<animate attributeName="width" values="0;0;{bar_w};{bar_w};0" keyTimes="{clk.k(0, first, last, reset, clk.total)}" {D}/></rect>')

    caption = (f"{total} contribution{'s' if total != 1 else ''} hunted in the last year"
               if hits else "Hunting season starts soon")
    legend_x = grid_right - 4 * STEP - 62
    legend = "".join(
        f'<rect x="{legend_x + 32 + i * STEP}" y="{height - 31}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>'
        for i, c in enumerate(t["levels"]))
    halo = ("#fef3c7", "0.22") if t["night"] else ("#fbbf24", "0.35")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{SANS}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t["sky"][0]}"/><stop offset="0.6" stop-color="{t["sky"][1]}"/><stop offset="1" stop-color="{t["sky"][2]}"/>
    </linearGradient>
    <radialGradient id="halo"><stop offset="0" stop-color="{halo[0]}" stop-opacity="{halo[1]}"/><stop offset="1" stop-color="{halo[0]}" stop-opacity="0"/></radialGradient>
    <radialGradient id="moonShade" cx="0.3" cy="0.3"><stop offset="0.55" stop-color="#fde68a" stop-opacity="0"/><stop offset="1" stop-color="#d6b46a" stop-opacity="0.45"/></radialGradient>
    <linearGradient id="shootGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#ffffff"/></linearGradient>
    <linearGradient id="trail" gradientUnits="userSpaceOnUse" x1="-74" y1="0" x2="-24" y2="0">
      <stop offset="0" stop-color="{t["fire"]}" stop-opacity="0"/><stop offset="0.7" stop-color="{t["fire"]}" stop-opacity="0.6"/><stop offset="1" stop-color="{t["gold"]}"/>
    </linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["rim"]}"/><stop offset="1" stop-color="{t["gold"]}"/></linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="rim" x="-30%" y="-30%" width="160%" height="160%">
      <feMorphology in="SourceAlpha" operator="dilate" radius="1.4" result="d"/>
      <feFlood flood-color="{t["rim"]}"/><feComposite in2="d" operator="in" result="edge"/>
      <feGaussianBlur in="edge" stdDeviation="2.4" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="edge"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="frame"><rect width="{width}" height="{height}" rx="18"/></clipPath>
  </defs>
  <style>
    @keyframes tw {{ 0%,100% {{ opacity: .15 }} 50% {{ opacity: 1 }} }}
    .s1 {{ animation: tw 2.6s ease-in-out infinite }} .s2 {{ animation: tw 3.8s ease-in-out infinite }} .s3 {{ animation: tw 5.2s ease-in-out infinite }}
    @keyframes shoot {{ 0%,86% {{ transform: translate({width * 0.35:.0f}px,-30px); opacity: 0 }} 88% {{ opacity: 1 }} 96%,100% {{ transform: translate({width * 0.62:.0f}px,40px); opacity: 0 }} }}
    .shoot {{ animation: shoot 9s linear infinite }}
    @keyframes flick {{ 0%,100% {{ opacity: .95 }} 50% {{ opacity: .45 }} }}
    .flame {{ animation: flick .18s linear infinite }}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{width}" height="{height}" fill="url(#sky)"/>
    {sky_layer(t, width, height, rnd)}
    {mountains(t, width, height, rnd)}
  </g>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="18" fill="none" stroke="{t["border"]}"/>

  <text x="{GX - 4}" y="34" font-size="13" font-weight="800" fill="{t["rim"]}" letter-spacing="3">THE CONTRIBUTION HUNT</text>
  <text x="{width - 92}" y="33" font-size="10.5" font-weight="700" fill="{t["muted"]}" text-anchor="end" letter-spacing="1.5">@{esc(login)} · HITS</text>
  {"".join(counter)}

  <rect x="{GX - 12}" y="{GY - 24}" width="{grid_right - GX + 24}" height="{7 * STEP + 44}" rx="12" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}" stroke="{t["border"]}" stroke-opacity="0.6"/>
  {"".join(labels)}
  <g>{"".join(cells)}</g>
  <g>{"".join(targets)}</g>
  <g filter="url(#glow)">{"".join(overlays)}</g>
  {progress}

  {archer(t, ground, string_anim, arm_anim, cape_anim)}

  <g filter="url(#glow)" fill="none" stroke-linecap="round">{"".join(arrows)}</g>
  <g>{"".join(impacts_svg)}</g>

  <text x="{GX - 4}" y="{height - 21}" font-size="14" font-weight="700" fill="{t["text"]}">{esc(caption)}</text>
  <text x="{legend_x}" y="{height - 21}" font-size="11" fill="{t["muted"]}">Less</text>
  {legend}
  <text x="{legend_x + 32 + 4 * STEP + 4}" y="{height - 21}" font-size="11" fill="{t["muted"]}">More</text>
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
