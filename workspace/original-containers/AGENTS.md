# best

See [README.md](README.md) for what this workspace is — the identity and the live
**Questions** map. This file is the standing instructions for working in it.

## Iterate forward
Nothing here is finished; each thing is its current-best version, and the standing job
is to keep making it better — everything, not just code. Global's *Do the work
before asking* governs how: build on the judgment already there rather than churn past it. What's
specific here is the feedback loop — anything I'll use repeatedly should have a
low-friction way to capture friction the moment I feel it, and a path from that friction
to a concrete change.

## Folders are questions
Every folder states its standing question as the first line of its `README.md`; its
`CLAUDE.md`, where present, just points there. The root **Questions** map is generated
from those first lines. Add a folder → give it a one-line-question `README.md` → rerun
sync-repos and it appears in the map. Nesting groups things on my mind; it is not strict
containment — a sub-folder needn't be a sub-category of its parent, and siblings may
reference each other.

## One mega-repo, a few nested repos
`best` is one Git repository of mostly plain folders. Only a few folders are their own
nested Git repos — the private ones, and a few standalone/deployed public ones (see the
**Sub-repositories** table in `README.md`). Git can't reach across a nested `.git`, so a
change inside one belongs to *that* repo: `cd` in and commit there, and don't copy
child contents into a parent repo — the child owns its files, and the parent's ignore
rules stay generated. The symlinked global instructions in `ai/dotfiles/` are one
such nested repo — editing them commits to dotfiles, not here.

Codex also treats a nested Git repo as a new project root. An agent started inside one
inherits the global instructions and that repo's `AGENTS.md`, not this file. Each nested
repo must therefore keep its project instructions self-contained.

Run `ai/sync-repos.py` after adding or removing a nested repo, or after adding a folder's
`README.md` question. It discovers the nested repos directly (no checked-in manifest) and
rewrites the managed `.gitignore` blocks, the per-parent **Sub-repositories** tables, and
the root **Questions** map. It records a nested repo but won't descend into a directory
that repo *ignores*, so a one-off's scratch clones stay off the map. Which nested repos
are private is the one thing it can't derive — hand-listed in `ai/private-paths`. A
tracked git hook (`ai/githooks/pre-commit`, activated by `ai/dotfiles/bin/install.sh`)
runs `--check` on commit and blocks if anything drifted.

## Visibility
The rule: **everything about me is public; things about others are private.** Making
something private is a deliberate call that it's really about someone else, holds their
confided content, or carries credentials. Private so far: `work/tools` (credentials),
`work/calls` (transcripts), `me/relationships/friend`, `me/relationships/partner`,
`other/advice`, and `other/travel/visa` (identity documents). `me/mind` is public — it's
about me.
