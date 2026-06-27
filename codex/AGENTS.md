# Global instructions for Claude Code

Each area below has a principle — what I'm actually after — and tips, the
defaults that usually get there. Follow the tips, but they serve the principle:
when the principle is better served another way, do that.

## Write things I want to read
Any document you draft for me should be enjoyable to read — clear, and with as
little friction as possible. That goes especially for README.md and CLAUDE.md
files, but also for intermediate work saved as markdown.

Tips:
- Lead with the rule; add explanation only when it changes what to do.
- Keep headings plain and one instruction per idea.
- Cut context that doesn't change the action.
- Pick the form that reads easiest — bullets when items are parallel, a sentence
  or short paragraph when prose carries the idea better. Don't bullet by reflex.

## Show finished work
When you finish something I'm meant to see or use, show it so I can see it right away. In many cases, that will be just replying to me on the terminal, but for apps or writing, it probably involves opening the resulting artifact.

Tips:
- For web work that creates or substantially changes a page, run `open` on the
  result.
- When I hand off a big task, run it to the finish on your own — don't pull me in
  at each step; surface once, when the finished product is ready.

## Default to public
Public is the default; making something private is a deliberate act — easy to
declare, hard to reverse by accident. Only two kinds of thing are private without
asking: credentials (keys, tokens, account access), and raw content someone
confided in me (transcripts, personal messages, my notes about people).
Everything else — including anything about me or that I produce — is public.

Tips:
- Push toward more public: offer to anonymize, add a `.env.example`, or share a
  high-level summary rather than holding the whole thing back.
- Always commit: when you find uncommitted work, commit and push it rather than
  leaving a dirty tree — after a quick check that nothing private (credentials,
  confided content) is going in. Don't ask whether to commit; it's the default.
- When something must stay private, keep it out of the public tree and point to
  it, eg., using a git submodule.

## Keep the root small
A folder's root is a pile I frequently look at. Make sure every spot counts. New things get a default home off the root, not a new
top-level entry. Don't create, archive, or delete anything at the root without my explicit guidance.

Tips:
- Not-yet-active ideas go in `upcoming/` — the default home when I don't name one
  — as a year-month folder (`2026-06-foo/`)
    -  Depending on what they are, you can store the prompt for further discussion (`prompt.md`) and draft a substantive reply, build a completely functional MVP for me to review later, etc. Default to doing the work so that when I revisit the idea there's something to engage with. 
- Retired work moves to `~/archive/`, mirroring its path under home
  (`~/archive/best/body/old-routine/`) so the path records where it came from.
  Delete instead only for obvious junk with little to reuse.
