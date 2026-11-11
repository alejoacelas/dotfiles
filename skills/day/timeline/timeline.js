// timeline.js: the day timeline's model and renderer. Used by index.html (the panel) and choices.html
// (several configured renders side by side). No dependencies.
"use strict";
const DT = (() => {
  const DEFAULTS = {
    attention: "inferred", // inferred | focus | spans
    strip: "coarse",       // coarse | blocks | hourly | none
    detail: "full",        // full | minimal
    browser: "lane",       // lane | categories | off
    grouping: "name",      // name | repo | area
    range: "trim",         // trim | fit | fixed
    auto: "hide",          // hide | faint
    priorities: "auto",    // auto | manual | off
    commitOnly: "group",   // group | lanes: repos with commits but no attention or prompts that day
    gapFill: 10,           // minutes: idle gaps inside one thread that still count as that thread
    smallMin: 5,           // threads under this many minutes (and few commits) fold into "minor"
    inspector: "right",    // right | bottom | off
    compact: false,
  };
  const CALLS = "§calls", WEB = "§web";
  const PALETTE = ["#3f6fd8", "#d0832a", "#8a5cc7", "#c2507a", "#2a9bb0", "#b8a12a", "#d1572f", "#5a8f3c",
    "#7a6bd8", "#c46fb3", "#3c8f86", "#a2703d"];
  const WEB_CATS = [
    ["docs", "Docs & Drive", /(^|\.)(docs|drive|sheets|slides)\.google\.com$|notion\.so$|airtable\.com$/],
    ["comms", "Mail & chat", /mail\.google\.com$|gmail\.com$|slack\.com$|whatsapp|telegram|signal|discord|messenger/],
    ["meet", "Video calls", /meet\.google\.com$|zoom\.us$|whereby|granola/],
    ["ai", "AI chat", /claude\.ai$|chatgpt\.com$|openai\.com$|gemini\.google|perplexity|anthropic\.com$/],
    ["tools", "Own tools & dev", /\.ts\.net$|^localhost$|^127\.|github\.com$|vercel|fly\.io|stripe|cloudflare/],
    ["cal", "Calendar", /calendar\.google\.com$|calendly\.com$|swapcard/],
    ["social", "Social & video", /(^|\.)x\.com$|twitter|youtube|reddit|facebook|instagram|linkedin|tiktok|netflix/],
    ["read", "Reading", /forum\.effectivealtruism|lesswrong|substack|medium\.com|wikipedia|arxiv|nytimes|economist/],
    ["other", "Other sites", /./]];
  const CAT_COLOR = {docs: "#4f7fd9", comms: "#d08a2a", meet: "#2f9b6a", ai: "#b0603a", tools: "#6f6f78",
    cal: "#2a9bb0", social: "#c2507a", read: "#8a5cc7", other: "#9a978f"};
  const STOP = new Set("about after again also and anything before being could each first from have into just like make making more most need next only other over pass people preparing prepare ready some such than that their them then there these they this those through to try very want what when which while widely will with work working your ideas cross mind main tasks format figure send share update don't quick task follow idea".split(" "));

  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
  const hm = m => { m = Math.max(0, Math.min(1440, m)); const h = Math.floor(m / 60), mm = Math.floor(m % 60);
    return `${String(h).padStart(2, "0")}:${String(mm).padStart(2, "0")}`; };
  const dur = m => { m = Math.round(m); return m >= 60 ? `${Math.floor(m / 60)}h${String(m % 60).padStart(2, "0")}` : `${m}m`; };
  const cut = (s, n) => s && s.length > n ? s.slice(0, n - 1) + "…" : (s || "");
  const webCat = host => WEB_CATS.find(c => c[2].test(host))[0];
  const catName = k => WEB_CATS.find(c => c[0] === k)[1];

  function normProject(p) {
    if (!p) return "(unknown)";
    if (p === "(temporary)" || /scratch-workspaces|^\/private|^\/tmp|^\/var\/folders/.test(p)) return "(temporary)";
    return p;
  }
  function threadKey(p, grouping) {
    p = normProject(p);
    if (p.startsWith("(")) return p;
    if (grouping === "repo") return p;
    if (grouping === "area") { const s = p.split("/"); return s.length > 1 && !p.startsWith("~") ? s[0] : p; }
    return (p.split("/").pop() || p).replace(/^\d{4}-\d{2}(-\d{2})?-/, "");
  }
  const threadName = k => k === CALLS ? "Calls" : k === WEB ? "Browser" : k === "best" || k === "~/best" ? "best (root)" : k === "~" ? "home folder" : k.includes("/") ? `${k.split("/").pop().replace(/^\d{4}-\d{2}(-\d{2})?-/, "").replace(/-/g, " ")} · ${k.split("/")[0]}` : k.replace(/-/g, " ");
  function hashColor(name, used) {
    let h = 0; for (const c of name) h = (h * 31 + c.charCodeAt(0)) >>> 0;
    for (let i = 0; i < PALETTE.length; i++) { const c = PALETTE[(h + i) % PALETTE.length]; if (!used.has(c)) { used.add(c); return c; } }
    return PALETTE[h % PALETTE.length];
  }
  function tokens(s) {
    return new Set((s || "").toLowerCase().match(/[a-zà-ü][a-zà-ü'’-]{3,}/g)?.map(w => w.replace(/^['’-]+|['’-]+$/g, "").replace(/['’]s$/, ""))
      .filter(w => w.length >= 4 && !STOP.has(w)).map(w => w.length > 5 ? w.replace(/(ing|ed|es|e|s)$/, "") : w.replace(/s$/, "")) || []);
  }
  function parsePlans(md) {
    if (!md) return {priorities: [], reflection: ""};
    const lines = md.split("\n"); let i = lines.findIndex(l => /^##\s*current priorities/i.test(l));
    const priorities = [];
    if (i >= 0) for (i++; i < lines.length && !/^##\s/.test(lines[i]); i++) {
      const m = lines[i].match(/^\s*(?:(\d+)\.|[-*])\s+(.*\S)/); if (m) priorities.push({text: m[2], numbered: !!m[1]});
    }
    const r = md.split(/^##\s*Sofi\s*$/m)[1] || "";
    return {priorities, reflection: r.split(/^##\s/m)[0].replace(/\\([\[\]])/g, "$1").trim()};
  }

  // ---------- model ----------
  function model(day, cfg) {
    const T = new Map();
    const thread = k => {
      if (!T.has(k)) T.set(k, {key: k, name: threadName(k), sessions: [], commits: [], auto: [], focus: [], visits: [],
        events: [], att: 0, agent: 0, prompts: 0, add: 0, del: 0, projects: new Set()});
      return T.get(k);
    };
    const sessById = new Map();
    for (const s of day.sessions) {
      const k = threadKey(s.project, cfg.grouping); const t = thread(k); t.projects.add(s.project);
      const ss = {...s, thread: k, first: s.prompts[0].m, last: Math.max(...s.prompts.map(p => p.end))};
      t.sessions.push(ss); t.prompts += s.prompts.length; sessById.set(s.id, ss);
    }
    for (const f of day.focus) {
      const s = f.session && sessById.get(f.session);
      const k = s ? s.thread : threadKey(f.project, cfg.grouping);
      thread(k).focus.push({...f, thread: k, sess: s?.id});
    }
    for (const c of day.commits) {
      const k = threadKey(c.repo, cfg.grouping); const t = thread(k); t.projects.add(c.repo);
      if (c.auto) t.auto.push({...c, thread: k}); else { t.commits.push({...c, thread: k}); t.add += c.add; t.del += c.del; }
    }
    const calls = day.events.filter(e => e.kind === "call"), blocks = day.events.filter(e => e.kind === "block"),
      sleep = day.events.filter(e => e.kind === "sleep");
    if (calls.length) thread(CALLS).events = calls;
    const visits = day.visits.map(v => ({...v, cat: webCat(v.host)}));
    if (visits.length) thread(WEB).visits = visits;

    // attention: per-minute evidence, strongest thread wins
    const score = new Map(); const sc = k => { if (!score.has(k)) score.set(k, new Float32Array(1440)); return score.get(k); };
    const put = (k, a, b, w) => { const arr = sc(k); for (let m = Math.max(0, Math.floor(a)); m < Math.min(1440, Math.ceil(b)); m++) if (arr[m] < w) arr[m] = w; };
    const focusCover = [];
    if (day.focus.length) { let a = day.focus[0].a, b = day.focus[0].b;
      for (const f of day.focus.slice(1)) { if (f.a - b > 90) { focusCover.push([a, b]); a = f.a; } b = Math.max(b, f.b); }
      focusCover.push([a, b]); }
    if (cfg.attention === "spans") {
      for (const t of T.values()) for (const s of t.sessions) put(t.key, s.first, Math.max(s.last, s.first + 1), 1 + s.first / 1e4);
    } else {
      for (const t of T.values()) for (const f of t.focus) if (t.key !== "(temporary)" || true) put(t.key, f.a, f.b, 3);
      if (cfg.attention === "inferred") {
        for (const t of T.values()) for (const s of t.sessions) {
          const ps = s.prompts;
          ps.forEach((p, i) => { put(t.key, p.m - 3, p.m + 1, 2);
            const n = ps[i + 1]; if (n && n.m - p.m <= cfg.gapFill) put(t.key, p.m, n.m, 1); });
        }
        const vs = visits;
        vs.forEach((v, i) => { put(WEB, v.m, v.m + Math.min(Math.max(v.dur, 1), 3), 0.8);
          const n = vs[i + 1]; if (n && n.m - v.m <= 4) put(WEB, v.m, n.m, 0.6); });
      }
    }
    for (const e of calls) put(CALLS, e.a, e.b, 5);
    const win = new Array(1440).fill(null);
    for (let m = 0; m < 1440; m++) { let best = null, bw = 0.4;
      for (const [k, arr] of score) if (arr[m] > bw) { bw = arr[m]; best = k; } win[m] = best; }
    // fill short idle gaps between the same thread, then fold 1-minute blips into a neighbour
    let runs = []; for (let m = 0; m < 1440; m++) { const k = win[m]; const r = runs[runs.length - 1];
      if (r && r.k === k && r.b === m) r.b = m + 1; else runs.push({k, a: m, b: m + 1}); }
    runs = runs.filter(r => r.k !== null);
    const merged = [];
    for (const r of runs) { const p = merged[merged.length - 1];
      if (p && p.k === r.k && r.a - p.b <= Math.min(cfg.gapFill, 15)) p.b = r.b; else merged.push({...r}); }
    for (let i = 0; i < merged.length; i++) { const r = merged[i];
      if (r.b - r.a <= 1 && r.k !== CALLS) { const p = merged[i - 1], n = merged[i + 1];
        const nb = [p, n].filter(x => x && (x.b === r.a || x.a === r.b)).sort((x, y) => (y.b - y.a) - (x.b - x.a))[0];
        if (nb) { if (nb === p) p.b = r.b; else n.a = r.a; merged.splice(i--, 1); } } }
    const segs = merged.map(r => ({thread: r.k, a: r.a, b: r.b}));
    for (const s of segs) thread(s.thread).att += s.b - s.a;

    // agent time: union of turn intervals per thread
    for (const t of T.values()) {
      const iv = t.sessions.flatMap(s => s.prompts.map(p => [p.m, Math.max(p.end, p.m + 0.5)])).sort((x, y) => x[0] - y[0]);
      let tot = 0, ca = null, cb = null; for (const [a, b] of iv) { if (ca === null || a > cb) { if (ca !== null) tot += cb - ca; ca = a; cb = b; } else cb = Math.max(cb, b); }
      if (ca !== null) tot += cb - ca; t.agent = tot;
    }
    // peak parallel agent turns
    const ev = day.sessions.flatMap(s => s.prompts.flatMap(p => [[p.m, 1], [Math.max(p.end, p.m + 0.5), -1]])).sort((x, y) => x[0] - y[0] || x[1] - y[1]);
    let cur = 0, peak = 0, agentSum = 0; ev.forEach(([, d]) => { cur += d; peak = Math.max(peak, cur); });
    day.sessions.forEach(s => s.prompts.forEach(p => agentSum += Math.max(0, p.end - p.m)));

    // order threads; fold the small ones
    const used = new Set();
    let threads = [...T.values()].filter(t => t.key !== "(temporary)" || t.att > 0);
    if (cfg.auto === "hide") threads = threads.filter(t => t.att || t.sessions.length || t.commits.length || t.events.length || t.visits.length);
    threads.sort((a, b) => (b.key === CALLS) - (a.key === CALLS) || b.att - a.att || b.commits.length - a.commits.length || b.prompts - a.prompts);
    for (const t of threads) t.color = t.key === CALLS ? "#2f9b6a" : t.key === WEB ? "#8d8a82" : hashColor(t.key, used);
    for (const t of threads) { t.commitOnly = t.key !== CALLS && t.key !== WEB && !t.att && !t.prompts && t.commits.length > 0;
      t.minor = t.key !== CALLS && t.key !== WEB && t.att < cfg.smallMin && t.commits.length < 3 && !(t.commitOnly && cfg.commitOnly === "group"); }

    // the active window; with "trim", activity before 04:00 that ends 2h+ before the day's main body is folded behind a marker
    const marks = [...segs.flatMap(s => [s.a, s.b]), ...calls.flatMap(e => [e.a, e.b])].sort((x, y) => x - y);
    let folded = null, body = marks;
    if (cfg.range === "trim" && marks.length) {
      let cut = 0; for (let i = 1; i < marks.length; i++) if (marks[i - 1] < 240 && marks[i] - marks[i - 1] >= 120) cut = i;
      if (cut) { folded = {a: marks[0], b: marks[cut - 1], min: segs.filter(s => s.b <= marks[cut - 1] + 0.01).reduce((x, s) => x + s.b - s.a, 0)}; body = marks.slice(cut); }
    }
    const lo = body.length ? body[0] : 8 * 60, hi = body.length ? body[body.length - 1] : 20 * 60;
    const range = cfg.range === "fixed" ? [6 * 60, 24 * 60] : cfg.range === "fit" && marks.length ?
      [Math.max(0, Math.floor(Math.min(lo, ...day.commits.filter(c => !c.auto).map(c => c.m)) / 60) * 60), Math.min(1440, Math.ceil(Math.max(hi, ...day.commits.filter(c => !c.auto).map(c => c.m)) / 60) * 60)] :
      [Math.max(0, Math.floor((lo - 20) / 60) * 60), Math.min(1440, Math.ceil((hi + 20) / 60) * 60)];
    const outside = side => { const f = side < 0 ? (m => m < range[0]) : (m => m > range[1]);
      const n = {commits: day.commits.filter(c => !c.auto && f(c.m)).length, prompts: day.sessions.reduce((a, s) => a + s.prompts.filter(p => f(p.m)).length, 0),
        visits: day.visits.filter(v => f(v.m)).length, active: segs.reduce((a, s) => a + Math.max(0, side < 0 ? Math.min(s.b, range[0]) - s.a : s.b - Math.max(s.a, range[1])), 0)};
      return n.commits + n.prompts + n.visits ? n : null; };
    folded = {left: outside(-1), right: outside(1)};

    const plans = parsePlans(day.plans);
    const pr = cfg.priorities === "off" ? [] : plans.priorities.map((p, i) => ({...p, i, threads: cfg.priorities === "auto" ? matchPriority(p.text, threads) : []}));
    const stats = {
      att: segs.reduce((a, s) => a + (s.thread === WEB ? 0 : s.b - s.a), 0),
      web: segs.reduce((a, s) => a + (s.thread === WEB ? s.b - s.a : 0), 0),
      calls: calls.reduce((a, e) => a + e.b - e.a, 0), ncalls: calls.length,
      first: segs.length ? segs[0].a : null, last: segs.length ? segs[segs.length - 1].b : null,
      prompts: day.sessions.reduce((a, s) => a + s.prompts.length, 0), sessions: day.sessions.length,
      commits: day.commits.filter(c => !c.auto).length, auto: day.commits.filter(c => c.auto).length,
      add: day.commits.filter(c => !c.auto).reduce((a, c) => a + c.add, 0), del: day.commits.filter(c => !c.auto).reduce((a, c) => a + c.del, 0),
      repos: new Set(day.commits.filter(c => !c.auto).map(c => c.repo)).size, agentSum, peak,
      visits: visits.length, scripted: Object.values(day.scripted || {}).reduce((a, b) => a + b, 0)};
    return {day, cfg, threads, segs, calls, blocks, sleep, visits, range, folded, plans, priorities: pr, stats, focusCover,
      byKey: new Map(threads.map(t => [t.key, t]))};
  }

  // A priority matches the threads sharing its rarer words; names (capitalised, not sentence-initial) count double.
  function matchPriority(text, threads) {
    const pt = tokens(text);
    const proper = new Set([...tokens((text.match(/(?<=\s)[A-Z][\wà-ü]{2,}/g) || []).join(" "))]);
    const cand = threads.filter(t => t.key !== WEB);
    if (!cand.length) return [];
    const sets = cand.map(t => t._tok || (t._tok = tokens([t.name, ...t.sessions.map(s => s.title + " " + s.prompts.map(p => p.text).join(" ")),
      ...t.commits.map(c => c.msg), ...t.events.map(e => e.title + " " + (e.summary?.gist || ""))].join(" "))));
    const N = cand.length, out = [];
    cand.forEach((t, i) => {
      let score = 0; const hits = [];
      for (const w of pt) if (sets[i].has(w)) { const df = sets.filter(s => s.has(w)).length;
        score += (proper.has(w) ? 2 : 1) * Math.log(1 + N / df); hits.push(w); }
      const nameToks = [...tokens(t.name)];
      if (nameToks.length && nameToks.every(w => pt.has(w))) { score += 6; hits.unshift("name"); }
      if (score >= 2.5 && (hits.some(w => proper.has(w)) || hits.length >= 2)) out.push({key: t.key, score, hits});
    });
    out.sort((a, b) => b.score - a.score);
    return out.filter(x => x.score >= out[0]?.score * 0.4).slice(0, 4);
  }

  // ---------- render ----------
  function render(root, data, cfgIn, opts = {}) {
    const cfg = {...DEFAULTS, ...cfgIn};
    let M, dayIdx = opts.day ?? data.days.length - 1, view = null, sel = null, brush = null, query = "", pin = null;
    const expanded = new Set(); let showMinor = false;
    root.classList.add("dt"); root.classList.toggle("dt-compact", !!cfg.compact);
    root.innerHTML = `<div class="dt-wrap dt-insp-${cfg.inspector}"><div class="dt-main"><div class="dt-grid"></div></div>${cfg.inspector !== "off" ? `<aside class="dt-insp"></aside>` : ""}</div><div class="dt-tip" hidden></div>`;
    const grid = root.querySelector(".dt-grid"), insp = root.querySelector(".dt-insp"), tip = root.querySelector(".dt-tip");
    const manualKey = (d, p) => `dt-prio:${d}:${p}`;

    function load(i) { dayIdx = Math.max(0, Math.min(data.days.length - 1, i)); M = model(data.days[dayIdx], cfg);
      view = null; sel = null; brush = null; pin = null; draw(); opts.onDay?.(M); }
    const domain = () => view || M.range;
    const X = m => { const [a, b] = domain(); return (m - a) / (b - a) * 100; };
    const W = (a, b) => Math.max(X(b) - X(a), 0);
    const visible = (a, b) => { const [lo, hi] = domain(); return b >= lo && a <= hi; };
    const manual = p => { try { return JSON.parse(localStorage.getItem(manualKey(M.day.date, p.text)) || "[]"); } catch { return []; } };
    const prioThreads = p => cfg.priorities === "manual" ? manual(p).map(key => ({key, hits: []})) :
      [...p.threads, ...manual(p).filter(k => !p.threads.some(x => x.key === k)).map(key => ({key, hits: []}))];
    const prioOf = t => M.priorities.filter(p => prioThreads(p).some(x => x.key === t.key)).map(p => p.i + 1);
    const matches = s => query && s && s.toLowerCase().includes(query);

    // item registry for tooltips / clicks
    let items = [];
    const reg = it => { items.push(it); return items.length - 1; };

    function axis() {
      const [a, b] = domain(), span = b - a;
      const step = span > 720 ? 120 : span > 300 ? 60 : span > 120 ? 30 : span > 50 ? 15 : 5;
      let h = ""; for (let m = Math.ceil(a / step) * step; m <= b; m += step) h += `<span style="left:${X(m)}%">${hm(m)}</span>`;
      return h;
    }
    function gridlines() {
      const [a, b] = domain(), span = b - a, step = span > 720 ? 60 : span > 300 ? 60 : span > 120 ? 30 : 15;
      let h = ""; for (let m = Math.ceil(a / step) * step; m <= b; m += step) h += `<i style="left:${X(m)}%"></i>`;
      for (const s of M.sleep) if (visible(s.a, s.b)) h += `<b class="dt-sleep" style="left:${X(s.a)}%;width:${W(s.a, s.b)}%"></b>`;
      if (pin != null && visible(pin, pin)) h += `<b class="dt-pin" style="left:${X(pin)}%"></b>`;
      if (brush) h += `<b class="dt-brushed" style="left:${X(brush[0])}%;width:${W(brush[0], brush[1])}%"></b>`;
      return h;
    }
    const seg = (cls, a, b, color, i, extra = "") => visible(a, b) ? `<b class="${cls}" data-i="${i}" style="left:${X(a)}%;width:${Math.max(W(a, b), 0.15)}%;${color ? `background:${color};` : ""}${extra}"></b>` : "";
    const dot = (cls, m, color, i, extra = "") => visible(m, m) ? `<b class="${cls}" data-i="${i}" style="left:${X(m)}%;${color ? `--c:${color};` : ""}${extra}"></b>` : "";

    function laneItems(t, opt = {}) {
      let h = "";
      const sessions = opt.sessions || t.sessions, full = cfg.detail === "full";
      if (!opt.noAtt) for (const s of M.segs) if (s.thread === t.key) h += seg("dt-att", s.a, s.b, t.color, reg({type: "seg", s, t}));
      if (t.key === CALLS) for (const e of t.events) h += seg("dt-call" + (matches(e.title) ? " dt-hit" : ""), e.a, e.b, t.color, reg({type: "call", e, t}));
      if (t.key === WEB) for (const v of (opt.visits || t.visits)) h += seg("dt-visit" + (matches(v.title + v.host) ? " dt-hit" : ""), v.m, v.m + Math.max(0.6, Math.min(v.dur, 8)), CAT_COLOR[v.cat], reg({type: "visit", v, t}));
      if (full || opt.sessions) for (const s of sessions) for (const p of s.prompts) {
        h += seg("dt-turn", p.m, Math.max(p.end, p.m + 0.4), t.color, reg({type: "turn", p, s, t}));
        h += dot("dt-prompt" + (matches(p.text) ? " dt-hit" : ""), p.m, null, reg({type: "prompt", p, s, t}));
      }
      if (!opt.noCommits) {
        for (const c of (opt.commits || t.commits)) h += dot("dt-commit" + (matches(c.msg) ? " dt-hit" : ""), c.m, t.color, reg({type: "commit", c, t}));
        if (cfg.auto === "faint" && !opt.commits) for (const c of t.auto) h += dot("dt-commit dt-auto", c.m, t.color, reg({type: "commit", c, t}));
      }
      return h;
    }
    function laneRow(cls, labelHTML, trackHTML, attrs = "") {
      return `<div class="dt-row ${cls}" ${attrs}><div class="dt-lab">${labelHTML}</div><div class="dt-track">${trackHTML}</div></div>`;
    }
    function threadLabel(t) {
      const pr = prioOf(t), ex = expanded.has(t.key);
      const n = t.key === WEB ? `${M.visits.length} visits` : t.key === CALLS ? `${t.events.length}` : "";
      return `<button class="dt-lbtn" data-thread="${esc(t.key)}" aria-expanded="${ex}" title="${esc([...t.projects].join(", ") || t.name)}">
        <span class="dt-caret">${ex ? "▾" : "▸"}</span><span class="dt-sw" style="background:${t.color}"></span>
        <span class="dt-name">${esc(t.name)}</span>${pr.map(n => `<span class="dt-pr">P${n}</span>`).join("")}
        <span class="dt-min">${t.att ? dur(t.att) : n || (t.commits.length ? t.commits.length + "c" : "")}</span></button>`;
    }

    function stripRow() {
      if (cfg.strip === "none") return "";
      let h = "";
      if (cfg.strip === "hourly") {
        const [a, b] = domain();
        for (let hr = Math.floor(a / 60) * 60; hr < b; hr += 60) {
          const parts = new Map(); for (const s of M.segs) { const o = Math.min(s.b, hr + 60) - Math.max(s.a, hr); if (o > 0) parts.set(s.thread, (parts.get(s.thread) || 0) + o); }
          let y = 0; const list = [...parts].sort((x, z) => z[1] - x[1]);
          h += `<div class="dt-hour" style="left:${X(hr)}%;width:${W(hr, hr + 60)}%">` + list.map(([k, v]) => { const t = M.byKey.get(k); const el = `<b data-i="${reg({type: "hour", hr, k, v, t})}" style="bottom:${y / 60 * 100}%;height:${v / 60 * 100}%;background:${t?.color}"></b>`; y += v; return el; }).join("") + `</div>`;
        }
      } else {
        const segs = cfg.strip === "coarse" ? coarse(M.segs, 15) : M.segs;
        const px = (grid.querySelector(".dt-track")?.clientWidth || 800) / 100;
        for (const s of segs) { if (!visible(s.a, s.b)) continue; const t = M.byKey.get(s.thread); const w = W(s.a, s.b);
          h += `<b class="dt-blk" data-i="${reg({type: "seg", s, t})}" style="left:${X(s.a)}%;width:${Math.max(w, 0.15)}%;background:${t?.color}">${w * px > 46 ? `<span>${esc(t?.name)}</span>` : ""}</b>`; }
      }
      for (const [a, b] of M.focusCover) if (visible(a, b)) h += `<i class="dt-cover" style="left:${X(a)}%;width:${W(a, b)}%"></i>`;
      if (!view) for (const [side, n] of [["left", M.folded.left], ["right", M.folded.right]]) if (n) {
        const parts = [n.active >= 1 && `${dur(n.active)} active`, n.prompts && `${n.prompts} prompts`, n.commits && `${n.commits} commits`, n.visits && `${n.visits} page visits`].filter(Boolean);
        h += `<button class="dt-fold dt-fold-${side}" data-unfold="${side}" title="${side === "left" ? "Before" : "After"} this range: ${parts.join(", ")}. Click to show it.">${side === "left" ? "◂ " : ""}${parts.slice(0, 2).join(" · ")}${side === "right" ? " ▸" : ""}</button>`; }
      return laneRow("dt-strip", `<span class="dt-striplab" title="${cfg.strip === "coarse" ? "Main thread in each 15 minutes (browsing counts a third). " : ""}Each minute goes to the thread with the strongest evidence: calls, then Umi focus, then prompts, then browsing. The thin line underneath marks when Umi's focus log was recording.">Attention <span class="dt-min">${dur(M.stats.att + M.stats.web)}</span></span>`, h);
    }
    function coarse(segs, size) {
      const out = []; const [a, b] = M.range;
      for (let w = Math.floor(a / size) * size; w < b; w += size) {
        const parts = new Map(); for (const s of segs) { const o = Math.min(s.b, w + size) - Math.max(s.a, w); if (o > 0) parts.set(s.thread, (parts.get(s.thread) || 0) + o * (s.thread === WEB ? 0.35 : 1)); }
        const top = [...parts].sort((x, y) => y[1] - x[1])[0]; if (!top || top[1] < size * 0.2) continue;
        const p = out[out.length - 1]; if (p && p.thread === top[0] && p.b === w) p.b = w + size; else out.push({thread: top[0], a: w, b: w + size});
      }
      return out;
    }
    function calRow() {
      const ev = [...M.calls, ...M.blocks]; if (!ev.length) return "";
      let h = ""; const px = (grid.querySelector(".dt-track")?.clientWidth || 800) / 100;
      for (const e of ev) { if (!visible(e.a, e.b)) continue; const w = W(e.a, e.b);
        h += `<b class="dt-ev ${e.kind}${matches(e.title) ? " dt-hit" : ""}" data-i="${reg({type: "call", e})}" style="left:${X(e.a)}%;width:${w}%">${w * px > 40 ? `<span>${esc(e.title)}</span>` : ""}</b>`; }
      return laneRow("dt-cal", `<span class="dt-striplab">Calendar <span class="dt-min">${M.stats.ncalls ? dur(M.stats.calls) : ""}</span></span>`, h);
    }

    function draw() {
      items = [];
      let h = laneRow("dt-axis", `<span class="dt-dayname">${esc(M.day.weekday.replace(/ \d{4}$/, ""))}</span>`, `<div class="dt-ticks">${axis()}</div><div class="dt-cursor" hidden><span></span></div>`);
      h += stripRow() + calRow();
      const lanes = M.threads.filter(t => t.key !== CALLS && !(t.key === WEB && cfg.browser === "off"));
      const grouped = cfg.commitOnly === "group" ? lanes.filter(t => t.commitOnly) : [];
      const major = lanes.filter(t => !t.minor && !grouped.includes(t)), minor = lanes.filter(t => t.minor);
      const drawThread = t => {
        h += laneRow("dt-lane" + (sel?.thread === t.key ? " dt-selrow" : ""), threadLabel(t), laneItems(t), `data-lane="${esc(t.key)}"`);
        const open = expanded.has(t.key) || (t.key === WEB && cfg.browser === "categories");
        if (!open) return;
        if (t.key === WEB) {
          const cats = [...new Set(t.visits.map(v => v.cat))].map(c => [c, t.visits.filter(v => v.cat === c)]).sort((x, y) => y[1].length - x[1].length);
          for (const [c, vs] of cats) h += laneRow("dt-sub", `<span class="dt-sublab"><span class="dt-sw" style="background:${CAT_COLOR[c]}"></span>${esc(catName(c))} <span class="dt-min">${vs.length}</span></span>`, laneItems(t, {visits: vs, noAtt: true}));
          return;
        }
        for (const s of [...t.sessions].sort((x, y) => x.first - y.first))
          h += laneRow("dt-sub", `<span class="dt-sublab" title="${esc(s.title)}">${s.tool === "Codex" ? "◇ " : ""}${esc(s.title)} <span class="dt-min">${s.prompts.length}</span></span>`, laneItems(t, {sessions: [s], noAtt: true, noCommits: true}));
        const fo = t.focus.filter(f => !f.sess);
        if (fo.length) h += laneRow("dt-sub", `<span class="dt-sublab">Other focus <span class="dt-min">${dur(fo.reduce((a, f) => a + f.b - f.a, 0))}</span></span>`, fo.map(f => seg("dt-att", f.a, f.b, t.color, reg({type: "focus", f, t}), "opacity:.6")).join(""));
        const repos = [...new Set([...t.commits, ...(cfg.auto === "faint" ? t.auto : [])].map(c => c.repo))];
        for (const r of repos) { const cs = t.commits.filter(c => c.repo === r), au = cfg.auto === "faint" ? t.auto.filter(c => c.repo === r) : [];
          h += laneRow("dt-sub", `<span class="dt-sublab" title="${esc(r)}">commits · ${esc(r.split("/").pop())} <span class="dt-min">${cs.length}</span></span>`, laneItems(t, {commits: [...cs, ...au], sessions: [], noAtt: true})); }
      };
      major.forEach(drawThread);
      if (grouped.length) {
        const open = expanded.has("§commits");
        h += laneRow("dt-lane dt-minor", `<button class="dt-lbtn" data-group="§commits" aria-expanded="${open}" title="Repositories with commits but no prompts or attention from you that day: agents or other machines committed there."><span class="dt-caret">${open ? "▾" : "▸"}</span><span class="dt-name">Commits elsewhere · ${grouped.length} repos</span><span class="dt-min">${grouped.reduce((a, t) => a + t.commits.length, 0)}c</span></button>`,
          open ? "" : grouped.map(t => laneItems(t, {sessions: []})).join(""));
        if (open) grouped.forEach(t => h += laneRow("dt-sub", `<button class="dt-lbtn dt-sublab" data-thread="${esc(t.key)}" title="${esc([...t.projects].join(", "))}"><span class="dt-sw" style="background:${t.color}"></span>${esc(t.name)} <span class="dt-min">${t.commits.length}c</span></button>`, laneItems(t, {sessions: []})));
      }
      if (minor.length) {
        h += laneRow("dt-lane dt-minor", `<button class="dt-lbtn" data-minor aria-expanded="${showMinor}"><span class="dt-caret">${showMinor ? "▾" : "▸"}</span><span class="dt-name">${minor.length} minor threads</span><span class="dt-min">${dur(minor.reduce((a, t) => a + t.att, 0))}</span></button>`,
          showMinor ? "" : minor.map(t => laneItems(t, {sessions: []})).join(""));
        if (showMinor) minor.forEach(drawThread);
      }
      grid.innerHTML = h + `<div class="dt-gridlines">${gridlines()}</div>`;
      grid.classList.toggle("dt-searching", !!query);
      if (insp) inspector();
    }

    // ---------- inspector ----------
    const pill = (txt, cls = "") => `<span class="dt-pill ${cls}">${txt}</span>`;
    const sw = c => `<span class="dt-sw" style="background:${c}"></span>`;
    function statGrid() {
      const s = M.stats;
      const cells = [["Active", s.att + s.web ? dur(s.att + s.web) : "–", s.first != null ? `${hm(s.first)}–${hm(s.last)}` : ""],
        ["On threads", s.att ? dur(s.att) : "–", "incl. calls"],
        ["Browser", s.web ? dur(s.web) : "–", `${s.visits} visits`],
        ["Calls", s.ncalls ? dur(s.calls) : "–", `${s.ncalls} call${s.ncalls === 1 ? "" : "s"}`],
        ["Prompts", s.prompts, `${s.sessions} sessions`],
        ["Agent time", dur(s.agentSum), `peak ${s.peak} at once`],
        ["Commits", s.commits, `${s.repos} repos · +${s.add} −${s.del}`]].filter(c => c[0] !== "Calls" || s.ncalls);
      return `<div class="dt-stats">${cells.map(([l, n, sub]) => `<div><div class="dt-sn">${n}</div><div class="dt-sl">${l}</div><div class="dt-ss">${esc(sub)}</div></div>`).join("")}</div>`;
    }
    function threadTable(list) {
      return `<table class="dt-tt"><thead><tr><th></th><th title="Minutes this thread held your attention">att</th><th title="Union of time agents were working on its turns">agent</th><th title="Prompts you sent">pr</th><th title="Your commits">cm</th></tr></thead><tbody>${
        list.map(t => `<tr data-thread="${esc(t.key)}"><td>${sw(t.color)}${esc(t.name)}${prioOf(t).map(n => ` <span class="dt-pr">P${n}</span>`).join("")}</td><td>${t.att ? dur(t.att) : ""}</td><td>${t.agent ? dur(t.agent) : ""}</td><td>${t.prompts || ""}</td><td>${t.commits.length || ""}</td></tr>`).join("")}</tbody></table>`;
    }
    function prioBlock() {
      if (!M.priorities.length) return cfg.priorities === "off" ? "" : `<h4>Priorities</h4><p class="dt-mute">No priorities on the Plans page for this day.</p>`;
      return `<h4>Priorities <span class="dt-mute">${cfg.priorities === "auto" ? "· matched by shared words; + to add a thread" : "· + to assign threads"}</span></h4>` + M.priorities.map(p => {
        const ts = prioThreads(p).map(x => ({...x, t: M.byKey.get(x.key)})).filter(x => x.t);
        const att = ts.reduce((a, x) => a + x.t.att, 0);
        return `<div class="dt-prio"><div class="dt-prio-h"><span class="dt-pr${p.numbered ? "" : " dt-pr-lo"}" title="${p.numbered ? "numbered priority" : "unnumbered item under the priorities"}">P${p.i + 1}</span> ${esc(p.text)} <span class="dt-min">${att ? dur(att) : ts.length ? "" : "nothing found"}</span></div>
          <div class="dt-prio-t">${ts.map(x => `<button class="dt-chip" data-thread="${esc(x.key)}" title="${x.hits.length ? "shared words: " + esc(x.hits.join(", ")) : "added by you"}">${sw(x.t.color)}${esc(x.t.name)} ${x.t.att ? dur(x.t.att) : ""}</button>`).join("")}
          <select class="dt-add" data-prio="${esc(p.text)}"><option value="">+</option>${M.threads.filter(t => t.key !== WEB && !ts.some(x => x.key === t.key)).map(t => `<option value="${esc(t.key)}">${esc(t.name)}</option>`).join("")}${manual(p).length ? `<option value="§clear">clear my additions</option>` : ""}</select></div></div>`;
      }).join("");
    }
    function callBlock(e) {
      return `<div class="dt-item"><div class="dt-it">${esc(e.title)} ${pill(`${hm(e.a)}–${hm(e.b)}`)}</div>${e.people?.length ? `<div class="dt-mute">${esc(e.people.join(", "))}</div>` : ""}
        ${e.summary ? `<div class="dt-q">${esc(e.summary.gist || e.summary.title)}</div><div class="dt-links">${e.summary.link ? `<a href="${esc(e.summary.link)}" target="_blank">Granola</a>` : ""}<span class="dt-mute">${esc(e.summary.path)}</span></div>` : e.kind === "call" ? `<div class="dt-mute">No filed summary matched.</div>` : ""}</div>`;
    }
    function sessBlock(s, hl) {
      return `<div class="dt-item"><div class="dt-it">${esc(s.title)} ${pill(`${hm(s.first)}–${hm(s.last)}`)} ${pill(s.tool)}</div><div class="dt-mute">${esc(s.cwd)} · ${s.prompts.length} prompts</div>
        <ol class="dt-plist">${s.prompts.map(p => `<li data-m="${p.m}" class="${p === hl ? "dt-hl" : ""}${matches(p.text) ? " dt-hit" : ""}"><span class="dt-tm">${hm(p.m)}</span><span>${esc(p.text)}<span class="dt-mute"> · agent ${dur(Math.max(0, p.end - p.m))}</span></span></li>`).join("")}</ol>
        ${s.last_reply ? `<details><summary>Last reply</summary><div class="dt-q">${esc(s.last_reply)}</div></details>` : ""}</div>`;
    }
    const commitLi = c => `<li data-m="${c.m}" class="${c.auto ? "dt-autoli" : ""}${matches(c.msg) ? " dt-hit" : ""}"><span class="dt-tm">${hm(c.m)}</span><span>${esc(c.msg)} <span class="dt-mute">${esc(c.repo.split("/").pop())} ${c.hash} +${c.add}−${c.del}${c.auto ? " · " + esc(c.auto) : ""}</span></span></li>`;
    function dayInsp() {
      let h = statGrid() + prioBlock();
      const tl = M.threads.filter(t => t.key !== WEB || cfg.browser !== "off");
      const folded = t => t.minor || (t.commitOnly && cfg.commitOnly === "group");
      h += `<h4>Threads</h4>` + threadTable(tl.filter(t => !folded(t)));
      const mn = tl.filter(folded);
      if (mn.length) h += `<details class="dt-minordet"><summary class="dt-mute">${mn.length} more: minor threads and commits elsewhere · ${mn.reduce((a, t) => a + t.commits.length, 0)} commits</summary>${threadTable(mn)}</details>`;
      if (M.calls.length) h += `<h4>Calls</h4>` + M.calls.map(callBlock).join("");
      if (M.day.calls?.length) h += `<h4>Filed call summaries without a calendar match</h4>` + M.day.calls.map(c => `<div class="dt-item"><div class="dt-it">${esc(c.title)}</div><div class="dt-q">${esc(c.gist)}</div></div>`).join("");
      if (M.plans.reflection) h += `<h4>Your reflection</h4><details><summary class="dt-mute">${esc(cut(M.plans.reflection.replace(/\*/g, ""), 120))}</summary><div class="dt-refl">${esc(M.plans.reflection.replace(/\*/g, ""))}</div></details>`;
      const notes = [];
      if (!M.day.focus.length) notes.push("No Umi focus log for this day: attention is inferred from prompts, calls and page visits only.");
      else if (M.focusCover.length) notes.push(`Umi focus log recorded ${M.focusCover.map(([a, b]) => `${hm(a)}–${hm(b)}`).join(", ")}.`);
      if (M.stats.auto) notes.push(`${M.stats.auto} commits by automations (${[...new Set(M.day.commits.filter(c => c.auto).map(c => c.auto))].join(", ")}) ${cfg.auto === "hide" ? "hidden" : "shown hollow"}.`);
      if (M.stats.scripted) notes.push(`${M.stats.scripted} scripted claude -p runs not shown.`);
      (data.errors || []).forEach(e => notes.push(e));
      h += `<h4>Data</h4><ul class="dt-notes">${notes.map(n => `<li>${esc(n)}</li>`).join("")}</ul>`;
      return h;
    }
    function threadInsp(t) {
      let h = `<div class="dt-ih">${sw(t.color)}<b>${esc(t.name)}</b>${prioOf(t).map(n => ` <span class="dt-pr">P${n}</span>`).join("")}</div><div class="dt-mute">${esc([...t.projects].join(" · "))}</div>`;
      if (t.key !== WEB && t.key !== CALLS) h += `<div class="dt-kv">${[["attention", t.att ? dur(t.att) : "–"], ["agent", t.agent ? dur(t.agent) : "–"], ["prompts", t.prompts], ["commits", t.commits.length], ["lines", `+${t.add} −${t.del}`]].map(([k, v]) => `<span><b>${v}</b> ${k}</span>`).join("")}</div>`;
      if (t.key === CALLS) h += t.events.map(callBlock).join("");
      if (t.key === WEB) { const hosts = new Map(); t.visits.forEach(v => { const x = hosts.get(v.host) || {n: 0, cat: v.cat, titles: new Set(), a: v.m, b: v.m}; x.n++; x.titles.add(v.title); x.b = v.m; hosts.set(v.host, x); });
        h += `<table class="dt-tt">${[...hosts].sort((a, b) => b[1].n - a[1].n).slice(0, 25).map(([host, x]) => `<tr><td>${sw(CAT_COLOR[x.cat])}${esc(host)}<div class="dt-mute">${esc(cut([...x.titles].slice(0, 3).join(" · "), 140))}</div></td><td>${x.n}</td><td class="dt-tm">${hm(x.a)}–${hm(x.b)}</td></tr>`).join("")}</table>`; }
      if (t.sessions.length) h += `<h4>Sessions</h4>` + [...t.sessions].sort((a, b) => a.first - b.first).map(s => sessBlock(s)).join("");
      if (t.commits.length || t.auto.length) h += `<h4>Commits</h4><ul class="dt-clist">${[...t.commits, ...(cfg.auto === "faint" ? t.auto : [])].sort((a, b) => a.m - b.m).map(commitLi).join("")}</ul>`;
      const fo = t.focus.filter(f => !f.sess); if (fo.length) h += `<h4>Other focus</h4><ul class="dt-clist">${fo.map(f => `<li><span class="dt-tm">${hm(f.a)}</span><span>${esc(f.title || f.path)} <span class="dt-mute">${f.kind} · ${dur(f.b - f.a)}</span></span></li>`).join("")}</ul>`;
      return h;
    }
    function windowInsp([a, b]) {
      const parts = new Map(); for (const s of M.segs) { const o = Math.min(s.b, b) - Math.max(s.a, a); if (o > 0) parts.set(s.thread, (parts.get(s.thread) || 0) + o); }
      const tot = [...parts.values()].reduce((x, y) => x + y, 0);
      let h = `<div class="dt-ih"><b>${hm(a)}–${hm(b)}</b> <span class="dt-mute">${dur(b - a)} selected · Z zooms in · Esc clears</span></div>`;
      h += `<div class="dt-share">${[...parts].sort((x, y) => y[1] - x[1]).map(([k, v]) => { const t = M.byKey.get(k); return `<b style="width:${v / (b - a) * 100}%;background:${t.color}" title="${esc(t.name)} ${dur(v)}"></b>`; }).join("")}</div>`;
      h += `<table class="dt-tt">${[...parts].sort((x, y) => y[1] - x[1]).map(([k, v]) => { const t = M.byKey.get(k); return `<tr data-thread="${esc(k)}"><td>${sw(t.color)}${esc(t.name)}</td><td>${dur(v)}</td><td class="dt-mute">${Math.round(v / Math.max(tot, 1) * 100)}%</td></tr>`; }).join("")}<tr><td class="dt-mute">idle or unknown</td><td class="dt-mute">${dur(b - a - tot)}</td><td></td></tr></table>`;
      const log = [];
      for (const s of M.day.sessions) for (const p of s.prompts) if (p.m >= a && p.m <= b) { const ss = [...M.byKey.values()].flatMap(t => t.sessions).find(x => x.id === s.id && x.prompts[0].m === s.prompts[0].m); log.push({m: p.m, kind: "prompt", c: M.byKey.get(ss?.thread)?.color, html: `${esc(cut(p.text, 220))} <span class="dt-mute">· ${esc(s.title)}</span>`}); }
      for (const c of M.day.commits) if (c.m >= a && c.m <= b && (!c.auto || cfg.auto === "faint")) log.push({m: c.m, kind: "commit", c: M.byKey.get(threadKey(c.repo, cfg.grouping))?.color, html: `${esc(c.msg)} <span class="dt-mute">· ${esc(c.repo.split("/").pop())}</span>`});
      for (const e of M.day.events) if (e.kind !== "sleep" && e.b >= a && e.a <= b) log.push({m: Math.max(e.a, a), kind: "call", c: "#2f9b6a", html: `${esc(e.title)} <span class="dt-mute">${hm(e.a)}–${hm(e.b)}</span>`});
      if (cfg.browser !== "off") { let last = null; for (const v of M.visits) if (v.m >= a && v.m <= b) {
        if (last && last.host === v.host && v.m - last.m2 < 10) { last.n++; last.m2 = v.m; if (!last.titles.includes(v.title)) last.titles.push(v.title); continue; }
        last = {m: v.m, m2: v.m, kind: "page", host: v.host, n: 1, titles: [v.title], c: CAT_COLOR[v.cat]}; log.push(last); }
        log.filter(x => x.kind === "page").forEach(x => x.html = `${esc(x.host)}${x.n > 1 ? ` ×${x.n}` : ""} <span class="dt-mute">· ${esc(cut(x.titles.slice(0, 2).join(" · "), 160))}</span>`); }
      log.sort((x, y) => x.m - y.m);
      const kinds = ["prompt", "commit", "call", "page"];
      h += `<h4>Log <span class="dt-filters">${kinds.map(k => `<label><input type="checkbox" data-kind="${k}" checked> ${k}s ${log.filter(x => x.kind === k).length}</label>`).join("")}</span></h4>`;
      h += `<ul class="dt-log">${log.map(x => `<li data-kind="${x.kind}" data-m="${x.m}"><span class="dt-tm">${hm(x.m)}</span><span class="dt-k" style="--c:${x.c || "#999"}">${x.kind[0]}</span><span>${x.html}</span></li>`).join("")}</ul>`;
      return h;
    }
    function itemInsp(it) {
      if (it.type === "prompt" || it.type === "turn") return `<div class="dt-mute">${sw(it.t.color)}${esc(it.t.name)}</div>` + sessBlock(it.s, it.p);
      if (it.type === "commit") { const near = [...it.t.commits, ...it.t.auto].filter(c => c.repo === it.c.repo && Math.abs(c.m - it.c.m) <= 30).sort((a, b) => a.m - b.m);
        return `<div class="dt-ih">${sw(it.t.color)}<b>${esc(it.c.msg)}</b></div><div class="dt-mute">${esc(it.c.repo)} · ${it.c.hash} · ${hm(it.c.m)} · ${it.c.files} files +${it.c.add} −${it.c.del}${it.c.auto ? " · by " + esc(it.c.auto) : ""}</div><h4>Same repo within 30 minutes</h4><ul class="dt-clist">${near.map(commitLi).join("")}</ul>`; }
      if (it.type === "call") return callBlock(it.e);
      if (it.type === "visit") { const same = M.visits.filter(v => v.host === it.v.host);
        return `<div class="dt-ih">${sw(CAT_COLOR[it.v.cat])}<b>${esc(it.v.host)}</b> <span class="dt-mute">${esc(catName(it.v.cat))} · ${esc(it.v.profile)}</span></div><div class="dt-q">${hm(it.v.m)} · ${esc(it.v.title)}</div><h4>All ${same.length} visits to this site</h4><ul class="dt-clist">${same.map(v => `<li class="${v === it.v ? "dt-hl" : ""}"><span class="dt-tm">${hm(v.m)}</span><span>${esc(v.title)}</span></li>`).join("")}</ul>`; }
      if (it.type === "focus") return `<div class="dt-ih">${sw(it.t.color)}<b>${esc(it.f.title || it.f.path)}</b></div><div class="dt-mute">${it.f.kind} · ${hm(it.f.a)}–${hm(it.f.b)} · ${esc(it.f.path)}</div>`;
      if (it.type === "seg" || it.type === "hour") return null;
      return "";
    }
    function searchInsp() {
      const hits = [];
      for (const t of M.threads) { for (const s of t.sessions) for (const p of s.prompts) if (matches(p.text) || matches(s.title)) hits.push({m: p.m, t, html: `${esc(cut(p.text, 200))} <span class="dt-mute">· ${esc(s.title)}</span>`});
        for (const c of t.commits) if (matches(c.msg)) hits.push({m: c.m, t, html: esc(c.msg)});
        for (const e of t.events) if (matches(e.title)) hits.push({m: e.a, t, html: esc(e.title)}); }
      for (const v of M.visits) if (matches(v.title + " " + v.host)) hits.push({m: v.m, t: M.byKey.get(WEB), html: `${esc(v.host)} · ${esc(v.title)}`});
      hits.sort((a, b) => a.m - b.m);
      return `<div class="dt-ih"><b>${hits.length}</b> matches for “${esc(query)}”</div><ul class="dt-log">${hits.slice(0, 300).map(x => `<li data-m="${x.m}"><span class="dt-tm">${hm(x.m)}</span><span class="dt-k" style="--c:${x.t?.color}">·</span><span>${x.html}</span></li>`).join("")}</ul>`;
    }
    function inspector() {
      let h;
      if (sel?.item) h = itemInsp(sel.item);
      if (h == null && (sel?.thread)) h = threadInsp(M.byKey.get(sel.thread));
      if (h == null && brush) h = windowInsp(brush);
      if (h == null && query) h = searchInsp();
      if (h == null) h = dayInsp();
      const crumbs = sel || brush || query ? `<button class="dt-back" data-back>← Day overview</button>` : "";
      insp.innerHTML = crumbs + h;
    }

    // ---------- interaction ----------
    function trackTime(ev) { const tr = grid.querySelector(".dt-axis .dt-track"); const r = tr.getBoundingClientRect(); const [a, b] = domain();
      return {m: a + (ev.clientX - r.left) / r.width * (b - a), inside: ev.clientX >= r.left && ev.clientX <= r.right, r}; }
    let drag = null;
    grid.addEventListener("mousedown", ev => {
      if (ev.button !== 0 || ev.target.closest(".dt-lab")) return;
      const {m, inside} = trackTime(ev); if (!inside) return;
      drag = {m0: m, x0: ev.clientX, moved: false}; ev.preventDefault();
    });
    window.addEventListener("mousemove", ev => {
      if (!root.isConnected) return;
      const {m, inside, r} = trackTime(ev); const cur = grid.querySelector(".dt-cursor");
      const gr = grid.getBoundingClientRect(); const over = inside && ev.clientY >= gr.top && ev.clientY <= gr.bottom;
      if (cur) { cur.hidden = !over && !drag; if (over || drag) { cur.style.left = `${(ev.clientX - r.left) / r.width * 100}%`; cur.querySelector("span").textContent = hm(m); cur.style.height = `${gr.bottom - r.top}px`; } }
      if (drag) { if (Math.abs(ev.clientX - drag.x0) > 4) drag.moved = true;
        if (drag.moved) { const [lo, hi] = domain(); brush = [Math.max(lo, Math.min(drag.m0, m)), Math.min(hi, Math.max(drag.m0, m))];
          const gl = grid.querySelector(".dt-gridlines"); gl.innerHTML = gridlines(); } }
      const el = ev.target.closest?.("[data-i]");
      if (el && root.contains(el) && !drag) showTip(el, ev); else tip.hidden = true;
    });
    window.addEventListener("mouseup", ev => {
      if (!drag) return; const d = drag; drag = null;
      if (d.moved) { sel = null; brush = brush && brush[1] - brush[0] >= 1 ? brush.map(Math.round) : null; draw(); return; }
      const el = ev.target.closest("[data-i]");
      if (el && root.contains(el)) { const it = items[+el.dataset.i];
        sel = it.type === "seg" || it.type === "hour" ? {thread: it.t?.key} : {item: it, thread: it.t?.key}; draw(); return; }
      if (brush || sel) { brush = null; sel = null; draw(); }
    });
    root.addEventListener("click", ev => {
      const b = ev.target.closest("[data-back]"); if (b) { sel = null; brush = null; query = ""; opts.onQuery?.(""); draw(); return; }
      const uf = ev.target.closest("[data-unfold]"); if (uf) { view = uf.dataset.unfold === "left" ? [0, M.range[1]] : [M.range[0], 1440]; draw(); return; }
      const gr = ev.target.closest("[data-group]"); if (gr) { const k = gr.dataset.group; expanded.has(k) ? expanded.delete(k) : expanded.add(k); draw(); return; }
      const mi = ev.target.closest("[data-minor]"); if (mi) { showMinor = !showMinor; draw(); return; }
      const lb = ev.target.closest(".dt-lbtn[data-thread]");
      if (lb) { const k = lb.dataset.thread; if (expanded.has(k)) expanded.delete(k); else expanded.add(k); sel = {thread: k}; draw(); return; }
      const th = ev.target.closest("[data-thread]"); if (th && insp?.contains(th)) { sel = {thread: th.dataset.thread}; draw(); return; }
      const lm = ev.target.closest("li[data-m]"); if (lm && insp?.contains(lm)) { pin = +lm.dataset.m;
        const [a, b] = domain(); if (pin < a || pin > b) view = null;
        insp.querySelectorAll("li.dt-pinned").forEach(x => x.classList.remove("dt-pinned")); lm.classList.add("dt-pinned");
        grid.querySelector(".dt-gridlines").innerHTML = gridlines(); return; }
    });
    root.addEventListener("change", ev => {
      const s = ev.target.closest(".dt-add");
      if (s) { const p = M.priorities.find(x => x.text === s.dataset.prio); let cur = manual(p);
        cur = s.value === "§clear" ? [] : [...new Set([...cur, s.value])];
        try { localStorage.setItem(manualKey(M.day.date, p.text), JSON.stringify(cur)); } catch {}
        draw(); return; }
      const k = ev.target.closest("[data-kind]"); if (k && k.type === "checkbox") insp.querySelectorAll(`.dt-log li[data-kind="${k.dataset.kind}"]`).forEach(li => li.hidden = !k.checked);
    });
    function showTip(el, ev) {
      const it = items[+el.dataset.i]; if (!it) return; let h = "";
      if (it.type === "prompt") h = `<b>${hm(it.p.m)} prompt</b> · ${esc(it.s.title)}<br>${esc(cut(it.p.text, 260))}`;
      else if (it.type === "turn") h = `<b>agent turn ${hm(it.p.m)}–${hm(it.p.end)}</b> (${dur(it.p.end - it.p.m)}) · ${esc(it.s.title)}`;
      else if (it.type === "commit") h = `<b>${hm(it.c.m)} commit</b> ${esc(it.c.repo.split("/").pop())} +${it.c.add}−${it.c.del}${it.c.auto ? " · " + esc(it.c.auto) : ""}<br>${esc(it.c.msg)}`;
      else if (it.type === "seg") h = `<b>${esc(it.t?.name)}</b> ${hm(it.s.a)}–${hm(it.s.b)} (${dur(it.s.b - it.s.a)})`;
      else if (it.type === "hour") h = `<b>${hm(it.hr)}</b> · ${esc(it.t?.name)} ${dur(it.v)}`;
      else if (it.type === "call") h = `<b>${hm(it.e.a)}–${hm(it.e.b)}</b> ${esc(it.e.title)}${it.e.summary ? "<br>" + esc(cut(it.e.summary.gist, 220)) : ""}`;
      else if (it.type === "visit") h = `<b>${hm(it.v.m)}</b> ${esc(it.v.host)}<br>${esc(it.v.title)}`;
      else if (it.type === "focus") h = `<b>focus ${hm(it.f.a)}–${hm(it.f.b)}</b> ${esc(it.f.title || it.f.path)}`;
      tip.innerHTML = h; tip.hidden = false;
      const rr = root.getBoundingClientRect(); let x = ev.clientX - rr.left + 12, y = ev.clientY - rr.top + 14;
      tip.style.left = Math.min(x, rr.width - 330) + "px"; tip.style.top = y + "px";
    }
    let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => root.isConnected && draw(), 120); });

    const api = {
      get model() { return M; }, get day() { return dayIdx; },
      load, step: d => load(dayIdx + d),
      zoom() { if (brush) { view = brush; brush = null; draw(); } },
      reset() { view = null; brush = null; sel = null; draw(); },
      clear() { if (sel || brush) { sel = null; brush = null; } else if (view) view = null; else if (query) { query = ""; opts.onQuery?.(""); } draw(); },
      search(q) { query = (q || "").trim().toLowerCase(); sel = null; draw(); },
      toggleAll() { const ks = M.threads.filter(t => !t.minor && t.key !== CALLS).map(t => t.key); const all = ks.every(k => expanded.has(k)); ks.forEach(k => all ? expanded.delete(k) : expanded.add(k)); draw(); },
      set(k, v) { cfg[k] = v; M = model(data.days[dayIdx], cfg); draw(); }, get cfg() { return cfg; },
    };
    load(dayIdx);
    return api;
  }
  return {render, model, DEFAULTS, hm, dur};
})();
