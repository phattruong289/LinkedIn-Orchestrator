# PLAY3 LinkedIn Content Agent Pipeline

A multi-agent pipeline that drafts ~1 LinkedIn post/day for Wil Lee (CEO of PLAY3), ending at a human approval gate
— see `docs/task-and-requirements.md` for the original brief and `docs/phase1-plan.md` for the build plan.

## Phase 1 scope lock (hardcoded — don't infer otherwise)

- **Profile:** Wil's personal LinkedIn only. No PLAY3 company-page posts yet.
- **Format:** text-only, for now. `text+single-graphic` is built (`art-director` agent) but currently **paused** —
  don't dispatch it until told otherwise. No carousels, no video.
- **Posting:** no LinkedIn API integration exists. The pipeline stops at a Slack draft for manual copy-paste —
  nothing auto-posts.
- **Cadence:** one job ticket per calendar day.

## How this is organized

- `.claude/rules/guardrails.md` — the non-negotiables every agent follows (human gate, no invented facts, voice
  separation, **naming rules**, brand lock, traceability, no near-duplicates). Read this before touching any agent
  or skill file.
- `.claude/agents/` — the specialist subagents: `librarian` (research across 6 source lanes),
  `strategist-writer` (scoring + pillar balance + copy), `producer-qa` (final check). `art-director` (visual)
  exists but is currently **paused** — text-only posts for now.
- `.claude/skills/daily-post/` — the Manager: runs the agents in order, owns the job ticket, delivers the draft.
- `.claude/skills/idea-harvest/` — the weekly ritual that stocks the Idea Bank so the daily run never starts blank.
- `.claude/skills/log-outcome/` — run manually after Wil acts on a draft, to close the loop.
- `resources/` — local files only: voice guides, brand kit, case facts. Everything else moved to Notion.
- `jobs/YYYY-MM-DD.json` — one job ticket per day; this is the pipeline's actual state, not the conversation.
- `posted-log.json` — local mirror of finalized topics for the repeat check.

## The five Notion databases (on the shared `TESTING` page, under `# LinkedIn`)

Split by **purpose**, so both humans and agents know exactly where a thing belongs:

| DB | Holds | Data source |
|---|---|---|
| **Content Playbook** | **HOW we write** — pillars + target mix, hook library, skeletons, scoring rubric, voice + naming rules | `collection://94187f4f-93aa-44c7-bbec-81c092b53fda` |
| **Reference Resources** | **WHAT WE KNOW** — company facts, positioning, case studies, external sources. Channel-agnostic: filter by `Use For` (linkedin/blog/pitch/meeting/any) so it's reusable beyond LinkedIn | `collection://777ba81f-e6a6-4eea-a5af-2fe48ade6ab1` |
| **Idea Bank** | **WHAT WE'LL WRITE NEXT** — scored idea pipeline (`fresh`/`parked`/`used`/`cut`) | `collection://9592e8bf-2758-4a95-9f8f-63400feb71a3` |
| **Post Log** | **WHAT WE WROTE** — one row per daily draft, with `Pillar`/`Skeleton Used`/`Idea Score` for mix tracking | `collection://edc91fd0-7523-407c-82d2-df69f4be616d` |
| **Past Posts** | **HOW WIL SOUNDS** — his 10 real past posts, the voice ground truth | `collection://5e65485f-b56e-42c1-9456-662a44e6656c` |

Rule of thumb for where new material goes: a *fact or source* → Reference Resources. A *method or rule* → Content
Playbook. A *thing we might write about* → Idea Bank.

## Running it

Invoke the `daily-post` skill to run today's pipeline. See `README.md` for setup and the scheduler smoke-test
before relying on any automated daily trigger.
