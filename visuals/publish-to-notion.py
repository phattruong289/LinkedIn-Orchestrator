#!/usr/bin/env python3
"""Upload a bundled deck to Notion and attach it to a page — without routing the file
through an agent's context.

    python visuals/publish-to-notion.py <file.html> <page_id> [--caption "..."]

Why this exists: the deck bundle is ~90 KB. An agent *can* read it and pass it to the
Notion MCP attachment tool, but that means reproducing 90 KB — a third of it base64 font
data — character for character, every run. One wrong byte silently breaks a font, and it
burns ~45k tokens each time. The file should go from disk to Notion directly, and this
does that.

Needs NOTION_TOKEN in the environment (a Notion internal integration token, and the
target page must be shared with that integration). Nothing else.
"""

import json, mimetypes, os, sys, urllib.request, urllib.error
from pathlib import Path

API = "https://api.notion.com/v1"
VERSION = os.environ.get("NOTION_VERSION", "2025-09-03")  # file uploads need a recent version


def token():
    t = os.environ.get("NOTION_TOKEN")
    if not t:
        raise SystemExit(
            "NOTION_TOKEN is not set.\n\n"
            "  1. Create an internal integration at https://www.notion.so/profile/integrations\n"
            "  2. Share the target page with it (page ... menu -> Connections)\n"
            "  3. Put the token in .env locally, and in the Routine environment for automated runs\n\n"
            "Note the cloud environment stores variables in plaintext visible to anyone who can "
            "edit it — scope the integration to just the databases it needs."
        )
    return t


def call(method, url, body=None, headers=None, raw=None):
    h = {"Authorization": f"Bearer {token()}", "Notion-Version": VERSION}
    h.update(headers or {})
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    if body is not None and raw is None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise SystemExit(f"Notion API {e.code} on {method} {url}\n{detail}")


def multipart(path: Path, content_type: str):
    """Minimal multipart/form-data body — avoids a requests dependency."""
    boundary = "----play3deck7f3a2b"
    body = b"".join([
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n".encode(),
        path.read_bytes(),
        f"\r\n--{boundary}--\r\n".encode(),
    ])
    return body, f"multipart/form-data; boundary={boundary}"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    caption = None
    if "--caption" in sys.argv:
        caption = sys.argv[sys.argv.index("--caption") + 1]
    if len(args) < 2:
        raise SystemExit("usage: python visuals/publish-to-notion.py <file.html> <page_id> [--caption ...]")

    path = Path(args[0])
    page_id = args[1].replace("-", "")
    if not path.exists():
        raise SystemExit(f"No such file: {path}")

    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    size = path.stat().st_size

    # 1. announce the upload
    up = call("POST", f"{API}/file_uploads",
              body={"mode": "single_part", "filename": path.name, "content_type": ctype})

    # 2. send the bytes straight from disk
    body, ct = multipart(path, ctype)
    call("POST", up["upload_url"], raw=body, headers={"Content-Type": ct})

    # 3. attach it to the page. HTML goes in as an embed so Notion renders the preview
    #    inline; anything else attaches as a file block.
    block = ({"object": "block", "type": "embed",
              "embed": {"url": f"file-upload://{up['id']}"}}
             if ctype.startswith("text/html") else
             {"object": "block", "type": "file",
              "file": {"type": "file_upload", "file_upload": {"id": up["id"]}}})
    children = [block]
    if caption:
        children.insert(0, {"object": "block", "type": "paragraph",
                            "paragraph": {"rich_text": [{"type": "text", "text": {"content": caption}}]}})

    call("PATCH", f"{API}/blocks/{page_id}/children", body={"children": children})
    print(f"Attached {path.name} ({size/1024:.0f} KB) to page {page_id}")


if __name__ == "__main__":
    main()
