---
name: hyper-menu
description: Give an app a Hyper menu, the list of its commands that a lone tap of Caps Lock opens and one letter runs, and choose its shortcuts. Use when Alejo asks for a Hyper menu, a command menu or palette, or keyboard shortcuts in one of his apps or pages (BB, the plans app, the docket), or asks to add or move a command in one.
---

# Hyper menu

Alejo's Caps Lock is Hyper: Karabiner sends ⌃⌥⇧⌘ while it is held
(`~/.config/karabiner/karabiner.json`). Every app of his follows one pattern, so a
shortcut learned in one works by the same rule in the next.

## The pattern

1. **A lone tap of Hyper opens the menu.** It slides up from the bottom edge, over the
   content, so nothing behind it moves or resizes. A second tap or Esc closes it.
2. **Inside the menu, one unmodified letter runs a command** and closes the menu. `/`
   searches every command by name; Enter runs the first match.
3. **Each row shows only the shortcut that runs the command with the menu closed**, at its
   left: `;-Z` for "`;` and Z together", or the usual glyphs (`⌘K`) for a shortcut the app
   already has. The key inside the menu is that shortcut's letter, so it isn't shown
   again, and a command reached by `⌘K` is K in the menu, never another letter.
4. **Outside the menu the letter needs Hyper.** The app binds Hyper+letter. Hyper can be
   pressed two ways: Caps Lock held with the left hand, or `;` with the right. Karabiner
   treats `;` and a letter or digit pressed right after it, while `;` is still down, as
   Hyper+that key in every app, which is why rows read `;-Z`. There is no hold to wait
   for, and `;` otherwise types as usual. `;` was chosen because a letter almost never
   follows it without a space, so typing doesn't set it off. A new app needs no Karabiner
   change.

## Choosing what goes in

- Put in the commands he runs often and the ones that need a modifier to reach. Leave the
  rest to `/` search or the app's own palette.
- The same letter means the same thing in every app: Z snooze or hide, X set aside for
  later, W close, R rename, T new, E fold, B sidebar, G go to what is
  waiting. Reuse these before inventing a letter.
- Letters for `;-` shortcuts sit under the left hand (Q W E R T A S D F G Z X C V B), since
  the right hand holds `;`. Inside the menu any key will do.
- Group rows by what they act on (this thread, all threads, the app), most used first, at
  most about six rows a group.
- A command that can't run now (no thread open) stays in its place, dimmed, so rows never
  move.

## Building it

- Web pages and web-based apps: copy `hyper-menu.js` and `hyper-menu.d.ts` from this
  folder and call `createHyperMenu({ groups })`. It draws the menu, detects the lone tap,
  and takes its colours from the page (`--hyper-menu-bg`, `--hyper-menu-ink`,
  `--hyper-menu-line` override them). When you fix the module, fix it here and copy it
  again to the apps that use it: `grep -rl createHyperMenu ~/best --include=hyper-menu.js`.
- Register each Hyper+letter shortcut the way the app registers shortcuts, and have the
  menu row and the shortcut call the same function.
- A command the app owns and gives no function for can be run by dispatching its own
  key event (BB's `⌘K` works this way). Check each one; some apps ignore made-up events.
- A native app detects the tap as all four modifiers going down and up with no key
  between.

## Checking it

Drive it in a browser before handing it over: the tap opens and closes it, a Hyper+letter
chord does not open it, every letter runs its command, `/` plus Enter runs a match, Esc
restores focus. Playwright presses the tap as four `keyboard.down` calls and four
`keyboard.up` calls. Karabiner only sees a real keyboard, so say that the Caps Lock key and
the `;` layer themselves were not pressed.

The first one is BB's, in `~/best/systems/bb-plugin/src/Controller.tsx`.
