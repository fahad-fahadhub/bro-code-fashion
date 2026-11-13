"""Step 5. Draw the app icons, favicon and the 1200x630 sharing image from the BCF mark -> static/
Needs: playwright with Chromium (or Google Chrome), Pillow, ffmpeg. The fonts are read from assets/fonts.
Set BRAND_OUT to write somewhere other than static/."""
import asyncio
import os
import subprocess
import sys
import tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.async_api import async_playwright
from PIL import Image
from grade import PIPE

ROOT = os.path.dirname(PIPE)
D = os.environ.get("BRAND_OUT", os.path.join(ROOT, "static")) + os.sep
os.makedirs(D, exist_ok=True)
FD = "file://" + os.path.join(ROOT, "assets", "fonts") + "/"
TMP = tempfile.gettempdir()
BG = os.path.join(TMP, "bcf_og_bg.png")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(ROOT, "assets", "video", "hero-1080.mp4"), "-frames:v", "1", BG], check=True)

FONTS = f"""@font-face{{font-family:Cinzel;font-weight:700;src:url({FD}cinzel-700.woff2)}}
@font-face{{font-family:'Space Mono';font-weight:700;src:url({FD}space-mono-700.woff2)}}
@font-face{{font-family:'Space Mono';font-weight:400;src:url({FD}space-mono-400.woff2)}}"""
GR = '<defs><linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff7a14"/><stop offset=".5" stop-color="#ffd27a"/><stop offset="1" stop-color="#ff8a1a"/></linearGradient><linearGradient id="t" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe9bd"/><stop offset=".5" stop-color="#fff8e6"/><stop offset="1" stop-color="#ffc46b"/></linearGradient></defs>'
MARK = '<path d="M78 84L66 36L102 62L130 22L158 62L194 36L182 84Z" fill="url(#a)"/><rect x="74" y="84" width="112" height="14" rx="4" fill="url(#a)"/><circle cx="66" cy="33" r="6" fill="url(#a)"/><circle cx="130" cy="17" r="6.5" fill="url(#a)"/><circle cx="194" cy="33" r="6" fill="url(#a)"/><text x="130" y="226" text-anchor="middle" font-family="Cinzel,serif" font-weight="700" font-size="104" fill="url(#t)">BCF</text>'
ICON = lambda s: f'<html><style>{FONTS}body{{margin:0;background:#0a0605}}</style><body><svg width="{s}" height="{s}" viewBox="0 0 260 280">{GR}<rect width="260" height="280" rx="0" fill="#0a0605"/><g transform="translate(0,0)">{MARK}</g></svg></body></html>'
OG = f'''<html><style>{FONTS}body{{margin:0;width:1200px;height:630px;position:relative;overflow:hidden;background:#0a0605;font-family:'Space Mono',monospace;color:#fff6e0}}
.bg{{position:absolute;inset:0;background:url(file://{BG}) 70% 20%/cover;opacity:.55}}.sh{{position:absolute;inset:0;background:linear-gradient(90deg,#0a0605 25%,rgba(10,6,5,.55) 70%,rgba(10,6,5,.2))}}
.c{{position:absolute;left:70px;top:70px;bottom:60px;display:flex;flex-direction:column;justify-content:space-between}}
h1{{font:700 74px/1 'Space Mono';text-transform:uppercase;letter-spacing:-3px;margin:0}}p{{margin:14px 0 0;font:400 26px 'Space Mono';color:#ffd9a0}}.b{{display:inline-block;background:#ffb13b;color:#1a0d00;padding:16px 26px;font:700 24px 'Space Mono';border-radius:6px}}</style><body><div class="bg"></div><div class="sh"></div>
<div class="c"><svg width="150" height="161" viewBox="0 0 260 280">{GR}{MARK}</svg><div><h1>Wear the<br>new code</h1><p>Men's casual wear · Bengaluru</p></div><div><span class="b">Order on WhatsApp</span></div></div></body></html>'''


async def main():
    async with async_playwright() as p:
        chrome = "/usr/bin/google-chrome"
        b = await p.chromium.launch(**({"executable_path": chrome} if os.path.exists(chrome) else {}), args=["--no-sandbox", "--allow-file-access-from-files"])
        for s, name in ((512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (64, "f64.png")):
            pg = await b.new_page(viewport={"width": s, "height": s})
            await pg.set_content(ICON(s))
            await pg.wait_for_timeout(500)
            await pg.screenshot(path=D + name)
            await pg.close()
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        html = os.path.join(TMP, "bcf_og.html")
        open(html, "w", encoding="utf8").write(OG)
        await pg.goto("file://" + html)
        await pg.wait_for_timeout(800)
        await pg.screenshot(path=os.path.join(TMP, "bcf_og.png"))
        await b.close()

asyncio.run(main())
Image.open(os.path.join(TMP, "bcf_og.png")).convert("RGB").save(D + "og-image.jpg", quality=84, optimize=True)
im = Image.open(D + "f64.png")
im.resize((32, 32), Image.LANCZOS).save(D + "favicon.ico", sizes=[(16, 16), (32, 32)])
os.remove(D + "f64.png")
open(D + "favicon.svg", "w", encoding="utf8").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 280"><defs><linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff7a14"/><stop offset=".5" stop-color="#ffd27a"/><stop offset="1" stop-color="#ff8a1a"/></linearGradient></defs><rect width="260" height="280" rx="36" fill="#0a0605"/><path d="M78 84L66 36L102 62L130 22L158 62L194 36L182 84Z" fill="url(#a)"/><rect x="74" y="84" width="112" height="14" rx="4" fill="url(#a)"/><text x="130" y="226" text-anchor="middle" font-family="Cinzel,Georgia,serif" font-weight="700" font-size="104" fill="#ffe9bd">BCF</text></svg>')
print("brand files written to", D)
