"""Generate the static animated SVGs for the profile README (dark + light).

Run from the repo root:  python scripts/build_assets.py
Writes assets/header-*.svg, typing-*.svg, divider-*.svg and assets/cards/*-*.svg.
Edit PROJECTS or TYPING_LINES below and re-run to update the graphics.
"""
from pathlib import Path
from xml.sax.saxutils import escape as esc

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,'DejaVu Sans Mono',Menlo,monospace"

THEMES = {
    "dark": dict(bg1="#070b18", bg2="#141033", card="#0d1424", text="#e6edf3", muted="#8b949e",
                 cyan="#22d3ee", violet="#a78bfa", gold="#fbbf24", green="#34d399", border="#283044",
                 grid="#ffffff", grid_op="0.045", chip_op="0.14"),
    "light": dict(bg1="#f8fafc", bg2="#eef2ff", card="#ffffff", text="#1f2328", muted="#57606a",
                  cyan="#0891b2", violet="#7c3aed", gold="#b45309", green="#059669", border="#d0d7de",
                  grid="#0f172a", grid_op="0.05", chip_op="0.10"),
}

TYPING_LINES = [
    "Building AI agents that actually ship",
    "Full-stack apps in TypeScript & Python",
    "OpenAI Hackathon · GFG Hack-4-Viksit Bharat",
    "Always learning, building, collaborating",
]

PROJECTS = [
    dict(slug="codeinsight", emoji="🧭", title="CodeInsight", ribbon="OpenAI Hackathon", live=True,
         tagline="Google Maps for software systems",
         lines=["Maps any repo's architecture as a live graph,",
                "answers questions and predicts bug impact."],
         chips=["Next.js", "FastAPI", "Neo4j", "tree-sitter", "OpenAI"]),
    dict(slug="orion", emoji="🛰️", title="ORION", ribbon=None, live=True,
         tagline="Energy supply-chain resilience platform",
         lines=["Real-time risk intelligence from 30+ APIs and",
                "500+ feeds across 160+ dashboard panels."],
         chips=["TypeScript", "Vite", "deck.gl", "MapLibre", "Convex"]),
    dict(slug="jarvis", emoji="🎙️", title="JARVIS", ribbon=None, live=False,
         tagline="Voice assistant, native on Windows",
         lines=["A JARVIS-style voice layer for a coding agent,",
                "with a 3D interface and every run recorded."],
         chips=["Python", "FastAPI", "WebSockets", "Three.js"]),
    dict(slug="studyhub", emoji="📚", title="StudyHub", ribbon=None, live=False,
         tagline="AI study assistant for DU FoT",
         lines=["Answers only from your own course material,",
                "with citations, flashcards, quizzes and more."],
         chips=["Next.js", "FastAPI", "ChromaDB", "Groq", "Firebase"]),
    dict(slug="audit-team", emoji="🏢", title="AI Website Audit Team", ribbon="New", live=False,
         tagline="A company of AI agents for your website",
         lines=["10 specialists, 5 supervisors and a CEO that",
                "find, fix and double-check every bug."],
         chips=["AI Agents", "Multi-agent", "Security", "QA"]),
    dict(slug="mediscan", emoji="🩺", title="MediScan", ribbon="GFG Hack-4-Viksit Bharat", live=False,
         tagline="AI-assisted dermatology diagnosis",
         lines=["Privacy-preserving skin-condition screening",
                "for doctors, powered by EfficientNet-B3."],
         chips=["PyTorch", "EfficientNet", "JavaScript", "Netlify"]),
    dict(slug="far-away", emoji="🚨", title="Far Away", ribbon=None, live=False,
         tagline="Emergency response agent platform",
         lines=["Detects incidents, allocates resources and",
                "optimises routes with cooperating AI agents."],
         chips=["Python", "FastAPI", "Docker", "Multi-agent"]),
]


def write(name: str, svg: str) -> None:
    path = ASSETS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def header(t: dict) -> str:
    chips = ["AI Agents", "Full-Stack", "Hackathons", "Open Source"]
    chip_svg, x = [], 64
    for c in chips:
        w = len(c) * 8.4 + 28
        chip_svg.append(
            f'<rect x="{x}" y="252" width="{w:.0f}" height="30" rx="15" fill="{t["cyan"]}" fill-opacity="{t["chip_op"]}" stroke="{t["cyan"]}" stroke-opacity="0.45"/>'
            f'<text x="{x + w / 2:.0f}" y="272" font-size="14" font-weight="600" fill="{t["cyan"]}" text-anchor="middle">{esc(c)}</text>')
        x += w + 10
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" font-family="{SANS}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/>
    </linearGradient>
    <radialGradient id="orbA"><stop offset="0" stop-color="{t["cyan"]}" stop-opacity="0.35"/><stop offset="1" stop-color="{t["cyan"]}" stop-opacity="0"/></radialGradient>
    <radialGradient id="orbB"><stop offset="0" stop-color="{t["violet"]}" stop-opacity="0.35"/><stop offset="1" stop-color="{t["violet"]}" stop-opacity="0"/></radialGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0" spreadMethod="repeat">
      <stop offset="0" stop-color="{t["cyan"]}"/><stop offset="0.5" stop-color="{t["violet"]}"/><stop offset="1" stop-color="{t["cyan"]}"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0" dur="6s" repeatCount="indefinite"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0 H0 V40" fill="none" stroke="{t["grid"]}" stroke-opacity="{t["grid_op"]}"/>
    </pattern>
    <clipPath id="round"><rect width="1200" height="320" rx="22"/></clipPath>
  </defs>
  <style>
    @keyframes driftA {{ 0%,100% {{ transform: translate(0px,0px) }} 50% {{ transform: translate(60px,30px) }} }}
    @keyframes driftB {{ 0%,100% {{ transform: translate(0px,0px) }} 50% {{ transform: translate(-50px,-25px) }} }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px) }} to {{ opacity: 1; transform: translateY(0) }} }}
    .a {{ animation: driftA 14s ease-in-out infinite }}
    .b {{ animation: driftB 11s ease-in-out infinite }}
    .r1 {{ animation: rise .8s ease-out both }}
    .r2 {{ animation: rise .8s ease-out .25s both }}
    .r3 {{ animation: rise .8s ease-out .5s both }}
    .r4 {{ animation: rise .8s ease-out .75s both }}
  </style>
  <g clip-path="url(#round)">
    <rect width="1200" height="320" fill="url(#bg)"/>
    <rect width="1200" height="320" fill="url(#grid)"/>
    <circle class="a" cx="260" cy="40" r="260" fill="url(#orbA)"/>
    <circle class="b" cx="1000" cy="300" r="240" fill="url(#orbB)"/>
  </g>
  <rect x="0.5" y="0.5" width="1199" height="319" rx="22" fill="none" stroke="{t["border"]}"/>

  <g class="r1"><text x="64" y="92" font-size="16" font-weight="700" fill="{t["muted"]}" letter-spacing="3">HI THERE, I'M</text></g>
  <g class="r2"><text x="62" y="160" font-size="66" font-weight="800" fill="{t["text"]}">Nishant Sharma</text></g>
  <g class="r3"><text x="64" y="206" font-size="30" font-weight="700" fill="url(#shine)">AI &amp; Full-Stack Developer</text>
    <text x="64" y="236" font-size="17" fill="{t["muted"]}">B.Tech @ Faculty of Technology, University of Delhi · Noida, India</text></g>
  <g class="r4">{"".join(chip_svg)}</g>

  <g transform="translate(985 160)">
    <circle r="112" fill="none" stroke="{t["cyan"]}" stroke-opacity="0.35" stroke-dasharray="4 10">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="40s" repeatCount="indefinite"/>
    </circle>
    <g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="14s" repeatCount="indefinite"/>
      <circle r="84" fill="none" stroke="{t["violet"]}" stroke-opacity="0.5"/>
      <circle cx="84" cy="0" r="7" fill="{t["violet"]}"/><circle cx="-84" cy="0" r="4" fill="{t["cyan"]}"/>
    </g>
    <g><animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="9s" repeatCount="indefinite"/>
      <circle r="56" fill="none" stroke="{t["cyan"]}" stroke-opacity="0.6"/>
      <circle cx="0" cy="-56" r="6" fill="{t["gold"]}"/>
    </g>
    <circle r="38" fill="{t["card"]}" stroke="{t["cyan"]}" stroke-width="2"/>
    <text y="10" font-family="{MONO}" font-size="26" font-weight="700" fill="{t["cyan"]}" text-anchor="middle">&lt;/&gt;</text>
  </g>
</svg>
'''


def typing(t: dict) -> str:
    fs, cw = 22, 22 * 0.58
    type_s, hold, erase_s, gap = 0.065, 1.6, 0.025, 0.35
    slots, start = [], 0.0
    for line in TYPING_LINES:
        n = len(line)
        dur = n * type_s + hold + n * erase_s + gap
        slots.append((line, start, n))
        start += dur
    total = start
    parts = []
    for i, (line, s, n) in enumerate(slots):
        w_full = n * cw
        x0 = 600 - w_full / 2
        times, widths = [0.0], [0.0]
        for k in range(1, n + 1):
            times.append(s + k * type_s)
            widths.append(k * cw)
        t_hold_end = s + n * type_s + hold
        for k in range(n - 1, -1, -1):
            times.append(t_hold_end + (n - k) * erase_s)
            widths.append(k * cw)
        kt = ";".join(f"{min(tt / total, 1):.5f}" for tt in times)
        wv = ";".join(f"{w + (cw * 0.4 if w else 0):.1f}" for w in widths)
        xv = ";".join(f"{x0 + w + 3:.1f}" for w in widths)
        vis = f'{0:.5f};{s / total:.5f};{min((t_hold_end + n * erase_s) / total, 1):.5f}'
        parts.append(f'''
  <clipPath id="c{i}"><rect x="{x0:.1f}" y="0" height="56" width="0">
    <animate attributeName="width" values="{wv}" keyTimes="{kt}" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite"/>
  </rect></clipPath>
  <text x="{x0:.1f}" y="36" font-size="{fs}" fill="{t["text"]}" clip-path="url(#c{i})" textLength="{w_full:.1f}" lengthAdjust="spacingAndGlyphs">{esc(line)}</text>
  <rect y="14" width="3" height="28" rx="1" fill="{t["cyan"]}" opacity="0" x="{x0:.1f}">
    <animate attributeName="x" values="{xv}" keyTimes="{kt}" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;1;0" keyTimes="{vis}" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite"/>
  </rect>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="56" viewBox="0 0 1200 56" font-family="{MONO}">
  <style>@keyframes blink {{ 50% {{ fill-opacity: 0 }} }} rect[height="28"] {{ animation: blink 1s step-end infinite }}</style>{"".join(parts)}
</svg>
'''


def divider(t: dict) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="18" viewBox="0 0 1200 18">
  <defs>
    <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{t["cyan"]}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{t["cyan"]}"/>
      <stop offset="0.75" stop-color="{t["violet"]}"/>
      <stop offset="1" stop-color="{t["violet"]}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="0" y="8.5" width="1200" height="1" fill="{t["border"]}"/>
  <rect y="7" width="360" height="4" rx="2" fill="url(#beam)">
    <animate attributeName="x" values="-360;1200" dur="4.5s" repeatCount="indefinite"/>
  </rect>
</svg>
'''


def card(p: dict, t: dict) -> str:
    chips, x = [], 28
    for c in p["chips"]:
        w = len(c) * 8.1 + 24
        chips.append(
            f'<rect x="{x:.0f}" y="178" width="{w:.0f}" height="28" rx="14" fill="{t["cyan"]}" fill-opacity="{t["chip_op"]}"/>'
            f'<text x="{x + w / 2:.0f}" y="196.5" font-family="{MONO}" font-size="13.5" fill="{t["cyan"]}" text-anchor="middle">{esc(c)}</text>')
        x += w + 8
    badges, bx = [], 572
    if p["live"]:
        w = 98
        bx -= w
        badges.append(
            f'<rect x="{bx}" y="24" width="{w}" height="26" rx="13" fill="{t["green"]}" fill-opacity="0.14" stroke="{t["green"]}" stroke-opacity="0.5"/>'
            f'<circle cx="{bx + 16}" cy="37" r="4" fill="{t["green"]}"><animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></circle>'
            f'<text x="{bx + 27}" y="41.5" font-size="12.5" font-weight="700" fill="{t["green"]}">Live demo</text>')
        bx -= 8
    if p["ribbon"]:
        w = len(p["ribbon"]) * 7.4 + 30
        bx -= w
        badges.append(
            f'<rect x="{bx:.0f}" y="24" width="{w:.0f}" height="26" rx="13" fill="{t["gold"]}" fill-opacity="0.14" stroke="{t["gold"]}" stroke-opacity="0.5"/>'
            f'<text x="{bx + w / 2:.0f}" y="41.5" font-size="12.5" font-weight="700" fill="{t["gold"]}" text-anchor="middle">★ {esc(p["ribbon"])}</text>')
    desc = "".join(
        f'<text x="28" y="{124 + i * 24}" font-size="17" fill="{t["muted"]}">{esc(line)}</text>'
        for i, line in enumerate(p["lines"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="240" viewBox="0 0 600 240" font-family="{SANS}">
  <defs>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t["cyan"]}"/><stop offset="0.5" stop-color="{t["border"]}"/><stop offset="1" stop-color="{t["violet"]}"/>
      <animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" dur="8s" repeatCount="indefinite"/>
    </linearGradient>
  </defs>
  <rect x="1.5" y="1.5" width="597" height="237" rx="18" fill="{t["card"]}" stroke="url(#edge)" stroke-width="2"/>
  <circle cx="52" cy="58" r="24" fill="{t["cyan"]}" fill-opacity="{t["chip_op"]}"/>
  <text x="52" y="67" font-size="24" text-anchor="middle">{p["emoji"]}</text>
  <text x="88" y="56" font-size="26" font-weight="800" fill="{t["text"]}">{esc(p["title"])}</text>
  <text x="88" y="81" font-size="16" font-weight="600" fill="{t["cyan"]}">{esc(p["tagline"])}</text>
  {"".join(badges)}
  {desc}
  {"".join(chips)}
  <text x="572" y="226" font-size="13" font-weight="600" fill="{t["muted"]}" text-anchor="end">View repo →</text>
</svg>
'''


def main() -> None:
    for name, t in THEMES.items():
        write(f"header-{name}.svg", header(t))
        write(f"typing-{name}.svg", typing(t))
        write(f"divider-{name}.svg", divider(t))
        for p in PROJECTS:
            write(f"cards/{p['slug']}-{name}.svg", card(p, t))
    print(f"wrote {3 * 2 + len(PROJECTS) * 2} SVGs to {ASSETS}")


if __name__ == "__main__":
    main()
