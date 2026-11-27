// hyper-menu.js: a menu of an app's commands that a lone tap of Hyper opens.
// Copy this file and hyper-menu.d.ts into the app; SKILL.md beside the original says how to
// choose what goes in the menu. No dependencies: it draws its own DOM in document.body.
//
//   const menu = createHyperMenu({
//     groups: () => [{ title: "This thread", items: [
//       { key: "z", label: "Snooze", outside: "M-Z", run: snooze, enabled: () => hasThread() },
//     ] }],
//   });
//   menu.open(); menu.close(); menu.toggle(); menu.destroy();
//
// Each row shows `outside`, the shortcut that runs the command with the menu closed. Inside
// the menu its letter alone (`key`) runs it, so `key` must be the letter `outside` ends in.

const MODIFIER_KEYS = new Set(["Meta", "Control", "Alt", "Shift", "CapsLock", "OS", "Hyper", "Super"]);

const STYLE = `
.hyper-menu { position: fixed; left: 0; right: 0; bottom: 0; z-index: 2147483000;
  box-sizing: border-box; max-height: 70vh; overflow-y: auto; padding: 12px 16px 10px;
  display: flex; flex-direction: column; gap: 10px;
  font: 13px/1.5 system-ui, -apple-system, sans-serif;
  background: var(--hyper-menu-bg, var(--popover, Canvas));
  color: var(--hyper-menu-ink, var(--popover-foreground, CanvasText));
  border-top: 1px solid var(--hyper-menu-line, var(--border, color-mix(in srgb, currentColor 20%, transparent)));
  box-shadow: 0 -8px 24px rgb(0 0 0 / 0.18); }
.hyper-menu[hidden] { display: none; }
.hyper-menu-cols { display: flex; flex-wrap: wrap; gap: 4px 32px; }
.hyper-menu-col { min-width: 220px; }
.hyper-menu h4 { margin: 0 0 4px; font-size: 10px; font-weight: 600; opacity: 0.6;
  text-transform: uppercase; letter-spacing: 0.05em; }
.hyper-menu-item { display: flex; align-items: center; gap: 8px; padding: 2px 4px; border-radius: 4px;
  cursor: pointer; }
.hyper-menu-item:hover, .hyper-menu-item.first { background: color-mix(in srgb, currentColor 10%, transparent); }
.hyper-menu-item.off { opacity: 0.35; cursor: default; }
.hyper-menu kbd { font: 11px ui-monospace, Menlo, monospace; min-width: 2.6em; text-align: center;
  border: 1px solid color-mix(in srgb, currentColor 30%, transparent); border-radius: 3px; padding: 0 4px; }
.hyper-menu-label { flex: 1; }
.hyper-menu-search { display: flex; align-items: center; gap: 8px; opacity: 0.8; }
.hyper-menu-search input { flex: 1; font: inherit; color: inherit; background: none; border: 0; outline: 0; }
`;

/**
 * Calls `onTap` when all four modifiers (⌃⌥⇧⌘, which Karabiner sends for Caps Lock) go down
 * and come up again with no other key pressed between. Returns a function that stops listening.
 */
export function onHyperTap(onTap, target = window) {
  let reached = false; // all four were down at once
  let spoiled = false; // another key was pressed while any modifier was down
  const all = (e) => e.metaKey && e.ctrlKey && e.altKey && e.shiftKey;
  const none = (e) => !e.metaKey && !e.ctrlKey && !e.altKey && !e.shiftKey;
  const down = (e) => {
    if (!MODIFIER_KEYS.has(e.key)) spoiled = true;
    else if (all(e)) reached = true;
  };
  const up = (e) => {
    if (!none(e)) return;
    const tapped = reached && !spoiled;
    reached = spoiled = false;
    if (tapped) onTap();
  };
  const reset = () => { reached = spoiled = false; };
  target.addEventListener("keydown", down, true);
  target.addEventListener("keyup", up, true);
  target.addEventListener("blur", reset);
  return () => {
    target.removeEventListener("keydown", down, true);
    target.removeEventListener("keyup", up, true);
    target.removeEventListener("blur", reset);
  };
}

export function createHyperMenu({ groups, hyperTap = true, onRun, attributes = {} }) {
  const read = () => (typeof groups === "function" ? groups() : groups);
  const style = document.createElement("style");
  style.textContent = STYLE;
  document.head.append(style);
  const el = document.createElement("div");
  el.className = "hyper-menu";
  el.hidden = true;
  el.setAttribute("role", "dialog");
  el.setAttribute("aria-label", "Commands");
  for (const [name, value] of Object.entries(attributes)) el.setAttribute(name, value);
  document.body.append(el);

  let query = null; // null: the columns show and letters run commands; a string: searching
  let returnFocus = null;
  const isOpen = () => !el.hidden;
  const usable = (item) => !item.enabled || item.enabled();

  function row(item, first) {
    const div = document.createElement("div");
    div.className = "hyper-menu-item" + (usable(item) ? "" : " off") + (first ? " first" : "");
    div.dataset.key = item.key || "";
    // The row shows the outside shortcut; its letter alone is the key inside the menu.
    const kbd = document.createElement("kbd");
    kbd.textContent = item.outside || (item.key || "").toUpperCase();
    const label = document.createElement("span");
    label.className = "hyper-menu-label";
    label.textContent = item.label;
    div.append(kbd, label);
    div.addEventListener("mousedown", (e) => { e.preventDefault(); run(item); });
    return div;
  }

  function matches() {
    const q = (query || "").trim().toLowerCase();
    return read().flatMap((g) => g.items).filter((i) => usable(i) && i.label.toLowerCase().includes(q));
  }

  function render() {
    el.textContent = "";
    const cols = document.createElement("div");
    cols.className = "hyper-menu-cols";
    if (query !== null) {
      const found = matches();
      found.forEach((item, i) => cols.append(row(item, i === 0)));
      if (!found.length) cols.textContent = "No command matches.";
    } else {
      for (const group of read()) {
        const col = document.createElement("div");
        col.className = "hyper-menu-col";
        const h = document.createElement("h4");
        h.textContent = group.title;
        col.append(h, ...group.items.map((item) => row(item, false)));
        cols.append(col);
      }
    }
    const search = document.createElement("div");
    search.className = "hyper-menu-search";
    const slash = document.createElement("span");
    slash.textContent = "/";
    const input = document.createElement("input");
    input.spellcheck = false;
    input.placeholder = "search commands · Esc closes";
    input.value = query || "";
    input.addEventListener("input", () => { query = input.value; render(); });
    search.append(slash, input);
    el.append(cols, search);
    if (query !== null) { input.focus(); input.setSelectionRange(input.value.length, input.value.length); }
  }

  function open() {
    if (isOpen()) return;
    returnFocus = document.activeElement;
    query = null;
    el.hidden = false;
    render();
    // Take focus off whatever had it, so nothing else receives the letters.
    if (returnFocus instanceof HTMLElement) returnFocus.blur();
  }
  function close(restore = true) {
    if (!isOpen()) return;
    el.hidden = true;
    if (restore && returnFocus instanceof HTMLElement && returnFocus.isConnected) returnFocus.focus();
    returnFocus = null;
  }
  function run(item) {
    if (!usable(item)) return;
    // Close first and give focus back, so a command that acts on the focused thing still can;
    // a command that opens its own dialog then takes focus itself.
    close();
    onRun?.(item);
    item.run();
  }

  // Capture phase, so the menu gets keys before the app's own shortcuts do.
  const onKey = (e) => {
    if (!isOpen() || e.isComposing) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return; // chords still reach the app
    if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); return close(); }
    if (query !== null) {
      if (e.key === "Enter") { e.preventDefault(); e.stopPropagation(); const first = matches()[0]; if (first) run(first); }
      else e.stopPropagation(); // typing goes to the search field only
      return;
    }
    if (MODIFIER_KEYS.has(e.key)) return;
    e.preventDefault();
    e.stopPropagation();
    if (e.key === "/") { query = ""; return render(); }
    const item = read().flatMap((g) => g.items).find((i) => i.key && i.key === e.key.toLowerCase());
    if (item) run(item);
  };
  window.addEventListener("keydown", onKey, true);
  const onPointer = (e) => { if (isOpen() && !el.contains(e.target)) close(false); };
  window.addEventListener("pointerdown", onPointer, true);
  const stopTap = hyperTap ? onHyperTap(() => (isOpen() ? close() : open())) : () => {};

  return {
    open, close, isOpen,
    toggle: () => (isOpen() ? close() : open()),
    destroy() {
      stopTap();
      window.removeEventListener("keydown", onKey, true);
      window.removeEventListener("pointerdown", onPointer, true);
      el.remove();
      style.remove();
    },
  };
}
