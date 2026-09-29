# Prepare repositories for sharing

## Idea and current state

Capture how to write README and setup documentation that lets peers decide whether to adopt a project and get it running. Preserve flexible document structure, concrete examples, and instructions suited to what the reader already knows.

Status: two draft versions tested; awaiting user comparison. Neither version is a selected winner. Both are now uninstalled so a fresh drafting attempt can start from the original case.

## Evidence and drafts

- [Full draft](draft/SKILL.md) and [concise candidate](draft/versions/concise.md), with their audience profiles. Moved unchanged from `skills/prepare-to-share/` at dotfiles commit `74a8c4c0677f5289e78a0f7a72921fbabdeda806`.
- [Trial manifest](evaluations/2026-09-29/manifest.json) records the exact task, model, input and result commits, and assigned variants; [reports and limitations](evaluations/2026-09-29/README.md) describe what was verified.
- Original requests, source conversation and subsequent corrections are employer-derived. Their private case record is `~/best/dotfiles/private-skills/skill-cases/prepare-to-share/case.md`; keep that evidence private.
- [Review interface](https://github.com/alejoacelas/2026-09-skill-review/tree/10fef0a2bef7c14c4e49092cf930a695b5b7feb7) preserves the compared documents, source manifest and grading interface. Local checkout: `~/best/projects/live/2026-09-skill-review`; run `python3 server.py` there and open http://127.0.0.1:8767.

## Review criteria

Inspect the opening and full README separately. Ask which opening to keep (A, B, combine, neither, cannot judge); mark passages as bad writing, remove, or move to a linked file. Record missing information with a note. Compare selected differences, choose what to retain, and decide whether it belongs in the README or a linked file. Executable setup scripts belong in a linked file when they distract from the README's purpose.

These criteria were refined by the user; the private evidence preserves their wording. Interface test feedback is synthetic, not user approval. The curated differences are not an exhaustive diff.

## Resume and next decision

The user requested a new Claude conversation ending before the first skill-creation request, without the existing drafts in its context. The original session remains intact. Drafts are stored here outside installed skill registries. Do not supply these drafts or the later evaluation discussion to that fresh attempt. This is context separation on one machine, not a filesystem sandbox.

After the user drafts a new version, compare it with these preserved candidates using agreed criteria. Do not run additional trials until authorized.
