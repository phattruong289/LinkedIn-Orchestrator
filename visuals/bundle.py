#!/usr/bin/env python3
"""Bundle a rendered deck into ONE HTML file Notion can render as a preview.

    python visuals/bundle.py <deck.json> [out.html]           # self-contained (~87 KB)
    python visuals/bundle.py <deck.json> [out.html] --lean     # source form (~22 KB)

Why this exists: a Routine run can't hand anyone a PNG. Its sandbox is discarded,
Notion's attachment tool takes text content or a public HTTPS URL but not local
binary, and pushing renders to the repo would publish them. Notion *does* render an
attached HTML file as a sandboxed preview, and HTML is text — so the deck can travel
as text and still be looked at.

Two forms, both driving the same templates the PNG renderer uses (so neither drifts
from the images):

- **Self-contained** (default): everything inlined — CSS, subsetted fonts, both SVGs,
  the baked DOM. No network at view time. Fonts are the size problem: four families
  inline is ~477 KB, but a deck uses ~70 glyphs, so subsetting drops it to ~22 KB and
  the whole bundle to ~87 KB. Needs `fonttools`+`brotli`.
- **--lean**: ships the deck as source (CSS, builder, spec, seed); fonts fetched from
  Google Fonts and the starfield regenerated from its seed at view time. ~22 KB, no
  dependencies. This is the form an agent can hand to Notion's attachment tool WITHOUT
  an upload token, because it's readable text rather than base64.

CAVEAT — media slides break the "no base64" property of --lean. A `media` slide with a
LOCAL image path is base64-inlined into the bundle (see img_data_uri), so a lean bundle
carrying a local image is NO LONGER hand-reproducible without a token — that is the
exact base64-by-hand trap to avoid. A media image given as a REMOTE https URL passes
through untouched and keeps the bundle small and token-free. So: remote cleared image →
token-free path works; local/owned image → needs publish-to-notion.py + NOTION_TOKEN,
or render the PNG/PDF separately. (The media→Notion path is still being finalised.)
"""

import base64, json, mimetypes, os, re, subprocess, sys, tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

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


def _shrink_for_preview(raw, max_px=1100, jpeg_q=82):
    """Downscale a raster image for the Notion preview, if Pillow is available.

    The preview only needs to be looked at, so a full-resolution screenshot is wasted
    bytes that push the bundle past Notion's 200 KiB ceiling. The postable PNG/PDF is
    rendered separately from the full-res original, so nothing that ships loses quality
    — this smaller copy exists only inside the Notion bundle. Returns (bytes, mime) or
    None (Pillow missing, decode failed, or shrinking didn't actually help).
    """
    try:
        import io
        from PIL import Image
    except ImportError:
        return None
    try:
        im = Image.open(io.BytesIO(raw))
    except Exception:
        return None
    w, h = im.size
    scale = min(1.0, max_px / max(w, h))
    if scale < 1.0:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    buf = io.BytesIO()
    if has_alpha:
        im.convert("RGBA").save(buf, format="PNG", optimize=True)
        out_mime = "image/png"
    else:
        im.convert("RGB").save(buf, format="JPEG", quality=jpeg_q, optimize=True)
        out_mime = "image/jpeg"
    data = buf.getvalue()
    return (data, out_mime) if len(data) < len(raw) else None


def img_data_uri(ref):
    """Inline a media-slide image so it survives in a Notion bundle, which has no
    filesystem to read a local path from.

    A remote URL (or an already-inlined data: URI) passes through unchanged — Notion's
    sandbox loads external images, and a cleared press asset is fine to hotlink. A local
    file, including a file:// URL, is read, shrunk for the preview if possible, and
    base64'd. A missing file fails loudly rather than shipping a broken image.
    """
    if ref.startswith(("http://", "https://", "data:")):
        return ref
    if ref.startswith("file://"):
        ref = url2pathname(urlparse(ref).path)   # handles the Windows /C:/ vs POSIX /home difference
    path = Path(ref)
    if not path.is_absolute():
        path = ROOT / ref
    if not path.exists():
        raise SystemExit(f"media image not found: {ref}  (resolved to {path})")
    raw = path.read_bytes()
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    if mime in ("image/png", "image/jpeg", "image/webp"):
        shrunk = _shrink_for_preview(raw)
        if shrunk:
            raw, mime = shrunk
    return "data:%s;base64,%s" % (mime, base64.b64encode(raw).decode("ascii"))


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


GOOGLE_FONTS = "https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@700&family=Poppins:ital,wght@0,500;0,900;1,500&family=Space+Mono:wght@700&display=swap"

# The vendored files and these Google families are the same typefaces — the local copies
# exist so a render needs no network, not because they differ.
FAMILY_MAP = {
    "P3Mono": "Space Mono",
    "P3Display": "Chakra Petch",
    "P3Figure": "Poppins",
    "P3Body": "Poppins",
}


def svg_uri(path):
    """Raw SVG as a data URI — percent-encoded, not base64.

    base64 costs a third more bytes and turns readable markup into a random-looking
    blob. Both matter here: the blob is what makes the self-contained bundle too large
    to hand over as text.
    """
    s = re.sub(r"\s+", " ", Path(path).read_text(encoding="utf-8")).strip()
    s = s.replace('"', "'")
    for ch, enc in (("%", "%25"), ("#", "%23"), ("<", "%3C"), (">", "%3E"), ("&", "%26")):
        s = s.replace(ch, enc)
    return "data:image/svg+xml;charset=utf-8," + s


def lean_bundle(full, out_path):
    """Bundle the deck as source rather than as output.

    Same CSS, same builder, same deck spec, same seed — so the browser rebuilds exactly
    what the PNG renderer produces. What it drops is the *baked* form of things that are
    already derivable: fonts fetched instead of inlined as base64, and the starfield
    regenerated from its seed instead of shipped as a thousand coordinates.

    Costs a network fetch at view time, which the self-contained bundle doesn't. Gains a
    file that is ~22 KB of readable code, which an agent can hand to Notion's attachment
    tool directly when no upload token is available.
    """
    html = (HERE / "slide.html").read_text(encoding="utf-8")
    css = (HERE / "base.css").read_text(encoding="utf-8")

    # Google Fonts supplies the @font-face rules, so drop the local ones and point the
    # stylesheet at the real family names. Every usage already states its weight
    # explicitly (`font: 700 76px/1.34 "P3Mono"`), so nothing depends on the dropped
    # @font-face weight declarations.
    css = re.sub(r"@font-face\s*\{[^}]*\}\s*", "", css)
    for old, new in FAMILY_MAP.items():
        css = css.replace('"%s"' % old, '"%s"' % new)
        html = html.replace('"%s"' % old, '"%s"' % new)

    html = html.replace(
        '<link rel="stylesheet" href="base.css">',
        '<link rel="stylesheet" href="%s">\n<style>\n%s\n</style>' % (GOOGLE_FONTS, css),
    )
    html = html.replace(
        '<script src="starfield.js"></script>',
        "<script>\n%s\n</script>" % (HERE / "starfield.js").read_text(encoding="utf-8"),
    )
    # A media slide's <img> is built at view time from the DECK JSON, so the image
    # reference has to be inlined there rather than in the static HTML.
    deck_js = []
    for s in full:
        s = dict(s)
        if s.get("type") == "media" and s.get("image"):
            s["image"] = img_data_uri(s["image"])
        deck_js.append(s)
    html = html.replace(
        '<script src="spec.js"></script>',
        "<script>window.DECK = %s;</script>" % json.dumps(deck_js, ensure_ascii=False),
    )
    html = html.replace('src="play3-logo.svg"', 'src="%s"' % svg_uri(HERE / "play3-logo.svg"))
    html = html.replace('src="play3-bolt.svg"', 'src="%s"' % svg_uri(HERE / "play3-bolt.svg"))

    html = html.replace(
        "</style>",
        "\nhtml,body{height:auto;overflow:visible;width:auto;}\n"
        "#stage{display:flex;flex-direction:column;align-items:center;gap:18px;}\n"
        ".slide{flex:none;}\n</style>",
        1,
    )

    out_path.write_text(html, encoding="utf-8")
    return out_path.stat().st_size


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python visuals/bundle.py <deck.json> [out.html] [--lean]")

    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    lean = "--lean" in sys.argv

    deck_path = Path(argv[0])
    deck = json.loads(deck_path.read_text(encoding="utf-8"))
    slides = deck.get("slides", [])
    if not slides:
        raise SystemExit("Deck has no slides.")

    slug = deck.get("slug", "deck")
    default_name = f"{slug}-lean.html" if lean else f"{slug}.html"
    out_path = Path(argv[1]) if len(argv) > 1 else ROOT / "out" / default_name
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

    if lean:
        kb = lean_bundle(full, out_path) / 1024
        print(f"{out_path}  {kb:.0f} KB   (lean — fonts and starfield resolved at view time)")
        return

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

    # media images arrive as <img src="file://..."> in the dumped DOM; inline them.
    # logo and bolt were already turned into data: URIs above, so they're skipped.
    html = re.sub(
        r'<img([^>]*?)src="([^"]+)"',
        lambda m: m.group(0) if m.group(2).startswith("data:")
        else '<img%ssrc="%s"' % (m.group(1), img_data_uri(m.group(2))),
        html,
    )

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
