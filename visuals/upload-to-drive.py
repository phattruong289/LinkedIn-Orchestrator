#!/usr/bin/env python3
"""Upload a rendered deck file to Google Drive and print a shareable link.

    python visuals/upload-to-drive.py <file> [--folder <folder_id>] [--name <title>]

Streams the file straight from disk to Drive (it never passes through an agent's
context, which is the whole reason this exists), sets it to "anyone with the link:
viewer", and prints the URL to drop on the Notion Post Log row. The link is the deck's
VIEWABLE copy; the deck spec on the ticket stays the durable artifact.

Credentials come from gdrive-token.json (or $GDRIVE_TOKEN path) = {client_id,
client_secret, refresh_token}, produced once by gdrive-auth.py. A default destination
folder can be set with $GDRIVE_FOLDER_ID. Pure standard library — no pip install.

Note on scope: gdrive-auth.py requests drive.file (only files this app creates). That's
enough to upload and to share what it uploaded. If you pass --folder and get a 404 on
the folder, the folder wasn't created by this app — either omit --folder (upload to My
Drive root) or re-mint the token with the broader drive scope.
"""
import json, mimetypes, os, sys, urllib.parse, urllib.request, urllib.error
from pathlib import Path

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD = "https://www.googleapis.com/upload/drive/v3/files"
FILES = "https://www.googleapis.com/drive/v3/files"


def access_token(cred):
    data = urllib.parse.urlencode({
        "client_id": cred["client_id"], "client_secret": cred["client_secret"],
        "refresh_token": cred["refresh_token"], "grant_type": "refresh_token",
    }).encode()
    try:
        return json.loads(urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=data)).read())["access_token"]
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Token refresh failed {e.code}:\n{e.read().decode(errors='replace')}")


def api(method, url, tok, body=None, raw=None, ctype=None):
    h = {"Authorization": "Bearer " + tok}
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    if ctype:
        h["Content-Type"] = ctype
    elif body is not None and raw is None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Drive API {e.code} on {method} {url}\n{e.read().decode(errors='replace')}")


def multipart(meta, content, ctype):
    """multipart/related: JSON metadata part + raw media part, in one request."""
    b = "----play3deck7f3a2b"
    body = b"".join([
        f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode(),
        json.dumps(meta).encode(),
        f"\r\n--{b}\r\nContent-Type: {ctype}\r\n\r\n".encode(),
        content,
        f"\r\n--{b}--\r\n".encode(),
    ])
    return body, f"multipart/related; boundary={b}"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    def opt(name):
        return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None

    if not args:
        raise SystemExit("usage: python visuals/upload-to-drive.py <file> [--folder <id>] [--name <title>]")
    path = Path(args[0])
    if not path.exists():
        raise SystemExit(f"No such file: {path}")

    folder = opt("--folder") or os.environ.get("GDRIVE_FOLDER_ID")
    name = opt("--name") or path.name

    tokfile = Path(os.environ.get("GDRIVE_TOKEN", "gdrive-token.json"))
    if not tokfile.exists():
        raise SystemExit(f"No credentials at {tokfile}. Run gdrive-auth.py first, or set $GDRIVE_TOKEN.")
    cred = json.loads(tokfile.read_text(encoding="utf-8"))
    tok = access_token(cred)

    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    meta = {"name": name}
    if folder:
        meta["parents"] = [folder]

    body, ct = multipart(meta, path.read_bytes(), ctype)
    f = api("POST", UPLOAD + "?uploadType=multipart&supportsAllDrives=true&fields=id,webViewLink",
            tok, raw=body, ctype=ct)

    # "anyone with the link" can view — this is what makes the link openable by a reviewer.
    api("POST", f"{FILES}/{f['id']}/permissions?supportsAllDrives=true",
        tok, body={"role": "reader", "type": "anyone"})

    print(f.get("webViewLink") or f"https://drive.google.com/file/d/{f['id']}/view")


if __name__ == "__main__":
    main()
