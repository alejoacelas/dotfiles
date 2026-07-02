#!/usr/bin/env node
// Point a Namecheap domain at Vercel by setting its Advanced-DNS host records.
//
//   node namecheap-dns.mjs --domain alejo.food
//   node namecheap-dns.mjs --domain foo.com --ip 76.76.21.21 --cname cname.vercel-dns.com
//
// Sets, idempotently:
//     A      @     <ip>            (apex → Vercel, default 76.76.21.21)
//     CNAME  www   <cname>         (www  → Vercel, default cname.vercel-dns.com)
// and removes the default parking records (URL Redirect @, CNAME www → parkingpage).
// Locked records (e.g. the email-forwarding SPF TXT) are left untouched.
//
// First run: a Chrome window opens; log into Namecheap once. The session is saved
// to ./.namecheap-profile so later runs are non-interactive.
//
// Setup once:  npm install  &&  npx playwright install chromium
import { chromium } from 'playwright';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const argv = Object.fromEntries(
  process.argv.slice(2).join('=').split('--').filter(Boolean)
    .map(s => s.trim().split('=')).map(([k, ...v]) => [k, v.join('=').trim()])
);
const DOMAIN = argv.domain;
const IP = argv.ip || '76.76.21.21';
const CNAME = argv.cname || 'cname.vercel-dns.com';
if (!DOMAIN) { console.error('Usage: node namecheap-dns.mjs --domain <name> [--ip x] [--cname y]'); process.exit(1); }

const here = dirname(fileURLToPath(import.meta.url));
const PROFILE = argv.profile || join(here, '.namecheap-profile');
const URL = `https://ap.www.namecheap.com/Domains/DomainControlPanel/${DOMAIN}/advancedns`;
const DESIRED = [
  { type: 'A Record', host: '@', value: IP },
  { type: 'CNAME Record', host: 'www', value: CNAME },
];

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function gotoDns(page) {
  await page.goto(URL, { waitUntil: 'domcontentloaded' });
  // Wait for the host-records UI, or for the user to finish logging in (up to 5 min).
  try {
    await page.waitForSelector('a.simple-btn.icon-add', { timeout: 8000 });
  } catch {
    console.log('→ Log into Namecheap in the open window; waiting for the DNS page…');
    await page.waitForSelector('a.simple-btn.icon-add', { timeout: 300000 });
  }
  await sleep(800);
}

// Read the editable (non-locked) host rows as {host, type, value}.
async function readRows(page) {
  return page.$$eval('a.remove.tooltip-toggle', removes => removes.map(rm => {
    const row = rm.closest('tr') || rm.closest('[ng-repeat]') || rm.parentElement.parentElement;
    const cells = [...row.querySelectorAll('td,div')].map(c => c.innerText.trim()).filter(Boolean);
    return { type: cells[0] || '', host: cells[1] || '', value: cells[2] || '' };
  }));
}

// Delete every deletable row whose host is @ or www (parking + stale), reloading
// between deletes — Namecheap's UI often throws a benign "Failed to retrieve" that
// a reload clears; the server-side delete still lands.
async function clearHosts(page, hosts) {
  for (let guard = 0; guard < 12; guard++) {
    const removes = page.locator('a.remove.tooltip-toggle');
    const n = await removes.count();
    let hitIndex = -1;
    for (let i = 0; i < n; i++) {
      const row = removes.nth(i).locator('xpath=ancestor::*[self::tr or @ng-repeat][1]');
      const txt = (await row.innerText().catch(() => '')).replace(/\s+/g, ' ').trim();
      if (hosts.some(h => new RegExp(`(^| )${h.replace('@', '\\@')}( |$)`).test(txt))) { hitIndex = i; break; }
    }
    if (hitIndex === -1) return;
    await removes.nth(hitIndex).click();
    await page.locator('a.yes').first().click().catch(() => {});
    await sleep(1500);
    await gotoDns(page); // resync after the (possibly noisy) delete
  }
}

async function addRecord(page, { type, host, value }) {
  await page.locator('a.simple-btn.icon-add', { hasText: 'ADD NEW RECORD' }).click();
  await sleep(500);
  // Record type via the select2 dropdown of the new (last) row.
  await page.locator('.select2-container.dashed-select').last().click();
  await page.locator('.select2-results .select2-result-label', { hasText: type }).first().click();
  await sleep(300);
  await page.locator('input.dashed-input[placeholder="Host"]').last().fill(host);
  await page.locator('input.dashed-input:not([placeholder="Host"])').last().fill(value);
  await page.locator('a.save').last().click(); // green ✓ commits the row
  await sleep(1200);
}

(async () => {
  const ctx = await chromium.launchPersistentContext(PROFILE, {
    headless: false, viewport: { width: 1280, height: 900 },
  });
  const page = ctx.pages()[0] || await ctx.newPage();
  try {
    await gotoDns(page);
    console.log('Before:', JSON.stringify(await readRows(page)));

    await clearHosts(page, ['@', 'www']);
    for (const rec of DESIRED) { await addRecord(page, rec); }

    await gotoDns(page);
    const after = await readRows(page);
    console.log('After :', JSON.stringify(after));

    const ok = DESIRED.every(d => after.some(r =>
      r.type.startsWith(d.type.split(' ')[0]) && r.host === d.host && r.value.replace(/\.$/, '') === d.value));
    console.log(ok ? `✓ ${DOMAIN} now points at Vercel (A @→${IP}, CNAME www→${CNAME})`
                   : '✗ Records not all confirmed — check the window / re-run.');
    process.exitCode = ok ? 0 : 1;
  } finally {
    if (!argv.keepopen) await ctx.close();
  }
})();
