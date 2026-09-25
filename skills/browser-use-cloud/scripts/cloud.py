# /// script
# requires-python = ">=3.11"
# dependencies = ["browser-use-sdk>=3.11.3,<4", "playwright>=1.63,<2"]
# ///
"""Named Browser Use v4 sessions; credentials and connection state stay local."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / '.state'
ACCOUNT = 'my.1password.com'
SECRET = 'op://Personal/Browser-use/BROWSER_USE_API_KEY'


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write(value)


def key():
    value = os.environ.get('BROWSER_USE_API_KEY')
    if not value:
        result = subprocess.run(['op', 'read', SECRET, '--account', ACCOUNT],
                                text=True, capture_output=True)
        if result.returncode:
            raise SystemExit('Unlock personal 1Password to load the Browser Use API key.')
        value = result.stdout.strip()
    if not value.startswith('bu_') or any(c.isspace() for c in value):
        raise SystemExit('Invalid Browser Use API key format.')
    save(ROOT / '.env', 'BROWSER_USE_API_KEY=' + value + '\n')
    return value


def mappings():
    path = ROOT / 'profiles.json'
    return json.loads(path.read_text()) if path.exists() else {}


def session_path(name):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', name):
        raise SystemExit('Use a session name with lowercase letters, digits, and dashes.')
    return STATE / (name + '.json')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    start = commands.add_parser('start')
    start.add_argument('name')
    start.add_argument('--profile', required=True, choices=['personal', 'work', 'clean'])
    start.add_argument('--timeout', type=int, default=15)
    start.add_argument('--country', default='gb')
    for command in ['exec', 'stop']:
        commands.add_parser(command).add_argument('name')
    commands.add_parser('status')
    commands.add_parser('profiles')
    commands.add_parser('sync').add_argument('profile', choices=['personal', 'work'])
    args = parser.parse_args()

    if args.command == 'profiles':
        print(json.dumps(mappings(), indent=2))
        return
    if args.command == 'status':
        for path in sorted(STATE.glob('*.json')):
            data = json.loads(path.read_text())
            print(json.dumps({k: data.get(k) for k in ['name', 'id', 'profile', 'status', 'timeout']}))
        return
    if args.command == 'sync':
        profile = mappings()[args.profile]
        for path in STATE.glob('*.json'):
            data = json.loads(path.read_text())
            if data['profile'] == args.profile and data['status'] != 'stopped':
                raise SystemExit('Stop existing sessions for this profile before syncing.')
        result = subprocess.run([
            str(Path.home() / '.local/bin/profile-use'), 'sync', '--browser',
            'Google Chrome', '--profile', profile['local_name'],
            '--cloud-profile-id', profile['id'],
        ], env={**os.environ, 'BROWSER_USE_API_KEY': key()})
        raise SystemExit(result.returncode)

    path = session_path(args.name)
    if args.command == 'start':
        if path.exists():
            raise SystemExit('Session name already recorded; choose a new name.')
        if not 1 <= args.timeout <= 240:
            raise SystemExit('Timeout must be 1–240 minutes.')
        profile_id = None if args.profile == 'clean' else mappings()[args.profile]['id']
        if profile_id:
            for other in STATE.glob('*.json'):
                data = json.loads(other.read_text())
                if data['profile'] == args.profile and data['status'] != 'stopped':
                    raise SystemExit('Stop the existing session for this profile first.')
        from browser_use_sdk.v4 import BrowserUse
        with BrowserUse(api_key=key()) as client:
            session = client.browsers.create(
                profile_id=profile_id, timeout=args.timeout,
                proxy_country_code=None if args.country == 'none' else args.country,
                enable_recording=False,
            )
            try:
                if not session.cdp_url:
                    raise RuntimeError('Cloud browser did not return a CDP URL.')
                data = {'name': args.name, 'id': str(session.id), 'profile': args.profile,
                        'status': 'running', 'timeout': args.timeout,
                        'cdp_url': session.cdp_url, 'live_url': session.live_url}
                save(path, json.dumps(data))
            except BaseException:
                client.browsers.stop(session.id)
                raise
        print(json.dumps({k: data[k] for k in ['name', 'id', 'profile', 'live_url', 'timeout']}))
        return

    data = json.loads(path.read_text())
    if args.command == 'stop':
        if data['status'] != 'stopped':
            from browser_use_sdk.v4 import BrowserUse
            with BrowserUse(api_key=key()) as client:
                client.browsers.stop(data['id'])
            data['status'] = 'stopped'
            data.pop('cdp_url', None)
            data.pop('live_url', None)
            save(path, json.dumps(data))
        print('Stopped ' + args.name)
        return
    if data['status'] == 'stopped':
        raise SystemExit('This session is stopped. Start a new session.')
    source = sys.stdin.read()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(data['cdp_url'])
        try:
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            exec(compile(source, '<bu-cloud>', 'exec'),
                 {'browser': browser, 'context': context, 'page': page})
        finally:
            browser.close()


if __name__ == '__main__':
    main()
