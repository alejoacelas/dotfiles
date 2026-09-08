---
name: gdoc-fidelity-test
description: Turn a gdoc CLI failure seen on a real Google Doc into a committed, anonymous fidelity test case in the local gdoc clone (fidelity-tests branch) — frozen snapshots, minimal scripted repro, repros.md entry, pinning pytest. Use when gdoc mangled a document ("every paragraph became a bullet", "edit stripped styles") and the failure should become a test, or when asked to add a fidelity repro or fixture.
---

# gdoc-fidelity-test — from a mangled doc to a committed repro

The harness and its full rules live in the gdoc clone:
`/Users/alejo/best/tools/active/gdoc/cli` (nested git repo, work on branch
`fidelity-tests`), skill `.claude/skills/gdoc-fidelity-test/SKILL.md` there, section
"Reducing a failure seen in a real document". This file is the short checklist.

## Checklist

- Freeze first: `gdoc structure --account <acct> --tab <id> <doc>` and `gdoc pull` of the
  misbehaving doc into a private folder outside the repo. The doc may be fixed or deleted
  any minute. Raw snapshots never enter the repo.
- Find the one odd property: diff the failing tab's structure against a tab that behaves,
  paragraph by paragraph (bullet, indent, namedStyleType, list properties).
- Rebuild only that property in a scratch doc with gdoc plus, if needed, one Docs API
  request from Python (`from gdoc.util import set_active_account`; `from gdoc.api.docs
  import get_docs_service`, run with the uv tool's python). Rerun the failing command.
- If it reproduces, the fixture is scripted and anonymous: `fidelity-tests/<area>/v<NN>/`
  with `build.sh`, seed and input files, `fixture.md` (`status: trashed after capture`),
  `built.md`, `prompt.md`, `tasks.md` (five fields), `baseline/` from `gdt capture`.
- If only the real snapshot reproduces, anonymise it: same-length placeholder text in
  every textRun, all style/bullet/list properties kept; confirm the anonymised copy still
  fails before committing it.
- Record the run: `runs/<YYYYMMDD>-<slug>/` with `before/`, `after/`, `copy_id.txt`,
  `copy_method.txt`, `transcript.md`, `gdt-diff --task` output, `verdict.md` (track
  `command`). Append the `repros.md` entry. Run `bin/gdt index`.
- Pin the fix with a pytest in `tests/`: mock `get_document_with_tabs` with the offending
  body, assert the request the fix must send. It must fail today.
- Add one line for the new test file to `docs/TESTS.md`.
- Trash every scratch doc (Google Drive trash tool). Commit on `fidelity-tests`; do not
  push unless asked. Add a `REPLICATE.md` entry in the repo, then the metadata commit.
- Worked example: `fidelity-tests/write/v01`, `tests/test_write_tab_terminal_bullet.py`,
  LucaDeLeo/gdoc#59.
