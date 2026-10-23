"""Render design/store.html into the PNG sections used by README.md.

    python design/render.py            # uses Microsoft Edge/Chrome headless
    EDGE=/path/to/chrome python design/render.py

Needs Pillow. Web fonts load from Google Fonts at render time only; the PNGs are
committed, so GitHub never needs them. Writes assets/store/*.png at 2x.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "design" / "store.html"
OUT = ROOT / "assets" / "store"
SCALE = 2
WIDTH = 920

# element id -> output file; each is the element's own box, trimmed to its border.
SLICES = {
    "masthead": "masthead.png",
    "banner": "banner.png",
    "item-codeinsight": "item-codeinsight.png",
    "item-orion": "item-orion.png",
    "item-jarvis": "item-jarvis.png",
    "item-studyhub": "item-studyhub.png",
    "item-audit": "item-audit.png",
    "item-mediscan": "item-mediscan.png",
    "item-faraway": "item-faraway.png",
    "item-learningc": "item-learningc.png",
    "stock": "stock.png",
    "close": "close.png",
}


def find_browser() -> str:
    env = os.environ.get("EDGE")
    candidates = [env] if env else []
    candidates += [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("msedge") or "",
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    raise SystemExit("Set EDGE to a Chrome/Edge executable.")


def run(browser: str, args: list[str]) -> subprocess.CompletedProcess:
    prof = tempfile.mkdtemp(prefix="store-")
    try:
        return subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={prof}",
             "--virtual-time-budget=20000", *args],
            capture_output=True, text=True, timeout=180)
    finally:
        shutil.rmtree(prof, ignore_errors=True)


def main() -> None:
    browser = find_browser()
    url = SRC.as_uri()

    dom = run(browser, ["--dump-dom", url]).stdout
    m = re.search(r'<pre id="rects">(.*?)</pre>', dom, re.S)
    if not m:
        raise SystemExit("Could not read element boxes from the page.")
    rects = json.loads(m.group(1).replace("&quot;", '"'))

    height = int(max(r[1] + r[3] for r in rects.values())) + 40
    raw = Path(tempfile.mkdtemp()) / "page.png"
    run(browser, [f"--force-device-scale-factor={SCALE}", f"--window-size={WIDTH},{height}",
                  f"--screenshot={raw}", url])
    page = Image.open(raw).convert("RGB")

    OUT.mkdir(parents=True, exist_ok=True)
    for ident, name in SLICES.items():
        x, y, w, h = (v * SCALE for v in rects[ident])
        pad = 6 * SCALE if ident != "banner" else 4 * SCALE
        crop = page.crop((int(x - pad), int(y - pad), int(x + w + pad), int(y + h + pad)))
        crop.save(OUT / name, optimize=True)
        print(f"{name:24s} {crop.width}x{crop.height}")


if __name__ == "__main__":
    main()
