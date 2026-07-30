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

The deck **spec** goes to Notion as text on every run — that's the durable artifact, and the renderer reproduces
the images from it exactly (the starfield is seeded). The rendered files are a separate question, because
`notion-create-attachment` only accepts text content or a **public HTTPS URL that doesn't redirect**; local binary
files need the Notion File Upload API, which isn't wired up.

Two routes that do work, neither of them currently automated:

- **Serve the file over HTTPS and pass `source_url`.** `raw.githubusercontent.com` was checked and returns 200
  with zero redirects, so committing a render into the repo makes it attachable. The trade: this repo is public
  and the output is binary, so it means publishing the deck early and adding binary churn to history. Fine for
  slides that are about to be posted publicly anyway; a deliberate choice, not a default.
- **Attach by hand.** Render locally, drag the PDF onto the Notion page. One file, and the obvious answer while
  the pipeline still stops at a human review.

Prefer the PDF for either — one file instead of five, vector text, and no quality loss.

## Known gaps

- **The two real typefaces aren't identified.** Current stand-ins: Space Mono (for the monospace), Chakra Petch
  (display), Poppins Black (figures). Close in character, not exact — the source mono in particular has different
  letterforms. Swap in the real files when they turn up and nothing else needs to change.
- **Screenshots have to be supplied.** If a slide needs a real game capture or dashboard and there isn't one, drop
  the slide — see the rule in `brand-kit.md`. Nothing here fabricates one.
- **Character/mascot art** appears on some real covers and isn't in `brand-assets/`.
