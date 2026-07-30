#!/usr/bin/env python3
"""Bundle a rendered deck into ONE self-contained HTML file.

    python visuals/bundle.py <deck.json> [out.html]

Why this exists: a Routine run can't hand anyone a PNG. Its sandbox is discarded,
Notion's attachment tool takes text content or a public HTTPS URL but not local
binary, and pushing renders to the repo would publish them. Notion *does* render an
attached HTML file as a sandboxed preview, and HTML is text — so the deck can travel
as text and still be looked at.

The size problem that made this look impossible was fonts: four families inline is
~477 KB, well past the 200 KiB ceiling. A deck uses ~70 distinct glyphs, so subsetting
to exactly those drops it to ~22 KB. That is the whole trick.

Output is fully self-contained: no external CSS, no fonts to fetch, no scripts, no
network. Same markup the PNG renderer produces, so the preview matches the images.
"""

import base64, json, os, re, subprocess, sys, tempfile
from pathlib import Path

try:
    from fontTools import subset as _subset_check  # noqa: F401
    import brotli  # noqa: F401  (fonttools needs it to write woff2)
except ImportError as e:
    raise SystemExit(
        f"Missing dependency: {e.name}. Install with:  pip install fonttools brotli\n"
        "Both are pure-Python and small. Without them the deck can't be bundled for "
        "Notion — render the PNGs and report the bundle as unavailable rather than "
        "shipping the run without a visual."
    )

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

FONTS = {
    "P3Mono": "SpaceMono-Bold.ttf",
    "P3Display": "ChakraPetch-Bold.ttf",
    "P3Figure": "Poppins-Black.ttf",
    "P3Body": "Poppins-Medium.ttf",
}

CHROME_CANDIDATES = [
    r"C:/Program Files/Google/Chrome/Application/chrome.exe",
    r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    r"C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]


def find_chrome():
    env = os.environ.get("CHROME")
    if env and Path(env).exists():
        return env
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    raise SystemExit("No Chrome or Edge found. Set CHROME to a browser binary.")


def glyphs_used(deck):
    """Every character the deck actually renders, plus the furniture the templates add."""
    chars = set()

    def walk(o):
        if isinstance(o, str):
            chars.update(o)
        elif isinstance(o, dict):
            for k, v in o.items():
                if k not in ("type", "font", "seed", "slug"):
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(deck)
    # numerals and punctuation the card/metric furniture emits regardless of copy
    chars.update("0123456789 .,:;!?'\"()-—…#⚡→%$&/+")
    return "".join(sorted(chars))


def subset_fonts(text):
    """Subset each family to `text` and return {family: base64 woff2}."""
    from fontTools import subset

    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for family, filename in FONTS.items():
            src = HERE / "fonts" / filename
            dst = Path(tmp) / (family + ".woff2")
            subset.main([
                str(src), f"--text={text}", "--flavor=woff2",
                "--layout-features=*", f"--output-file={dst}",
            ])
            out[family] = base64.b64encode(dst.read_bytes()).decode("ascii")
    return out


def data_uri_svg(path):
    return "data:image/svg+xml;base64," + base64.b64encode(Path(path).read_bytes()).decode("ascii")


STAR_RE = re.compile(
    r'<i style="left:(?P<x>[\d.]+)%;top:(?P<y>[\d.]+)%;'
    r'width:(?P<w>[\d.]+)px;height:[\d.]+px;opacity:(?P<o>[\d.]+)"></i>'
)


def compact_starfield(html):
    """Collapse the per-dot starfield into box-shadow lists.

    The renderer emits one <i> per star, which is fine in a browser but is 57% of the
    bundle's bytes — and it scales with slide count, so an 8-slide deck would blow past
    Notion's 200 KiB ceiling. Each dot becomes a single box-shadow instead, which says
    the same thing in about a fifth of the characters. Positions are preserved exactly;
    opacity is bucketed into three passes so the colour doesn't have to be repeated per
    dot. Visually identical, and it makes long decks fit.
    """
    SIZE = 1080
    BUCKETS = ((0.40, ".35"), (0.70, ".62"), (1.01, ".9"))

    def collapse(match):
        block = match.group(0)
        stars = list(STAR_RE.finditer(block))
        if len(stars) < 40:          # bokeh and other small groups aren't worth rewriting
            return block
        lanes = {alpha: [] for _, alpha in BUCKETS}
        for s in stars:
            x = round(float(s.group("x")) / 100 * SIZE)
            y = round(float(s.group("y")) / 100 * SIZE)
            r = max(0, round(float(s.group("w")) / 2, 1))
            o = float(s.group("o"))
            alpha = next(a for cut, a in BUCKETS if o < cut)
            lanes[alpha].append(f"{x}px {y}px 0 {r}px")
        out = []
        for alpha, shadows in lanes.items():
            if not shadows:
                continue
            # box-shadow with no colour falls back to currentColor, which inherits to
            # black here and renders invisibly on a black slide. Setting color once per
            # lane costs eleven characters; repeating it per dot would cost hundreds.
            out.append(
                '<i style="left:0;top:0;width:1px;height:1px;background:0 0;color:#fff;'
                'opacity:%s;box-shadow:%s"></i>' % (alpha, ",".join(shadows))
            )
        return '<div class="stars">' + "".join(out) + "</div>"

    return re.sub(r'<div class="stars">.*?</div>', collapse, html, flags=re.S)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python visuals/bundle.py <deck.json> [out.html]")

    deck_path = Path(sys.argv[1])
    deck = json.loads(deck_path.read_text(encoding="utf-8"))
    slides = deck.get("slides", [])
    if not slides:
        raise SystemExit("Deck has no slides.")

    slug = deck.get("slug", "deck")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "out" / f"{slug}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Same seed/swipe/footer derivation as render.mjs, so the bundle matches the PNGs.
    base_seed = deck.get("seed", 20260730)
    full = []
    for i, s in enumerate(slides):
        s = dict(s)
        s["seed"] = base_seed + i * 977
        s.setdefault("swipe", i < len(slides) - 1)
        if "footer" not in s and i == 0 and deck.get("footer"):
            s["footer"] = deck["footer"]
        full.append(s)

    spec_js = HERE / "spec.js"
    spec_js.write_text("window.DECK = " + json.dumps(full, ensure_ascii=False) + ";\n", encoding="utf-8")

    # Let the real renderer build the DOM, so the preview can't drift from the images.
    chrome = find_chrome()
    url = "file:///" + str(HERE / "slide.html").replace("\\", "/")
    dom = subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--virtual-time-budget=3000", "--dump-dom", url],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout
    spec_js.unlink(missing_ok=True)

    if 'class="slide"' not in dom:
        raise SystemExit("Renderer produced no slides — check the deck spec.")

    # ---- make it self-contained -------------------------------------------------
    fonts = subset_fonts(glyphs_used(deck))
    css = (HERE / "base.css").read_text(encoding="utf-8")

    # replace the @font-face src urls with inlined subsets
    for family, b64 in fonts.items():
        css = re.sub(
            r'(@font-face\s*\{[^}]*?font-family:\s*"%s";[^}]*?src:\s*)url\([^)]*\)\s*format\("truetype"\)' % family,
            lambda m, b=b64: m.group(1) + 'url(data:font/woff2;base64,%s) format("woff2")' % b,
            css, flags=re.S,
        )

    html = dom.replace(
        '<link rel="stylesheet" href="base.css">',
        "<style>\n" + css + "\n</style>",
    )
    html = html.replace('src="play3-logo.svg"', 'src="%s"' % data_uri_svg(HERE / "play3-logo.svg"))
    html = html.replace('src="play3-bolt.svg"', 'src="%s"' % data_uri_svg(HERE / "play3-bolt.svg"))

    # scripts already ran; the DOM they produced is baked in. Notion's sandbox may not
    # execute them anyway, so strip rather than depend on it.
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.S)
    html = re.sub(r"<template\b.*?</template>", "", html, flags=re.S)
    html = compact_starfield(html)

    # stack the slides for a scrollable preview
    html = html.replace(
        "</style>",
        "\nhtml,body{height:auto;overflow:visible;width:auto;}\n"
        "#stage{display:flex;flex-direction:column;align-items:center;gap:18px;}\n"
        ".slide{flex:none;}\n</style>",
    )

    out_path.write_text(html, encoding="utf-8")
    kb = out_path.stat().st_size / 1024
    print(f"{out_path}  {kb:.0f} KB   (Notion inline-content ceiling is 200 KiB)")
    if kb > 200:
        print("  OVER the ceiling — reduce the starfield density or slide count.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
