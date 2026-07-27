# Past posts

Moved to Notion as of 2026-07-23 — **no local mirror anymore** (a manually-kept copy here would just drift out of
sync with what Wil actually edits in Notion).

**Source of truth:** the "Past Posts" database on the shared `TESTING` Notion page, under the `# LinkedIn` heading:
https://app.notion.com/p/3a47bffd8bc34fa3a7c1b714e550e605 (data source:
`collection://5e65485f-b56e-42c1-9456-662a44e6656c`). 10 real posts from Wil currently in there, each tagged
`Author: Wil (personal)`.

`librarian.md` reads this directly via the Notion MCP connector (`9787b242-...`), with a defensive fallback if
Notion is unreachable in a given run — see that agent file for details. This folder exists as a placeholder so the
path referenced elsewhere in the project (`resources/past-posts/`) still resolves to something, even though it's
empty locally.

**Adding a new post:** paste it into the Notion database directly (set `Author`, `Format`, `Tags`) — no need to
touch any local file.
