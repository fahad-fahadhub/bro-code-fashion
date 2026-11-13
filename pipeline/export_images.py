"""Step 4. Export the web images into assets/img as WebP.

  p-<tee>-<view>-800 / -480   product photos from pipeline/up/ (4:5)
  a-<tee>-960 / -520          ember-graded mood images from pipeline/clean/ (hero reel and marquee)
  poster-land / poster-port   first frame of each hero video (shown while the video loads)

Set IMG_OUT to write somewhere other than assets/img.
"""
import os
import subprocess
import sys
import tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
from PIL import Image
from crops import V
from grade import PIPE, SRC, grade

ROOT = os.path.dirname(PIPE)
os.chdir(PIPE)
OUT = os.environ.get("IMG_OUT", os.path.join(ROOT, "assets", "img"))
os.makedirs(OUT, exist_ok=True)


def save(im, name, w, q, ratio=None):
    """Resize to width w. ratio (height / width) forces the shape, otherwise the photo's own shape is kept."""
    im = im.convert("RGB")
    h = round(w * ratio) if ratio else int(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".webp"), "WEBP", quality=q, method=6)


for k, views in V.items():
    for v, *_ in views:
        src = Image.open(f"up/{k}-{v}.png")
        for w in (800, 480):
            save(src, f"p-{k}-{v}-{w}", w, 80)
for k in SRC:
    g = grade(cv2.imread(f"clean/{k}.png"), "g2")
    src = Image.fromarray(g)
    for w in (960, 520):
        save(src, f"a-{k}-{w}", w, 72)

vid = os.path.join(ROOT, "assets", "video")
for name, f, w in (("poster-land", "hero-1080.mp4", 1600), ("poster-port", "hero-720.mp4", 720)):
    if not os.path.exists(os.path.join(vid, f)):
        print("skip", name, "(render the hero video first)")
        continue
    tmp = os.path.join(tempfile.gettempdir(), name + ".png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(vid, f), "-frames:v", "1", tmp], check=True)
    save(Image.open(tmp), name, w, 80)
print("exported to", OUT)
