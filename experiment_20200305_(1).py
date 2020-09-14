import os
import skimage
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
import milad
import reportlab
from reportlab.lib.pagesizes import LETTER, inch
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Image, PageBreak
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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

root = "/Users/Julia/PycharmProjects/pythonProject/Testing Images"
csvs = [csv for csv in os.listdir(root) if ".csv" in csv]
datetime = [ ]
temp = [ ]

for csv in sorted(csvs):
    files = str([csv[:-4]])
    if files[22:24] == '46':
        if (not files[-8:-2] == 'header'):
            print(f"Processing {csv} ...")
            raw, offset = readCSV(os.path.join(root, csv), 1)
            img = raw - offset

            bpRemoved = correctBP(img)

            fig, ax = plt.subplots(1)
            ax.imshow(bpRemoved, cmap="gray")
            ax.axes.xaxis.set_visible(False)
            ax.axes.yaxis.set_visible(False)

            plt.savefig(csv[:-4] + ".png", transparent=True, bbox_inches='tight', pad_inches=0)
        else:
            headerdata = pd.read_csv(os.path.join(root, csv))
            datetime.append(files[14] + '/' + files[16:18] + ' ' + files[19:21] + ':' + files[22:24]+'\n'+headerdata.iloc[19, 1])

#loads letter-sized pdf template with desired size and margins
pdffile = SimpleDocTemplate("Automated Image Comparison.pdf", pagesize=LETTER, topMargin = 0.9*inch, bottomMargin = 0.4*inch, leftMargin = 1*inch, rightMargin = 1*inch)
elements = []

#creates and styles header row
styles = getSampleStyleSheet()
headerstyle = styles["BodyText"]
headerstyle.alignment = TA_CENTER
sensortemp = Paragraph('<b>Date Sensor Temp</b>', headerstyle)
imagelabel = Paragraph('<b>Image</b>', headerstyle)
header = [[sensortemp, imagelabel, sensortemp, imagelabel]]

pngroot = "/Users/Julia/PycharmProjects/pythonProject"
processedpng = sorted([png for png in os.listdir(pngroot) if ".png" in png])
print(len(processedpng))
pagenum = math.ceil(len(processedpng)/12) #create pdf with multiple pages
for i in range(0, pagenum):
    ## start and stop index for the current page
    start = i * 12
    stop = min((i + 1) * 12, len(processedpng))
    ## page contents
    body = []
    for j in range(start, min(start + 6, stop)):  # create remaining rows by looping through datetime and images in
        # specific sizes
        I = Image(processedpng[j])
        I.drawHeight = 1.38 * inch
        I.drawWidth = 1.83 * inch
        ## the first column
        row = [datetime[j], I]
        if (j + 6) < stop:
            II = Image(processedpng[j + 6])
            II.drawHeight = 1.38 * inch
            II.drawWidth = 1.83 * inch
            ## the second column
            row += [datetime[j + 6], II]  # alternate columns of labels and images
        body.append(row)
    data = header + body
    t = Table(data)  # generates table for pdf
    t.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('INNERGRID', (0, 0), (-1, -1), .7, colors.black),
                           ('BOX', (0, 0), (-1, -1), .7, colors.black)]))
    elements.append(t)
    elements.append(PageBreak())
pdffile.build(elements)
