#!/usr/bin/env bash
# Render a slide template to a 1080x1080 PNG with headless Chrome.
# Usage: ./visuals/render.sh cover.html slide-test.png
#
# No dependencies beyond a local Chrome — deliberately, so a run doesn't need
# npm install or a network fetch. Fonts are vendored in visuals/fonts/.

set -euo pipefail
cd "$(dirname "$0")/.."

TEMPLATE="${1:-cover.html}"
OUT="${2:-slide-test.png}"

CHROME=""
for c in \
  "/c/Program Files/Google/Chrome/Application/chrome.exe" \
  "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
  "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  "/c/Program Files/Microsoft/Edge/Application/msedge.exe" \
  "$(command -v google-chrome || true)" \
  "$(command -v chromium || true)"
do
  if [ -n "$c" ] && [ -f "$c" ]; then CHROME="$c"; break; fi
done
if [ -z "$CHROME" ]; then
  echo "No Chrome or Edge found. Install one, or point CHROME at a binary." >&2
  exit 1
fi

# Chrome needs a file:// URL with a Windows-style path
ABS="$(cd visuals && pwd)/$TEMPLATE"
URL="file:///$(echo "$ABS" | sed 's|^/\([a-z]\)/|\1:/|')"
ABS_OUT="$(pwd)/$OUT"
WIN_OUT="$(echo "$ABS_OUT" | sed 's|^/\([a-z]\)/|\1:/|')"

"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=1080,1080 \
  --virtual-time-budget=2500 \
  --screenshot="$WIN_OUT" "$URL" 2>&1 | grep -vE "^\[|DevTools|Fontconfig" || true

if [ ! -f "$OUT" ]; then echo "Render failed: no output at $OUT" >&2; exit 1; fi
echo "Rendered $TEMPLATE -> $OUT"
