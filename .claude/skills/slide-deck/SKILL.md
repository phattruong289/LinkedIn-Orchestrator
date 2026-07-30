---
name: slide-deck
description: Builds the visual carousel that ships with a LinkedIn post. Turns the finished copy into a slide spec, renders it to 1080x1080 PNGs from HTML/CSS templates, and reports what it produced. Invoked by daily-post after the copy is written, or standalone to build a deck for an existing post.
---

# Slide deck

Turns finished post copy into a rendered carousel. **The deck restates the post's spine visually — it is not a
transcript of the post and not new material.** Every figure and claim on a slide must already exist in the copy or
its research pack; a slide is not a place to introduce something the post didn't earn.

Read `resources/brand-kit.md` first — it holds the design system, the slide vocabulary, and the format spec.
`visuals/README.md` covers the renderer and the spec shape.

## Before starting

- **This produces images, nothing else.** No posting, no publishing. The deck is delivered alongside the draft for
  the same human review the copy goes through.
- **Rendering needs a local Chrome or Edge.** Whether one exists in a cloud Routine sandbox is unverified. If the
  renderer can't find a browser, don't improvise a substitute — write the deck spec to the ticket anyway, report
  that rendering was unavailable, and let it be rendered later from the spec. A spec with no images is a recoverable
  state; a made-up description of images is not.
- **Nothing here generates imagery.** Slides are rendered from HTML/CSS templates. If a slide needs a real
  screenshot — a game capture, an analytics dashboard — and one hasn't been supplied, **drop that slide**. Don't
  substitute a mockup, a generated image, a stand-in chart, or a description of what the capture would show. A
  fabricated dashboard is a fabricated statistic that happens to be rendered.

## Steps

1. **Read the copy** you're building for, plus its research pack, so every slide traces to something already
   written. If invoked by `daily-post`, both are on the ticket.

2. **Decide the deck length.** Three to six slides. The real decks run 3-8, but longer decks need material that
   genuinely carries — a five-slide deck padded to eight is worse than a clean three. Cover and CTA are near-always
   present; the middle is whatever the post actually supports.

3. **Pick slide types** from the five in the vocabulary. Match the type to what the post is doing, not to variety
   for its own sake:

   | Type | Use when |
   |---|---|
   | `cover` | Always first. Carries the hook |
   | `list` | The post has discrete objectives, steps, or lessons |
   | `metrics` | Several figures matter and none is the single story |
   | `compare` | The story is a *change* — before and after — not a static number |
   | `cta` | Always last. The commercial landing |

   A post whose argument is one number wants `cover` → `metrics` → `cta` and nothing more.

4. **Write the deck spec** as JSON — see `visuals/example-deck.json` for a complete one. Per slide, the fields for
   its type; per deck, a `slug`, a `seed`, and an optional `footer`.

   Two things that carry most of the visual quality:
   - **Break headlines by hand** with `\n`. Where a line lands changes how it reads, and auto-wrap picks the wrong
     place more often than not.
   - **Keep `accent` to one or two words.** Green marks the thing that matters — the figure, or the single word the
     argument turns on. Spread across four words it stops marking anything.

5. **Render:**
   ```bash
   node visuals/render.mjs <deck.json> out/ --pdf
   ```
   Numbered PNGs (`<slug>-01.png` onward, in deck order) plus a single `<slug>.pdf` — one 1080×1080 page per
   slide, text kept vector. Prefer the PDF when handing the deck to a person: one file, crisp at any zoom, and the
   format PLAY3 already uses for decks. Needs a local Chrome or Edge; no install, no network.

6. **Look at what you rendered.** Read the PNGs back and check each one:
   - Text fits, nothing clipped at an edge or colliding with the swipe cue
   - Headline breaks land where intended
   - Figures match the copy exactly — same rounding, same attribution
   - Accent is on one or two words, not scattered
   - `cta` is last and carries no swipe arrow

   A slide that's wrong is a slide to fix and re-render, not to hand over with a caveat.

7. **Save the spec to Notion — this is the durable artifact, not the PNGs.** Write the deck JSON into the day's
   Job Tickets page under `stages.visual`, and put the same JSON in a code block on the Post Log row so the deck
   travels with the draft a human reviews.

   The reasoning matters, because it's easy to get backwards: the rendered images are *derived*. Given the spec,
   the renderer reproduces them exactly — the starfield is seeded, so the same spec yields the same pixels. Keep
   the spec and nothing is lost; keep only the images and the deck can't be corrected. This is also why a run in a
   cloud sandbox has to write the spec out: that filesystem is discarded when the run ends.

   **The rendered files can't currently be attached automatically.** `notion-create-attachment` takes text content
   or a public HTTPS URL that doesn't redirect; local binary files need the separate Notion File Upload API, which
   isn't wired up. Two routes work but neither is automated — serving the file over HTTPS and passing `source_url`,
   or attaching the PDF by hand. See `visuals/README.md`. Don't work around the gap by describing the slides in
   prose as though that were equivalent: record the spec, note where the files were written, and leave it there.

8. **Report:** slide count, type per slide, output paths, where the spec was saved, and anything dropped along with
   why — a missing screenshot, a figure that wasn't in the copy. If a slide was dropped, say so plainly rather than
   quietly shipping a shorter deck.

## Not to do

- **Don't put a figure on a slide that isn't in the copy.** The same no-invented-facts rule applies; a number is no
  more verified for being set in large type.
- **Don't restate the post.** If a slide's text is a sentence lifted from the body, it's adding nothing — a slide
  either compresses a point or shows something the text can only describe.
- **Don't pad to a slide count.** Deck length follows the material.
- **Don't invent a chart.** The `chart` field plots real series data. Without real numbers, leave it out — a
  shape drawn to look like growth is a fabricated claim.
- **Don't restyle.** The design system is fixed in `base.css`; a deck that looks different from the last one isn't
  a fresh take, it's off-brand. Layout problems get fixed in the template so every future deck inherits the fix.
