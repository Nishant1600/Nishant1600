"""Airport-themed art for the profile README.

Writes four SVGs to assets/airport/: a boarding-pass header, a split-flap
departures board of projects, a baggage-claim belt of skills, and a flight log
where a plane lights up the GitHub contribution calendar as it flies over.

Usage:
    python scripts/airport.py                # reads the public contribution calendar
    python scripts/airport.py --demo         # synthetic calendar, works offline
Standard library only; no token needed.
"""
import argparse
import random
import re
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape as esc

ROOT = Path(__file__).resolve().parent.parent
W = 860
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
PLANE = "M22 12c0 1-1 1.5-2 1.5h-6l-4 7H8l2-7H5l-1.5 2.5H2l1-4-1-4h1.5L5 10.5h5l-2-7h2l4 7h6c1 0 2 .5 2 1.5z"

T = dict(night="#0B0D10", board="#15181D", rim="#2A2F37", rule="#20242B", tile="#23272E", band="#101318",
         amber="#FFD23F", text="#F4F1E8", muted="#8A93A3", via="#C9CFDA", green="#3DDC84", orange="#FFB23F",
         paper="#F7F4EC", ink="#16181D", label="#7A7468", perf="#CFC8B6",
         levels=["#23272E", "#5C4A12", "#9A7514", "#D9A520", "#FFD23F"],
         bags=["#FFD23F", "#3DDC84", "#FF8A65", "#7FB2FF", "#C9A7FF", "#F4F1E8"])

# Gates group the flights: A live demos, B agent systems, C AI & ML apps, D practice.
FLIGHTS = [
    ("09:41", "CODEINSIGHT", "NEO4J · FASTAPI · OPENAI", "A1", "LIVE"),
    ("10:15", "ORION", "DECK.GL · MAPLIBRE · VITE", "A2", "LIVE"),
    ("11:30", "AUDIT TEAM", "16 AGENTS · QA", "B1", "NEW"),
    ("12:05", "FAR AWAY", "AGENTS · FASTAPI · DOCKER", "B2", "ON TIME"),
    ("13:20", "JARVIS", "THREE.JS · WEBSOCKETS", "B3", "ON TIME"),
    ("14:45", "STUDYHUB", "RAG · CHROMADB · GROQ", "C1", "ON TIME"),
    ("16:10", "MEDISCAN", "PYTORCH · EFFICIENTNET", "C2", "LANDED"),
    ("18:00", "LEARNING-C", "C · EVERY SINGLE DAY", "D1", "DAILY"),
]
STATUS = {"LIVE": "green", "NEW": "orange", "DAILY": "orange"}
TICKER = ("GATE A · LIVE DEMOS     GATE B · AGENT SYSTEMS     GATE C · AI & ML     GATE D · PRACTICE     "
          "ALL FLIGHTS OPERATED BY NISHANT SHARMA · B.TECH, DU FACULTY OF TECHNOLOGY · NOIDA     ")
BELTS = [("BELT 1 · LANGUAGES & FRAMEWORKS", ["PYTHON", "TYPESCRIPT", "JAVASCRIPT", "C", "SQL", "REACT",
                                             "NEXT.JS", "TAILWIND", "VITE", "THREE.JS", "FASTAPI", "NODE.JS"]),
         ("BELT 2 · AI, DATA & TOOLS", ["PYTORCH", "SCIKIT-LEARN", "OPENAI API", "GROQ", "RAG", "CHROMADB",
                                       "NEO4J", "MULTI-AGENT", "FIREBASE", "DOCKER", "GIT", "VERCEL"])]


def fetch(login: str):
    req = urllib.request.Request(f"https://github.com/users/{login}/contributions",
                                 headers={"User-Agent": "airport-readme"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8")
    days = []
    for tag in re.findall(r"<td[^>]*data-date[^>]*>", html):
        d, lv = re.search(r'data-date="([\d-]+)"', tag), re.search(r'data-level="(\d)"', tag)
        if d and lv:
            days.append((date.fromisoformat(d.group(1)), int(lv.group(1))))
    if not days:
        raise SystemExit("No contribution calendar found; GitHub may have changed its markup (try --demo).")
    m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
    return (int(m.group(1).replace(",", "")) if m else 0), sorted(days)


def demo(seed: int = 7):
    rnd, end = random.Random(seed), date.today()
    days = [(end - timedelta(days=i), rnd.choice([0, 0, 0, 1, 2, 3, 4])) for i in range(364, -1, -1)]
    return sum(lv * 3 for _, lv in days), days


def svg(h: int, title: str, body: str, css: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
            f'font-family="{MONO}" font-weight="700"><title>{esc(title)}</title>'
            f'<style>{css}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>{body}</svg>\n')


def panel(h: int, title: str, note: str) -> str:
    """The dark board every section sits on, with its sign across the top."""
    return (f'<rect x="1.5" y="1.5" width="{W - 3}" height="{h - 3}" rx="12" fill="{T["night"]}"/>'
            f'<rect x="16" y="16" width="{W - 32}" height="{h - 32}" rx="8" fill="{T["board"]}" stroke="{T["rim"]}" stroke-width="3"/>'
            f'<clipPath id="inner"><rect x="18" y="18" width="{W - 36}" height="{h - 36}" rx="6"/></clipPath>'
            f'<path transform="translate(32 33) scale(1.15)" d="{PLANE}" fill="{T["amber"]}"/>'
            f'<text x="70" y="57" font-size="24" letter-spacing="5" fill="{T["amber"]}">{title}</text>'
            f'<text x="{W - 34}" y="55" font-size="11" font-weight="500" letter-spacing="2" fill="{T["muted"]}" text-anchor="end">{note}</text>'
            f'<path d="M18 72H{W - 18}" stroke="{T["rim"]}" stroke-width="2"/>')


def boarding_pass(rnd: random.Random) -> str:
    h, cut, route = 330, 636, "M168 128Q322 70 476 128"
    lab =f'font-family="{SANS}" font-size="10.5" font-weight="800" letter-spacing="2" fill="{T["label"]}"'
    val = f'font-size="15" fill="{T["ink"]}"'
    fields = "".join(f'<text x="{x}" y="200" {lab}>{k}</text><text x="{x}" y="222" {val}>{v}</text>'
                     for x, k, v in ((40, "PASSENGER", "NISHANT SHARMA"), (230, "CLASS", "B.TECH · YEAR 1"),
                                     (410, "COLLEGE", "DU · FOT"), (530, "SEAT", "1A")))
    bars, x = [], 662.0
    while x < 824:
        w = rnd.choice([1.5, 2, 2, 3, 4])
        bars.append(f'<rect x="{x:.1f}" y="206" width="{w}" height="70" fill="{T["ink"]}"/>')
        x += w + rnd.choice([1.5, 2, 3])
    body = f'''<mask id="notch"><rect width="{W}" height="{h}" fill="#fff"/><circle cx="{cut}" cy="12" r="14"/><circle cx="{cut}" cy="{h - 12}" r="14"/></mask>
<g mask="url(#notch)"><rect x="12" y="12" width="{W - 24}" height="{h - 24}" rx="18" fill="{T["paper"]}"/>
<path d="M12 64V30a18 18 0 0 1 18-18H{W - 30}a18 18 0 0 1 18 18V64Z" fill="{T["amber"]}"/></g>
<path d="M{cut} 30V{h - 30}" stroke="{T["perf"]}" stroke-width="2" stroke-dasharray="2 6"/>
<path transform="translate(34 26)" d="{PLANE}" fill="{T["ink"]}"/>
<text x="66" y="45" font-family="{SANS}" font-size="15" font-weight="800" letter-spacing="4" fill="{T["ink"]}">BOARDING PASS</text>
<text x="{cut - 24}" y="45" font-size="13" fill="{T["ink"]}" text-anchor="end">FLIGHT NS1600</text>
<text x="{(cut + W - 12) / 2}" y="45" font-size="13" fill="{T["ink"]}" text-anchor="middle">NS1600 · 1A</text>
<text x="40" y="96" {lab}>FROM</text><text x="{cut - 24}" y="96" {lab} text-anchor="end">TO</text>
<text x="38" y="146" font-size="52" fill="{T["ink"]}">NOI</text><text x="{cut - 24}" y="146" font-size="52" fill="{T["ink"]}" text-anchor="end">AGT</text>
<text x="40" y="168" {lab}>NOIDA, INDIA</text><text x="{cut - 24}" y="168" {lab} text-anchor="end">AI AGENTS + FULL-STACK APPS</text>
<path d="{route}" fill="none" stroke="{T["perf"]}" stroke-width="2" stroke-dasharray="3 6"/>
<g opacity="0"><path d="{PLANE}" transform="translate(-12 -12)" fill="{T["ink"]}"/>
<animateMotion path="{route}" dur="5s" repeatCount="indefinite" rotate="auto" keyPoints="0;1;1" keyTimes="0;.85;1" calcMode="linear"/>
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.08;.78;.85;1" dur="5s" repeatCount="indefinite"/></g>
{fields}
<path d="M40 242H{cut - 24}" stroke="{T["perf"]}" stroke-dasharray="2 4"/>
<text x="40" y="272" {lab}>PRIORITY</text><text x="150" y="272" font-size="13" fill="{T["ink"]}">OPENAI HACKATHON · GFG HACK-4-VIKSIT BHARAT</text>
<text x="40" y="300" {lab}>IN-FLIGHT</text><text x="150" y="300" font-size="13" fill="{T["ink"]}">C EVERY DAY · VISION MODELS IN PYTORCH</text>
<text x="660" y="96" {lab}>PASSENGER</text><text x="660" y="118" {val}>NISHANT</text><text x="660" y="138" {val}>SHARMA</text>
<text x="660" y="166" {lab}>FLIGHT</text><text x="660" y="186" {val}>NS1600</text>
<text x="770" y="166" {lab}>SEAT</text><text x="770" y="186" {val}>1A</text>
{"".join(bars)}
<rect class="scan" x="656" y="205" width="172" height="2" fill="#E5341D"/>
<text x="{(cut + W - 12) / 2}" y="298" font-size="11" fill="{T["label"]}" text-anchor="middle">@NISHANT1600</text>'''
    css = ".scan{animation:scan 2.4s ease-in-out infinite alternate}@keyframes scan{to{transform:translateY(70px)}}"
    return svg(h, "Boarding pass: Nishant Sharma, flight NS1600, Noida to AI agents and full-stack apps", body, css)


def board(rnd: random.Random) -> str:
    h, y0, rh, step = 500, 104, 41, 19
    rows, flaps = [], []
    for i, (tm, dest, via, gate, status) in enumerate(FLIGHTS):
        y = y0 + i * rh
        rows.append(f'<text x="34" y="{y + 26}" font-size="16" fill="{T["amber"]}">{tm}</text>'
                    f'<text x="346" y="{y + 25}" font-size="12.5" font-weight="500" fill="{T["via"]}">{esc(via)}</text>'
                    f'<text x="660" y="{y + 26}" font-size="15" fill="{T["text"]}" text-anchor="middle">{gate}</text>'
                    f'<path d="M34 {y + rh}H826" stroke="{T["rule"]}"/>')
        for x0, word, n, lag, color in ((106, dest, 12, 0, T["text"]), (695, status, 7, .7, T[STATUS.get(status, "text")])):
            for j, ch in enumerate(word.ljust(n)):
                junk = "".join(f'<text class="s s{k}">{rnd.choice(CHARS)}</text>' for k in range(3))
                flaps.append(f'<g transform="translate({x0 + j * step + 8.5} {y + 26.5})" fill="{color}" '
                             f'style="--d:{.8 + i * .35 + lag + j * .05:.2f}s"><use href="#tile"/>{junk}<text class="f">{esc(ch)}</text></g>')
    span = len(TICKER) * 7.8
    ticker = "".join(f'<text x="{34 + k * span:.0f}" y="470" font-size="13" fill="{T["amber"]}" textLength="{span:.0f}" '
                     f'lengthAdjust="spacing" xml:space="preserve">{esc(TICKER)}</text>' for k in range(2))
    cols = "".join(f'<text x="{x}" y="94" font-size="10.5" font-weight="500" letter-spacing="2" fill="{T["muted"]}"{a}>{k}</text>'
                   for x, k, a in ((34, "TIME", ""), (106, "DESTINATION", ""), (346, "VIA", ""),
                                   (660, "GATE", ' text-anchor="middle"'), (695, "STATUS", "")))
    body = (panel(h, "DEPARTURES", "NSH · NOIDA TERMINAL · ALL TIMES IST")
            + f'<defs><g id="tile"><rect x="-8.5" y="-19.5" width="17" height="27" rx="2" fill="{T["tile"]}"/>'
              f'<path d="M-8.5 -6H8.5" stroke="{T["night"]}"/></g></defs>'
            + cols + "".join(rows) + "".join(flaps)
            + f'<g clip-path="url(#inner)"><rect x="18" y="444" width="{W - 36}" height="40" fill="{T["band"]}"/>'
              f'<path d="M18 444H{W - 18}" stroke="{T["rim"]}" stroke-width="2"/><g class="tick">{ticker}</g></g>')
    css = (".f,.s{font-size:16px;text-anchor:middle}"
           ".f{animation:f 10s steps(1,end) infinite;animation-delay:var(--d)}@keyframes f{0%{opacity:0}3%{opacity:1}}"
           ".s{opacity:0;animation:s 10s steps(1,end) infinite;animation-delay:var(--d)}@keyframes s{0%{opacity:1}1%{opacity:0}}"
           ".s1{animation-delay:calc(var(--d) + .1s)}.s2{animation-delay:calc(var(--d) + .2s)}"
           f".tick{{animation:tick {span / 45:.0f}s linear infinite}}@keyframes tick{{to{{transform:translateX(-{span:.0f}px)}}}}")
    return svg(h, "Departures board: Nishant Sharma's projects as flights", body, css)


def baggage() -> str:
    h, body, css = 310, [panel(310, "BAGGAGE CLAIM", "SKILLS ON THE BELT")], []
    for b, (name, items) in enumerate(BELTS):
        rail, bags, x = 170 + b * 104, [], 0
        for i, item in enumerate(items):
            w, bh = len(item) * 8.4 + 30, 40 + (i * 7) % 15
            top, color = rail - bh, T["bags"][(i + b * 3) % len(T["bags"])]
            bags.append(f'<path d="M{x + w / 2 - 11} {top}v-6a4 4 0 0 1 4-4h14a4 4 0 0 1 4 4v6" fill="none" stroke="{color}" stroke-width="3"/>'
                        f'<rect x="{x}" y="{top}" width="{w}" height="{bh}" rx="7" fill="{color}"/>'
                        f'<path d="M{x + 8} {top + 6}v{bh - 12}M{x + w - 8} {top + 6}v{bh - 12}" stroke="{T["ink"]}" stroke-opacity=".18" stroke-width="2"/>'
                        f'<text x="{x + w / 2}" y="{top + bh / 2 + 5}" font-size="13" fill="{T["ink"]}" text-anchor="middle">{esc(item)}</text>')
            x += w + 16
        way = "" if b == 0 else " reverse"
        body.append(f'<text x="34" y="{rail - 76}" font-size="10.5" font-weight="500" letter-spacing="2" fill="{T["muted"]}">{esc(name)}</text>'
                    f'<g clip-path="url(#inner)"><g class="belt{b}">' + "".join(f'<g transform="translate({34 + k * x:.0f} 0)">{"".join(bags)}</g>' for k in range(2))
                    + f'</g><rect x="18" y="{rail}" width="{W - 36}" height="12" fill="{T["tile"]}"/>'
                    f'<path class="slat{b}" d="M18 {rail + 6}H{W - 18}" stroke="{T["rim"]}" stroke-width="12" stroke-dasharray="3 9"/></g>')
        css.append(f".belt{b}{{animation:belt{b} {x / 40:.0f}s linear infinite{way}}}@keyframes belt{b}{{to{{transform:translateX(-{x:.0f}px)}}}}"
                   f".slat{b}{{animation:slat .3s linear infinite{way}}}")
    css.append("@keyframes slat{to{stroke-dashoffset:12}}")
    return svg(h, "Baggage claim: Nishant Sharma's skills riding two conveyor belts", "".join(body), "".join(css))


def flight_log(login: str, total: int, days: list) -> str:
    h, cell, step, gy, period = 280, 11, 14, 128, 12
    start = days[0][0] - timedelta(days=(days[0][0].weekday() + 1) % 7)
    ncols = (days[-1][0] - start).days // 7 + 1
    gx = (W - (ncols * step - 3)) / 2
    base, lit, months = [], {}, []
    for d, lv in days:
        col, row = (d - start).days // 7, (d.weekday() + 1) % 7
        x, y = gx + col * step, gy + row * step
        base.append(f'<rect x="{x:.0f}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{T["levels"][0]}"/>')
        if lv:
            lit.setdefault(col, []).append(f'<rect x="{x:.0f}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{T["levels"][lv]}"/>')
        if row == 0 and (not months or months[-1][1] != d.month) and col < ncols - 2:
            if months and x - months[-1][0] < 3 * step:      # a month that barely starts: drop its label
                months.pop()
            months.append((x, d.month, d.strftime("%b").upper()))
    columns = "".join(f'<g class="col" style="--d:{.75 * period * (gx + c * step + 45) / (W + 80):.2f}s">{"".join(r)}</g>'
                      for c, r in sorted(lit.items()))
    active = sum(1 for _, lv in days if lv)
    best = run = 0
    for _, lv in days:
        run = run + 1 if lv else 0
        best = max(best, run)
    num = f'<tspan fill="{T["amber"]}" font-weight="700">{{}}</tspan>'.format
    stats = f"{num(total)} CONTRIBUTIONS · {num(active)} DAYS IN THE AIR · BEST STREAK {num(best)}"
    legend = "".join(f'<rect x="{W - 134 + i * 14}" y="{h - 52}" width="{cell}" height="{cell}" rx="2" fill="{c}"/>'
                     for i, c in enumerate(T["levels"]))
    body = (panel(h, "FLIGHT LOG", stats)
            + f'<defs><linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["amber"]}" stop-opacity=".35"/>'
              f'<stop offset="1" stop-color="{T["amber"]}" stop-opacity="0"/></linearGradient>'
              f'<linearGradient id="trail"><stop offset="0" stop-color="{T["amber"]}" stop-opacity="0"/>'
              f'<stop offset="1" stop-color="{T["amber"]}" stop-opacity=".7"/></linearGradient></defs>'
            + "".join(f'<text x="{x:.0f}" y="{gy - 9}" font-size="10" font-weight="500" fill="{T["muted"]}">{m}</text>' for x, _, m in months)
            + "".join(base) + columns
            + f'<g clip-path="url(#inner)"><g class="fly"><rect x="-6" y="100" width="12" height="{gy + 7 * step - 100}" fill="url(#beam)"/>'
              f'<path d="M-150 92H-14" stroke="url(#trail)" stroke-width="2"/>'
              f'<path transform="translate(-12 80)" d="{PLANE}" fill="{T["amber"]}"/></g></g>'
            + f'<text x="34" y="{h - 42}" font-size="10.5" font-weight="500" letter-spacing="1.5" fill="{T["muted"]}">'
              f'EACH SQUARE IS A DAY · THE PLANE LIGHTS UP THE DAYS I SHIPPED CODE</text>'
            + f'<text x="{W - 142}" y="{h - 42}" font-size="10" font-weight="500" fill="{T["muted"]}" text-anchor="end">LESS</text>'
            + legend + f'<text x="{W - 60}" y="{h - 42}" font-size="10" font-weight="500" fill="{T["muted"]}">MORE</text>')
    css = (f".fly{{animation:fly {period}s linear infinite}}"
           f"@keyframes fly{{0%{{transform:translateX(-40px)}}75%,100%{{transform:translateX({W + 40}px)}}}}"
           f".col{{animation:lit {period}s steps(1,end) infinite;animation-delay:var(--d)}}@keyframes lit{{70%{{opacity:0}}}}")
    return svg(h, f"Flight log: @{login}'s GitHub contributions over the last year", body, css)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--user", default="Nishant1600")
    ap.add_argument("--out", default=str(ROOT / "assets" / "airport"))
    ap.add_argument("--demo", action="store_true", help="use a synthetic calendar instead of GitHub")
    args = ap.parse_args()

    total, days = demo() if args.demo else fetch(args.user)
    out, rnd = Path(args.out), random.Random(1600)
    out.mkdir(parents=True, exist_ok=True)
    for name, art in (("pass", boarding_pass(rnd)), ("board", board(rnd)), ("baggage", baggage()),
                      ("flightlog", flight_log(args.user, total, days))):
        (out / f"{name}.svg").write_text(art, encoding="utf-8")
        print(f"{name}.svg  {len(art) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
