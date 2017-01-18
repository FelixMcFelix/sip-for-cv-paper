import argparse
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import skimage.color as color
import skimage.data as data
import skimage.filters as filters
import skimage.morphology as morph

def makegraph(input, output, plot=False):
	##
	# Step 1: read input image
	##
	image = color.rgb2grey(data.imread(input))
	show(plot, image)

	##
	# Step 2: threshold, and invert to make text "foreground"
	##
	thres = np.invert(image > filters.threshold_li(image))
	show(plot, thres)

	##
	# Step 3: skeletonize
	##
	skel = morph.skeletonize(thres)
	show(plot, skel)

	##
	# Step 4: connected component analysis
	##
	cc = morph.label(skel)
	show(plot, cc)

	##
	# Step 5: endpoints, intersections, keypoints
	##
	[endpoints, inters] = initial_keypoints(cc, skel)
	starts = find_starts(cc, endpoints, inters)
	keyp_sets = [merge_pts(endpoints[i], inters[i], starts[i]) for i in xrange(len(starts))]

	# print endpoints, inters, starts
	print starts, keyp_sets

	##
	# Step 6: Line/Path detection
	##
	# walk graph to find all paths.
	# from start point, check all values in 3x3 nhood for next place to go.
	# upon hitting another keypoint, queue it up to visit after the current kp
	# is exhausted.
	for start, keyps in zip(starts, keyp_sets):
		work_queue = [start]
		visited = set()
		while len(work_queue) > 0:
			curr = work_queue.pop(0)
			print "took", curr, "now", work_queue
			(y, x) = curr

			local_pts = get_nhood_pts(x, y)

			for direction, (ly, lx) in enumerate(local_pts):
				pt = (ly, lx)
				last = curr
				seg = cc[ly, lx] - 1
				if seg > 0 and pt not in visited:
					while pt not in keyps:
						search_pts = get_nhood_pts(pt[1], pt[0])
						visited.add(pt)
						# print pt

						for (sy, sx) in search_pts:
							if (cc[sy, sx] - 1) > 0 and (sy, sx) not in visited and (sy, sx) != last:
								last = pt
								pt = (sy, sx)
								break

					# path completed now.
					if pt not in work_queue:
						work_queue.append(pt)

					print "path from", curr, "to", pt, ": dir", direction

			visited.add(curr)


	##
	# Step 7: North and Component connection
	##

def merge_pts(end, inter, start):
	pts = set()
	if len(end) == 0 and len(inter) == 0:
		pts.add(start)
	else:
		for el in end:
			pts.add(el)
		for el in inter:
			pts.add(el)
	return pts

def get_nhood(image, x, y):
	nhood = np.zeros((3,3), dtype=np.int8)

	for (ny, r) in enumerate(nhood):
		for (nx, v) in enumerate(r):
			im_x = x + nx - 1
			im_y = y + ny - 1
			nhood[ny, nx] = fetch(image, im_x, im_y, val=0)

	return nhood

def get_nhood_pts(x, y):
	return [
		# N, NE,
		# E, SE,
		# S, SW,
		# W, NW
		(y-1,x), (y-1,x+1),
		(y,x+1), (y+1,x+1),
		(y+1,x), (y+1,x-1),
		(y,x-1), (y-1,x-1),
	]

def initial_keypoints(cc, skel):
	n_classes = np.max(cc)
	endpoints = nest_arr(n_classes)
	inters    = nest_arr(n_classes)

	# Find endpoints and intersections in each shape.
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
			seg = cc[y, x] - 1

			if degree > 2:
				inters[seg].append((y,x))
			elif degree == 1:
				endpoints[seg].append((y,x))

		it.iternext()

	return [endpoints, inters]

def find_starts(cc, endpoints, inters):
	starts = []
	n_classes = len(endpoints)

	# Identify the top-left pixel of each segment
	top_lefts  = [None] * n_classes

	found = 0
	for y in xrange(cc.shape[0]):
		for x in xrange(cc.shape[1]):
			if found >= n_classes:
				break

			seg = cc[y,x] - 1
			if seg >= 0 and top_lefts[seg] is None:
				top_lefts[seg] = (y,x)
				found += 1
		else:
			continue
		break

	# Choose best starting point for CC-driven search
	# Prefer endpoints to intersection points to top-leftmost points
	for (ends, cuts, top_left) in zip(endpoints, inters, top_lefts):
		el = None

		if len(ends) > 0:
			el = ends[0]
		elif len(cuts) > 0:
			el = cuts[0]
		else:
			el = top_left

		starts.append(el)

	return starts

def fetch(image, x, y, val=-1):
	h, w = image.shape[:2]
	if x < 0 or x >= w or y < 0 or y >= h:
		return val
	else:
		return image[y, x]

def show(trigger, img, grey=True):
	if trigger:
		if grey:
			plt.imshow(img, cmap="gray")
		else:
			plt.imshow(img)
		plt.show()

def nest_arr(size):
	return [[] for i in xrange(size)]

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
	makegraph(args.input, args.output, args.plots)