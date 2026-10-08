# Projects

Alejo's own projects. Client work goes in `~/best/clients/`, tool trials in
`~/best/trials/`.

Start a project with `proj <name>`, which creates `YYYY-MM-name` at the top of
this folder. Give it a remote on the first commit and state its scope in
`AGENTS.md`. Topic folders are ordinary directories whose shared files live in
dotfiles.

## File and archive

The `today` skill lists top-level projects untouched for two weeks. When it does,
or when asked: read the project, commit pending work, check for running sessions,
then move it to its topic folder, to `in-use/` if Alejo now relies on it, or to
`<topic>/archive/` if it is unlikely to be revisited. Preserve Git history and
privacy, record the move and its reason in the archive's `DECISIONS.md`, and update
links and indexes. Move a project back to the top when work resumes. If no folder
fits, suggest a structural change.

## Android

Connect to the phone with `~/best/dotfiles/bin/adb-phone`. It prints the serial
to pass to `adb -s`, or runs `adb` with any arguments you give it. If it can't
find the phone, ask Alejo to turn on Wireless debugging. The phone stays awake
while charging, so plug it in for tests that run in the background.
