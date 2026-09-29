# Prepare-to-share: full and concise versions

Four independent runs on two public repositories. These are the agents’ original outputs, published for review without editorial corrections. The default branches were not changed.

## Review the results

| Project | Starting README | Full skill (A) | Concise skill (B) |
| --- | --- | --- | --- |
| Morning reader | [original](https://github.com/alejoacelas/2026-09-morning-reader/blob/d5f83458bfc708d08433f457113fb5384b623390/README.md) | [README](https://github.com/alejoacelas/2026-09-morning-reader/blob/84de5c5448dda14efd344a594e31d95add3b9743/README.md) · [diff](https://github.com/alejoacelas/2026-09-morning-reader/compare/d5f83458bfc708d08433f457113fb5384b623390...84de5c5448dda14efd344a594e31d95add3b9743) | [README](https://github.com/alejoacelas/2026-09-morning-reader/blob/b46323645b06fd1fd0c91aca9afad2cd013fe9ec/README.md) · [diff](https://github.com/alejoacelas/2026-09-morning-reader/compare/d5f83458bfc708d08433f457113fb5384b623390...b46323645b06fd1fd0c91aca9afad2cd013fe9ec) |
| Writing checks | [original](https://github.com/alejoacelas/writing-checks/blob/904f3f84a27b03cc112167e5950d69676d5d793b/README.md) | [README](https://github.com/alejoacelas/writing-checks/blob/2c5e0dbfaef20175ec98e79a273e40671af7d481/README.md) · [diff](https://github.com/alejoacelas/writing-checks/compare/904f3f84a27b03cc112167e5950d69676d5d793b...2c5e0dbfaef20175ec98e79a273e40671af7d481) | [README](https://github.com/alejoacelas/writing-checks/blob/c085425615c1b05e38bfb443e3fb9ad217080059/README.md) · [diff](https://github.com/alejoacelas/writing-checks/compare/904f3f84a27b03cc112167e5950d69676d5d793b...c085425615c1b05e38bfb443e3fb9ad217080059) |

Morning reader A also produced a separate [setup guide](https://github.com/alejoacelas/2026-09-morning-reader/blob/84de5c5448dda14efd344a594e31d95add3b9743/docs/setup.md). B keeps setup in the README. Both writing-checks outputs keep setup in the README.

Read the artifacts before treating either version as better. Useful questions: does the first screen make the value clear; can a peer get to a first useful result; which details earn their space; and what is missing or inaccurate?

## Inputs and independence

- [Full skill](https://github.com/alejoacelas/dotfiles/blob/1c5f387/skills/prepare-to-share/SKILL.md): 1,384 words, including frontmatter.
- [Concise candidate](https://github.com/alejoacelas/dotfiles/blob/1c5f387/skills/prepare-to-share/versions/concise.md): 538 words, including frontmatter. Audience profiles were identical in all four bundles.
- The same task and starting commit were used for both versions on each repository. The exact task template, hashes, commits and output locations are in [manifest.json](manifest.json).
- Each run used a fresh GPT-6 Astra agent at medium reasoning effort. No drafting conversation, experiment description, desired result or other variant was supplied. Agents were restricted to their assigned checkout and skill bundle, with official external documentation allowed.
- Recorded tool calls were checked for references to other trial workspaces, the installed source skill, and conversation logs; none were found. The clones shared a machine and installed tools, so this was context isolation, not a security sandbox.
- Agents were asked to leave uncommitted changes and a report. The coordinator reviewed scope and publication suitability, then committed and pushed the outputs unchanged. The reports retain their original handover wording.

## Checks and limitations

Both writing-checks runs passed all 14 tests and verified the documented CLI example results. Both morning-reader runs passed Android debug builds, public catalog searches and mocked ADB transfer checks. Neither used paid APIs or installed on a phone; first-use phone behavior remains unverified. No built APKs, credentials or generated writing snapshots were published.

Both projects lack an app/project-wide reuse license; all runs recorded that owner decision without choosing a license. Morning reader’s pre-existing public history retains the author’s personal setup references. The test branches remove current references but retain the same public baseline history.

These are one run per version per repository. They show concrete behavior, not a reliable estimate of each skill’s performance across repeated runs. No winning version has been selected.

## Concrete differences to inspect

- **Morning reader:** A separates overview and setup, and gives a labeled setup-time estimate and a token-based cost example. B keeps the path together and asks readers to inspect actual usage, without a numeric cost or time estimate.
- **Portability:** both independently replaced the author-only ADB helper with ordinary `adb` and an optional executable override. B supplies an empty `.env.example`; A puts the configuration example in its setup guide.
- **Example choice:** writing-checks A shows a real flagged sentence and output; B describes a review-and-recheck workflow and shows expected scores later.
- **A concrete miss:** morning-reader B says to find the book in “Books”; the actual app tab is “Library” (`MainActivity.kt`). It is left unchanged so the published result remains the trial output. A uses the implemented label.

## Agent reports

- [Morning reader A](morning-a-report.md)
- [Morning reader B](morning-b-report.md)
- [Writing checks A](writing-a-report.md)
- [Writing checks B](writing-b-report.md)
