import argparse
import networkx as nx
import numpy as np
import skimage.color as color
import skimage.data as data
import skimage.filters as filters
import skimage.morphology as morph

import matplotlib.pyplot as plt

def main(input, output, plot):
	# Step 1: read input image
	image = color.rgb2grey(data.imread(input))
	show(plot, image)

	# Step 2: threshold, and invert to make text "foreground"
	thres = np.invert(image > filters.threshold_li(image))
	show(plot, thres)

	# Step 3: skeletonize
	skel = morph.skeletonize(thres)
	show(plot, skel)

	# Step 4: connected component analysis
	cc = morph.label(skel)
	n_classes = np.max(cc)
	show(plot, cc)

	# Step 5: endpoints, intersections, keypoints
	endpoint_sets = [[] for i in xrange(n_classes)]
	inters = []

	it = np.nditer(cc, flags=["multi_index"])
	while not it.finished:
		# Operate only on foreground
		if it[0] > 0:
			[y,x] = it.multi_index

			# Take nhood from skel (since binary) -- this allows
			# some nice tricks.
			nh = get_nhood(skel, x, y)

			# Count neighbours (non-centre)
			degree = np.sum(nh) - 1
			if degree > 2:
				inters.append((y,x))
			elif degree == 1:
				endpoint_sets[cc[y, x]-1].append((y,x))


		it.iternext()

	print endpoint_sets, inters

	# Step 6: Line/Path detection
	# Step 7: North and Component connection

def get_nhood(image, x, y):
	nhood = np.zeros((3,3), dtype=np.int8)

	for (ny, r) in enumerate(nhood):
		for (nx, v) in enumerate(r):
			im_x = x + nx - 1
			im_y = y + ny - 1
			nhood[ny, nx] = fetch(image, im_x, im_y, val=0)

	return nhood

def fetch(image, x, y, val=-1):
	h, w = image.shape[:2]
	if x < 0 or x >= w or y < 0 or y >= h:
		return val
	else:
		return image[y, x]

def invert_binary(img):
	return (img + 1) % 2

def show(trigger, img, grey=True):
	if trigger:
		if grey:
			plt.imshow(img, cmap="gray")
		else:
			plt.imshow(img)
		plt.show()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="")
	parser.add_argument("input",
						help="Filename of an input character image.")
	parser.add_argument("output", nargs="?",
						default=None, type=argparse.FileType("w"),
						help="Path of graph output file. "+
							"If not present, output to stdout.")
	parser.add_argument("-p", "--plots", action='store_true',
						default=False,
						help="Show plots of intermediate steps.")
	args = parser.parse_args()
	main(args.input, args.output, args.plots)