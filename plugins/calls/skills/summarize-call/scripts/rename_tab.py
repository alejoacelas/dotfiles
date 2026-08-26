#!/usr/bin/env python3
"""Rename a Google Docs tab: rename_tab.py <doc_id> <tab_id> <new title>.

`gdoc` can add tabs but not rename one, and a new doc's first tab is always
"Tab 1". Uses gdoc's default-account token, or $GDOC_ACCOUNT if set; run it with
gdoc's interpreter:  $(head -1 "$(which gdoc)" | cut -c3-) rename_tab.py ...
"""
import json, os, sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession, Request

doc, tab, title = sys.argv[1:4]
cfg = os.path.expanduser("~/.config/gdoc")
account = os.environ.get("GDOC_ACCOUNT") or json.load(open(f"{cfg}/config.json"))["default_account"]
creds = Credentials.from_authorized_user_info(json.load(open(f"{cfg}/accounts/{account}/token.json")))
if not creds.valid:
    creds.refresh(Request())
body = {"requests": [{"updateDocumentTabProperties": {
    "tabProperties": {"tabId": tab, "title": title}, "fields": "title"}}]}
r = AuthorizedSession(creds).post(f"https://docs.googleapis.com/v1/documents/{doc}:batchUpdate", json=body)
r.raise_for_status()
print(f"renamed {tab} → {title!r}")
