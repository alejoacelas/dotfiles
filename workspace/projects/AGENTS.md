# Projects

Alejo's own projects. Client work goes in `~/best/clients/`. Follow the `AGENTS.md`
inside each.

Start a project with `proj <name>`, which creates `YYYY-MM-DD-name` at the top of
this folder. Give it a remote on the first commit and state its scope in
`AGENTS.md`. Parked projects go to `archive/`; keep the date prefix when moving a
project.

## In regular use

Folders without a date prefix hold work Alejo uses regularly. Each has a pointer
below with the date it was last confirmed in use; update that date when you
confirm it again, and archive the folder when it stops being used.

- [cmd-tab](cmd-tab/): the Command-Tab switcher, run as a login item from
  `.build/CmdTab.app`. Running on 2026-10-29.
- [sleep](sleep/): source of the dont-sleep daemon, installed and running from
  `/usr/local/libexec/dont-sleep.sh`. Running on 2026-10-29.
- [gdoc](gdoc/): Google Docs CLI clone, MCP wrapper and notes; the
  `gdoc-fidelity-test` skill works in `cli/`. Last changed 2026-10-08.
- [trials](trials/): structured tool tests, each ending in a one-page verdict.
  Start one with `proj projects/trials/<tool>`. Last trial started 2026-10-08.
- [writing](writing/): essays and explainers; work before October 2026, including
  the guides behind [alejo.wiki](https://alejo.wiki), is in its archive. Last
  changed 2026-09-20.

## File and archive

The `today` skill lists dated projects untouched for two weeks. When it does, or
when asked: read the project, commit pending work, check for running sessions,
then leave it at the top, drop the date prefix and add a pointer above if Alejo
now uses it regularly, or move it to `archive/` if it is unlikely to be
revisited. Before archiving a tool, stop anything that runs it (launchd jobs,
login items, symlinks on `PATH`). Preserve Git history and privacy, record
archive moves and their reason in `archive/README.md`, and update links. Move a project back to the top when work resumes.

## Android

Connect to the phone with `~/best/dotfiles/bin/adb-phone`. It prints the serial
to pass to `adb -s`, or runs `adb` with any arguments you give it. If it can't
find the phone, ask Alejo to turn on Wireless debugging. The phone stays awake
while charging, so plug it in for tests that run in the background.
