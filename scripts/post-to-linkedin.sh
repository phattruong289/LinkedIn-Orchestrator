#!/usr/bin/env bash
# LinkedIn post via the Posts API — Phase 2+ experiment only, scoped to Quang's own personal account.
#
# This is NOT wired into the daily-post pipeline and never touches Wil's profile (see .env / the environment —
# LINKEDIN_PERSON_URN belongs to Quang, not Wil). It can run unattended (e.g. from a scheduled Routine) only when
# LINKEDIN_AUTOPOST_CONFIRM=PUBLISH is explicitly set in that run's environment, per the scoped exception in
# .claude/rules/guardrails.md — setting that var is itself the human authorization. Without it, every invocation
# stops for an interactive PUBLISH confirmation.
#
# Usage:
#   ./scripts/post-to-linkedin.sh "post text here"
#   ./scripts/post-to-linkedin.sh < draft.txt

set -euo pipefail
cd "$(dirname "$0")/.."

# Works two ways: a local .env file (git-ignored, never committed), or the three vars already exported in the
# shell environment (e.g. set manually in a cloud environment's config — also never committed anywhere).
if [ -f .env ]; then
  set -a; source .env; set +a
fi
: "${LINKEDIN_ACCESS_TOKEN:?Not set. Provide via .env or the environment — see script header.}"
: "${LINKEDIN_PERSON_URN:?Not set. Provide via .env or the environment — see script header.}"
: "${LINKEDIN_API_VERSION:?Not set. Provide via .env or the environment — see script header.}"

if [ -n "${1:-}" ]; then
  TEXT="$1"
else
  TEXT="$(cat)"
fi

if [ -z "$TEXT" ]; then
  echo "No text provided (arg or stdin)." >&2
  exit 1
fi

PAYLOAD=$(python3 -c '
import json, sys
text = sys.stdin.read()
person_urn = sys.argv[1]
print(json.dumps({
    "author": person_urn,
    "commentary": text,
    "visibility": "PUBLIC",
    "distribution": {
        "feedDistribution": "MAIN_FEED",
        "targetEntities": [],
        "thirdPartyDistributionChannels": []
    },
    "lifecycleState": "PUBLISHED",
    "isReshareDisabledByAuthor": False
}))
' "$LINKEDIN_PERSON_URN" <<< "$TEXT")

echo "About to POST as $LINKEDIN_PERSON_URN. Preview:"
echo "---"
echo "$TEXT"
echo "---"

# Unattended runs (e.g. a scheduled Routine) can't answer an interactive prompt. Setting
# LINKEDIN_AUTOPOST_CONFIRM=PUBLISH in that run's own environment IS the human authorization for that run — see
# the "Scoped exception" note in .claude/rules/guardrails.md. Scoped to this script and Quang's own account only.
if [ "${LINKEDIN_AUTOPOST_CONFIRM:-}" = "PUBLISH" ]; then
  echo "LINKEDIN_AUTOPOST_CONFIRM=PUBLISH set — skipping interactive prompt."
else
  read -r -p "Type PUBLISH to confirm, anything else to abort: " CONFIRM
  if [ "$CONFIRM" != "PUBLISH" ]; then
    echo "Aborted."
    exit 1
  fi
fi

HTTP_CODE=$(curl -s -o /tmp/li-post-response.json -w "%{http_code}" \
  -X POST "https://api.linkedin.com/rest/posts" \
  -H "Authorization: Bearer $LINKEDIN_ACCESS_TOKEN" \
  -H "Linkedin-Version: $LINKEDIN_API_VERSION" \
  -H "X-Restli-Protocol-Version: 2.0.0" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "HTTP $HTTP_CODE"
cat /tmp/li-post-response.json 2>/dev/null || true
echo ""

if [ "$HTTP_CODE" != "201" ]; then
  echo "Post failed." >&2
  exit 1
fi
echo "Posted."
