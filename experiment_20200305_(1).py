import os
import skimage
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
import milad

def readCSV(P, resoltion = 1):
    data = pd.read_csv(P,
                        skiprows=100,
                        skip_blank_lines=False,
                        names=range(64))
    raw = np.array(data[:(resoltion**2)*12288]).reshape(resoltion*768,resoltion*1024)
    offset = np.array(data[(resoltion**2)*12288+1:]).reshape(768,1024)
    if resoltion>1:
        offset = np.array(Image.fromarray(offset).resize((resoltion*1024,resoltion*768)))
    return raw, offset

def correctBP(img, size=3):
    bp = milad.badPixels(img, size)
    bpRemoved = milad.removeBadpixels(img, bp, size)
    return bpRemoved

root = "/Users/Julia/PycharmProjects/pythonProject"
csvs = [csv for csv in os.listdir(root) if ".csv" in csv]
sorted(csvs)
files = [csv[:-4] for csv in csvs]

for csv, f in zip(csvs, files):
    print(f"Processing {csv} ...")
    raw, offset = readCSV(os.path.join(root, csv), 1)
    img = raw - offset

    bpRemoved = img

    fig, ax = plt.subplots(1)
    ax.imshow(bpRemoved, cmap="gray")
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.savefig(f + ".png", transparent=True, bbox_inches = 'tight', pad_inches = 0)
