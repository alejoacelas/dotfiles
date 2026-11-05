---
name: use-telegram
description: Read and, with Alejo's approval, act on Alejo's personal Telegram account with the `tg` command-line tool. Use when he asks about Telegram chats or messages, wants something found, summarised or answered in Telegram, or wants his Telegram chat list tidied.
---

# Telegram

`tg` reads Alejo's personal Telegram account. It is on `PATH` on the Mac and for the
`agent` user on the agent server. Reading never marks messages as read.

```bash
tg chats --unread            # chats with unread messages, newest first
tg chats --archived          # the Archive folder
tg read "Daniel Zambrano" -n 30 --since 2026-11-01
tg search "invoice" --chat @someone
tg --json read 1347659769    # JSON output for processing
```

A chat can be named by title (exact or a unique part), `@username`, t.me link, numeric id,
a contact's phone number, or `me` (Saved Messages). If a title matches several chats, `tg`
lists them with ids; rerun with the right id.

## Changing anything

`send`, `mark-read`, `archive`, `unarchive`, `archive-joined` and `joined-alerts` need
`--write` and run only on the Mac; the agent server allows only the read commands. Before
`send`, show Alejo the exact recipient and message and wait for his confirmation.

```bash
tg --write send "Daniel Zambrano" "Thanks!" --reply-to 1005
tg --write archive-joined   # archive chats that hold only "X joined Telegram"
```

Setup, credentials and re-login are in
[telegram-cli's AGENTS.md](/Users/alejo/best/projects/2026-11-05-telegram-cli/AGENTS.md).
