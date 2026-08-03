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

3. **Pick slide types** from the six in the vocabulary. Match the type to what the post is doing, not to variety
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
   - **The cover `chip` is a reader-facing label, never an internal tag.** "CASE STUDY" is fine; a pillar name
     ("DOGFOODING", "CATEGORY POV"), a skeleton letter, or a status is not — those are pipeline plumbing and leak
     onto the slide. No honest label → leave `chip` off. Most slides don't need one.

4b. **If a slide would carry a real image (`media`), clear it first — this is a hard gate, not a nicety.** An
   image makes a feature or a moment land harder than type, but only a *real, sourced* one qualifies; generating one
   is banned (see `.claude/rules/guardrails.md`). Before writing a `media` slide, place the image in one of three
   tiers:
   - **Embed directly** when it's an asset PLAY3 owns (platform/campaign captures, `resources/brand-assets/`), an
     official press/newsroom asset offered for editorial use, or an image the user supplied or approved. Set
     `credit` to the source **only when the image isn't PLAY3's own** — a press asset or third-party image needs the
     attribution line; a play3.ai screenshot or an owned capture does not (omit `credit`; crediting our own site on
     our own post is clutter). Record the provenance in your report regardless.
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

5. **Render:**
   ```bash
   node visuals/render.mjs <deck.json> out/ --pdf
   ```
   Produces numbered PNGs (`<slug>-01.png` onward, in deck order) plus a single `<slug>.pdf` — one 1080×1080 page
   per slide, text kept vector. Needs a local Chrome or Edge; no install, no network.

   **The PDF is what ships.** It's one file, crisp at any zoom, and already the postable review copy — a human
   downloads it and posts it to LinkedIn as-is. It goes to Google Drive in step 7. The PNGs are there for when
   separate square images are wanted.

   (`python visuals/bundle.py <deck.json> --lean` still exists — it turns the deck into a ~22 KB HTML file for
   the Notion-attach *fallback* in step 7, only used when Drive credentials aren't available. It's no longer the
   primary delivery.)

6. **Look at what you rendered.** Read the PNGs back and check each one:
   - Text fits, nothing clipped at an edge or colliding with the swipe cue
   - Headline breaks land where intended
   - Figures match the copy exactly — same rounding, same attribution
   - Accent is on one or two words, not scattered
   - `cta` is last and carries no swipe arrow

   A slide that's wrong is a slide to fix and re-render, not to hand over with a caveat.

7. **Save the spec to Notion, then deliver the deck via Google Drive.**

   **The spec is the durable artifact — not the PNGs.** Write the deck JSON into the day's Job Tickets page under
   `stages.visual`, and put the same JSON in a code block on the Post Log row. The rendered images are *derived*:
   given the spec, the renderer reproduces them exactly (the starfield is seeded, so the same spec yields the same
   pixels). Keep the spec and nothing is lost; keep only images and the deck can't be corrected. A cloud sandbox's
   filesystem is discarded at run end, so writing the spec out is what makes the deck survivable.

   **The viewable deck goes to Drive, and its link goes on the Post Log row.** Upload the rendered PDF:
   ```bash
   python visuals/upload-to-drive.py out/<slug>.pdf --folder $GDRIVE_FOLDER_ID --name "<date> — <slug> (deck).pdf"
   ```
   It streams the file straight from disk to Drive (never through your context), sets it to "anyone with the link:
   viewer", and prints a shareable URL. Put that URL on the Post Log row as the deck link, so the deck travels with
   the draft a human reviews. This is the whole delivery — the file on Drive is the real, sharp PDF: no 200 KiB
   ceiling, no base64, no Notion upload token, and it's already the postable file (download → post to LinkedIn).

   Credentials: `upload-to-drive.py` reads `gdrive-token.json` (or `$GDRIVE_TOKEN`) — a one-time OAuth setup, see
   `visuals/README.md`. `$GDRIVE_FOLDER_ID` is the shared deck folder. In a Routine, both live in the run
   environment; run the script with the environment loaded, or pass `--folder <id>` explicitly.

   **Fallback — only if Drive credentials are absent this run.** Attach the lean bundle to Notion as text instead:
   `python visuals/bundle.py <deck.json> --lean`, then attach `<slug>-lean.html` with `notion-create-attachment` +
   `<embed src="file-upload://...">`, verifying the returned `content_length` equals the file's LF-normalised byte
   count (on Windows the on-disk file is CRLF, so raw size is larger — compare like for like). This ~22 KB text
   route is base64-free **only** for text decks or media slides with a remote-URL image; a media slide with a
   **local** image base64-inlines and breaks it. So for any deck with a local media image, don't use this fallback
   — re-render and deliver via Drive, or note the deck as spec-only. Never hand-attach the self-contained bundle
   (~90 KB, a third base64 font data — one wrong character silently breaks a typeface).

   **Binary never travels through context.** PNGs and PDFs are binary; the Notion MCP tools would carry them as
   base64 through an agent's context at hundreds of thousands of tokens per run. That's exactly why the deck goes to
   Drive (disk→Drive, zero context) and only a text link lands in Notion. Don't attach a PNG/PDF through the tools,
   and don't describe the slides in prose as a substitute.

   **Postable file:** the Drive PDF already is one — download and post, or print its pages as square images. If you
   only have the spec later, re-render deterministically: `node visuals/render.mjs <deck.json> out/ --pdf`.

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
