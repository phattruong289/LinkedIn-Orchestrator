#!/usr/bin/env bash
# One-off, manually-confirmed LinkedIn comment via the same Posts API credentials — Phase 2+ experiment only,
# scoped to Quang's own personal account, same spirit as post-to-linkedin.sh.
#
# Manual-only by design: unlike post-to-linkedin.sh, this script has NO unattended/AUTOPOST_CONFIRM bypass.
# Scripted/bulk commenting is explicitly out of scope here — see .claude/rules/guardrails.md and the deferred
# "growth engine" discussion (docs/newtask.md §12). This is a single manual technical test, nothing more.
#
# Usage:
#   ./scripts/comment-on-linkedin.sh "urn:li:share:XXXXXXXXXX" "comment text"
#   ./scripts/comment-on-linkedin.sh "urn:li:share:XXXXXXXXXX" < comment.txt

set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -a; source .env; set +a
fi
: "${LINKEDIN_ACCESS_TOKEN:?Not set. Provide via .env or the environment.}"
: "${LINKEDIN_PERSON_URN:?Not set. Provide via .env or the environment.}"
: "${LINKEDIN_API_VERSION:?Not set. Provide via .env or the environment.}"

# Some Windows setups alias `python3` to a Microsoft Store stub that fails at runtime rather than being absent —
# `command -v` alone can't detect that, so actually try running it.
PYBIN=python3
if ! "$PYBIN" -c "" >/dev/null 2>&1; then PYBIN=python; fi

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <target-post-urn> [comment text]" >&2
  echo 'Example target URN: urn:li:share:7123456789012345678' >&2
  exit 1
fi
OBJECT_URN="$1"

if [ -n "${2:-}" ]; then
  TEXT="$2"
else
  TEXT="$(cat)"
fi
if [ -z "$TEXT" ]; then
  echo "No comment text provided (2nd arg or stdin)." >&2
  exit 1
fi

PAYLOAD=$("$PYBIN" -c '
import json, sys
actor, text = sys.argv[1], sys.argv[2]
print(json.dumps({"actor": actor, "message": {"text": text}}))
' "$LINKEDIN_PERSON_URN" "$TEXT")

# LinkedIn requires the object URN URL-encoded as the path segment.
ENCODED_URN=$("$PYBIN" -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$OBJECT_URN")

echo "About to comment as $LINKEDIN_PERSON_URN on $OBJECT_URN. Preview:"
echo "---"
echo "$TEXT"
echo "---"
read -r -p "Type PUBLISH to confirm, anything else to abort: " CONFIRM
if [ "$CONFIRM" != "PUBLISH" ]; then
  echo "Aborted."
  exit 1
fi

HTTP_CODE=$(curl -s -o /tmp/li-comment-response.json -w "%{http_code}" \
  -X POST "https://api.linkedin.com/rest/socialActions/${ENCODED_URN}/comments" \
  -H "Authorization: Bearer $LINKEDIN_ACCESS_TOKEN" \
  -H "Linkedin-Version: $LINKEDIN_API_VERSION" \
  -H "X-Restli-Protocol-Version: 2.0.0" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "HTTP $HTTP_CODE"
cat /tmp/li-comment-response.json 2>/dev/null || true
echo ""

if [ "$HTTP_CODE" != "201" ]; then
  echo "Comment failed." >&2
  exit 1
fi
echo "Comment posted."
