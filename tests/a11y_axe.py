"""Accessibility check: runs axe-core on the home page and lists any violations.

Setup:   cd pipeline && npm install            (installs axe-core)
         python3 -m http.server 8123 -d website  (in another terminal, from the project folder)
Run:     python3 tests/a11y_axe.py               (exit code 1 if anything is found)
"""
import asyncio
import os
import sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
AXE = os.path.join(os.path.dirname(HERE), "pipeline", "node_modules", "axe-core", "axe.min.js")
BASE = os.environ.get("BASE", "http://localhost:8123/index.html")
CHROME = {"executable_path": "/usr/bin/google-chrome"} if os.path.exists("/usr/bin/google-chrome") else {}


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**CHROME, args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1366, "height": 820})
        await pg.goto(BASE)
        await pg.wait_for_timeout(1500)
        await pg.add_script_tag(path=AXE)
        r = await pg.evaluate("axe.run(document, {resultTypes: ['violations']})")
        v = r["violations"]
        print(len(v), "violations")
        for x in v:
            print(x["id"], x["impact"], len(x["nodes"]), x["help"])
        await b.close()
        sys.exit(1 if v else 0)

asyncio.run(main())
