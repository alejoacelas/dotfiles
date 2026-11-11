// timeline.js: where Alejo's attention went on a day, by topic and task (from story.py), plus what agents did.
// Views: attention (timeline rows), tasks (list), agents (agent turns and commits). No dependencies.
"use strict";
const DT = (() => {
  const DEFAULTS = {view: "attention", rows: "topics", range: "fixed", gapFill: 10, taskSort: "attention", inspector: "right"};
  const KIND_ORDER = ["building", "calls", "comms", "admin", "learning", "personal", "leisure"];
  const KIND_NAME = {building: "Building", calls: "Calls", comms: "Messages & email", admin: "Admin", learning: "Reading & learning",
    personal: "Personal", leisure: "Leisure"};
  const PALETTE = ["#3f6fd8", "#d0832a", "#8a5cc7", "#2f9b6a", "#c2507a", "#2a9bb0", "#b8a12a", "#d1572f", "#5a8f3c",
    "#7a6bd8", "#c46fb3", "#3c8f86", "#a2703d", "#6d7fa8"];
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
  const hm = m => { m = Math.max(0, Math.min(1440, m)); return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(Math.floor(m % 60)).padStart(2, "0")}`; };
  const dur = m => { m = Math.round(m); return m >= 60 ? `${Math.floor(m / 60)}h${String(m % 60).padStart(2, "0")}` : `${m}m`; };
  const cut = (s, n) => s && s.length > n ? s.slice(0, n - 1) + "…" : (s || "");
  function hashColor(name, used) {
    let h = 0; for (const c of name.toLowerCase()) h = (h * 31 + c.charCodeAt(0)) >>> 0;
    for (let i = 0; i < PALETTE.length; i++) { const c = PALETTE[(h + i) % PALETTE.length]; if (!used.has(c)) { used.add(c); return c; } }
    return PALETTE[h % PALETTE.length];
  }
  function parsePriorities(md) {
    const out = []; let on = false;
    for (const l of (md || "").split("\n")) {
      if (/^##\s*current priorities/i.test(l)) { on = true; continue; }
      if (on && /^##\s/.test(l)) break;
      const m = on && l.match(/^\s*(?:(\d+)\.|[-*])\s+(.*\S)/); if (m) out.push({text: m[2], numbered: !!m[1], n: out.length + 1});
    }
    return out;
  }
  const reflection = md => ((md || "").split(/^##\s*Sofi\s*$/m)[1] || "").split(/^##\s/m)[0].replace(/\\([\[\]])/g, "$1").replace(/\*/g, "").trim();

  // ---------- model ----------
  function model(day, story, cfg) {
    const S = story || folderStory(day);
    const used = new Set();
    const topics = new Map(S.topics.map(t => [t.id, {...t, short: t.short || cut(t.label, 14), tasks: [], att: 0, agent: 0, unattended: 0, commits: []}]));
    const tasks = new Map();
    for (const k of S.tasks) { const t = topics.get(k.topic); if (!t) continue;
      const x = {...k, topicObj: t, att: 0, events: [], segs: [], agent: 0}; tasks.set(k.id, x); t.tasks.push(x); }
    const taskOfEv = new Map(); for (const a of S.assign) for (const id of a.events) if (tasks.has(a.task)) taskOfEv.set(id, tasks.get(a.task));
    const evs = (S.events || []).map(e => ({...e, task: taskOfEv.get(e.id)}));
    for (const e of evs) if (e.task) e.task.events.push(e);
    // join raw records to story events
    const promptTask = new Map(evs.filter(e => e.type === "prompt").map(e => [`${e.sid}:${e.pi}`, e.task]));
    const pages = evs.filter(e => e.type === "page");
    const visitTask = v => { const p = pages.find(p => p.title === v.title && v.m >= p.m - 0.02 && v.m <= (p.m2 ?? p.m) + 0.02); return p?.task; };
    const callEv = evs.filter(e => e.type === "call" || e.type === "calendar");
    const focusEv = evs.filter(e => e.type === "focus");
    const commitTask = new Map(evs.filter(e => e.type === "commit").map(e => [`${e.repo}:${e.m}`, e.task]));

    const score = new Map(); const sc = k => { if (!score.has(k)) score.set(k, new Float32Array(1440)); return score.get(k); };
    const put = (task, a, b, w) => { if (!task) return; const arr = sc(task.id); for (let m = Math.max(0, Math.floor(a)); m < Math.min(1440, Math.ceil(b)); m++) if (arr[m] < w) arr[m] = w; };
    const calls = [];
    for (const e of day.events) { if (e.kind === "sleep") continue;
      const se = callEv.find(c => Math.abs(c.m - e.a) < 0.02); const x = {...e, task: se?.task}; if (e.kind === "call") calls.push(x);
      if (e.kind === "call") put(x.task, e.a, e.b, 5); }
    const sessions = day.sessions.map(s => ({...s, prompts: s.prompts.map((p, i) => ({...p, task: promptTask.get(`${s.id}:${i}`)}))}));
    const sessById = new Map(sessions.map(s => [s.id, s]));
    for (const f of day.focus) {
      let task;
      if (f.session && sessById.has(f.session)) { const ps = sessById.get(f.session).prompts;
        const before = ps.filter(p => p.m <= f.a + 1); task = (before[before.length - 1] || ps[0])?.task; }
      else task = focusEv.find(e => Math.abs(e.m - f.a) < 0.02)?.task;
      put(task, f.a, f.b, 3);
    }
    for (const s of sessions) s.prompts.forEach((p, i) => { put(p.task, p.m - 3, p.m + 1, 2);
      const n = s.prompts[i + 1]; if (n && n.task === p.task && n.m - p.m <= cfg.gapFill) put(p.task, p.m, n.m, 1); });
    const visits = day.visits.map(v => ({...v, task: visitTask(v)}));
    visits.forEach((v, i) => { put(v.task, v.m, v.m + Math.min(Math.max(v.dur, 1), 3), 0.8);
      const n = visits[i + 1]; if (n && n.task === v.task && n.m - v.m <= 4) put(v.task, v.m, n.m, 0.6); });
    // each minute goes to the task with the strongest evidence
    const win = new Array(1440).fill(null);
    for (let m = 0; m < 1440; m++) { let best = null, bw = 0.4; for (const [k, arr] of score) if (arr[m] > bw) { bw = arr[m]; best = k; } win[m] = best; }
    let runs = []; for (let m = 0; m < 1440; m++) { const k = win[m]; const r = runs[runs.length - 1];
      if (r && r.k === k && r.b === m) r.b++; else runs.push({k, a: m, b: m + 1}); }
    runs = runs.filter(r => r.k).map(r => ({task: tasks.get(r.k), a: r.a, b: r.b}));
    // short gaps inside one topic count for the task before the gap; one-minute blips join a neighbour
    const fill = Math.min(cfg.gapFill, 15);
    for (let i = 1; i < runs.length; i++) { const p = runs[i - 1], r = runs[i];
      if (r.a > p.b && r.a - p.b <= fill && r.task.topicObj === p.task.topicObj) p.b = r.a; }
    for (let i = 0; i < runs.length; i++) { const r = runs[i]; if (r.b - r.a > 1) continue;
      const p = runs[i - 1], n = runs[i + 1]; const nb = [p, n].filter(x => x && (x.b === r.a || x.a === r.b)).sort((x, y) => (y.b - y.a) - (x.b - x.a))[0];
      if (nb && r.task.topicObj.kind !== "calls") { if (nb === p) p.b = r.b; else n.a = r.a; runs.splice(i--, 1); } }
    for (const r of runs) { r.task.att += r.b - r.a; r.task.segs.push(r); r.task.topicObj.att += r.b - r.a; }
    // topic blocks: consecutive runs of one topic
    const blocks = [];
    for (const r of runs) { const p = blocks[blocks.length - 1]; const t = r.task.topicObj;
      if (p && p.topic === t && r.a - p.b <= fill) { p.b = r.b; p.runs.push(r); } else blocks.push({topic: t, a: r.a, b: r.b, runs: [r]}); }

    // agents: turns per topic, and how much of it ran while attention was elsewhere
    const winTopic = m => { const k = win[m]; return k ? tasks.get(k).topicObj : null; };
    const turns = [];
    for (const s of sessions) for (const p of s.prompts) if (p.task) turns.push({s, p, task: p.task, topic: p.task.topicObj, a: p.m, b: Math.max(p.end, p.m + 0.5)});
    const agentAt = new Map();
    for (const t of turns) for (let m = Math.floor(t.a); m < Math.ceil(t.b); m++) { const set = agentAt.get(t.topic) || new Set(); set.add(m); agentAt.set(t.topic, set); }
    for (const [t, set] of agentAt) { t.agent = set.size; t.unattended = [...set].filter(m => winTopic(m) !== t).length; }
    for (const t of tasks.values()) t.agent = new Set(turns.filter(x => x.task === t).flatMap(x => { const r = []; for (let m = Math.floor(x.a); m < Math.ceil(x.b); m++) r.push(m); return r; })).size;
    const conc = new Uint8Array(1440); for (const t of turns) for (let m = Math.floor(t.a); m < Math.min(1440, Math.ceil(t.b)); m++) conc[m]++;
    const commits = day.commits.filter(c => !c.auto).map(c => ({...c, task: commitTask.get(`${c.repo}:${c.m}`)}));
    for (const c of commits) if (c.task) c.task.topicObj.commits.push(c);

    const topicList = [...topics.values()].filter(t => t.att || t.agent || t.tasks.some(k => k.events.length))
      .sort((a, b) => b.att - a.att || b.agent - a.agent);
    for (const t of topicList) { t.color = hashColor(t.label, used); t.tasks.sort((a, b) => b.att - a.att || b.agent - a.agent); }
    const taskList = topicList.flatMap(t => t.tasks);

    const marks = runs.flatMap(r => [r.a, r.b]).concat(calls.flatMap(e => [e.a, e.b]));
    const lo = marks.length ? Math.min(...marks) : 480, hi = marks.length ? Math.max(...marks) : 1200;
    const range = cfg.range === "fixed" ? [360, 1440] : [Math.max(0, Math.floor((lo - 20) / 60) * 60), Math.min(1440, Math.ceil((hi + 20) / 60) * 60)];
    const outside = side => { const f = side < 0 ? (m => m < range[0]) : (m => m >= range[1]);
      const n = {active: runs.reduce((a, r) => a + Math.max(0, side < 0 ? Math.min(r.b, range[0]) - r.a : r.b - Math.max(r.a, range[1])), 0),
        prompts: sessions.reduce((a, s) => a + s.prompts.filter(p => f(p.m)).length, 0)};
      return n.active >= 1 || n.prompts ? n : null; };
    const prios = parsePriorities(day.plans).map(p => ({...p, topics: topicList.filter(t => t.priority === p.n)}));
    const stats = {att: runs.reduce((a, r) => a + r.b - r.a, 0), calls: calls.reduce((a, e) => a + e.b - e.a, 0), ncalls: calls.length,
      first: runs[0]?.a, last: runs[runs.length - 1]?.b, prompts: sessions.reduce((a, s) => a + s.prompts.length, 0),
      agent: conc.reduce((a, v) => a + (v > 0), 0), peak: Math.max(0, ...conc), commits: commits.length,
      work: topicList.filter(t => !["personal", "leisure"].includes(t.kind)).reduce((a, t) => a + t.att, 0)};
    return {day, story: S, fromFolders: !story, cfg, topics: topicList, tasks: taskList, runs, blocks, calls, visits, sessions, turns, conc, commits,
      range, folded: {left: outside(-1), right: outside(1)}, prios, reflection: reflection(day.plans), stats,
      sleep: day.events.filter(e => e.kind === "sleep"), evs, unassigned: (S.missing || []).length};
  }

  // A day without a story yet: one topic per folder, browsing as one topic. Shown with a notice.
  function folderStory(day) {
    const key = p => (p || "other").split("/").pop().replace(/^\d{4}-\d{2}(-\d{2})?-/, "");
    const topics = new Map(), tasks = [], assign = new Map(), events = [];
    const add = (k, kind) => { if (!topics.has(k)) { topics.set(k, {id: k, label: k.replace(/-/g, " "), short: cut(k.replace(/-/g, " "), 14), kind, priority: null, summary: ""});
      tasks.push({id: k + "·t", topic: k, label: "Work in " + k.replace(/-/g, " "), outcome: "", highlights: []}); assign.set(k + "·t", []); } return k + "·t"; };
    let i = 0;
    for (const s of day.sessions) s.prompts.forEach((p, pi) => { const id = "p" + i++; events.push({id, type: "prompt", m: p.m, sid: s.id, pi, text: p.text, session: s.title}); assign.get(add(key(s.project), "building")).push(id); });
    for (const v of day.visits) { const id = "w" + i++; events.push({id, type: "page", m: v.m, m2: v.m, title: v.title, host: v.host}); assign.get(add("browsing", "learning")).push(id); }
    for (const e of day.events) if (e.kind !== "sleep") { const id = "c" + i++; events.push({id, type: e.kind === "call" ? "call" : "calendar", m: e.a, m2: e.b, title: e.title}); assign.get(add("calls", "calls")).push(id); }
    return {topics: [...topics.values()], tasks, assign: [...assign].map(([task, events]) => ({task, events})), events, missing: []};
  }

  // ---------- render ----------
  function render(root, data, cfgIn, opts = {}) {
    const cfg = {...DEFAULTS, ...cfgIn};
    let M, dayIdx = opts.day ?? data.days.length - 1, view = null, sel = null, brush = null, query = "", pin = null, win = null;
    const expanded = new Set();
    root.classList.add("dt");
    root.innerHTML = `<div class="dt-wrap dt-insp-${cfg.inspector}"><div class="dt-main"></div><aside class="dt-insp"></aside></div><div class="dt-tip" hidden></div>`;
    const main = root.querySelector(".dt-main"), insp = root.querySelector(".dt-insp"), tip = root.querySelector(".dt-tip");
    let grid = null, items = [];
    const reg = it => { items.push(it); return items.length - 1; };
    const story = d => data.stories?.[d.date];
    function load(i) { dayIdx = Math.max(0, Math.min(data.days.length - 1, i)); M = model(data.days[dayIdx], story(data.days[dayIdx]), cfg);
      view = null; win = null; sel = null; brush = null; pin = null; expanded.clear(); draw(); opts.onDay?.(M); }
    const domain = () => view || M.range;
    const X = m => { const [a, b] = domain(); return (m - a) / (b - a) * 100; };
    const W = (a, b) => Math.max(X(b) - X(a), 0);
    const visible = (a, b) => { const [lo, hi] = domain(); return b >= lo && a <= hi; };
    const matches = s => query && s && s.toLowerCase().includes(query);
    const trackPx = () => (grid?.querySelector(".dt-track")?.clientWidth || 900) / 100;
    const sw = c => `<span class="dt-sw" style="background:${c}"></span>`;
    const prioBadge = t => t.priority ? `<span class="dt-pr" title="Serves priority ${t.priority}">P${t.priority}</span>` : "";

    function row(cls, lab, track, attrs = "") { return `<div class="dt-row ${cls}" ${attrs}><div class="dt-lab">${lab}</div><div class="dt-track">${track}</div></div>`; }
    function axis() { const [a, b] = domain(), span = b - a; const step = span > 720 ? 120 : span > 300 ? 60 : span > 120 ? 30 : span > 50 ? 15 : 5;
      let h = ""; for (let m = Math.ceil(a / step) * step; m <= b; m += step) h += `<span style="left:${X(m)}%">${hm(m)}</span>`; return h; }
    function gridlines() { const [a, b] = domain(), span = b - a, step = span > 300 ? 60 : span > 120 ? 30 : 15;
      let h = ""; for (let m = Math.ceil(a / step) * step; m <= b; m += step) h += `<i style="left:${X(m)}%"></i>`;
      for (const s of M.sleep) if (visible(s.a, s.b)) h += `<b class="dt-sleep" style="left:${X(s.a)}%;width:${W(s.a, s.b)}%"></b>`;
      if (pin != null && visible(pin, pin)) h += `<b class="dt-pin" style="left:${X(pin)}%"></b>`;
      if (brush) h += `<b class="dt-brushed" style="left:${X(brush[0])}%;width:${W(brush[0], brush[1])}%"></b>`;
      return h; }
    const bar = (cls, a, b, color, it, extra = "") => visible(a, b) ? `<b class="${cls}" data-i="${reg(it)}" style="left:${X(a)}%;width:${Math.max(W(a, b), 0.15)}%;background:${color};${extra}"></b>` : "";

    function axisRow() {
      return row("dt-axis", `<span class="dt-dayname">${esc(M.day.weekday.replace(/ \d{4}$/, ""))}</span>`, `<div class="dt-ticks">${axis()}</div><div class="dt-cursor" hidden><span></span></div>`);
    }
    function foldMarks() {
      let h = ""; if (view) return h;
      for (const [side, n] of [["left", M.folded.left], ["right", M.folded.right]]) if (n) {
        const parts = [n.active >= 1 && `${dur(n.active)} attention`, n.prompts && `${n.prompts} prompts`].filter(Boolean).join(" · ");
        h += `<button class="dt-fold dt-fold-${side}" data-unfold="${side}" title="${side === "left" ? "Before" : "After"} this range. Click to show it.">${side === "left" ? "◂ " : ""}${parts}${side === "right" ? " ▸" : ""}</button>`; }
      return h;
    }
    // hourly bars: the top two topics of each hour, then a label row naming the hour's main topic
    function hourRows() {
      const [a, b] = domain(); let bars = "", labels = "";
      const hours = [];
      for (let h = Math.floor(a / 60) * 60; h < b; h += 60) {
        const parts = new Map(); for (const r of M.runs) { const o = Math.min(r.b, h + 60) - Math.max(r.a, h); if (o > 0) parts.set(r.task.topicObj, (parts.get(r.task.topicObj) || 0) + o); }
        const all = [...parts].sort((x, y) => y[1] - x[1]); const top = all.slice(0, 2), rest = all.slice(2).reduce((x, y) => x + y[1], 0);
        hours.push({h, top, rest, total: all.reduce((x, y) => x + y[1], 0)});
      }
      for (const {h, top, rest, total} of hours) {
        let y = 0; bars += `<div class="dt-hour" style="left:${X(h)}%;width:${W(h, h + 60)}%">` + top.map(([t, v]) => {
          const el = `<b data-i="${reg({type: "hour", h, t, v, total, rest})}" style="bottom:${y / 60 * 100}%;height:${v / 60 * 100}%;background:${t.color}"></b>`; y += v; return el; }).join("") + `</div>`;
      }
      const px = trackPx(); let i = 0;
      while (i < hours.length) { const t = hours[i].top[0]?.[0]; let j = i; while (j + 1 < hours.length && hours[j + 1].top[0]?.[0] === t) j++;
        if (t && hours.slice(i, j + 1).some(x => x.top[0][1] >= 15)) { const w = W(hours[i].h, hours[j].h + 60);
          labels += `<span class="dt-hlab" style="left:${X(hours[i].h)}%;width:${w}%;color:${t.color}" data-i="${reg({type: "topic", t})}">${esc(w * px > 30 ? (w * px > 90 ? t.label : t.short) : "")}</span>`; }
        i = j + 1; }
      return row("dt-hours", `<span class="dt-striplab" title="Each hour shows the two topics that held your attention longest; the bar's height is minutes out of 60.">Each hour <span class="dt-min">${dur(M.stats.att)}</span></span>`, bars + foldMarks()) +
        row("dt-hlabels", "", labels);
    }
    function calRow() {
      const ev = M.day.events.filter(e => e.kind !== "sleep"); if (!ev.length) return "";
      let h = ""; const px = trackPx();
      for (const e of ev) { if (!visible(e.a, e.b)) continue; const w = W(e.a, e.b); const c = M.calls.find(x => x.a === e.a && x.title === e.title);
        h += `<b class="dt-ev ${e.kind}${matches(e.title) ? " dt-hit" : ""}" data-i="${reg({type: "call", e: c || e})}" style="left:${X(e.a)}%;width:${w}%">${w * px > 40 ? `<span>${esc(e.title)}</span>` : ""}</b>`; }
      return row("dt-cal", `<span class="dt-striplab">Calendar <span class="dt-min">${M.stats.ncalls ? dur(M.stats.calls) : ""}</span></span>`, h);
    }
    const runBars = (runs, opt = {}) => runs.map(r => bar("dt-att" + (opt.cls || ""), r.a, r.b, r.task.topicObj.color, {type: "block", r, block: M.blocks.find(b => b.runs.includes(r))})).join("");
    const topicLabel = (t, open) => `<button class="dt-lbtn" data-topic="${esc(t.id)}" aria-expanded="${open}"><span class="dt-caret">${open ? "▾" : "▸"}</span>${sw(t.color)}<span class="dt-name" title="${esc(t.label)}">${esc(t.label)}</span>${prioBadge(t)}<span class="dt-min">${dur(t.att)}</span></button>`;
    const taskLabel = k => `<button class="dt-lbtn dt-sublab" data-task="${esc(k.id)}" title="${esc(k.label)}"><span class="dt-name">${esc(k.label)}</span><span class="dt-min">${k.att ? dur(k.att) : ""}</span></button>`;

    function attentionRows() {
      let h = "";
      const att = M.topics.filter(t => t.att > 0), rest = M.topics.filter(t => !t.att);
      if (cfg.rows === "topics" || cfg.rows === "tasks") {
        for (const t of att) {
          const open = cfg.rows === "tasks" || expanded.has(t.id);
          h += row("dt-lane" + (sel?.topic === t ? " dt-selrow" : ""), topicLabel(t, open), runBars(M.runs.filter(r => r.task.topicObj === t)));
          if (open) for (const k of t.tasks.filter(k => k.att)) h += row("dt-sub" + (sel?.task === k ? " dt-selrow" : ""), taskLabel(k), runBars(k.segs, {cls: " dt-taskbar"}));
        }
        if (rest.length) h += row("dt-lane dt-minor", `<span class="dt-sublab" title="${esc(rest.map(t => t.label).join(", "))}">${rest.length} topics with agent work only · see Agents</span>`, "");
      } else {
        const groups = cfg.rows === "kinds"
          ? KIND_ORDER.map(k => ({key: k, label: KIND_NAME[k], topics: att.filter(t => t.kind === k)}))
          : [...M.prios.map(p => ({key: "p" + p.n, label: `P${p.n} ${p.text}`, topics: att.filter(t => t.priority === p.n), dim: !p.numbered})),
             {key: "other", label: "Other work", topics: att.filter(t => !M.prios.some(p => p.n === t.priority) && !["personal", "leisure"].includes(t.kind))},
             {key: "life", label: "Personal & leisure", topics: att.filter(t => !M.prios.some(p => p.n === t.priority) && ["personal", "leisure"].includes(t.kind))}];
        for (const g of groups) {
          if (!g.topics.length && cfg.rows === "kinds") continue;
          const min = g.topics.reduce((a, t) => a + t.att, 0), open = expanded.has(g.key);
          h += row("dt-lane", `<button class="dt-lbtn" data-group="${esc(g.key)}" aria-expanded="${open}"><span class="dt-caret">${g.topics.length ? (open ? "▾" : "▸") : ""}</span><span class="dt-name${g.dim ? " dt-mute" : ""}" title="${esc(g.label)}">${esc(g.label)}</span><span class="dt-min">${min ? dur(min) : "–"}</span></button>`,
            runBars(M.runs.filter(r => g.topics.includes(r.task.topicObj))));
          if (open) for (const t of g.topics) h += row("dt-sub", `<button class="dt-lbtn dt-sublab" data-topic="${esc(t.id)}">${sw(t.color)}<span class="dt-name">${esc(t.label)}</span><span class="dt-min">${dur(t.att)}</span></button>`, runBars(M.runs.filter(r => r.task.topicObj === t)));
        }
      }
      return h;
    }
    function agentRows() {
      let h = "";
      const max = Math.max(1, ...M.conc);
      let area = ""; const [a, b] = domain(); const step = (b - a) > 600 ? 5 : 1;
      for (let m = Math.floor(a / step) * step; m < b; m += step) { let v = 0; for (let k = m; k < m + step; k++) v = Math.max(v, M.conc[k] || 0);
        if (v) area += `<b class="dt-conc" style="left:${X(m)}%;width:${W(m, m + step)}%;height:${v / max * 100}%" data-i="${reg({type: "conc", m, v})}"></b>`; }
      h += row("dt-hours", `<span class="dt-striplab" title="How many agent turns were running at once">Agents working <span class="dt-min">peak ${M.stats.peak}</span></span>`, area + foldMarks());
      for (const t of M.topics.filter(t => t.agent || t.commits.length).sort((x, y) => y.agent - x.agent)) {
        const open = expanded.has(t.id);
        let tr = M.runs.filter(r => r.task.topicObj === t).map(r => bar("dt-you", r.a, r.b, t.color, {type: "block", r, block: M.blocks.find(bk => bk.runs.includes(r))})).join("");
        tr += M.turns.filter(x => x.topic === t).map(x => bar("dt-turnbar", x.a, x.b, t.color, {type: "turn", x})).join("");
        tr += t.commits.map(c => visible(c.m, c.m) ? `<b class="dt-commit${matches(c.msg) ? " dt-hit" : ""}" data-i="${reg({type: "commit", c, t})}" style="left:${X(c.m)}%;--c:${t.color}"></b>` : "").join("");
        h += row("dt-lane dt-agentlane" + (sel?.topic === t ? " dt-selrow" : ""), `<button class="dt-lbtn" data-topic="${esc(t.id)}" aria-expanded="${open}"><span class="dt-caret">${open ? "▾" : "▸"}</span>${sw(t.color)}<span class="dt-name" title="${esc(t.label)}">${esc(t.label)}</span><span class="dt-min" title="agent time · of it while your attention was elsewhere">${dur(t.agent)} · ${dur(t.unattended)}</span></button>`, tr);
        if (open) for (const k of t.tasks.filter(k => k.agent || M.commits.some(c => c.task === k))) {
          let st = M.turns.filter(x => x.task === k).map(x => bar("dt-turnbar", x.a, x.b, t.color, {type: "turn", x})).join("");
          st += M.commits.filter(c => c.task === k).map(c => visible(c.m, c.m) ? `<b class="dt-commit" data-i="${reg({type: "commit", c, t})}" style="left:${X(c.m)}%;--c:${t.color}"></b>` : "").join("");
          h += row("dt-sub", taskLabel(k), st);
        }
      }
      const loose = M.commits.filter(c => !c.task);
      if (loose.length) h += row("dt-lane dt-minor", `<span class="dt-sublab">Unlabelled commits <span class="dt-min">${loose.length}</span></span>`, loose.map(c => visible(c.m, c.m) ? `<b class="dt-commit" data-i="${reg({type: "commit", c})}" style="left:${X(c.m)}%;--c:#999"></b>` : "").join(""));
      return h;
    }
    function tasksList() {
      const list = [...M.tasks].filter(k => k.att || k.events.some(e => e.type !== "commit"));
      if (cfg.taskSort === "time") list.sort((a, b) => (a.segs[0]?.a ?? a.events[0]?.m ?? 1e4) - (b.segs[0]?.a ?? b.events[0]?.m ?? 1e4)); else list.sort((a, b) => b.att - a.att);
      const max = Math.max(1, ...list.map(k => k.att)); const [a, b] = M.range;
      const spark = k => `<span class="dt-spark">${k.segs.map(r => `<b style="left:${(r.a - a) / (b - a) * 100}%;width:${Math.max(0.6, (r.b - r.a) / (b - a) * 100)}%;background:${k.topicObj.color}"></b>`).join("")}</span>`;
      return `<div class="dt-tasks"><div class="dt-tasks-h"><span>Task · sorted by ${cfg.taskSort === "time" ? "start" : "attention"} (S)</span><span>Your attention</span><span>When (${hm(a)}–${hm(b)})</span><span>Outcome</span></div>${list.map(k =>
        `<div class="dt-taskrow${sel?.task === k ? " dt-selrow" : ""}" data-task="${esc(k.id)}"><span class="dt-tl">${sw(k.topicObj.color)}<span><b>${esc(k.label)}</b><br><span class="dt-mute">${esc(k.topicObj.label)}</span> ${prioBadge(k.topicObj)}</span></span>
         <span class="dt-ta"><span class="dt-tbar"><b style="width:${k.att / max * 100}%;background:${k.topicObj.color}"></b></span><span class="dt-min">${k.att ? dur(k.att) : "–"}</span></span>${spark(k)}<span class="dt-to">${esc(k.outcome)}</span></div>`).join("")}</div>`;
    }

    function draw() {
      items = []; tip.hidden = true;
      let h = "";
      if (cfg.view === "tasks") h = tasksList();
      else h = `<div class="dt-grid">${axisRow()}${cfg.view === "agents" ? agentRows() : hourRows() + calRow() + attentionRows()}<div class="dt-gridlines"></div></div>`;
      main.innerHTML = (M.fromFolders ? `<div class="dt-notice">No story for this day yet, so topics are folders. Run build.py to label it.</div>` : "") + h;
      grid = main.querySelector(".dt-grid");
      if (grid) { main.querySelector(".dt-gridlines").innerHTML = gridlines();
        // labels in the hour row need the measured width; redraw once if the first pass guessed
        if (!draw.measured) { draw.measured = true; return draw(); } }
      main.classList.toggle("dt-searching", !!query);
      inspector();
    }

    // ---------- inspector ----------
    const quote = (e, extra = "") => {
      const t = hm(e.m);
      if (e.type === "prompt") return `<li data-m="${e.m}"${extra}><span class="dt-tm">${t}</span><span><q title="${esc(e.text)}">${esc(cut(e.text, 240))}</q>${e.session ? ` <span class="dt-mute">· ${esc(cut(e.session, 50))}</span>` : ""}</span></li>`;
      if (e.type === "page") return `<li data-m="${e.m}"${extra}><span class="dt-tm">${t}</span><span><span class="dt-mute">opened</span> ${esc(e.title)} <span class="dt-mute">· ${esc(e.host || "")}</span></span></li>`;
      if (e.type === "call" || e.type === "calendar") return `<li data-m="${e.m}"${extra}><span class="dt-tm">${t}</span><span><b>${esc(e.title)}</b>${e.gist ? `<br><q>${esc(e.gist)}</q>` : ""}</span></li>`;
      if (e.type === "commit") return `<li data-m="${e.m}"${extra}><span class="dt-tm">${t}</span><span><span class="dt-mute">agent committed</span> ${esc(e.msg)}</span></li>`;
      return `<li data-m="${e.m}"${extra}><span class="dt-tm">${t}</span><span>${esc(e.title || e.text || "")}</span></li>`;
    };
    const evById = id => M.evs.find(e => e.id === id);
    // the verbatim snippets that best show what a stretch of time was about: the story's highlights first,
    // then the longest of your own prompts, then distinct page titles
    function snippets(taskSet, a, b, n = 5) {
      const inWin = e => e.m >= a - 3 && e.m <= b + 1;
      const hl = [...taskSet].flatMap(k => (k.highlights || []).map(evById)).filter(e => e && inWin(e) && e.type !== "commit");
      const evs = [...taskSet].flatMap(k => k.events);
      const prompts = evs.filter(e => e.type === "prompt" && inWin(e) && !hl.includes(e) && (e.text || "").length >= 40)
        .sort((x, y) => Math.min(y.text.length, 300) - Math.min(x.text.length, 300));
      const calls = evs.filter(e => e.type === "call" && e.m < b && (e.m2 ?? e.m) > a && !hl.includes(e));
      const seen = new Set(); const pages = evs.filter(e => e.type === "page" && inWin(e) && !hl.includes(e) && !/sign.?in|log in|redirect|^https?:|^(inbox|new tab|new session)/i.test(e.title || "") && !seen.has(e.title) && seen.add(e.title));
      return [...calls, ...hl, ...prompts.slice(0, Math.max(0, n - hl.length - calls.length)), ...pages.slice(0, 2)].sort((x, y) => x.m - y.m);
    }
    function overview() {
      const s = M.stats;
      let h = `<div class="dt-ov"><div><b>${dur(s.att)}</b> attention${s.first != null ? ` <span class="dt-mute">${hm(s.first)}–${hm(s.last)}</span>` : ""}</div><div><b>${dur(s.work)}</b> on work · <b>${dur(s.att - s.work)}</b> personal & leisure</div>
        <div class="dt-mute">${s.ncalls ? `${s.ncalls} call${s.ncalls > 1 ? "s" : ""} ${dur(s.calls)} · ` : ""}${s.prompts} prompts · agents ran ${dur(s.agent)}, up to ${s.peak} at once</div></div>`;
      h += `<h4>Where your attention went</h4><div class="dt-share">${M.topics.filter(t => t.att).map(t => `<b style="width:${t.att / Math.max(1, s.att) * 100}%;background:${t.color}" title="${esc(t.label)} ${dur(t.att)}"></b>`).join("")}</div>`;
      h += M.topics.filter(t => t.att).map(t => `<div class="dt-topic" data-topic="${esc(t.id)}"><div class="dt-topic-h">${sw(t.color)}<b>${esc(t.label)}</b>${prioBadge(t)}<span class="dt-min">${dur(t.att)} · ${Math.round(t.att / Math.max(1, s.att) * 100)}%</span></div>
        <div class="dt-mute">${esc(t.summary)}</div>${t.tasks.filter(k => k.att >= 3).slice(0, 3).map(k => `<div class="dt-tk" data-task="${esc(k.id)}">${esc(k.label)} <span class="dt-min">${dur(k.att)}</span></div>`).join("")}</div>`).join("");
      if (M.prios.length) h += `<h4>Priorities</h4>` + M.prios.map(p => { const m = p.topics.reduce((a, t) => a + t.att, 0);
        return `<div class="dt-prio"><span class="dt-pr${p.numbered ? "" : " dt-pr-lo"}">P${p.n}</span> <span>${esc(p.text)}</span> <span class="dt-min">${m ? dur(m) : p.topics.length ? "agents only" : "nothing"}</span></div>`; }).join("");
      if (M.calls.length) h += `<h4>Calls</h4><ul class="dt-qlist">${M.calls.map(e => quote({type: "call", m: e.a, title: `${e.title} · ${hm(e.a)}–${hm(e.b)}`, gist: e.summary?.gist})).join("")}</ul>`;
      if (M.reflection) h += `<h4>Your reflection</h4><details><summary class="dt-mute">${esc(cut(M.reflection, 110))}</summary><div class="dt-refl">${esc(M.reflection)}</div></details>`;
      const notes = [];
      if (M.fromFolders) notes.push("No story yet: topics are folders and all browsing is one topic.");
      if (!M.day.focus.length) notes.push("No Umi focus log for this day: attention comes from prompts, calls and page visits.");
      if (M.unassigned) notes.push(`${M.unassigned} events weren't placed in a task.`);
      (data.errors || []).forEach(e => notes.push(e));
      if (notes.length) h += `<h4>Data</h4><ul class="dt-notes">${notes.map(n => `<li>${esc(n)}</li>`).join("")}</ul>`;
      return h;
    }
    function topicInsp(t) {
      let h = `<div class="dt-ih">${sw(t.color)}<b>${esc(t.label)}</b> ${prioBadge(t)}</div><div class="dt-mute">${esc(KIND_NAME[t.kind] || t.kind)} · ${dur(t.att)} attention · agents ${dur(t.agent)}</div><p>${esc(t.summary)}</p>`;
      h += t.tasks.map(k => taskBlock(k)).join("");
      return h;
    }
    function taskBlock(k, full) {
      const hl = (k.highlights || []).map(evById).filter(Boolean).sort((a, b) => a.m - b.m);
      const spans = k.segs.length ? k.segs.map(r => `${hm(r.a)}–${hm(r.b)}`).slice(0, 4).join(", ") + (k.segs.length > 4 ? ` +${k.segs.length - 4}` : "") : "";
      let h = `<div class="dt-item"><div class="dt-it" data-task="${esc(k.id)}">${esc(k.label)} <span class="dt-min">${k.att ? dur(k.att) : "agents only"}</span></div><div class="dt-mute">${esc(spans)}</div><div class="dt-q">${esc(k.outcome)}</div>
        <ul class="dt-qlist">${hl.map(e => quote(e)).join("")}</ul>`;
      if (full) { const rest = k.events.filter(e => !hl.includes(e)).sort((a, b) => a.m - b.m);
        h += `<details><summary class="dt-mute">All ${rest.length} other events</summary><ul class="dt-qlist dt-small">${rest.map(e => quote(e)).join("")}</ul></details>`; }
      return h + `</div>`;
    }
    function blockInsp(r, block) {
      const bl = block || {topic: r.task.topicObj, a: r.a, b: r.b, runs: [r]}; const t = bl.topic;
      const per = new Map(); for (const x of bl.runs) per.set(x.task, (per.get(x.task) || 0) + x.b - x.a);
      let h = `<div class="dt-ih">${sw(t.color)}<b>${esc(t.label)}</b> ${prioBadge(t)}</div><div class="dt-mute">${hm(bl.a)}–${hm(bl.b)} · ${dur(bl.b - bl.a)} in this block · ${dur(t.att)} all day</div>`;
      h += [...per].sort((a, b) => b[1] - a[1]).map(([k, v]) => `<div class="dt-tk" data-task="${esc(k.id)}">${esc(k.label)} <span class="dt-min">${dur(v)}</span></div>`).join("");
      h += `<h4>In your words</h4><ul class="dt-qlist">${snippets(new Set(per.keys()), bl.a, bl.b).map(e => quote(e)).join("") || `<li class="dt-mute">No prompts or pages in this block; it comes from focus or a call.</li>`}</ul>`;
      return h;
    }
    function windowInsp([a, b]) {
      const per = new Map(); for (const r of M.runs) { const o = Math.min(r.b, b) - Math.max(r.a, a); if (o > 0) per.set(r.task, (per.get(r.task) || 0) + o); }
      const tot = [...per.values()].reduce((x, y) => x + y, 0);
      let h = `<div class="dt-ih"><b>${hm(a)}–${hm(b)}</b> <span class="dt-mute">${dur(b - a)} · double-click the timeline for the whole day</span></div>`;
      h += `<div class="dt-share">${[...per].sort((x, y) => y[1] - x[1]).map(([k, v]) => `<b style="width:${v / (b - a) * 100}%;background:${k.topicObj.color}" title="${esc(k.label)} ${dur(v)}"></b>`).join("")}</div>`;
      h += [...per].sort((x, y) => y[1] - x[1]).map(([k, v]) => `<div class="dt-tk" data-task="${esc(k.id)}">${sw(k.topicObj.color)}${esc(k.label)} <span class="dt-min">${dur(v)}</span></div>`).join("") + `<div class="dt-tk dt-mute">idle or unknown <span class="dt-min">${dur(b - a - tot)}</span></div>`;
      h += `<h4>In your words</h4><ul class="dt-qlist">${snippets(new Set(per.keys()), a, b, 8).map(e => quote(e)).join("")}</ul>`;
      return h;
    }
    function itemInsp(it) {
      if (it.type === "block") return blockInsp(it.r, it.block);
      if (it.type === "hour") return windowInsp([it.h, it.h + 60]);
      if (it.type === "topic") return topicInsp(it.t);
      if (it.type === "call") { const e = it.e; const k = e.task;
        return `<div class="dt-ih"><b>${esc(e.title)}</b></div><div class="dt-mute">${hm(e.a)}–${hm(e.b)}${e.people?.length ? " · " + esc(e.people.join(", ")) : ""}</div>${e.summary ? `<p><q>${esc(e.summary.gist)}</q></p><div class="dt-links">${e.summary.link ? `<a href="${esc(e.summary.link)}" target="_blank">Granola</a>` : ""} <span class="dt-mute">${esc(e.summary.path)}</span></div>` : ""}${k ? taskBlock(k) : ""}`; }
      if (it.type === "turn") return `<div class="dt-ih">${sw(it.x.topic.color)}<b>${esc(it.x.task.label)}</b></div><div class="dt-mute">agent turn ${hm(it.x.a)}–${hm(it.x.b)} (${dur(it.x.b - it.x.a)}) · ${esc(it.x.s.title)}</div><ul class="dt-qlist">${quote({type: "prompt", m: it.x.p.m, text: it.x.p.text})}</ul>${it.x.s.last_reply ? `<h4>Session's last reply</h4><p class="dt-q">${esc(it.x.s.last_reply)}</p>` : ""}`;
      if (it.type === "commit") { const near = M.commits.filter(c => c.repo === it.c.repo && Math.abs(c.m - it.c.m) <= 30).sort((a, b) => a.m - b.m);
        return `<div class="dt-ih"><b>${esc(it.c.msg)}</b></div><div class="dt-mute">${esc(it.c.repo)} · ${it.c.hash} · ${hm(it.c.m)} · +${it.c.add} −${it.c.del}${it.c.task ? " · " + esc(it.c.task.label) : ""}</div><h4>Same repository within 30 minutes</h4><ul class="dt-qlist">${near.map(c => quote({type: "commit", m: c.m, msg: c.msg})).join("")}</ul>`; }
      return null;
    }
    function agentsOverview() {
      let h = `<div class="dt-ov"><div><b>${dur(M.stats.agent)}</b> with at least one agent working, up to ${M.stats.peak} at once</div><div class="dt-mute">${M.stats.commits} commits by your agents</div></div>`;
      h += `<h4>By topic <span class="dt-mute">· agent time · while you were elsewhere</span></h4>`;
      h += M.topics.filter(t => t.agent || t.commits.length).sort((a, b) => b.agent - a.agent).map(t => `<div class="dt-topic" data-topic="${esc(t.id)}"><div class="dt-topic-h">${sw(t.color)}<b>${esc(t.label)}</b><span class="dt-min">${dur(t.agent)} · ${dur(t.unattended)}</span></div>
        <ul class="dt-qlist dt-small">${t.commits.slice(-4).map(c => quote({type: "commit", m: c.m, msg: c.msg})).join("")}</ul>${t.commits.length > 4 ? `<div class="dt-mute">${t.commits.length - 4} more commits</div>` : ""}</div>`).join("");
      return h;
    }
    function searchInsp() {
      const hits = M.evs.filter(e => matches(e.text) || matches(e.title) || matches(e.msg) || matches(e.task?.label)).sort((a, b) => a.m - b.m);
      return `<div class="dt-ih"><b>${hits.length}</b> matches for “${esc(query)}”</div><ul class="dt-qlist">${hits.slice(0, 200).map(e => quote(e)).join("")}</ul>`;
    }
    function inspector() {
      let h = null;
      if (sel?.item) h = itemInsp(sel.item);
      if (h == null && sel?.task) h = `<div class="dt-mute">${sw(sel.task.topicObj.color)}${esc(sel.task.topicObj.label)}</div>` + taskBlock(sel.task, true);
      if (h == null && sel?.topic) h = topicInsp(sel.topic);
      if (h == null && win) h = windowInsp(win);
      if (h == null && query) h = searchInsp();
      if (h == null) h = cfg.view === "agents" ? agentsOverview() : overview();
      insp.innerHTML = (sel || win || query ? `<button class="dt-back" data-back>← Day overview</button>` : "") + h;
    }

    // ---------- interaction ----------
    function trackTime(ev) { const tr = grid?.querySelector(".dt-axis .dt-track"); if (!tr) return {inside: false}; const r = tr.getBoundingClientRect(); const [a, b] = domain();
      return {m: a + (ev.clientX - r.left) / r.width * (b - a), inside: ev.clientX >= r.left && ev.clientX <= r.right, r}; }
    let drag = null;
    main.addEventListener("mousedown", ev => { if (ev.button !== 0 || ev.target.closest(".dt-lab, button")) return;
      const {m, inside} = trackTime(ev); if (!inside) return; drag = {m0: m, x0: ev.clientX, moved: false}; ev.preventDefault(); });
    window.addEventListener("mousemove", ev => {
      if (!root.isConnected) return;
      if (grid) { const {m, inside, r} = trackTime(ev); const cur = grid.querySelector(".dt-cursor"); const gr = grid.getBoundingClientRect();
        const over = inside && ev.clientY >= gr.top && ev.clientY <= gr.bottom;
        if (cur) { cur.hidden = !over && !drag; if (over || drag) { cur.style.left = `${(ev.clientX - r.left) / r.width * 100}%`; cur.querySelector("span").textContent = hm(m); cur.style.height = `${gr.bottom - r.top}px`; } }
        if (drag) { if (Math.abs(ev.clientX - drag.x0) > 4) drag.moved = true;
          if (drag.moved) { const [lo, hi] = domain(); brush = [Math.max(lo, Math.min(drag.m0, m)), Math.min(hi, Math.max(drag.m0, m))]; grid.querySelector(".dt-gridlines").innerHTML = gridlines(); } } }
      const el = ev.target.closest?.("[data-i]"); if (el && root.contains(el) && !drag) showTip(el, ev); else tip.hidden = true;
    });
    window.addEventListener("mouseup", ev => {
      if (!drag) return; const d = drag; drag = null;
      if (d.moved) { sel = null; if (brush && brush[1] - brush[0] >= 2) { view = brush.map(Math.round); win = view; } brush = null; draw(); return; }
      const el = ev.target.closest("[data-i]");
      if (el && root.contains(el)) { const it = items[+el.dataset.i]; sel = {item: it, topic: it.t || it.block?.topic || it.x?.topic}; draw(); return; }
      if (sel) { sel = null; draw(); }
    });
    // double-click anywhere on the timeline returns to the whole day
    main.addEventListener("dblclick", ev => { if (!grid || ev.target.closest(".dt-lab")) return; ev.preventDefault(); view = null; win = null; sel = null; pin = null; draw(); });
    root.addEventListener("click", ev => {
      if (ev.target.closest("[data-back]")) { sel = null; win = null; view = null; query = ""; opts.onQuery?.(""); draw(); return; }
      const uf = ev.target.closest("[data-unfold]"); if (uf) { view = uf.dataset.unfold === "left" ? [0, M.range[1]] : [M.range[0], 1440]; draw(); return; }
      const g = ev.target.closest("[data-group]"); if (g) { const k = g.dataset.group; expanded.has(k) ? expanded.delete(k) : expanded.add(k); draw(); return; }
      const tk = ev.target.closest("[data-task]"); if (tk) { sel = {task: M.tasks.find(k => k.id === tk.dataset.task)}; draw(); return; }
      const tp = ev.target.closest("[data-topic]"); if (tp) { const t = M.topics.find(x => x.id === tp.dataset.topic);
        if (tp.classList.contains("dt-lbtn") && !tp.classList.contains("dt-sublab")) expanded.has(t.id) ? expanded.delete(t.id) : expanded.add(t.id);
        sel = {topic: t}; draw(); return; }
      const lm = ev.target.closest("li[data-m]"); if (lm && insp.contains(lm) && grid) { pin = +lm.dataset.m; const [a, b] = domain(); if (pin < a || pin > b) { view = null; draw(); }
        insp.querySelectorAll(".dt-pinned").forEach(x => x.classList.remove("dt-pinned")); lm.classList.add("dt-pinned"); grid.querySelector(".dt-gridlines").innerHTML = gridlines(); }
    });
    function showTip(el, ev) {
      const it = items[+el.dataset.i]; if (!it) return; let h = "";
      if (it.type === "block") { const b = it.block || {a: it.r.a, b: it.r.b, topic: it.r.task.topicObj}; h = `<b>${esc(b.topic.label)}</b> ${hm(b.a)}–${hm(b.b)}<br>${esc(it.r.task.label)} ${hm(it.r.a)}–${hm(it.r.b)}`; }
      else if (it.type === "hour") h = `<b>${hm(it.h)}–${hm(it.h + 60)}</b> · ${esc(it.t.label)} ${dur(it.v)}${it.rest ? `<br>${dur(it.rest)} on other topics` : ""}`;
      else if (it.type === "topic") h = `<b>${esc(it.t.label)}</b> ${dur(it.t.att)}`;
      else if (it.type === "call") h = `<b>${hm(it.e.a)}–${hm(it.e.b)}</b> ${esc(it.e.title)}`;
      else if (it.type === "turn") h = `<b>agent ${hm(it.x.a)}–${hm(it.x.b)}</b> ${esc(it.x.task.label)}<br>${esc(cut(it.x.p.text, 200))}`;
      else if (it.type === "commit") h = `<b>${hm(it.c.m)} commit</b> ${esc(it.c.repo.split("/").pop())}<br>${esc(it.c.msg)}`;
      else if (it.type === "conc") h = `${hm(it.m)}: ${it.v} agent turn${it.v > 1 ? "s" : ""} running`;
      tip.innerHTML = h; tip.hidden = false;
      const rr = root.getBoundingClientRect(); tip.style.left = Math.min(ev.clientX - rr.left + 12, rr.width - 330) + "px"; tip.style.top = (ev.clientY - rr.top + 14) + "px";
    }
    let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => root.isConnected && (draw.measured = false, draw()), 120); });

    const api = {
      get model() { return M; }, get day() { return dayIdx; }, get cfg() { return cfg; },
      load, step: d => load(dayIdx + d),
      reset() { view = null; win = null; sel = null; draw(); },
      clear() { if (sel) sel = null; else if (view || win) { view = null; win = null; } else if (query) { query = ""; opts.onQuery?.(""); } draw(); },
      search(q) { query = (q || "").trim().toLowerCase(); sel = null; draw(); },
      set(k, v) { cfg[k] = v; if (k === "view") { sel = null; win = null; view = null; } if (k !== "view" && k !== "rows" && k !== "taskSort") M = model(data.days[dayIdx], story(data.days[dayIdx]), cfg); draw.measured = false; draw(); },
      toggleAll() { const ks = M.topics.map(t => t.id); const all = ks.every(k => expanded.has(k)); ks.forEach(k => all ? expanded.delete(k) : expanded.add(k)); draw(); },
    };
    load(dayIdx);
    return api;
  }
  return {render, model, DEFAULTS, hm, dur};
})();
