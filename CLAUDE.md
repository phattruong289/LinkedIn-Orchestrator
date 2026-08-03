# PLAY3 LinkedIn Content Agent Pipeline

A multi-agent pipeline that drafts ~1 LinkedIn post/day for PLAY3, ending at a human approval gate — see
`docs/task-and-requirements.md` for the original brief and `docs/phase1-plan.md` for the build plan.

## Scope lock (hardcoded — don't infer otherwise)

- **Profile / voice:** PLAY3's company page by default. Pass **`--wil_style`** to draft for Wil Lee's personal
  profile instead; that run reads `resources/voice-guide-wil-personal.md` in place of the company guide. Both
  guides are validated against real published posts, and the two voices never mix.
- **Format:** text, optionally with a rendered slide carousel (`slide-deck` skill → `visuals/`). No video.
  **No generated imagery** — slides come from HTML/CSS templates, and a slide needing a screenshot that wasn't
  supplied gets dropped rather than faked.
- **Posting:** the `daily-post` pipeline never auto-posts; it stops at a draft for human review and manual
  copy-paste. (`scripts/post-to-linkedin.sh` is a separate, scoped experiment — see the guardrails.)
- **Cadence:** one job ticket per calendar day.

## How this is organized

- `.claude/rules/guardrails.md` — the non-negotiables every agent follows (human gate, no invented facts, voice
  separation, **naming rules**, brand lock, traceability, no near-duplicates). Read this before touching any agent
  or skill file.
- `.claude/agents/` — the specialist subagents: `feedback-reviewer` (Stage 0: folds yesterday's Post Log comments
  into the rules before writing), `librarian` (research across 6 source lanes), `strategist-writer` (scoring +
  pillar balance + copy), `producer-qa` (final check).
- `.claude/skills/slide-deck/` — builds the visual carousel that ships with a post; renders via `visuals/`.
- `visuals/` — the slide design system: HTML/CSS templates, vendored fonts, and the headless-Chrome renderer.
- `.claude/skills/daily-post/` — the Manager: runs the agents in order, owns the job ticket, delivers the draft.
- `.claude/skills/idea-harvest/` — the weekly ritual that stocks the Idea Bank so the daily run never starts blank.
- `.claude/skills/log-outcome/` — run manually after Wil acts on a draft, to close the loop.
- `resources/` — local files only: voice guides, brand kit, case facts. Everything else lives in Notion.
- `scripts/` — standalone LinkedIn API experiments, not part of the pipeline. See the guardrails before touching.
- **Pipeline runtime state lives entirely in Notion** — "Job Tickets" (one page per day) and "Post Log" (the
  repeat-check source), both in the table below. There is no local job-ticket file and no `posted-log.json`; state
  was moved off git on 2026-07-27 so a daily run needs Notion access only, never a GitHub write grant.

## The six Notion databases (on the shared `TESTING` page, under `# LinkedIn`)

Split by **purpose**, so both humans and agents know exactly where a thing belongs:

| DB | Holds | Data source |
|---|---|---|
| **Content Playbook** | **HOW we write** — core five: pillars + target mix, hook library, skeletons, scoring rubric, voice + naming rules; plus extended structure library, content territories, standing topic guidance (the set grows — `strategist-writer` reads the current list) | `collection://94187f4f-93aa-44c7-bbec-81c092b53fda` |
| **Reference Resources** | **WHAT WE KNOW** — company facts, positioning, case studies, external sources. Channel-agnostic: filter by `Use For` (linkedin/blog/pitch/meeting/any) so it's reusable beyond LinkedIn | `collection://777ba81f-e6a6-4eea-a5af-2fe48ade6ab1` |
| **Idea Bank** | **WHAT WE'LL WRITE NEXT** — scored idea pipeline (`fresh`/`parked`/`used`/`cut`) | `collection://9592e8bf-2758-4a95-9f8f-63400feb71a3` |
| **Post Log** | **WHAT WE WROTE** — one row per daily draft, with `Pillar`/`Skeleton Used`/`Idea Score` for mix tracking | `collection://edc91fd0-7523-407c-82d2-df69f4be616d` |
| **Past Posts** | **HOW WE SOUND** — two authors, kept distinct by the `Author` field. `Wil (personal)`: his 10 real posts, the voice ground truth for everything this pipeline writes. `PLAY3 (company)`: the company page's posts, studied for structure and subject range only — never as a voice model (see voice separation in the guardrails) | `collection://5e65485f-b56e-42c1-9456-662a44e6656c` |
| **Job Tickets** | **RUNTIME PIPELINE STATE** — one page per daily run (research pack, idea candidates, copy, QA report, run_log) | `collection://d135687d-c675-4541-a22b-21170343b397` |

Rule of thumb for where new material goes: a *fact or source* → Reference Resources. A *method or rule* → Content
Playbook. A *thing we might write about* → Idea Bank.

## Running it

Invoke the `daily-post` skill to run today's pipeline. See `README.md` for setup and the scheduler smoke-test
before relying on any automated daily trigger.
