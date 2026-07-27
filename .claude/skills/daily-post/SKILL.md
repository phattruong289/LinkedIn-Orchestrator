---
name: daily-post
description: Manager/Orchestrator for PLAY3's Phase 1 LinkedIn pipeline. Runs librarian, then strategist-writer, then producer-qa, in order, for Wil's personal profile, text-only format (art-director/graphics paused for now) — then posts the finished draft to Slack for human approve/tweak/kill. Invoke manually, or via a scheduled task, once daily.
---

# Daily post — the Manager

You are the **Manager/Orchestrator** for PLAY3's Phase 1 LinkedIn pipeline. This is plain orchestration logic, not
an LLM "agent" persona — your job is to run the stages in order, keep the job ticket honest, and stop at the human
gate. Read `.claude/rules/guardrails.md` first.

**Phase 1 scope, hardcoded — do not infer otherwise from context:** profile is always `wil-personal`; format is
always `text-only` **for now** (`text+single-graphic`/`art-director` are paused — see `.claude/rules/guardrails.md`);
one post per calendar day; never auto-post.

## State model

**All pipeline runtime state lives in Notion "Job Tickets"** (`collection://d135687d-c675-4541-a22b-21170343b397`)
— one page per calendar day. There is no local job-ticket file. This is deliberate: it means a daily run needs
Notion access only, never git write access, which is what actually blocked the first real Routine run on
2026-07-27 (the GitHub App installed on that environment had no `Contents: write` permission). A page's `Status`
property (`started|failed|qa_failed|draft_ready|posted_to_slack|closed`) is the source of truth for idempotency;
the page body holds a single JSON code block shaped `{"run_log": [...], "stages": {...}}` that every step below
reads and rewrites via `notion-update-page`'s `update_content` (target just that code block, don't replace the
whole page each time).

**Cross-environment tool ID note:** the Notion connector ID differs between local sessions
(`mcp__9787b242-3013-4204-91ee-022fa3fa29e5__notion-*`) and cloud Routines (`mcp__Notion__notion-*`) even though
both point at the same "REDACTED Studios" workspace. Try whichever is already loaded; if it comes back as an
unrecognized tool, `ToolSearch` for `"notion"` and retry with whatever it finds.

## Steps

1. **Resolve today's ticket** — query Job Tickets for a page with today's `Date` (local date):
   - No page for today → create one: `Name` = today's date (`YYYY-MM-DD`), `Status: started`, `Profile:
     wil-personal`, `Format Target` left unset, body seeded with `{"run_log": [], "stages": {}}`.
   - Page exists with `Status` already `posted_to_slack`, `qa_failed`, `failed`, or `closed` → **stop**, report
     "today's post is already handled, see the ticket" (idempotency guard against a double-fire or accidental
     re-run).
   - Page exists mid-pipeline (`Status: started`, a stage errored last run) → **resume from the first incomplete
     stage** found in the body JSON, don't restart.
2. Append a `run_log` entry (`{ts, event: "manager_start"}`) to the body JSON.
3. **Dispatch `librarian`** (Agent tool). Write its output to `stages.research` in the body JSON. If it reports the
   resource pool is too thin for any decent angle → set the page's `Status` property to `failed`, log why in
   `run_log`, **stop and report** — don't force a weak post.
4. **Dispatch `strategist-writer`, Step A (ideation)**, telling it explicitly that `text+single-graphic` is paused
   this run — it should only propose `text-only` ideas. Get `idea_candidates` (each scored, with a `pillar` and
   `skeleton`). **You (the Manager) pick:**
   - Prefer the highest-scoring idea that isn't `repeat_risk: true`.
   - **Scoring thresholds are a real gate, not decoration.** If the top candidate scores <70, don't write it —
     set the page's `Status` property to `failed`, note that nothing cleared the bar, and recommend running
     `idea-harvest`. If the top candidate is 70-89, you may proceed, but record in the ticket that it was written
     below the ≥90 "write now" threshold, so the human reviewer knows.
   - Break near-ties (within ~10 points) in favour of the under-served pillar the Strategist reported.
   - Write `stages.idea_chosen` (including `pillar`, `skeleton`, `score`, `score_breakdown`); `format_target` is
     always `"text-only"` for now.
   - **Park the leftovers:** any candidate scoring 70-89 that wasn't chosen goes into Notion "Idea Bank"
     (`collection://9592e8bf-2758-4a95-9f8f-63400feb71a3`) as `Status: parked`; anything auto-cut goes in as
     `Status: cut` with its `Cut Reason`. Today's research shouldn't evaporate just because only one post ships.
   - If the chosen idea came *from* the Idea Bank, update that row to `Status: used` with `Used On` = today.
5. **Dispatch `strategist-writer`, Step B (copywriting)** with the chosen idea, its pillar, and the matching
   skeleton. Write `stages.copy`.
6. **Skip `art-director` entirely** and set `stages.visual: null` — it's paused (see step 4). Don't dispatch it
   even if an idea's research would support a graphic; that capability comes back later by explicit instruction.
7. **Dispatch `producer-qa`** with everything gathered so far. Write `stages.draft`, `stages.qa_report`,
   `stages.qa_status`.
   - `qa_status: "fail"` → set the page's `Status` property to `qa_failed`. **Do not proceed to Slack.** Still send
     a short Slack notice ("today's draft failed QA — <reason> — needs manual attention"). Stop.
8. **On `qa_status: "pass"` — deliver the draft for human review.**
   - **Always write a row to Notion "Post Log"** (`collection://edc91fd0-7523-407c-82d2-df69f4be616d`):
     `Name`, `Date`, `Profile`, `Format`, `Status: draft_ready`, `Pillar`, `Skeleton Used`, `Idea Score`,
     `Topic Tags`, `Core Argument`, `Key Facts Cited`, `QA Notes`. Put the full copy + sources in the page body.
     **`Pillar` and `Idea Score` are not optional** — they're what makes the mix tracking and threshold auditing
     work on future runs.
   - **Then, if Slack is authorized**, `ToolSearch` for the Slack tool defensively (it may not be loaded in a
     fresh run) and post the draft there too: final copy (no hashtags — Wil's voice guide shows he never uses
     them), plus the image if any. Ask plainly for **approve / tweak / kill**, and state explicitly: *this is a
     draft for manual copy-paste to LinkedIn — nothing auto-posts.* If Slack isn't authorized yet, the Notion row
     is the review surface — say so in your report rather than failing.
   - Either way, **carry the caveats through**: any voice-confidence, repeat-risk, below-threshold-score, or
     medium-confidence-source flag from earlier stages goes into the delivered draft, not just the ticket. A
     caveat that dies between the ticket and the human is a caveat that did nothing.
   - Set the page's `Status` property to `draft_ready` (or `posted_to_slack` if Slack delivery succeeded), append
     to `run_log` in the body JSON.
9. **Stop.** Do not wait for a Slack reply — a single invocation can't block for human input. Closing the loop
   (recording what Wil actually did) is the separate `log-outcome` skill, run manually after he acts.

## Failure handling

Any stage error (not a QA fail — an actual exception/tool failure): log it into `run_log` with the stage name and
error, set the page's `Status` property to `failed`, stop, and report clearly what broke and at which stage —
don't retry silently or paper over a broken stage.
