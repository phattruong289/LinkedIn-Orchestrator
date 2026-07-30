---
name: log-outcome
description: Closes the loop after Wil reviews a draft. Updates today's Notion Post Log row (posted/killed/tweaked-then-posted) and closes the matching Notion Job Tickets page. Invoke manually after Wil actually acts on a draft — e.g. "mark today's post as posted."
---

# Log outcome

Run this after Wil has actually approved/tweaked/killed a draft — this is what keeps `strategist-writer`'s and
`producer-qa`'s repeat-checks honest, since both compare directly against Notion "Post Log" rows. Notion is the
only place this outcome is recorded.

1. Find today's page in Notion "Job Tickets" (`collection://d135687d-c675-4541-a22b-21170343b397`) — or the date
   the user specifies — and the matching row in Notion "Post Log"
   (`collection://edc91fd0-7523-407c-82d2-df69f4be616d`) for that date.
2. Ask the user (if not already stated) what happened: `posted`, `killed`, or `tweaked_then_posted`.
3. **Update the Post Log row's `Status`** to `posted` / `killed` / `tweaked_then_posted`. Its `Core Argument` and
   `Key Facts Cited` columns were already filled in by `producer-qa` when the draft was created — that's what
   future repeat-checks compare against, so nothing further needs restating here. This status change is also what
   keeps pillar-mix tracking honest — a draft that was killed shouldn't count toward the mix the same way a
   published post does.
4. If the post came from an Idea Bank row, confirm that row is marked `Status: used`.
5. Set the Job Tickets page's `Status` property to `closed`.
6. Confirm back to the user what was logged.
