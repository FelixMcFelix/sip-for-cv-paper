import csv
import json
from PIL import Image, ImageDraw
import math
import numpy as np
import matplotlib.pyplot as plt

from config import *

#
# Modified from
# https://github.com/MartinThoma/hwrt/blob/master/hwrt/handwritten_data.py
#

def get_hwrt_image(data, pen_width=5, scale=1.0):
	# Load as data:
	pointlist = json.loads(data)

	# Now sort nicely
	for i in range(len(pointlist)):
		pointlist[i] = sorted(pointlist[i], key=lambda p: p['time'])
	pointlist = sorted(pointlist, key=lambda stroke: stroke[0]['time'])

	# Get bounding box
	minx, maxx = pointlist[0][0]["x"], pointlist[0][0]["x"]
	miny, maxy = pointlist[0][0]["y"], pointlist[0][0]["y"]
	mint, maxt = pointlist[0][0]["time"], pointlist[0][0]["time"]

	for stroke in pointlist:
		for p in stroke:
			minx, maxx = min(minx, p["x"]), max(maxx, p["x"])
			miny, maxy = min(miny, p["y"]), max(maxy, p["y"])
			mint, maxt = min(mint, p["time"]), max(maxt, p["time"])

	minx -= pen_width
	miny -= pen_width
	maxx += pen_width
	maxy += pen_width

	width = int((maxx - minx) * scale)
	height = int((maxy - miny) * scale)

	img = Image.new("L", (width, height), "white")
	draw = ImageDraw.Draw(img, 'L')

	for stroke in pointlist:
		walk = zip(stroke, stroke[1:]) if len(stroke) > 1 else zip(stroke, stroke)

		for p1, p2 in walk:
			y_from = int((-miny + p1['y']) * scale)
			x_from = int((-minx + p1['x']) * scale)
			y_to = int((-miny + p2['y']) * scale)
			x_to = int((-minx + p2['x']) * scale)

			if pen_width > 1:
				rad = math.ceil(float(pen_width)/2)
				# draw.ellipse([x_from - rad, y_from - rad, x_from + rad, y_from + rad], fill="#000000", outline="#000000")
				# draw.ellipse([x_to - rad, y_to - rad, x_to + rad, y_to + rad], fill="#000000", outline="#000000")
				for x, y in bresenham(x_from, y_from, x_to, y_to):
					draw.ellipse([x - rad, y - rad, x + rad, y + rad], fill="#000000", outline="#000000")
			else:
				draw.line([x_from, y_from, x_to, y_to], fill="#000000", width=pen_width*2)

	del draw
	return img

def gen_dataset_imgs():
	for dset in datasets:
		dsetpart = "{}{}/".format(img_dir, dset)
		for split in splits:
			outfile = open("{}{}.csv".format(dsetpart, split), "wb")
			wrt = csv.writer(outfile)
			first = True
			for r in pen_rads:
				print "building {}/{}, r={}".format(dset, split, r)
				start_draw = 0 if r not in pen_to_start else pen_to_start[r]

				outpart = "{}r-{}/".format(dsetpart, r)
				outpath = "{}{}/".format(outpart, split)

				mkdirnotex(outpath)

				with open("{}{}/{}-data.csv".format(font_dir, dset, split)) as csvfile:
					rdr = csv.reader(csvfile, delimiter=";", quotechar="'")

					#Skip header
					next(rdr, None)

					for num, row in enumerate(rdr):
						fname = "{}.png".format(num)

						if num >= start_draw:
							get_hwrt_image(row[2], pen_width=r).save("{}{}".format(outpath, fname))

						if first: wrt.writerow([fname, row[0]])

				first = False

			outfile.close()


def bresenham(x0, y0, x1, y1):
	dx = x1 - x0
	dy = y1 - y0

	# Correct for direction, slope.
	steep = abs(dy) > abs(dx)
	if steep:
		x0, y0 = y0, x0
		x1, y1 = y1, x1

	reverse = False
	if x0 > x1:
		x0, x1 = x1, x0
		y0, y1 = y1, y0
		reverse = True

	# recalculate
	dx = x1 - x0
	dy = y1 - y0
	D = 2*dy - dx
	y = y0

	ydir = -1 if y0 > y1 else 1
	out = []

	for x in xrange(x0, x1+1):
		out.append((y,x) if steep else (x, y))
		if D > 0:
			y += ydir
			D -= 2 * dx
		D += 2*dy*ydir

	if reverse:
		out.reverse()

	# print out

	return out

if __name__ == '__main__':
	gen_dataset_imgs()
