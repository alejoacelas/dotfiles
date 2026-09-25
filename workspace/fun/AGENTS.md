# Fun

This folder is for projects aimed at exploration and fun.

Start new projects directly here. Name them `YYYY-MM-project-name`, give each its
own Git repository and remote, and state what it explores in its `AGENTS.md`.
Topic folders are ordinary directories whose shared files live in dotfiles.

When asked to organize: read the projects, commit pending work, and check for running
sessions before moving anything. Group related projects in topic folders and move
projects unlikely to be revisited into `archive/` or `<topic>/archive/`. Preserve
Git history and privacy, record each move and its reason in the archive's
`DECISIONS.md`, and update links and indexes. Move a project back out of its archive
when work resumes.

For Android apps, connect to the phone with `~/best/fun/adb-phone`. It prints the
serial to pass to `adb -s`, or runs `adb` with any arguments you give it. If it
can't find the phone, ask me to turn on Wireless debugging.
The phone stays awake while charging (`svc power stayon true`), so plug it in
for tests that run in the background.
