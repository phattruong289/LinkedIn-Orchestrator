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
| `slide.html` | All six slide types. Renders one slide (`window.SPEC`) for PNG capture, or a whole deck (`window.DECK`) stacked one-per-page for PDF — same builder either way, so a slide can't look different depending on which output it came from |
| `render.mjs` | Deck JSON → numbered PNGs, plus a PDF with `--pdf`. Finds Chrome or Edge automatically |
| `upload-to-drive.py` | **Primary delivery.** Uploads the rendered PDF/PNG to Google Drive, sets "anyone with link", prints a shareable URL for the Post Log row. Reads `gdrive-token.json` |
| `gdrive-auth.py` | One-time: turns a downloaded OAuth client secret into `gdrive-token.json` (a refresh token). Run once, see setup below |
| `bundle.py` | *Fallback route.* Deck JSON → one HTML file for a Notion inline preview when Drive creds are absent. Self-contained by default; `--lean` fetches fonts and regenerates the starfield instead of baking both in |
| `publish-to-notion.py` | Sends that HTML from disk to Notion and embeds it. Needs `NOTION_TOKEN` (only for the fallback route) |
| `render.sh` | Single-template shortcut, kept for quick one-off renders |
| `example-deck.json` | A complete five-slide deck — one of each type except `media`, which needs a real sourced image and so isn't shown here |
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

## Delivering the deck — Google Drive (primary route)

The rendered PDF is the deck a reviewer actually wants: the real, sharp, postable file. It goes to Google Drive,
and only its link lands in Notion.

```bash
node visuals/render.mjs <deck.json> out/ --pdf
python visuals/upload-to-drive.py out/<slug>.pdf --folder $GDRIVE_FOLDER_ID --name "<date> — <slug> (deck).pdf"
```

`upload-to-drive.py` streams the file **disk → Drive** (never through an agent's context), sets it to "anyone with
the link: viewer", and prints a shareable URL to put on the Post Log row. This sidesteps everything that made the
Notion route painful: no 200 KiB text ceiling, no base64 through context, no Notion upload token, and no fidelity
loss — it's the actual PDF, already postable to LinkedIn.

### One-time OAuth setup

Google has no "paste a token" route for private Drive that this org allows — service-account keys are blocked by
org policy — so this uses an OAuth **Internal** app (Workspace-only, no verification, no key). Once done, day-to-day
is just running the script; there's no interactive step per run.

1. In Google Cloud Console (signed in as the account that owns the deck folder): create/pick a project → enable
   **Google Drive API**.
2. **Google Auth Platform** → Audience = **Internal**.
3. **Clients** → Create client → **Desktop app** → Download JSON (e.g. `client_secret.json`).
4. Mint the refresh token once:
   ```bash
   python visuals/gdrive-auth.py client_secret.json      # -> gdrive-token.json
   ```
   A browser opens; approve as the folder-owning account. `gdrive-token.json` = {client_id, client_secret,
   refresh_token}.
5. Set `GDRIVE_FOLDER_ID` to the target folder (from its URL) in `.env`, and in the Routine environment paste
   `gdrive-token.json`'s contents plus `GDRIVE_FOLDER_ID`.

`gdrive-token.json` and `client_secret*.json` are secrets — both are git-ignored. Scope is `drive.file` (the app
only ever touches files it creates), which is enough to upload into a folder you share the ID of.

## Fallback — getting a deck into Notion as an inline preview

Use this only when Drive credentials aren't available. It renders the deck as an HTML file Notion can preview inline.

```bash
python visuals/bundle.py <deck.json> --lean   # -> out/<slug>-lean.html,  ~22 KB
python visuals/bundle.py <deck.json>          # -> out/<slug>.html,       ~87 KB, self-contained
```

`notion-create-attachment` takes **text content** or a public HTTPS URL that doesn't redirect. PNGs and PDFs are
binary and local, so neither fits — and a cloud Routine has no way to publish them and no filesystem that outlives
the run. An HTML file is text. That's the opening.

Both forms drive the same `slide.html` the PNG renderer uses, so neither can drift from the images. They differ
only in how much they resolve ahead of time.

### Lean — the default route

Ships the deck as source: `base.css`, the builder, the deck spec, and the seed. Fonts come from Google Fonts, and
the starfield is regenerated from its seed rather than shipped as a thousand coordinates. About 22 KB, none of it
base64, which is what makes it small enough for an agent to hand to `notion-create-attachment` directly — no
upload token needed.

**Exception — a `media` slide with a local image.** The "none of it base64" property only holds for text decks and
for media slides whose image is a **remote https URL** (which passes through untouched). A media slide pointing at
a **local/owned** file base64-inlines that image into the bundle, so it's no longer hand-reproducible without a
token — that's the base64-by-hand trap. For a local/owned image, use `publish-to-notion.py` with `NOTION_TOKEN`, or
render the PNG/PDF separately and skip the Notion preview. (This media→Notion path is still being finalised.)

**It is not a reduced deck.** Same CSS, same builder, same spec, same seed, so the browser rebuilds exactly what
the renderer produced. Measured against the PNGs: slide 1 pixel-identical, the rest differing by at most 3/255 on
text antialiasing. Nothing is dropped or simplified.

The cost is a network fetch at view time. If Google Fonts is unreachable the text falls back to system faces —
everything else still renders, since it's all CSS and inline SVG.

Notion's HTML sandbox was verified to run scripts and load external fonts before this became the default. Both
matter: without scripts there's no starfield and no slides at all.

### Self-contained — for archival

Inlines everything: CSS, subsetted fonts, both SVGs, and the already-rendered DOM. No network at view time, so it
survives Google Fonts changing or disappearing. About 87 KB for four slides.

Fonts are why this one is large. Four families inline is ~477 KB, well past Notion's 200 KiB ceiling; a deck uses
about 70 distinct glyphs, so subsetting to exactly those brings it to ~22 KB. The starfield was the second
problem — one `<i>` per dot is 57% of the bytes and scales with slide count, so it's collapsed into `box-shadow`
lists. Eight slides still fit.

Requires `pip install fonttools brotli` for the subsetting. Both are small and pure-Python. If they're missing,
bundling fails loudly — use `--lean`, which needs neither.

## Publishing it

```bash
python visuals/publish-to-notion.py out/<slug>-lean.html <page_id> --caption "Deck — 4 slides"
```

Sends the file from disk to Notion's File Upload API and embeds it on the page. Needs `NOTION_TOKEN` (a Notion
internal integration token, with the target page shared to that integration); the script prints setup steps if it's
missing. This is the better route when a token exists: bytes move disk-to-Notion, costing no context and risking
no corruption, and it handles either bundle form.

**Without a token, attach the lean bundle with `notion-create-attachment` instead.** That means an agent reproduces
the file through its context, which is the reason the lean form exists: 22 KB of readable CSS and JS is
reproducible in a way that 90 KB of base64 font data is not. Verify the upload by comparing the returned
`content_length` against the file's LF-normalised byte count — they should match exactly. (Note the file on disk
has CRLF endings on Windows, so its raw size is larger; compare like for like or the check will look like a
mismatch when nothing is wrong.)

Don't attach the self-contained bundle this way. It costs ~45k tokens and a third of it is base64 font data, where
one wrong character silently breaks a typeface. For scale: the same deck as a PDF through context would be ~550k
tokens, and as four PNGs ~194k — which is why neither of those is a viable automated path at all.

One more alternative, not automated: commit a render and pass the `raw.githubusercontent.com` URL as `source_url`
(verified to return 200 with zero redirects — but it publishes the deck into a public repo before posting).

## Getting a postable file back out

What lands in Notion is for reading. LinkedIn takes images or a PDF, so the review copy has to become one of those
before it can ship.

**From the Notion attachment, with nothing installed:** download it, open it in a browser, and print to PDF. The
bundle carries `@page { size: 1080px 1080px }` and a page break per slide, so this yields one square page per
slide — measured at 810×810 pt, which is 1080 px (PDF units are 1/72 in, CSS px are 1/96 in). Output lands within
a couple of percent of what `render.mjs --pdf` produces.

This matters more than it first looks. A cloud Routine's files are discarded when the run ends, and whoever
reviews the draft may be on a machine that has never seen this repo. That path needs no repo, no Node, no Python
and no credentials — only a browser. It does need a network connection when the file is opened, since the lean
bundle fetches its fonts; offline, the layout and colour survive but the typefaces fall back.

**For separate PNGs**, re-render from the spec saved on the ticket:

```bash
node visuals/render.mjs <deck.json> out/ --pdf
```

Deterministic, so this reproduces the original pixels rather than something close to them. That's the reason the
spec is treated as the durable artifact and the images as derived.

## Known gaps

- **The two real typefaces aren't identified.** Current stand-ins: Space Mono (for the monospace), Chakra Petch
  (display), Poppins Black (figures). Close in character, not exact — the source mono in particular has different
  letterforms. Swap in the real files when they turn up and nothing else needs to change.
- **Screenshots have to be supplied.** If a slide needs a real game capture or dashboard and there isn't one, drop
  the slide — see the rule in `brand-kit.md`. Nothing here fabricates one.
- **Character/mascot art** appears on some real covers and isn't in `brand-assets/`.
