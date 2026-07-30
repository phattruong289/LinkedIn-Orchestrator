# Slide rendering

Renders PLAY3 carousel slides as 1080×1080 PNGs from HTML/CSS templates. Design tokens and the slide vocabulary
come from `resources/brand-kit.md`, which was derived from real PLAY3 decks.

```bash
node visuals/render.mjs visuals/example-deck.json out/          # numbered PNGs
node visuals/render.mjs visuals/example-deck.json out/ --pdf    # PNGs + one PDF
```

`--pdf` adds a single file with one 1080×1080 page per slide. **Text stays vector**, so it's crisp at any zoom and
smaller than the equivalent PNGs — and it's one file to hand over rather than five. It also matches how PLAY3
already exchanges decks; the source decks this system was derived from arrived as PDFs.

## Why HTML/CSS rather than image generation

The design is text-first and exact: a specific word inside a headline goes green, the wordmark has to be the real
SVG rather than something that resembles it, figures have to read as the actual numbers, and charts have to plot
real data. Generative image models are unreliable at all four — an earlier attempt at this pipeline produced the
wrong canvas size and an approximated logo, which is why it was paused.

Rendering from markup makes each of those a non-issue, and makes a re-render after a copy tweak produce the same
slide rather than a new interpretation of it.

## Files

| | |
|---|---|
| `base.css` | Design tokens and shared furniture — background layers, logo, chips, swipe cue, accent treatment |
| `starfield.js` | Seeded starfield generator. Same seed → same background, so a copy edit doesn't reshuffle the stars |
| `slide.html` | All five slide types. Renders one slide (`window.SPEC`) for PNG capture, or a whole deck (`window.DECK`) stacked one-per-page for PDF — same builder either way, so a slide can't look different depending on which output it came from |
| `render.mjs` | Deck JSON → numbered PNGs, plus a PDF with `--pdf`. Finds Chrome or Edge automatically |
| `bundle.py` | Deck JSON → one self-contained HTML, the file Notion can take |
| `publish-to-notion.py` | Sends that HTML from disk to Notion and embeds it. Needs `NOTION_TOKEN` |
| `render.sh` | Single-template shortcut, kept for quick one-off renders |
| `example-deck.json` | A complete five-slide deck, one of each type |
| `fonts/` | Vendored so a render needs no network |
| `play3-logo.svg` | Copy of the core asset, kept alongside the templates so the render has no path dependency outside this folder |

## The slide spec

Each template carries a `SPEC` object near the bottom — this is the shape `strategist-writer` would emit per slide:

```js
{
  type: "cover",
  font: "mono",                                  // "mono" reads technical, "display" reads loud
  headline: "We Lifted Every\nSingle Metric",    // \n forces a break; headlines are broken by hand
  accent: ["Lifted"],                            // words that go green — one or two, no more
  chip: "CASE STUDY",                            // optional label
  subtitle: null,
  footer: null,
  seed: 20260730,
}
```

**On the accent:** green marks the thing that matters — the figure, or the single word the argument turns on.
Spreading it across several words is the fastest way to lose the look.

## Getting a deck into Notion

```bash
python visuals/bundle.py <deck.json>      # -> out/<slug>.html, self-contained
```

`notion-create-attachment` takes **text content** or a public HTTPS URL that doesn't redirect. PNGs and PDFs are
binary and local, so neither fits — and a cloud Routine has no way to publish them and no filesystem that outlives
the run. An HTML file is text. That's the opening.

The bundle inlines everything: CSS, fonts, both SVGs, and the already-rendered DOM. No external requests, no
scripts. It's produced by driving the same `slide.html` the PNG renderer uses, so the preview can't drift from
the images.

**Fonts were the reason this looked impossible.** Four families inline is ~477 KB, well past Notion's 200 KiB
ceiling. A deck uses about 70 distinct glyphs, so subsetting to exactly those brings it to ~22 KB. The starfield
was the second problem — one `<i>` per dot is 57% of the bytes and scales with slide count, so it's collapsed into
`box-shadow` lists. A four-slide deck lands around 87 KB; eight slides still fit.

Requires `pip install fonttools brotli`. Both are small and pure-Python. If they're missing, bundling fails loudly
— report the bundle as unavailable rather than shipping a run with no visual.

## Publishing it

```bash
python visuals/publish-to-notion.py out/<slug>.html <page_id> --caption "Deck — 4 slides"
```

Sends the file from disk to Notion's File Upload API and embeds it on the page. Needs `NOTION_TOKEN` (a Notion
internal integration token, with the target page shared to that integration); the script prints setup steps if it's
missing.

**Why a script rather than the MCP attachment tool.** The MCP tool does accept the bundle — it takes text content,
and this is text. But that route reads ~90 KB into an agent's context and has it reproduce every character on the
way out. A third of those bytes are base64 font data, where a single wrong character silently breaks a typeface,
and it costs roughly 45k tokens per run. Moving bytes is not work an LLM should be doing. The script does it with
neither the risk nor the cost.

For scale: the same deck as a PDF through context would be ~550k tokens, and as four PNGs ~194k. That's why neither
of those is a viable automated path at all, bundle or no bundle.

Alternatives, neither automated: commit a render and pass the `raw.githubusercontent.com` URL as `source_url`
(verified to return 200 with zero redirects — but it publishes the deck into a public repo before posting), or
drag the PDF onto the Notion page by hand.

## Known gaps

- **The two real typefaces aren't identified.** Current stand-ins: Space Mono (for the monospace), Chakra Petch
  (display), Poppins Black (figures). Close in character, not exact — the source mono in particular has different
  letterforms. Swap in the real files when they turn up and nothing else needs to change.
- **Screenshots have to be supplied.** If a slide needs a real game capture or dashboard and there isn't one, drop
  the slide — see the rule in `brand-kit.md`. Nothing here fabricates one.
- **Character/mascot art** appears on some real covers and isn't in `brand-assets/`.
