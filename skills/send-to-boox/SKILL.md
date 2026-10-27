---
name: send-to-boox
description: Put books and files on Alejo's Boox Go7 e-reader. Use when he points you to an EPUB, PDF or other file (often in ~/Downloads) and asks to read it on the Boox, send it to the e-reader, or add it to Morning reader.
---

# Send to Boox

Run these from `~/best/projects/2026-09-25-morning-reader`, whose `AGENTS.md` and
README cover the details.

- **Books to read in sittings** (EPUB or text PDF): `./pack file --boox PATH ...`.
  Each becomes a Morning reader pack, split into 5–15 minute blocks that show on
  Today, the Boox's home screen. Building calls Claude and takes a few minutes per
  book; the run reports its cost.
- **Anything else** (papers, scanned PDFs, illustrated books, comics):
  `./pack send PATH ...` copies the file unchanged into the Boox's `Books` folder,
  where Boox's own reader opens it from the library.

When a PDF book relies on figures, worksheets or tables, do both: the pack drops
them. If the Boox isn't found, ask Alejo to plug it into the Mac by USB.

Afterwards, say which books became packs (with their block counts) and which files
went to the library.
