---
name: idea-harvest
description: The weekly ~30-minute idea harvest. Sweeps the six source lanes, scores candidates against the rubric, and tops the Notion Idea Bank back up to 15+ fresh/parked ideas so the daily pipeline never writes from a blank page. Run weekly (Friday) or any time the bank runs low.
---

# Idea harvest — weekly ritual

The daily pipeline should never start from a blank page. It should draw from a stocked Idea Bank. This skill is
what stocks it.

**Target: add 8-10 scored ideas per run, and never let the bank's `fresh` + `parked` count drop below ~15.**

Read `.claude/rules/guardrails.md` first — the naming rules apply here as hard filters, not suggestions.

## Skip gate — check this before anything else

Query Notion "Idea Bank" (`collection://9592e8bf-2758-4a95-9f8f-63400feb71a3`) and count rows with `Status` in
(`fresh`, `parked`). **If that count is above 10, skip the harvest** — report the count and stop, no further
steps. This applies whether the run was triggered on schedule or invoked manually.

**Exception:** if the invoking prompt contains `--force`, ignore the count and run the full harvest anyway — don't
ask for confirmation, don't second-guess it, just proceed straight to Step 1.

## Steps

1. **Check the bank's level.** (Skip this re-check if you already counted above for the skip gate — reuse that
   number.) Report the number up front. Below ~15 means this run needs to do real work, not a token top-up.

2. **Check the pillar gap.** Query the last ~20 rows of Notion "Post Log"
   (`collection://edc91fd0-7523-407c-82d2-df69f4be616d`) and count actual `Pillar` shares vs the Content
   Playbook's targets (currently ~40/25/10/20/5 — read them from the Playbook rather than assuming, they get
   revised). **Harvest deliberately against the gap** — if Category POV is
   under-served, go looking for POV ideas specifically rather than taking whatever the news happens to offer.

3. **Sweep the six lanes** (priority order — spend the most effort on lane 1, it produces the highest-scoring
   ideas):
   - `1-own-campaign-moment` — Notion "Past Posts", `resources/company-docs/case-facts.md`, Notion "Reference
     Resources", `resources/bww-transcripts/`. Look for facts, moments, and numbers *not yet used* in any Post Log
     row. These are the most ownable ideas available.
   - `2-industry-news` — **two halves, do both.**
     *(a) Sweep the known outlets:* Digiday, Campaign, The Drum, Marketing Dive, Mobile Marketer, Roblox newsroom,
     Business of Fashion. Only take items with a genuine PLAY3 angle, not everything that happened.
     *(b) Actively hunt new territory* — this half is what keeps the bank alive, and it is the half that gets
     skipped. Run **several distinct searches**, not one. Go looking for: trends in brand-gaming nobody has
     written up yet · arguments being debated in adjacent spaces (creator economy, ad-tech, Gen Z marketing,
     AI-and-IP, virtual goods) · places where the consensus take looks wrong · questions brands are asking that
     nobody has answered publicly. One search returning one idea means this half didn't happen.
   - `3-competitor-adjacent-pattern` — brand gaming activations worth reacting to **as a pattern**. Never record a
     competitor name in the idea; describe the shape.
   - `4-prospect-post` — not wired up yet; note as unavailable rather than inventing.
   - `5-reader-question` — not wired up yet; same.
   - `6-other`
   Re-check existing `parked` rows too: if one was parked for missing evidence and that evidence now exists,
   re-score it and flip it to `fresh`.

4. **Score each candidate** against the Content Playbook's Idea Scoring Rubric
   (`collection://94187f4f-93aa-44c7-bbec-81c092b53fda`): Ownability 30 + Evidence 25 + Audience relevance 20 +
   Hook strength 15 + Freshness 10. Apply all six auto-cut triggers. Record the per-dimension breakdown.

5. **Write rows into the Idea Bank**, one per candidate:
   - `Status`: **≥90 → `fresh`** · **70-89 → `parked`** · **<70 → `cut`** (still write cut ideas, with a
     `Cut Reason` — a cut idea whose blocker later clears is reusable; a discarded one is lost work)
   - Fill `Pillar`, `Source Lane`, `Score`, `Score Breakdown`, `Hook Draft`, `Core Argument`,
     `Evidence On Hand`, `Date Added`
   - Never write an idea that names a competitor or an uncleared client — cut it at this step with the reason
     recorded, rather than letting it reach the daily pipeline

6. **Report:** bank level before → after, the pillar gap and how this harvest addressed it, per-lane yield, the
   score distribution, anything auto-cut and why, and — if the bank is still under 15 — say so plainly rather than
   padding with weak ideas to hit a number.

## What not to do

- Don't pad the bank with low-scoring filler to hit 8-10. A short honest harvest beats a padded one; the daily
  pipeline will just cut the filler anyway.
- Don't harvest only from lane 2 because news is easy to find. That's the pipeline's known failure mode.
- **Don't skip step 3(b) — the active hunt — because lane 1 already produced enough ideas to hit the number.**
  Lane 1 (PLAY3's own material) is a finite pool: it scores highest but it depletes, and the first harvest
  (2026-07-25) already mined most of it out. External discovery is the only lane that refills week over week
  without new campaign data. A harvest that hits its number purely from lane 1 is borrowing from next week.
- Don't invent an angle's supporting evidence. An idea with no evidence yet is a legitimate `parked` row with
  `Evidence On Hand: "none yet — needs X"`, not a `fresh` one.
