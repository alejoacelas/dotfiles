# Projects

Alejo's own projects, each a repository named `YYYY-MM-DD-name`. Client work goes
in `~/best/clients/`. Follow the `AGENTS.md` inside each.

Start a project with `proj <name>`, which creates `YYYY-MM-DD-name` here. Give it
a remote on the first commit and state its scope in `AGENTS.md`.

## File and archive

The `today` skill lists projects untouched for two weeks. When it does, or when
asked: read the project, commit pending work and check for running sessions. Then
leave it here, move it to `~/best/archive/` with its date prefix if it is unlikely
to be revisited, or, if Alejo now uses it regularly, propose moving it to
`~/best/stash/` without the date prefix and move it only once he approves. Before archiving a tool, stop anything that runs it
(launchd jobs, login items, symlinks on `PATH`). Preserve Git history and privacy,
record archive moves and their reason in `~/best/archive/README.md`, and update
links. Move a project back here when work resumes.

## Android

Connect to the phone with `~/best/stash/dotfiles/bin/adb-phone`. It prints the
serial to pass to `adb -s`, or runs `adb` with any arguments you give it. If it
can't find the phone, ask Alejo to turn on Wireless debugging. The phone stays
awake while charging, so plug it in for tests that run in the background.
