# Guardrails (non-negotiable, applies to every agent in this pipeline)

**Human gate.** No auto-posting, ever, for the `daily-post` pipeline or Wil's profile. Phase 1 has no LinkedIn API
integration at all for that pipeline, so this is trivially true today — keep it true when Phase 2/3 add posting
capability there; don't add auto-posting to Wil's profile without explicitly revisiting this file.

**Scoped exception — `scripts/post-to-linkedin.sh`.** This one script is authorized to run unattended, including
from a scheduled Routine, and to skip its interactive confirmation when `LINKEDIN_AUTOPOST_CONFIRM=PUBLISH` is set
in the environment. This is safe specifically because `LINKEDIN_PERSON_URN` for this script is always Quang's own
personal LinkedIn account, never Wil's — setting that env var in a given run's environment is itself the human
authorization for that run. The text it posts may come from Notion ("Post Log" or "Job Tickets") as well as
manually-typed text — sourcing from Notion does not change the requirement below; what makes this safe is the
*destination account*, not where the text came from. This exception is scoped to this one script and this one
destination account only; it does not extend to any path that posts to Wil's profile, regardless of content
source.

**No invented facts.** Every claim, quote, or stat in a post must trace to a source: Notion's "Past Posts" or
"Reference Resources" databases, `resources/bww-transcripts/`, `resources/company-docs/case-facts.md`, or a live
web/news source with a URL. If nothing verifiable supports an angle, say so — "not found" is a normal, expected
answer. A fabricated stat is not.

**Voice separation.** The default voice is PLAY3's company voice (`resources/voice-guide-play3-company.md`);
`--wil_style` in a run's prompt switches to Wil's personal voice (`resources/voice-guide-wil-personal.md`) for that
run. Both are validated against real posts. They never mix — writing one in the other's register is the failure
this rule prevents.

Only **execution** is voice-specific: register, emoji density, hashtags, section labels, CTA style. Every rule in
this file and in the Content Playbook applies to both unchanged.

**Never name a PLAY3 competitor. Never disparage anyone by name.** These are two separate rules; keep them
separate, because collapsing them was blocking legitimate writing.

*Rule 1 — PLAY3's own competitors stay unnamed.* Anyone selling what PLAY3 sells (brand activations, AI agents,
or intelligence layers inside virtual worlds) is never named, not even neutrally or admiringly. React to the
*pattern* instead: "another studio just ran a gaming activation, here's what that approach misses" is fine; naming
the studio is not. The "named enemy" hook targets a **tactic or a habit** ("rented reach," "counting
impressions," "one-off stunts") — never a company, team, or person. If it's genuinely unclear whether a company
competes with PLAY3, treat it as one.

*Rule 2 — other companies can be named as market context, but never as a target.* Brands, platforms, and IP that
PLAY3 doesn't compete with can appear when they're genuinely part of the picture: the platforms PLAY3 builds on
(Roblox, Fortnite, Discord, Minecraft, Zepeto, TikTok, YouTube, LinkedIn), and a client's own competitive set when
the post is about that client's market. PLAY3's own company page does this — a beauty-brand post naming the other
beauty brands players compare it to is market analysis, not an attack. What's still off-limits regardless of who
it is: implying a company's product is bad, failing, or dishonest, or "unlike {company}, we…" framing.

**Talk about the gap, not the failure.** This applies with extra force to large, well-known companies and to
Roblox itself. There's a real difference between "here's what nobody has solved yet" and "here's what they got
wrong" — write the first. Unmet potential, a missing layer, a question the current tooling can't answer: all fair.
Naming a specific company and then attaching a negative: not fair, even when the criticism is accurate, and
especially when it's a platform PLAY3 depends on.

**Don't congratulate, and don't gush.** A post can reference someone else's campaign as evidence that the category
is working — but if the framing reads as applause for another player in the space, it's a post promoting them, not
PLAY3. Real reader feedback on one such post: it read like congratulating a competitor. When referencing outside
work, the centre of gravity stays on the insight or the gap, not on how impressive the other party was. Flattery
also just reads as inauthentic, which costs more than the goodwill it buys.

**Argue from capability, not from constraint.** PLAY3's case — that signal players give on purpose beats signal
inferred about them — holds for any audience and needs no rulebook to stand up. There are two ways a draft leans
on a sensitive reference instead of the mechanism, and they carry equal weight — neither is a subclause of the
other:

- *Making it about who the audience is.* Dwelling on how young players are, or on what is or isn't served to them,
  narrows a general claim into a special case about minors. At best that reads as uncomfortable; at worst it
  invites the reader to wonder whether the pitch is a route around protections that exist for good reason.
- *Making it about the rules.* Referencing what a privacy regime requires or forbids — GDPR, COPPA, a platform's
  ad policy quoted as law, "data you're not allowed to collect" — casts PLAY3 as the interpreter of regulation
  that isn't its expertise and that shifts underneath it. This includes framing PLAY3's approach as a way to stay
  compliant or to sidestep an infringement: that still puts the rulebook at the centre. Write what the environment
  makes *possible*, not what the rules take away.

Platform rules and the protections around minors stay usable as *context* for why a capability gap exists — what
moves is the weight: onto the gap and PLAY3's answer to it, off the protected group and off the regulation. The
test runs in two passes, because either reference can carry an argument on its own: delete every mention of the
audience's age and re-read, then delete every claim about what a rule requires, forbids, or lets you avoid, and
re-read again. If the argument survives both, it stands on the mechanism. If either deletion collapses it, that
reference was load-bearing and the angle needs replacing, not rewording.

**Only name publicly-cleared clients.** A client name may appear only if it's already public in PLAY3's own
published material — currently Diesel/OTB, Vinamilk/SUSU, Super League, Animal Troll Tower, plus the play3.ai logo
wall (Samsung,
American Eagle, Canon, Casetify, Pudgy Penguins, VeeFriends, Time Studios, Nelvana). Anything heard in a call,
seen in a pipeline, or found in an internal doc is **not** cleared — describe it generically ("a household-name
fashion brand") or don't use it. When in doubt: don't name it — describe it generically and flag the call in the QA
report so whoever reviews the draft can decide.

**Content Playbook, not a voice override.** Notion's **Content Playbook** database
(`collection://94187f4f-93aa-44c7-bbec-81c092b53fda`) holds the method in 5 components: content pillars + target
mix, hook library, post skeletons, idea scoring rubric, and voice + naming rules. It's a layer that improves a
draft's odds of landing — it never overrides the run's active voice guide, which stays authoritative on how that
profile actually sounds. `strategist-writer` applies it; `producer-qa` independently re-checks banned
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
argument/fact comparison against Notion "Post Log"'s (`collection://edc91fd0-7523-407c-82d2-df69f4be616d`) `Core Argument`/`Key Facts Cited` columns), and `producer-qa` again independently as the last check before a human sees
it. This depends on `log-outcome` actually being run after every real post so each row's `Status` reflects what
actually happened — a Post Log with no `posted` rows yet means this check has nothing real to compare against.

**Scope lock.** Profile: PLAY3 company page by default; `--wil_style` switches that run to Wil's personal profile.
Format: text, optionally with a rendered slide carousel — see the `slide-deck` skill. No video. One post per
calendar day. Don't infer otherwise from context — these are hardcoded.

**No generated imagery, anywhere.** Slides are rendered from the HTML/CSS templates in `visuals/`, which means
exact type, the real logo file, and figures that match the copy. Image generation was removed on 2026-07-30 after
producing the wrong canvas size and an approximated wordmark. If a slide needs a real screenshot — a game capture,
an analytics dashboard — and none has been supplied, **drop that slide.** Never substitute a mockup, a generated
image, a stand-in chart, or a description of the missing capture: a fabricated dashboard is a fabricated statistic
that happens to be rendered, and the no-invented-facts rule covers images exactly as it covers text.

**A real, sourced image may go on a slide — under three conditions, all required.** The `media` slide type frames
one real image in-brand (see `slide-deck` and `brand-kit.md`). This is not a loosening of the rule above:
a *generated* image is still banned; only a *real, sourced* one qualifies, and only if —
1. **It has a source, and depicts what the slide claims.** An image that implies something the copy can't support
   is a fabricated claim that happens to be a photo — the no-invented-facts rule applies to it exactly as to a
   stat. A **visible credit line is required whenever the image isn't PLAY3's own** — a press asset, a third-party
   image, anything where attribution is the point. For a PLAY3-owned asset (a play3.ai screenshot, a campaign
   capture) the credit is **optional and usually omitted**: crediting your own site on your own post is clutter,
   not attribution. The provenance still has to be established in the run's report either way; what changes is
   whether it shows on the slide.
2. **Its rights are clear for this use.** Three provenance tiers are usable directly: an asset PLAY3 owns (platform
   or campaign captures), an official press/newsroom asset offered for editorial use, or an image the user supplied
   or approved. An image lifted from an article or a third party, whose rights are unknown, is **not** embedded —
   the run surfaces it to the reviewer as a suggestion with its source link, and it only ships if the human at the
   gate approves it. Republishing someone else's copyrighted image into a branded post unattended is the specific
   thing this prevents.
3. **When either is uncertain, it drops** — the same reflex as a missing screenshot, extended: drop rather than
   fake, and drop rather than infringe. A text slide is a complete slide; an uncleared image is not worth the risk
   it carries.

**`scripts/post-to-linkedin.sh` is a standalone technical experiment, not part of the pipeline.** It exists so
Quang can manually test the LinkedIn Posts API against his own personal account (`LINKEDIN_PERSON_URN` in `.env`
is his, never Wil's). Nothing in `daily-post`, `librarian`, `strategist-writer`, or `producer-qa` calls it — the
"no auto-posting, ever" rule for Wil's actual pipeline is unchanged. The script itself still requires a typed
`PUBLISH` confirmation per run; it does not turn into automated posting on its own.
