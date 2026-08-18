# Orca Markdown collapsibles

Use Orca's canonical source form:

~~~markdown
<details class="orca-details">
<summary>Full output</summary>

```json
{
  "result": "Markdown and fenced code are supported"
}
```

</details>
~~~

The opening tag must contain `class="orca-details"`. Orca's serializer adds that
class, while its rich-mode guard requires embedded HTML to survive an exact
round trip. A plain `<details>` therefore changes during the check and leaves the
document editable only as code.

The supported subset has four practical constraints:

- `<summary>` has no attributes or nested HTML.
- The body is Markdown, not additional raw HTML.
- Collapsibles are not nested.
- Code blocks inside a collapsible cannot contain literal HTML-like tags. In JSON,
  preserve them with escapes such as `\u003ctd\u003e` and `\u003c/td\u003e`.
- Files containing HTML stay below 50,000 body characters. Above that threshold,
  Orca skips the expensive round-trip check and conservatively disables rich mode.

Fenced code is removed before the document-level HTML check, but Orca's dedicated
collapsible parser still sees HTML-like strings inside its body. This is why ordinary
JSON fences work while JSON containing literal table tags does not.

Sources: Orca's
[`details` parser](https://github.com/stablyai/orca/blob/main/src/renderer/src/components/editor/details-markdown-html.ts),
[`details` serializer](https://github.com/stablyai/orca/blob/main/src/renderer/src/components/editor/rich-markdown-details-extension.ts),
and [rich-mode guard](https://github.com/stablyai/orca/blob/main/src/renderer/src/components/editor/markdown-rich-mode.ts).

Input lineage: the failure was first investigated in the August 5, 2026 Codex
session at
`~/.codex/sessions/2026/08/05/rollout-2026-08-05T17-19-17-019fd470-4c2b-70f1-aaa4-6ab6a3d9397d.jsonl`.
The August 17 reproduction was `/tmp/agi-2030-structural-prompt-trace.md`: nine plain
opening tags made Orca's byte-preserving check fail. Canonical tags made seven blocks
render; Unicode-escaping literal table tags in two JSON outputs made the remaining
blocks render.

Checks:

- Every opening tag is canonical, optionally followed by `open`.
- Opening and closing tag counts match.
- No collapsible appears inside another.
- Collapsible bodies contain no literal raw HTML.
- `wc -m` reports fewer than 50,000 characters for an HTML-bearing file.
