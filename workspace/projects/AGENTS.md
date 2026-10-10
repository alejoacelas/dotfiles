# Projects

Alejo's own projects. Client work goes in `~/best/clients/`, tool trials in
`~/best/trials/`.

Start a project with `proj <name>`, which creates `YYYY-MM-DD-name` at the top of
this folder. Give it a remote on the first commit and state its scope in
`AGENTS.md`. Active projects stay at the top; `in-use/` and `archive/` are
ordinary directories whose shared files live in dotfiles. Keep the date prefix
when moving a project.

## File and archive

The `today` skill lists top-level projects untouched for two weeks. When it does,
or when asked: read the project, commit pending work, check for running sessions,
then leave it at the top, move it to `in-use/` if Alejo now relies on it (dropping
the date prefix), or to `archive/` if it is unlikely to be revisited. Preserve Git
history and privacy, record archive moves and their reason in
`archive/DECISIONS.md`, and update links, `archive/README.md` and the `in-use/`
README. Move a project back to the top when work resumes.

## Android

Connect to the phone with `~/best/dotfiles/bin/adb-phone`. It prints the serial
to pass to `adb -s`, or runs `adb` with any arguments you give it. If it can't
find the phone, ask Alejo to turn on Wireless debugging. The phone stays awake
while charging, so plug it in for tests that run in the background.
