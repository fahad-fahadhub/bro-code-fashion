"""Step 1. Paint out the corner mark on each original photo -> pipeline/clean/<tee>.png"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
from grade import SRC, clean, PIPE

out = os.path.join(PIPE, "clean")
os.makedirs(out, exist_ok=True)
for k in SRC:
    cv2.imwrite(os.path.join(out, k + ".png"), clean(k))
    print("cleaned", k)
