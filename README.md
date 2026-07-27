# PLAY3 LinkedIn Content Agent Pipeline — Phase 1

See `CLAUDE.md` for how the project is organized, `docs/task-and-requirements.md` for the original brief, and
`docs/phase1-plan.md` for the full build plan.

## Prerequisites before the first real run

1. **Authorize the Slack connector** (`marketing:slack`) and tell it which channel `daily-post` should post drafts
   to. Until this is done, the pipeline can run through Producer-QA but can't deliver the final draft.
2. **(Optional, improves quality) Supply real content**: drop a few of Wil's actual past LinkedIn posts into
   `resources/past-posts/`, and any BWW transcripts into `resources/bww-transcripts/`. Without these, every draft
   is flagged as voice-unvalidated (see `resources/voice-guide-wil-personal.md`).

**Images are currently paused** — the pipeline runs text-only for now. `art-director` (Stage 4, visuals) exists and
was validated in a test run, but a real image-gen tooling gap surfaced (output came out ~1024×1024, not the
required 1200×1200; the brand logo was a prompted approximation, not a pixel-exact composite) — resolve that before
turning graphics back on. Until then, `daily-post` never dispatches `art-director` and always sets `stages.visual: null`.

## Running manually

Ask Claude to run the `daily-post` skill. It creates/resumes today's `jobs/YYYY-MM-DD.json`, runs the pipeline
stages in order, and posts a Slack message when a draft passes QA.

After you act on a Slack draft (post it, tweak it, or kill it), run the `log-outcome` skill so
`posted-log.json` grows and future ideation avoids repeating today's topic.

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

1. Run `daily-post` manually a few times first and confirm the output quality/Slack flow works.
2. Verify working-directory/file-access behavior once, either via a one-time Local Scheduled Task (fully
   self-contained prompt: "cd to this project folder, confirm `.claude/agents/` has 4 files, write
   `jobs/_scheduler-probe.json` with `{"ok": true}`, then stop") or via a one-off Routine — check it actually ran
   with the right working directory and could write the file.
3. Set up the **recurring daily trigger as a Routine**, not a Local Scheduled Task, so it survives the machine
   being off/asleep.
