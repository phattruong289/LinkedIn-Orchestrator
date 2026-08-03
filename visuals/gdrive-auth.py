#!/usr/bin/env python3
"""One-time: turn a downloaded OAuth *client* secret into a stored refresh token.

    python visuals/gdrive-auth.py <client_secret.json> [gdrive-token.json]

Run this ONCE, on your own machine, signed in (in the browser it opens) to the Google
account that owns the Drive the decks should live in. It writes gdrive-token.json =
{client_id, client_secret, refresh_token}. That file is the credential upload-to-drive.py
reads; put its contents in the Routine environment for automated runs.

  - It is a secret — never commit it (see .gitignore).
  - Pure standard library: no pip install.
  - Uses the OAuth loopback flow (Google removed the copy-paste "oob" flow), so it
    briefly runs a localhost server to catch the redirect. Your OAuth client must be of
    type "Desktop app", which permits any localhost port.
"""
import http.server, json, sys, urllib.parse, urllib.request, urllib.error, webbrowser
from pathlib import Path

SCOPE = "https://www.googleapis.com/auth/drive.file"  # only files this app creates
AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN = "https://oauth2.googleapis.com/token"


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python visuals/gdrive-auth.py <client_secret.json> [gdrive-token.json]")
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    cfg = cfg.get("installed") or cfg.get("web") or cfg
    client_id, client_secret = cfg["client_id"], cfg["client_secret"]
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("gdrive-token.json")

    got = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            got.update(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query))
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Done. Close this tab and return to the terminal.".encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    redirect = f"http://127.0.0.1:{srv.server_address[1]}"
    url = f"{AUTH}?" + urllib.parse.urlencode({
        "client_id": client_id, "redirect_uri": redirect, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent",
    })
    print("A browser will open for you to approve. If it doesn't, paste this URL:\n", url)
    webbrowser.open(url)
    srv.handle_request()  # blocks until the redirect arrives, then returns

    if "code" not in got:
        raise SystemExit(f"No authorization code received: {got}")

    data = urllib.parse.urlencode({
        "code": got["code"][0], "client_id": client_id, "client_secret": client_secret,
        "redirect_uri": redirect, "grant_type": "authorization_code",
    }).encode()
    try:
        resp = json.loads(urllib.request.urlopen(urllib.request.Request(TOKEN, data=data)).read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Token exchange failed {e.code}:\n{e.read().decode(errors='replace')}")

    refresh = resp.get("refresh_token")
    if not refresh:
        raise SystemExit(
            "No refresh_token returned. Google only sends one on first consent — revoke the app at "
            "https://myaccount.google.com/permissions and run this again (prompt=consent is already set).\n"
            f"Response: {resp}"
        )

    out.write_text(json.dumps(
        {"client_id": client_id, "client_secret": client_secret, "refresh_token": refresh}, indent=2
    ), encoding="utf-8")
    print(f"\nWrote {out}. This is a secret — keep it out of git. You're done here.")


if __name__ == "__main__":
    main()
