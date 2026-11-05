#!/usr/bin/env python3
"""Run read-only SQL on a copy of the Mac's Signal Desktop database.

  desktop.py "SELECT id, name, profileFullName FROM conversations WHERE name LIKE '%Lydia%'"

Needs `sqlcipher` (brew install sqlcipher) and keychain access to "Signal Safe Storage".
"""
import glob, hashlib, json, os, shutil, subprocess, sys, tempfile

SIGNAL = os.path.expanduser("~/Library/Application Support/Signal")

def db_key():
    password = subprocess.check_output(
        ["security", "find-generic-password", "-s", "Signal Safe Storage", "-w"]).strip()
    with open(f"{SIGNAL}/config.json") as f:
        encrypted = bytes.fromhex(json.load(f)["encryptedKey"])
    aes = hashlib.pbkdf2_hmac("sha1", password, b"saltysalt", 1003, 16)
    return subprocess.check_output(
        ["openssl", "enc", "-d", "-aes-128-cbc", "-K", aes.hex(), "-iv", "20" * 16],
        input=encrypted[3:]).decode().strip()  # drop Chromium's "v10" prefix

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with tempfile.TemporaryDirectory() as tmp:
        for f in glob.glob(f"{SIGNAL}/sql/db.sqlite*"):  # copy so the running app's lock doesn't matter
            shutil.copy(f, tmp)
        script = f"PRAGMA key = \"x'{db_key()}'\";\n.mode list\n.separator ' | '\n{sys.argv[1]};\n"
        out = subprocess.run(["sqlcipher", f"{tmp}/db.sqlite"], input=script, capture_output=True, text=True)
        sys.stdout.write(out.stdout.removeprefix("ok\n"))
        sys.stderr.write(out.stderr)
        sys.exit(out.returncode)

main()
