---
name: tidy-project
description: Reorganize a cluttered project or folder into a small reader-facing root, current implementation and data folders, a maintained construction record, and a dated archive. Use only when the user explicitly asks to tidy, organize, clean up, simplify, prune, regroup, or restructure a project or folder. Do not invoke merely because a project appears messy, difficult to navigate, or would benefit from cleanup.
---

# Tidy a project

Read the repository and nearest project instructions before changing files. Inspect the
worktree and preserve unrelated changes.

Infer the project's current outcome from the user's request, working code, current
outputs, and maintained documents. Treat older plans and superseded prototypes as
lineage, not equal alternatives.

Build the smallest useful root from the categories the project actually needs:

- `README.md`: what the project does and what to read next;
- `SPEC.md`: intended outcome, boundary, interfaces, and acceptance checks;
- `STATUS.md`: what works, what is missing, and the next test;
- `pipeline/` or `app/`: executable implementation;
- `data/`: current bounded inputs and outputs;
- `docs/`: current supporting contracts or evidence;
- `reproduce/`: one maintained construction record;
- `archive/`: dated superseded work;
- `private/`: ignored secrets or restricted inputs.

Do not create empty categories. Prefer product stages over file types. Keep the root to
the few documents and folders a new reader needs.

Before moving files, classify each top-level item as current entry point, current
implementation, current data, supporting evidence, reproducibility, private, generated,
or superseded. Resolve ambiguous items from references, imports, tests, dates, and output
lineage. Ask the user only if two plausible classifications imply different project
outcomes, unrelated changes prevent safe moves, a secret may become tracked, or permanent
deletion is required.

Move superseded material into one dated archive package rather than scattering loose
files. Never permanently delete without explicit confirmation. Preserve Git history with
moves where practical.

After moving:

1. Rewrite the root README as a concise map.
2. Update every command, import root, local path, symlink, and Markdown link.
3. Update the construction record with the new paths and decisive request.
4. Run narrow tests, the full relevant suite, realistic entry commands, schema checks,
   symlink checks, and local-link checks.
5. Show the final root and explain what moved to the archive.
6. Commit and push when repository instructions require it.

Do not use this skill to initiate unsolicited cleanup. Once explicitly invoked, make
reversible structural decisions autonomously unless one of the stop conditions above
applies.
