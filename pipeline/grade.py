"""Photo helpers shared by the pipeline scripts.

clean(k)  paints out the small corner mark on a source photo (see SRC).
grade()   the warm "ember" colour grade used on mood images (hero video, reel, marquee).
          The site uses mode "g2". "g1" and "g3" are alternative looks kept for reference.
"""
import os
import numpy as np
import cv2
from PIL import Image

PIPE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(PIPE, "originals") + os.sep

# key: (photo file id, [boxes (x0, y0, x1, y1) covering the corner mark to paint out])
SRC = {
    "scorpion": ("cbf6f371", [(1085, 830, 1140, 885)]),
    "unreal":   ("7aa2d4b9", [(810, 960, 870, 1020)]),
    "thisday":  ("dd6e8311", [(1025, 765, 1080, 820)]),
    "balance":  ("03862cab", [(1030, 750, 1085, 805), (1085, 830, 1140, 885), (1150, 690, 1176, 740)]),
    "lablack":  ("bbbcecfa", [(1050, 735, 1105, 790)]),
    "mythic":   ("78937770", [(1062, 828, 1118, 884)]),
    "labrown":  ("5b4af0e7", [(1025, 748, 1080, 802)]),
    "silence":  ("20503bae", [(1005, 765, 1065, 835)]),
    "eagle":    ("f36b4ae7", [(1003, 733, 1058, 788)]),
    "spider":   ("d9c5bf93", [(1050, 720, 1106, 776)]),
}


def clean(k):
    f, boxes = SRC[k]
    im = cv2.imread(A + f + "-image.jpg")
    m = np.zeros(im.shape[:2], np.uint8)
    for x0, y0, x1, y1 in boxes:
        m[y0:y1, x0:x1] = 255
    return cv2.inpaint(im, m, 7, cv2.INPAINT_TELEA)


def lut(stops, n=256):
    xs = [s[0] for s in stops]
    out = np.zeros((n, 3))
    for c in range(3):
        out[:, c] = np.interp(np.linspace(0, 1, n), xs, [s[1][c] for s in stops])
    return out


def gmap(L, stops):
    l = lut(stops)
    return l[(L * 255).astype(np.uint8)]


def hexc(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


def vig(shape, s=.55):
    h, w = shape[:2]
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h * .45) / (h / 2)) ** 2)
    return (1 - s * np.clip(d - .35, 0, 1) ** 1.4)[..., None]


def grain(shape, a=.035):
    return np.random.default_rng(3).normal(0, a, shape[:2])[..., None]


def grade(bgr, mode):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    L = (rgb @ np.array([.299, .587, .114]))
    L = np.clip((L - .04) / .92, 0, 1)
    if mode == "g1":
        L2 = L ** 1.12
        gm = gmap(L2, [(0, hexc("#080706")), (.35, hexc("#2e2314")), (.65, hexc("#a77a33")), (1, hexc("#fff0cc"))])
        out = gm * .78 + rgb * .22 * np.array([1, .92, .78])
        out *= vig(out.shape, .6)
    elif mode == "g2":
        L2 = L ** 1.0
        gm = gmap(L2, [(0, hexc("#080203")), (.3, hexc("#4a1204")), (.6, hexc("#ff6a14")), (.85, hexc("#ffc060")), (1, hexc("#fff2cf"))])
        hsv = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[..., 1] *= 1.15
        sat = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32) / 255
        out = gm * .74 + sat * .16 * np.array([1.1, .8, .6])
        bl = cv2.GaussianBlur(np.clip(out - .55, 0, 1), (0, 0), 18)
        out = 1 - (1 - out) * (1 - bl * .9)
        out *= vig(out.shape, .7)
    else:
        L2 = np.clip((L - .5) * 1.18 + .5, 0, 1)
        gm = gmap(L2, [(0, hexc("#0b0b0c")), (.5, hexc("#7b7c80")), (1, hexc("#f2f1ec"))])
        out = gm * .96 + rgb * .04
        out *= vig(out.shape, .35)
    out = np.clip(out + grain(out.shape), 0, 1)
    return (out * 255).astype(np.uint8)
