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
   | `media` | A real image makes the point more vividly than type — a platform screenshot, a press asset, a product capture. Only with a cleared, sourced image (see step 4b) |
   | `cta` | Always last. The commercial landing |

   A post whose argument is one number wants `cover` → `metrics` → `cta` and nothing more.

4. **Write the deck spec** as JSON — see `visuals/example-deck.json` for a complete one. Per slide, the fields for
   its type; per deck, a `slug`, a `seed`, and an optional `footer`.

   Two things that carry most of the visual quality:
   - **Break headlines by hand** with `\n`. Where a line lands changes how it reads, and auto-wrap picks the wrong
     place more often than not.
   - **Keep `accent` to one or two words.** Green marks the thing that matters — the figure, or the single word the
     argument turns on. Spread across four words it stops marking anything.

4b. **If a slide would carry a real image (`media`), clear it first — this is a hard gate, not a nicety.** An
   image makes a feature or a moment land harder than type, but only a *real, sourced* one qualifies; generating one
   is banned (see `.claude/rules/guardrails.md`). Before writing a `media` slide, place the image in one of three
   tiers:
   - **Embed directly** when it's an asset PLAY3 owns (platform/campaign captures, `resources/brand-assets/`), an
     official press/newsroom asset offered for editorial use, or an image the user supplied or approved. Set
     `credit` to the source; it renders as a visible line.
   - **A cleared image already in Notion "Reference Resources"** (a row with a source and a rights note) is usable
     the same way — this is where the pipeline should look first, and where the user stocks images over time.
   - **Propose, don't embed**, when the image is lifted from an article or any third party whose rights are
     unknown. Don't put it on a slide; instead note it in your report as a suggestion *with its source URL*, for
     the human at the review gate to approve or reject. Republishing someone else's copyrighted image into a
     branded post unattended is the thing this avoids.

   Two tests every media image must pass regardless of tier: it **depicts what the copy claims** (an image standing
   in for something it doesn't show is a fabricated claim in picture form), and it **carries a credit**. Fail either,
   or can't establish rights → **drop the slide and build the deck without it.** Drop rather than fake, drop rather
   than infringe. Say in your report what was dropped and why.

5. **Render, then bundle:**
   ```bash
   node visuals/render.mjs <deck.json> out/ --pdf
   python visuals/bundle.py <deck.json> --lean
   ```
   The first produces numbered PNGs (`<slug>-01.png` onward, in deck order) plus a single `<slug>.pdf` — one
   1080×1080 page per slide, text kept vector. Needs a local Chrome or Edge; no install, no network.

   The second produces `<slug>-lean.html`, ~22 KB — this is the file that goes into Notion in step 7. It exists
   because a PNG or PDF can't go there: Notion's attachment tool takes text content or a public URL, and a cloud
   run has neither a way to publish nor a filesystem that survives the run. HTML is text, so it fits.

   It's built by driving the same templates as the PNGs, and ships the deck as source — CSS, builder, spec, seed —
   with fonts fetched and the starfield regenerated at view time rather than baked in. That keeps it small enough
   to hand over without an upload token. It is not a reduced deck: same spec and same seed rebuild the same pixels.

   Drop `--lean` for the self-contained form (~87 KB, everything inlined, no network at view time). Prefer it only
   when the deck needs to survive without Google Fonts; it needs `pip install fonttools brotli`, and if those are
   missing it fails loudly. **Don't treat that as fatal:** `--lean` needs neither, and the PNGs and spec still
   deliver regardless.

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

   **Then attach the bundle so a reviewer can actually see the deck.** With `NOTION_TOKEN` in the environment:
   ```bash
   python visuals/publish-to-notion.py out/<slug>-lean.html <post-log-page-id> --caption "Deck — N slides"
   ```
   This sends the file from disk straight to Notion's File Upload API. Prefer it whenever the token exists — bytes
   never touch your context, so there's nothing to cost and nothing to corrupt.

   **Without a token, attach `<slug>-lean.html` with `notion-create-attachment`** and place it with
   `<embed src="file-upload://...">`. That means reproducing the file through your context, which is exactly what
   the lean form is sized for: ~22 KB of readable CSS and JS, no base64. **Verify it:** the returned
   `content_length` must equal the file's LF-normalised byte count. On Windows the file on disk has CRLF endings,
   so its raw size is larger — compare like for like, or a correct upload will look broken.

   Never attach the self-contained bundle this way. Its ~90 KB is a third base64 font data, where one wrong
   character silently breaks a typeface and you'd have no way to tell.

   Two things that stay true either way:
   - **The bundle is text, which is the whole reason any of this works.** PNGs and PDFs are binary and local, and
     Notion takes neither — through the MCP tools, binary would have to travel as base64 through an agent's
     context, which costs hundreds of thousands of tokens per run. Don't try to attach them, and don't describe
     the slides in prose as a substitute.
   - **If a bundle would exceed Notion's 200 KiB ceiling**, `bundle.py` says so and exits. Shorten the deck;
     never truncate the file.

   **Then say how to turn it into something postable**, in the caption — don't assume it's obvious. What's on the
   page is for reading; LinkedIn takes images or a PDF, not HTML. Downloading the attachment and printing it from
   a browser yields the deck as a correctly-sized PDF, because the bundle carries its own page-size rule. That
   path needs no repo, no tooling and no credentials, which is what makes it the one to name: whoever reviews the
   draft may be nowhere near the machine that rendered it, and a cloud run's own files are gone by then. Separate
   PNGs still need a local `render.mjs` run against the saved spec.

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
