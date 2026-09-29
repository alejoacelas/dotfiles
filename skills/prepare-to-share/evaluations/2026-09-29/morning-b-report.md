# Morning reader sharing preparation

Changes are uncommitted in `repo/` for review. No deployment, account access,
paid API calls, device installation, artifact publication or license change occurred.

## Changed files

- `README.md`: replaced the author's setup with a developer-peer path from tools
  and personal API credentials to one book on Android. Added prerequisites,
  service roles, API spending/data flow, embedded-key limitations, concrete success
  checks, optional feed import and troubleshooting. Removed unverified fixed price
  and elapsed-time promises.
- `AGENTS.md`: made agent setup portable, documented checks and paid-operation
  boundaries, removed personal 1Password/cloud-account details.
- `.env.example`: added the two required variable names with empty values.
- `packer/__main__.py`: replaced an unavailable author-specific ADB helper with
  `adb` on PATH; an `ADB` executable override preserves wrapper support. Uses
  normal `ANDROID_SERIAL` device selection through ADB.
- `.gitignore`: ignores uv's `.venv/`.
- `DECISIONS.md`: records portable setup and the pending license decision; removes
  references attributing the starter shelf to a private reading list.

## Checks and results

- Inspected CLI commands, Gradle versions, app storage/import behavior, reading
  budget, API clients and feed filtering against documentation claims.
- `uv sync --locked`: passed with the committed lockfile.
- `./pack --help`: passed.
- `./pack search frankenstein`: passed against the public Gutenberg catalog;
  returned ID 84 and other editions without API credentials.
- Stubbed subprocess checks: passed for default ADB, a custom executable path
  containing a space, pack transfer, OPML transfer and app launch when the target
  directory is missing. No device commands were sent.
- `git diff --check`: passed. Relative documentation links exist. Ignore rules
  cover `.env`, packs, cache, APK output and `.venv`.
- Reachable-history audit: inspected 10 commits and 72 unique blobs. No matches
  for common OpenRouter, Google API, GitHub token or private-key patterns. This is
  a targeted scan, not a guarantee that history contains no sensitive material.
  No tracked `.env`, `cache/` or `packs/` history was found. Historical README and
  AGENTS versions retain personal account/project/password-item references.
- Consulted official Android ADB documentation, YouTube API getting-started
  documentation and the configured model's OpenRouter page; links are in README.
- `GRADLE_USER_HOME="$PWD/.gradle/verification" ./gradlew assembleDebug --no-daemon`: passed
  with JDK 17 in 4m 26s (38 tasks). The APK remains in ignored build output; it was
  not installed or published. Gradle reported that `libandroidx.graphics.path.so`
  could not be stripped and packaged it as-is; the build still succeeded.

## Owner decisions and remaining verification

1. Choose an app-wide reuse license. Only the bundled font has an explicit license;
   no license was added or changed.
2. Review whether the historical personal account/item references may be shared.
   Current source docs remove them. If history must remain private, publish a fresh
   reviewed source copy instead of these commits; no history rewrite was performed.
3. Run the documented first-book path using authorized personal credentials and an
   Android target. Paid segmentation, YouTube discovery, APK installation, actual
   phone import, Explain and the visual reading flow were not exercised here.
4. The APK embeds its builder's OpenRouter key and release builds use debug signing.
   The README directs peers to build privately with their own keys. Distribution of
   a shared binary requires a separate credential/signing design.

Build verification uses an ignored local Gradle home under `.gradle/verification`.
The CLI environment and download cache also remain ignored inside the checkout.
