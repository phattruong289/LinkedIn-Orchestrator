# Guardrails (non-negotiable, applies to every agent in this pipeline)

**Human gate.** No auto-posting, ever. The pipeline stops at a Slack draft for Wil to review and manually post.
Phase 1 has no LinkedIn API integration at all, so this is trivially true today — keep it true when Phase 2/3 add
posting capability; don't add auto-posting without explicitly revisiting this file.

**No invented facts.** Every claim, quote, or stat in a post must trace to a source: Notion's "Past Posts" or
"Reference Resources" databases, `resources/bww-transcripts/`, `resources/company-docs/case-facts.md`, or a live
web/news source with a URL. If nothing verifiable supports an angle, say so — "not found" is a normal, expected
answer. A fabricated stat is not.

**Voice separation.** Wil's personal voice (`resources/voice-guide-wil-personal.md`) and PLAY3's company voice
(`resources/voice-guide-play3-company.md`) never mix. Phase 1 only uses the personal voice guide. If that guide is
still a placeholder (no real past posts exist yet), say so plainly in the draft so the human reviewer can weigh a
placeholder-voice draft more skeptically than a validated one.

**Never name a competitor. Never disparage by name.** React to the *pattern*, never the company — "another brand
just ran a gaming activation, here's what that approach misses" is fine; naming the company that ran it is not.
This holds even for neutral or complimentary mentions: a blanket rule is harder to get wrong than a judgment call
each time. No "unlike {company}, we…". No implying another company's product is bad, failing, or dishonest. The
"named enemy" hook pattern targets a **tactic or a habit** ("rented reach," "counting impressions," "one-off
stunts") — never a company, a team, or a person. *Exception:* platforms PLAY3 builds on or reacts to as industry
news (Roblox, Fortnite, Discord, Minecraft, Zepeto, TikTok, YouTube, LinkedIn) are not competitors and can be
named. If it's ambiguous whether something is a platform or a competitor, treat it as a competitor.

**Only name publicly-cleared clients.** A client name may appear only if it's already public in PLAY3's own
published material — currently Diesel/OTB, Vinamilk/SUSU, Super League, plus the play3.ai logo wall (Samsung,
American Eagle, Canon, Casetify, Pudgy Penguins, VeeFriends, Time Studios, Nelvana). Anything heard in a call,
seen in a pipeline, or found in an internal doc is **not** cleared — describe it generically ("a household-name
fashion brand") or don't use it. When in doubt: don't name, ask Wil.

**Content Playbook, not a voice override.** Notion's **Content Playbook** database
(`collection://94187f4f-93aa-44c7-bbec-81c092b53fda`) holds the method in 5 components: content pillars + target
mix, hook library, post skeletons, idea scoring rubric, and voice + naming rules. It's a layer that improves a
draft's odds of landing — it never overrides `resources/voice-guide-wil-personal.md`, which stays authoritative on
how Wil actually sounds. `strategist-writer` applies it; `producer-qa` independently re-checks banned
words/phrases, naming-rule violations, and in-body external links (not allowed — reach-suppressing; links belong
in a first-comment note, not the post text).

**Brand lock.** Visuals use `resources/brand-kit.md`'s locked palette/logo/spec — no free-forming a new look each
run. Case-study-specific assets (e.g. `brand-assets/case-studies/susu/`) are only used when the post is actually
about that case study.

**Traceability.** Every job ticket (Notion "Job Tickets", `collection://d135687d-c675-4541-a22b-21170343b397`)
keeps a `run_log` of what ran and when, and every fact in the research pack keeps its source. This is what makes
the pipeline auditable later — and, since it lives in Notion rather than a local file, means a daily run never
needs git write access to complete.

**No near-duplicate posts.** Recurring topics and repeated mentions of the same theme are fine — but a post must
never land ~80% the same in substance (same core argument + same key facts/case-study) as something posted in the
last ~30 days. Checked twice: `strategist-writer` at ideation (tag overlap as a cheap filter, then an actual
argument/fact comparison against Notion "Post Log"'s (`collection://edc91fd0-7523-407c-82d2-df69f4be616d`) `Core
Argument`/`Key Facts Cited` columns), and `producer-qa` again independently as the last check before a human sees
it. This depends on `log-outcome` actually being run after every real post so each row's `Status` reflects what
actually happened — a Post Log with no `posted` rows yet means this check has nothing real to compare against.

**Phase 1 scope lock.** Profile: Wil's personal only (no company page). Format: **text-only only, for now** — no
carousels, no video. `text+single-graphic` is a documented Phase 1 capability (`art-director` agent exists) but is
currently paused by explicit instruction; don't dispatch `art-director` or propose graphic-format ideas until that
pause is lifted. One post per calendar day. Don't infer otherwise from context — these are hardcoded.

**`scripts/post-to-linkedin.sh` is a standalone technical experiment, not part of the pipeline.** It exists so
Quang can manually test the LinkedIn Posts API against his own personal account (`LINKEDIN_PERSON_URN` in `.env`
is his, never Wil's). Nothing in `daily-post`, `librarian`, `strategist-writer`, or `producer-qa` calls it — the
"no auto-posting, ever" rule for Wil's actual pipeline is unchanged. The script itself still requires a typed
`PUBLISH` confirmation per run; it does not turn into automated posting on its own.
