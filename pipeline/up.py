"""Step 2. Crop each tee view and enlarge it 2x with the FSRCNN model, keeping the true garment colour.
Needs: opencv-contrib-python (for cv2.dnn_superres). Output: pipeline/up/<tee>-<view>.png (800 x 1000)."""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
from crops import V
from grade import PIPE

os.chdir(PIPE)
sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel(os.path.join("models", "fsrcnn_x2.pb"))
sr.setModel("fsrcnn", 2)
os.makedirs("up", exist_ok=True)
t = time.time()
for k, vs in V.items():
    im = cv2.imread(f"clean/{k}.png")
    for v, x0, y0, x1, y1 in vs:
        c = im[y0:y1, x0:x1]
        u = sr.upsample(c)
        b = cv2.GaussianBlur(u, (0, 0), 1.2)
        u = cv2.addWeighted(u, 1.25, b, -.25, 0)  # light sharpen
        cv2.imwrite(f"up/{k}-{v}.png", u)
        print(k, v, u.shape, round(time.time() - t), flush=True)
