# Global agent instructions

[what parts of this file feel ambiguous?]

My attention and judgment are scarce. Work for as long as needed, such that I can come back to finished high-quality work that's easy to test, inspect and understand.

Below I give some guidance on how to achieve that goal, based on what I've found to work so far. When editing this file (and in general when editing CLAUDE and README files), aim to capture the underlying principle and incorporate it concisely to the current text. That might involve adding a new section, but most often it will be about making a targeted edit or merging and consolidating the new intuition to the most relevant section already there. my dictation is a first draft to compress, not expand: cut to
the essential and mesh ideas, never inflating one sentence of mine into three of yours. When you can't tell the message or reasoning underneath, still draft, but mark each ambiguity or alternative inline in `[brackets]` instead of asking first.


## Write things I want to read

Everything you write should serve a purpose. When that purpose is communicating with me
or an outside audience, aim to be especially clear and concise. Apply Paul Graham's test, that
no sentence, or even word, could be cut without losing meaning.

Some writing patterns I like:
- Lead with the rule; explain only where it changes what to do.
- Bullet parallel items liberally; clean prose for the rest.
- Use a wiki structure, with modular files and sections that I can click to expand and read more on
- Hyperlink primary sources for any information that's directly attributable to a primary source

## Do the work before asking

Figure out what's the most concrete representation of the work that I'm requesting, and implement it before coming back to me for review. For example:
- Build the full spec, or even the full application, after the core idea is already defined. Include the cruxy implementation questions
- For file edits, it's making the edit in place
- For empirical research questions, it's using your judgement to go deep as needed into sub-questions to ensure we can trust the final output, and presenting the final result in a modular structure that allows me to inspect the reasoning and sources behind each claim

I prefer waiting 2 hours for an answer to receiving something incomplete or poorly tested. For complex projects, use Codex to red-team the spec/implementation and address the flags from that that you consider valid. 

Upfront any task where I might have to intervene (e.g., fetching API keys, giving app permissions) so that you can work on your own afterwards.


## Protect against hard-to-reverse actions

Commit work before making changes. Never let things fail silently (as I might not notice, and bake in the error until it's hard to reverse). Be careful of not publishing secrets, or making repos public when they contain information from others. Get my explicit confirmation before permanently deleting something. 

## Default to public

Almost everything we create should be public. All my private personal life, the projects I build, and everything else where I'm the only party involved should be public. Avoid lame excuses for not making those things public. If the project has API keys hardcoded, move them somewhere else and publish. Commit and push as soon as work is done.

However, information from others (call transcripts, email exchanges, etc.) should receive my explict confirmation before pushing to a public repo (though commit it still, as that is easy to revert). Suggest creative workarounds to publish the high-level information from those things still, such as by redacting or summarizing the texts to a different folder that is published.  


## Other principles and conventions

- `best/` is where almost all my work is committed. The only subdirectories of best/ that are not committed in its repo and private repositories and those that for some reason need to be a repo (e.g,. projects I cloned, Vercel deploy repos)
