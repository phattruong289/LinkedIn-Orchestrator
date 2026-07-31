# Brand kit

> **Derived 2026-07-30 from 5 real PLAY3 carousel decks** (27 slides, exported as PDFs). Before this, the palette
> and typography were recorded as unknown — the decks answer both. Anything below marked *observed* comes from
> those slides; anything marked *open* still doesn't have an answer.

## Format spec

- **1080 × 1080 px**, square. *Observed* — every one of the 27 slides is exactly this size. An earlier version of
  this file specified 1200×1200, which was wrong and is the likely origin of the dimension mismatch that got the
  earlier image-generation attempt paused.
- PNG, under 5MB.
- Native square post, not a link-preview ratio.
- **Multi-slide carousels are the real practice** — the decks run 3 to 8 slides. Single graphics are the exception,
  not the norm.

## Palette (observed)

| Role | Value | Use |
|---|---|---|
| Background | near-black, `#000000`–`#050505` | every slide |
| Accent | acid lime, exactly **`#ADFF00`** | emphasised words, all large numbers, charts, arrows, buttons, glows |
| Text | white `#FFFFFF` | body and non-emphasised headline words |
| Muted text | white at ~55-60% | footers, captions, parentheticals |
| Sticker accent | electric blue, approx `#2B2BF5` | **rare** — one rotated "sticker" callout per deck at most |

The accent does a lot of work and its discipline is part of the look: **green marks the thing that matters** — the
number, the one word in the headline that carries the argument, the CTA. Everything else stays white. A slide with
green on more than a couple of elements loses the effect.

## Typography (observed, families unidentified)

Two families, used for different jobs:

- **Wide geometric sans, heavy weight** — headlines and the very large metric numbers. Squarish, slightly
  condensed-feeling caps with wide letterforms.
- **Monospace** — subtitles, CTA headlines, numerals inside cards, small labels. This is what gives the decks their
  technical feel and it's a deliberate contrast against the sans.

**Open:** the exact typefaces aren't identified. Until they are, use the closest available match and note the
substitution in the QA report rather than guessing silently. Do not use Anton/Baloo2/Montserrat/NotoSans as "the"
brand font — those appear only in unrelated video templates elsewhere and are not PLAY3's.

## Slide vocabulary (observed)

Six types. A deck picks from these rather than inventing layouts.

1. **Cover** — logo top-centre · optional pill chip label ("CASE STUDY") · large headline mixing white and green
   words · monospace subtitle · optional in-game screenshot in a rounded panel · green swipe arrow bottom-centre ·
   small italic muted footer tagline.
2. **Numbered list** — headline with one green word · `01`/`02`/`03` cards on dark translucent green panels with
   **chamfered corners** and a thin green border · outlined monospace numerals · white body text · circular icon
   badge · progress indicator in the bottom corners.
3. **Metric stack** — several very large green numbers with white labels beneath · radial green glow behind ·
   a green line chart with fill along the bottom.
4. **Before → after** — bracketed container · two large green figures separated by `>` · white labels with italic
   parentheticals · a rotated blue sticker badge for the headline percentage · hand-drawn green curved arrow ·
   a real dashboard screenshot in a rounded panel.
5. **CTA** — logo · oversized lightning-bolt watermark set diagonally · monospace headline · payoff line in green
   with a glow · green pill button with black label and a white cursor arrow.
6. **Media** — headline with one green word · one real image in a rounded frame with a thin green border, on a
   near-black panel · a white caption and a muted **source credit** beneath it. The image is held, not full-bleed:
   it `contain`-fits so a non-square capture letterboxes cleanly rather than cropping out its point (`fit: "cover"`
   opts into cropping when that's genuinely better). Use it when a real image — a platform screenshot, a press
   asset, a product capture — makes the point more vividly than type can. Fields: `image` (path or URL), `credit`
   (required), optional `caption`, optional `fit`. This is the only type that carries an image sourced from
   outside the template, so the image rules below are load-bearing, not decoration.

## Motifs (observed)

Four-pointed sparkle stars · starfield background (fine white dots plus a few soft bokeh glows) · oversized
lightning bolt as watermark · radial green glow · chamfered card corners · hand-drawn arrows · rotated sticker
badges · pill-shaped chips and buttons · year chips (`2026`) in top corners on some covers · character/avatar
renders bleeding in from the edges.

Real screenshots — game capture, analytics dashboards — are embedded in rounded panels with a subtle border, and
they carry a lot of the credibility.

**Screenshots can't be generated, and a missing one is not something to work around.** If a slide type needs a real
capture and none has been supplied, drop that slide and build the deck without it — don't substitute a mockup, a
generated image, a stand-in chart, or a description of what the screenshot would show. A deck of three honest
slides beats four with one invented. This is the no-invented-facts rule applied to images: a fabricated dashboard
is a fabricated statistic that happens to be rendered.

**A real image is allowed; a fabricated or unrightsed one is not.** The `media` slide exists precisely so a real,
sourced image can be used — but three things must hold, and they mirror the guardrails' image rule:
- **It depicts what the slide claims.** An image standing in for something it doesn't actually show is a fabricated
  claim in picture form.
- **Its rights are clear.** Directly usable: an asset PLAY3 owns, an official press/newsroom asset for editorial
  use, or an image the user supplied or approved. An image lifted from an article with unknown rights is *not*
  embedded — it goes to the reviewer as a suggestion with its source, to approve or not.
- **Every media slide shows a credit.** The `credit` field is required; an image with no traceable source doesn't
  go on a slide.
Uncertain on either the depiction or the rights → drop the slide. Drop rather than fake, drop rather than infringe.

## Assets on hand

`brand-assets/core/`: `play3-logo.svg` / `.png`, `play3-logo-black.svg`, `favicon.svg`, `play3-icon-512.png`.

The wordmark appears as `PLAY3ᴬᴵ` with a green lightning bolt as the leading glyph, and it must be composited from
these files — never approximated or redrawn.

**Case-study-only:** `brand-assets/case-studies/susu/` (Vinamilk/SUSU lockup + VNM fonts). Only for posts actually
about that campaign — see `company-docs/case-facts.md`.

## Still open

- **The two typefaces**, as above.
- **Character/avatar art** appears on some covers (including a yellow blocky figure carrying the lightning-bolt
  mark, which reads as a PLAY3 mascot). Not in `brand-assets/`; source unknown.
- **Chart styling** is consistent in spirit but the decks show both hand-styled charts and raw dashboard
  screenshots. No rule yet for which to use when.
