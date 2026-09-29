# Morning reader documentation handover

Changes are uncommitted in `repo/`. No deployment, publication, paid API call,
private account access, phone connection, or license change was performed.

## Changed files

- `README.md`: leads with the reading outcome and a representative book command;
  explains prerequisites, estimated setup effort, API costs with dated primary
  sources, data flows, implemented limits, maintenance and the license gap.
- `docs/setup.md` (new): build-first setup, ordinary USB/adb connection, creation
  of the adopter's keys, first book and blog workflows, expected results,
  troubleshooting, and explicit verification limits.
- `AGENTS.md`: replaces machine paths and personal credential locations with
  instructions usable by a peer's agent; documents checks, secrets, model locations,
  and history/publication concerns.
- `DECISIONS.md`: removes personal context from current decisions and records the
  standard-adb portability choice.
- `packer/__main__.py`: replaces the unavailable personal adb helper with `adb`
  on PATH and optional `ADB` executable override. `ANDROID_SERIAL` is inherited.
- `packer/videos.py`: replaces the outdated 500-quota-units comment with the
  actual request count and a reference to the README's current quota source.
- `.gitignore`: ignores the local Python virtual environment.

## Checks and results

- Inspected Android build configuration, manifest, storage, feed fetching,
  AI prompts, session selection, reader actions, and the Python preparation and
  transfer implementation to check claims and required values.
- `./pack --help`, `./pack add --help`, `./pack starter --help`, and
  `./pack videos --help`: passed with locked dependencies through uv.
- `./pack search 'tale of two cities'`: live public search passed; Gutenberg ID 98
  was the first result, matching the setup example. No authenticated API used.
- Mocked `subprocess.run` checks: passed for default `adb`, executable override
  containing spaces, application launch when the destination is absent, pack and
  OPML destinations, and inheritance of the device-selection environment.
  These are command-construction checks, not proof of a successful phone transfer.
- Local Markdown links and heading anchors: passed.
- `git diff --check`: passed.
- `GRADLE_USER_HOME="$PWD/.gradle-user" ./gradlew assembleDebug`: passed on macOS
  with JDK 17 and the available Android SDK, without `.env`; 38 tasks executed in
  4m 2s, including a fresh Gradle distribution/dependency download. Produced the
  debug APK locally. Nonfatal warning: `libandroidx.graphics.path.so` could not
  be stripped and was packaged as-is. No install or runtime test was performed.
- Primary-source checks on 2026-09-29: OpenRouter's configured model page lists
  promotional input/output prices of $0.75/$3.75 per million tokens; Google's
  current quota page gives search its own default bucket of 100 calls/day.
  README links to these sources and labels the $0.15 example as a token-based
  estimate, not measured consumption.
- Reviewed all ten commits' file inventory and documentation changes. A search
  across their snapshots found personal account, project, password-manager and
  machine-path references in history. A narrow scan for OpenRouter/Google API
  key patterns and private-key headers found no matches; this is not a complete
  secret audit. No `.env` was present in this checkout.

## Owner decisions and unverified work

1. Choose a project-wide reuse license; none exists, and the font's OFL does not
   license the app. No license was added or changed.
2. Decide what historical personal references may be public. Current docs remove
   them, but every reviewed commit retains some references. If they must remain
   private, publish a cleaned source copy with fresh history after review. No
   history was rewritten or published here.
3. Complete onboarding with a new adopter's own keys and device: authenticated
   book segmentation/video screening, installation/import, Explain, and background
   feed refresh remain unverified. Account creation/payment and USB authorization
   are human actions identified in the setup guide.
4. APKs still embed the OpenRouter key and release builds use debug signing.
   Documentation restricts the path to private personal installs; redesigning
   key storage or preparing store distribution was outside this documentation task.

Build artifacts and an isolated `.gradle-user/` cache were created locally for
verification. They are ignored (the cache via `.git/info/exclude`) and have not
been published. No automated test suite was added for this small portability
change; the focused mock checks above were run directly.
