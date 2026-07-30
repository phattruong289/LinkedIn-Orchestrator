# Slide rendering

Renders PLAY3 carousel slides as 1080×1080 PNGs from HTML/CSS templates. Design tokens and the slide vocabulary
come from `resources/brand-kit.md`, which was derived from real PLAY3 decks.

```bash
bash visuals/render.sh cover.html slide-test.png
```

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
| `cover.html` | Cover slide template |
| `render.sh` | Headless Chrome → PNG. Finds Chrome or Edge automatically |
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

## Not yet built

The other four slide types in the vocabulary: numbered list, metric stack, before→after, CTA.

## Known gaps

- **The two real typefaces aren't identified.** Current stand-ins: Space Mono (for the monospace), Chakra Petch
  (display), Poppins Black (figures). Close in character, not exact — the source mono in particular has different
  letterforms. Swap in the real files when they turn up and nothing else needs to change.
- **Screenshots have to be supplied.** If a slide needs a real game capture or dashboard and there isn't one, drop
  the slide — see the rule in `brand-kit.md`. Nothing here fabricates one.
- **Character/mascot art** appears on some real covers and isn't in `brand-assets/`.
