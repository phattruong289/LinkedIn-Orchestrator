#!/usr/bin/env bash
# Manual, one-off LinkedIn post via the Posts API — Phase 2+ experiment only.
#
# This is NOT wired into the daily-post pipeline and never runs automatically. It exists so Quang can manually
# test the posting path on his own LinkedIn account (see .env — LINKEDIN_PERSON_URN belongs to Quang, not Wil).
# Every invocation requires the caller to have already confirmed the exact text with a human before running this.
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
read -r -p "Type PUBLISH to confirm, anything else to abort: " CONFIRM
if [ "$CONFIRM" != "PUBLISH" ]; then
  echo "Aborted."
  exit 1
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
