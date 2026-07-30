# PLAY3 LinkedIn Content Agent Pipeline

See `CLAUDE.md` for how the project is organized and `docs/` for the original brief and build plan.

## Prerequisites

**Notion access is the only hard requirement** — all pipeline state and every reference database live there. Slack
is optional: if its connector isn't authorized, drafts are delivered as Notion "Post Log" rows instead and the run
still completes.

Optional, improves quality: drop any BWW transcripts into `resources/bww-transcripts/`. Both voice guides are
already validated against real published posts (10 of Wil's, 9 of the company page's, all in Notion "Past Posts").

**Images are currently paused** — the pipeline runs text-only for now. `art-director` (Stage 4, visuals) exists and
was validated in a test run, but a real image-gen tooling gap surfaced (output came out ~1024×1024, not the
required 1200×1200; the brand logo was a prompted approximation, not a pixel-exact composite) — resolve that before
turning graphics back on. Until then, `daily-post` never dispatches `art-director` and always sets `stages.visual: null`.

## Running manually

Ask Claude to run the `daily-post` skill. It creates or resumes today's page in Notion "Job Tickets", runs the
stages in order, and writes the finished draft to Notion "Post Log" (plus Slack, if authorized). Runtime state is
entirely in Notion, so a run needs no local file and no git write access.

Writes in PLAY3's company voice by default. Add **`--wil_style`** to draft for Wil's personal profile instead.

After acting on a draft, run `log-outcome` so the Post Log row's `Status` reflects what happened — the
repeat-checks depend on it.

## Turning on a daily schedule — two different mechanisms, pick the right one

Do **not** use `CronCreate`/the ephemeral cron tools for this — they're session-only and auto-expire within a week.

There are two real options, with very different reliability:

- **Local Scheduled Tasks** (`mcp__scheduled-tasks`, the local `schedule` skill) — stored on this machine
  (`C:\Users\<user>\.claude\scheduled-tasks\`), but **only runs while the Claude Code app is open and the
  computer is awake**. If the app is closed or the machine is asleep/off when the task is due, it just runs on
  next launch — silently late, not a real daily trigger unless you keep the app running continuously.
- **Routines** (`/schedule` from an authenticated claude.ai session, or `claude.ai/code/routines`) — runs on
  Anthropic's cloud infrastructure, independent of whether your machine or the app is on. This is the one to use
  for a real "fires every day no matter what" trigger.

**Recommended path:**

1. Run `daily-post` manually a few times and confirm the output quality.
2. Set up the **recurring trigger as a Routine**, not a Local Scheduled Task, so it survives the machine being
   off or asleep. Two currently live: `daily-post-linkedin` (daily) and `idea-harvest-linkedin` (Fridays).

A Routine needs the repo connected as its cloud environment's source, and Notion added as a connector at
`claude.ai/customize/connectors` with access to the workspace holding the databases. **It does not need GitHub
write access** — pipeline state is in Notion. Write access only matters if you want a Routine to commit code
changes to the pipeline itself.

Two limits worth knowing before debugging a failed run: the cloud environment's egress is allowlisted, so an
external API call fails with a proxy `403` unless that host is added under **Network access → Custom**; and
environment variables there are stored in plaintext visible to anyone who can edit the environment, so don't leave
credentials in them.
