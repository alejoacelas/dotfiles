"""Screenshot each HTML mockup's <main> to a PNG beside it at 2x scale.

Run: uv run --with playwright python render.py mockup.html [...]
First run on a new machine: uv run --with playwright playwright install chromium
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1000, "height": 600}, device_scale_factor=2)
    for name in sys.argv[1:]:
        src = Path(name).resolve()
        page.goto(src.as_uri())
        page.wait_for_load_state("networkidle")
        out = src.with_suffix(".png")
        page.locator("body > main").screenshot(path=str(out))
        print(out)
    browser.close()
