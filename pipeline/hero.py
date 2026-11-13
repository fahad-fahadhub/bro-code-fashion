"""Step 3. Render the hero video from the cleaned photos: slow zoom, crossfades, vignette and film grain,
piped straight into ffmpeg (H.264). Needs ffmpeg on the PATH.

  python3 hero.py all                         -> assets/video/hero-1080.mp4 (desktop) and hero-720.mp4 (phone, portrait)
  python3 hero.py land 1920 1080 out.mp4      -> one custom render ("land" = landscape, "port" = portrait)

Set HERO_OUT to write somewhere other than assets/video.
"""
import os
import subprocess
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import numpy as np
from grade import PIPE, grade

ROOT = os.path.dirname(PIPE)
os.chdir(PIPE)


def still(k):
    b = cv2.imread(f"clean/{k}.png")
    g = grade(b, "g2")
    return cv2.cvtColor(g, cv2.COLOR_RGB2BGR)


ORDER = ["mythic", "lablack", "balance", "scorpion", "eagle", "mythic"]
FOC = {"land": {"mythic": (.52, 330), "lablack": (.5, 340), "balance": (.5, 400), "scorpion": (.5, 340), "eagle": (.5, 430)},
       "port": {"mythic": 590, "lablack": 600, "balance": 470, "scorpion": 595, "eagle": 380}}


def run(mode, W, H, out, fps=24, T=3.2, X=.9):
    imgs = {k: still(k) for k in set(ORDER)}
    n = len(ORDER)
    Tf = int(T * fps)
    Xf = int(X * fps)
    total = n * Tf
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                          "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-profile:v", "high", out],
                         stdin=subprocess.PIPE)
    rng = np.random.default_rng(1)
    yy, xx = np.mgrid[0:H, 0:W]
    vg = (1 - .55 * np.clip(np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) - .45, 0, 1) ** 1.5).astype(np.float32)[..., None]

    def frame(i, fi, rev):
        k = ORDER[i]
        im = imgs[k]
        h, w = im.shape[:2]
        t = (1 - fi / (Tf - 1)) if rev else fi / max(1, Tf + Xf - 1)
        z = 1 + .14 * t
        if mode == "land":
            bw = w
            bh = w * 9 / 16
            fx, fy = FOC["land"][k]
            cx = fx * w
            cy = fy
        else:
            bh = h
            bw = h * 9 / 16
            cx = FOC["port"][k]
            cy = h / 2
        cw, ch = bw / z, bh / z
        x0 = min(max(cx - cw / 2, 0), w - cw)
        y0 = min(max(cy - ch / 2, 0), h - ch)
        M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
        return cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)

    for f in range(total):
        i = min(n - 1, f // Tf)
        fi = f - i * Tf
        a = frame(i, fi, i == n - 1)
        if i > 0 and fi < Xf:
            b = frame(i - 1, Tf + fi, (i - 1) == n - 1)
            al = fi / Xf
            al = al * al * (3 - 2 * al)
            a = b * (1 - al) + a * al
        a = a * vg * (1 + .04 * np.sin(f / fps * 1.3))
        a += rng.normal(0, 5, (H, W, 1)).astype(np.float32)
        p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()
    print(out, "done")


if __name__ == "__main__":
    out_dir = os.environ.get("HERO_OUT", os.path.join(ROOT, "assets", "video"))
    os.makedirs(out_dir, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        run("land", 1920, 1080, os.path.join(out_dir, "hero-1080.mp4"))
        run("port", 720, 1280, os.path.join(out_dir, "hero-720.mp4"))
    elif len(sys.argv) == 5:
        run(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    else:
        print(__doc__)
