---
name: log-outcome
description: Closes the loop after Wil reviews a draft. Appends today's outcome (posted/killed/tweaked-then-posted, topic tags, core argument, key facts cited) to posted-log.json and marks the day's job ticket closed. Invoke manually after Wil actually acts on a draft — e.g. "mark today's post as posted."
---

# Log outcome

Run this after Wil has actually approved/tweaked/killed a draft — this is what lets `strategist-writer`'s
repeat-check work at all; without it, `posted-log.json` never grows.

1. Find today's `jobs/YYYY-MM-DD.json` (or the date the user specifies).
2. Ask the user (if not already stated) what happened: `posted`, `killed`, or `tweaked_then_posted`.
3. Append one entry to `posted-log.json`:
   ```json
   {
     "date": "...",
     "topic_tags": [...],
     "hook_summary": "...",
     "core_argument": "1-2 sentence gist of the actual angle/claim, not just the hook",
     "key_facts_cited": ["short label per distinct fact/stat/case-study used, e.g. 'Diesel repeat-campaign', '80-90% studio skim'"],
     "status": "posted|killed|tweaked_then_posted"
   }
   ```
   `topic_tags`/`hook_summary` come from `stages.idea_chosen`; `core_argument`/`key_facts_cited` come from
   `stages.copy` (summarize the actual argument and list which specific facts/stats/case-studies got cited —
   this is what makes future repeat-checks compare substance, not just surface tags).
4. **Update the Notion "Post Log" row** (`collection://edc91fd0-7523-407c-82d2-df69f4be616d`) for that date: set
   `Status` to `posted` / `killed` / `tweaked_then_posted`. This is what keeps the pillar-mix tracking honest —
   a draft that was killed shouldn't count toward the mix the same way a published post does.
5. If the post came from an Idea Bank row, confirm that row is marked `Status: used`.
6. Set the ticket's `status` to `"closed"`.
7. Confirm back to the user what was logged.
