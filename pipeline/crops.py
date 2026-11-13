"""Crop boxes for the product photos.

For each tee, one entry per visible side: (view, x0, y0, x1, y1). Boxes are 4:5 and use
pixel coordinates of the cleaned original in pipeline/clean/<tee>.png.
up.py reads V from here. To add a tee, add its photo to grade.SRC and its boxes here.
"""
V = {
    "scorpion": [("back", 405, 60, 785, 535)],
    "thisday":  [("back", 300, 30, 900, 780)],
    "balance":  [("front", 300, 120, 612, 510), ("back", 610, 140, 915, 521)],
    "lablack":  [("back", 410, 70, 790, 545)],
    "mythic":   [("front", 310, 40, 870, 740)],
    "labrown":  [("back", 290, 0, 890, 750)],
    "silence":  [("front", 215, 215, 605, 702), ("back", 585, 215, 955, 677)],
    "eagle":    [("front", 190, 110, 590, 610), ("back", 600, 230, 1010, 742)],
    "spider":   [("front", 200, 215, 600, 715), ("back", 610, 215, 1010, 715)],
    "unreal":   [("back", 150, 180, 470, 580), ("front", 520, 170, 860, 595)],
}
