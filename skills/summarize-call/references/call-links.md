# Links to share after a call

After the call's doc is shared, Alejo gets one email, to himself only, with the doc and
the links he might send the other participants. Nobody else gets it.

## What to collect

1. **Mentioned**: every resource the call hinted at: a doc, post, tool, repo, paper,
   person's site or anything either side said they'd send ("I'll send you the playbook").
   Find the actual URL; leave one out rather than guess. Cap: none, but list each once.
2. **Suggested**: at most 7 others he could share because they bear on what the call
   discussed. Fewer is fine; none is fine. Pick the most useful, not the most.

Where to look, for both:

- His Google Docs, private and public: `gog -a <account> -j drive search "<words>" --max 10`
  on both accounts (`alejoacelas@gmail.com`, `alejo@impact-ops.org`), a few searches with
  the call's topics.
- `~/best/desk/sent/`: what he has already sent people (its `gdoc:` and links).
- `~/best/desk/notes/` with `written_by: alejo` or `mixed`, and their `gdoc:`.
- His public repositories: `gh repo list alejoacelas --visibility public --limit 100`.
- `~/best/desk/links/work/`: pages he has read lately (`rg -i '<topic>' ~/best/desk/links/work`).
- The web, only to find the URL of something named in the call.

Never suggest anything from another person's call or private conversation, a doc someone
else owns that wasn't shared with this participant, or an item in `generated/` or
`requested/`.

## Private or public

For each Google Doc, check sharing: `gog -a <account> -j drive permissions <file id>`.
It is `public` only when anyone with the link can view; otherwise `private`, so Alejo
checks sharing before passing it on. Mark a private repository or any page that needs
his login `private` too.

## What it looks like

```json
{"mentioned": [{"title": "...", "url": "...", "private": false, "note": "Nic asked for it"}],
 "suggested": [{"title": "...", "url": "...", "private": true, "note": "why it fits, in one line"}]}
```

The email, plain text and short:

```
Subject: Links to share: <call doc title>

Call doc: <title>
<doc link> (shared with <names>, or "not shared")

Mentioned in the call:
- <title> [private]: <url>
  <note>

You could also share:
- ...

[private] means only you can open it so far: check its sharing before you pass it on.
```

Leave out a section that has nothing. Send it from and to `alejoacelas@gmail.com`,
whatever account owns the doc:

```bash
gog -a alejoacelas@gmail.com gmail send --to alejoacelas@gmail.com --subject "<subject>" --body-file "$CALL_TMP/links-email.txt"
```
