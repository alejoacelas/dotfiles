# Workspace decisions

## Core decisions

### Give projects independent homes

- [Keep best and topic folders as ordinary directories](#keep-containers-out-of-git), with separate repositories for projects and coherent note collections.
- [Preserve history and privacy when moving work](#move-projects-with-their-history); parking a project does not reactivate it or authorize publication.

### Keep shared configuration in one place

- [Maintain container instructions in dotfiles](#maintain-container-instructions-in-dotfiles), adding them only where the folder needs shared rules.

## Details

### Keep containers out of Git

A repository spanning the whole workspace would mix unrelated projects, histories
and privacy requirements. Project repositories have their own remotes; lifecycle
and topic folders organize them without becoming repositories themselves. See
[workspace instructions](/Users/alejo/best/AGENTS.md) and the dotfiles reorganization
commits `971fe1e` and `54fb63c`.

### Move projects with their history

Read destination instructions before moving a project, preserve its repository and
uncommitted work, and repair affected paths. Use the archive appropriate to the
project and the user's choices; the former single-archive rule is obsolete.
Record a consequential move's old location and reason where future work will find
it. Employer material and other people's private information stay private.
See [move procedures](/Users/alejo/best/dotfiles/agents/workflows.md#creating-or-moving-projects).

### Maintain container instructions in dotfiles

The dotfiles workspace tree supplies files through symlinks. It is configuration
for ordinary folders, not duplicate project repositories. A folder needs its own
AGENTS.md only when it has rules worth applying there; individual projects keep
their essential instructions inside their own repositories.

The installer backs up conflicting real files. Update the source and installer
mapping instead of maintaining divergent installed copies. See the
[dotfiles decisions](/Users/alejo/best/dotfiles/DECISIONS.md#version-projects-and-container-configuration-separately)
and the [workspace source](/Users/alejo/best/dotfiles/workspace/).

## Decision log

### 2026-09-25

Keep projects aimed at exploration and fun in `~/best/fun/`. New projects start directly in this
folder and retain the independent repositories and archiving conventions used
elsewhere. See [fun instructions](fun/AGENTS.md) and `0b96174`.
