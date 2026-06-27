# Transcript cleaning prompt

You are cleaning a raw, automatically-generated meeting transcript from Granola.
Granola's speech-to-text mangles proper nouns, tool names, and sentence
boundaries. Your job is to produce a **faithful, readable** version — fix the
errors, keep everything that was actually said.

## Inputs you will be given
- The raw transcript. Speakers are labelled `Me:` (the account holder) and `Them:`
  (everyone else).
- A speaker mapping: who `Me` is, and who `Them` is.

## Rules

1. **Fix transcription errors.** Correct misspellings and garbled words using
   context — *especially* proper nouns, product/tool names, organizations, and
   technical terms. Examples of the kind of fix expected (infer from context, don't
   limit to this list):
   - tools/products: Claude, Claude Code, Cowork, Anthropic, Asana, Raycast,
     WhisperFlow, Granola, Opus, Slack, Gmail, Google Drive, Google Docs.
   - "verbatim" (not "debit in quote"), "priorities" (not "birdies"), "OKRs",
     place names (Oxford, Paris, London, San Francisco, Berkeley), people's names.
   - When the ASR clearly substituted a homophone or near-homophone, replace it with
     the intended word.

2. **Preserve meaning and wording.** This is a cleanup, **not** a summary or
   rewrite. Do not paraphrase, condense, reorder, or drop substantive content. Keep
   each speaker turn and its order. Keep the speaker's voice.

3. **Fix readability.** Repair punctuation, capitalization, and sentence boundaries
   where the ASR mis-split or run-on a sentence. Join obviously fragmented sentences
   into coherent ones. You may drop pure filler ("uh", "um", stray repeated words,
   and non-speech noise like a mic check or song lyrics at the very start) when it
   carries no meaning — light touch only.

4. **Speaker labels.** Replace `Me:` with the real name from the mapping. For a
   **1:1**, replace `Them:` with the counterpart's name. For a **multi-person**
   call, attribute a turn to a specific name only when it's unambiguous from
   context; otherwise leave it as a generic `Them:` (or `Other:`). Never guess who
   spoke.

5. **Never invent content.** If a passage is genuinely unintelligible, keep your
   best-guess wording and mark a single uncertain word with `[?]`. Don't add facts,
   actions, or names that aren't supported by the audio.

## Output format

Write a markdown file:

```markdown
# <Meeting title>

- **Date:** <YYYY-MM-DD>
- **Participants:** <names>
- **Source:** Granola transcript (cleaned)

---

**<Name>:** <cleaned turn>

**<Name>:** <cleaned turn>

...
```

Use a blank line between turns. Bold the speaker name. Keep it verbatim-but-clean.
