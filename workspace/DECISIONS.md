# Workspace decisions

## Core decisions

### Give projects independent homes

- [Keep best and topic folders as ordinary directories](#keep-containers-out-of-git), with separate repositories for projects and coherent note collections.
- [Preserve history and privacy when moving work](#move-projects-with-their-history); parking a project does not reactivate it or authorize publication.

### Name folders by who the work is for

- [File work by client, purpose or kind of output](#file-work-by-who-it-is-for), with `inbox/` for anything unclear.

### Keep shared configuration in one place

- [Maintain container instructions in dotfiles](#maintain-container-instructions-in-dotfiles), adding them only where the folder needs shared rules.

## Details

### File work by who it is for

Status folders (`live/`, `active/`, `stable/`) and loose topics made every new
project start with a guess about how important or finished it would be, so client
work and tool trials ended up scattered across four folders each. The top level
now answers who the work is for: `clients/<company>/` for client projects, linked
to `calls/clients/<company>/`; `projects/` for Alejo's own work, with `in-use/`
for tools he relies on; `trials/` for structured tool tests in one public
repository; `inbox/` when the home is unclear. `proj` creates projects and the
`today` skill files stale ones. 80k and AIM work moved to `archive/` as those
engagements ended. See [projects instructions](projects/AGENTS.md) and
[clients instructions](clients/AGENTS.md).

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

### 2026-10-08

Replace `tools/`, `fun/`, `life/`, `work/` and `projects/live/` with `inbox/`,
`clients/`, `projects/in-use/`, `trials/` and top-level `strategy/`. Moves are
recorded in [archive decisions](/Users/alejo/best/archive/DECISIONS.md) and
[others archive decisions](/Users/alejo/best/projects/others/archive/DECISIONS.md).
