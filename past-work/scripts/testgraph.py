import sys
import random
import argparse
import math
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from skimage import *
import skimage.io as io
import skimage.data as data
import skimage.color as color
import skimage.segmentation as seg
import skimage.feature as feat
import skimage.transform as trans

import shapely
from shapely.geometry import Polygon
from shapely.geometry import LineString
from scipy.spatial import Delaunay

IMG = 0
IMG_180 = 1
SEG = 2

def randint(max=256):
	return math.floor(random.random()*max)

def rand_color():
	return [randint(), randint(), randint()]

def seg_file(path):
	with open(path, "r") as f:
		content = f.readlines()
		width = int([x for x in content if x.startswith("width")][0][6:])
		height = int([x for x in content if x.startswith("height")][0][7:])
		segments = int([x for x in content if x.startswith("segments")][0][9:])

		out = np.zeros((height, width), dtype=np.uint8)

		cols = []
		for n in xrange(0, segments):
			cols.append(rand_color())

		for row in content[content.index("data\n")+1:]:
			# segment, row, x1, x2 (xs inclusive)
			nums = [int(x) for x in row.split(" ")]
			out[nums[1], nums[2]:nums[3]+1] = nums[0]

		return (out, segments)

def paint_segments(image, number):
	cols = []
	for n in xrange(0, number):
		cols.append(rand_color())

	new = color.gray2rgb(np.array(image, dtype=np.uint8))

	it = np.nditer(new, flags=['multi_index'], op_flags=['readwrite'])
	while not it.finished:
		it[0] = cols[it[0]][it.multi_index[2]]
		it.iternext()

	return new

def get_boundaries(dat):
	return seg.mark_boundaries(np.ones(dat.shape), dat, color=(0,0,0), background_label=np.max(dat)+1)

def get_nhood(image, x, y):
	nhood = np.zeros((3,3), dtype=np.int8)

	for (ny, r) in enumerate(nhood):
		for (nx, v) in enumerate(r):
			im_x = x + nx - 1
			im_y = y + ny - 1
			nhood[ny, nx] = fetch(image, im_x, im_y)

	return nhood

def fetch(image, x, y, val=-1):
	h, w = image.shape[:2]
	if x < 0 or x >= w or y < 0 or y >= h:
		return val
	else:
		return image[y, x]

def kp_set_to_np(kset):
	arr = []
	for el in kset:
		(y, x) = el
		arr.append([y,x])

	return np.array(arr)

def get_pointels(x, y):
	out = []
	for x in [x, x+1]:
		for y in [y, y+1]:
			out.append((y,x))
	return out

def get_pointel_pxs(image, x, y, val=-1):
	# get the 4 pixels which meet at a given pointel x, y.
	# flat 1-d array as described in paper -- clockwise around point.
	# just give (-1) for any external values? idk
	return [
		fetch(image, x-1, y-1, val),
		fetch(image, x,   y-1, val),
		fetch(image, x,   y,   val),
		fetch(image, x-1, y,   val),
	]

def array_rotate(arr, n):
	return arr[n:] + arr[:n]

def flip_arr(arr, vert=True, horiz=False):
	out = arr
	if(vert):
		out = out[::-1]
	if(horiz):
		out = out[:,::-1]
	return out

def main(input, out, format=IMG, seg_file=""):
	# Presegmented data
	image = preseg_image = nsegs = None

	if format==SEG:
		# image = data.imread("../seg-test/bsd-157055.jpg")
		# preseg_image = data.imread("../seg-test/bsd-157055-pre8.jpg")
		# (preseg_real, nsegs) = seg_file("../seg-test/157055.seg")
		image = data.imread(input)
		preseg_image = data.imread(input)
		(preseg_real, nsegs) = seg_file(seg_file)
	else:
		# Image file
		image = data.imread("../imgs/gbu3-smr.png")
		preseg_real = seg.slic(image, convert2lab=True, n_segments=7, compactness=30.0, sigma=0.5, enforce_connectivity=True)
		nsegs = np.max(preseg_real) + 1

		if format==IMG_180:
			# Rotate 180
			image = flip_arr(image, horiz=True)
			preseg_real = flip_arr(preseg_real, horiz=True)

			# Flip Vert
			# image = flip_arr(image)
			# preseg_real = flip_arr(preseg_real)

	preseg_real_c = paint_segments(preseg_real, nsegs)

	# kp = feat.corner_peaks(feat.corner_kitchen_rosenfeld(color.rgb2gray(get_boundaries(preseg_real))))
	kp = feat.corner_peaks(feat.corner_harris(color.rgb2gray(get_boundaries(preseg_real))))
	# kp = feat.corner_peaks(feat.corner_harris(color.rgb2gray(preseg_real_c)))

	# Now, go over all keypoints.
	# Remove all with only one region in 3x3 nhood.

	keep = set()

	for (y, x) in kp:
		nh = get_nhood(preseg_real, x, y)
		els = set()
		for neighbour in np.nditer(nh):
			if neighbour >= 0:
				els.add(int(neighbour))

		if len(els) > 1:
			keep.add((int(y),int(x)))

	print len(keep)

	# Add any points with 3 regions (or 2 and on an edge) in nhood.
	# HINT: -1 counts as another region ;)

	print len(keep)

	for y in xrange(0, image.shape[0]):
		for x in xrange(0, image.shape[1]):
			nh = get_nhood(preseg_real, x, y)
			els = set()
			for neighbour in np.nditer(nh):
				els.add(int(neighbour))

			if len(els) > 2:
				keep.add((y,x))

	print len(keep)

	# Add 4 corner points

	for x in [0, image.shape[1]-1]:
		for y in [0, image.shape[0]-1]:
			keep.add((y,x))

	print len(keep)

	# Mark image edges as boundaries

	bound_img = get_boundaries(preseg_real)
	bound_img[0,:] = (0,0,0)
	bound_img[image.shape[0]-1,:] = (0,0,0)
	bound_img[:,0] = (0,0,0)
	bound_img[:,image.shape[1]-1] = (0,0,0)

	# Extract pointels from pixels
	# Visit each pointel no more than once -- each pixel admits 4.
	# Store the neighbouring regions of each chosen pointel
	# This is important for traversal!

	visited_pointels = set()
	pointel_list = []
	pointel_ids = {}
	pointel_region_sets = []
	pointels_by_region = {}

	for (y, x) in keep:
		for pt in get_pointels(x, y):
			if pt not in visited_pointels:
				(py, px) = pt
				im_px = get_pointel_pxs(image, px, py, (0,0,0))
				sg_px = get_pointel_pxs(preseg_real, px, py)

				for (i, ci) in enumerate(im_px):
					pred = im_px[(i-1)%4]
					succ = im_px[(i+1)%4]
					# pred = sg_px[(i-1)%4]
					# succ = sg_px[(i+1)%4]

					if not(np.array_equal(ci, pred) or np.array_equal(ci, succ)):
						#chosen pointel
						index = len(pointel_list)
						pointel_list.append(pt)
						regions = np.unique(sg_px)

						pointel_ids[pt] = index
						pointel_region_sets.append(regions)

						for n in regions:
							if n >= 0:
								if n not in pointels_by_region:
									pointels_by_region[n] = set()
								pointels_by_region[n].add(pt)
						break

				visited_pointels.add(pt)

	print len(pointel_list)

	# Now walk the image in some fashion
	# ---
	# Start with the top-most, then left-most pixel in each segment.
	# This is (by construction of the segmented image) a pixel on the outer hull of that segment.
	# NOW:
	# \-> Follow clockwise until hitting a point or returning to the start pixel.
	#        | If returned to start (point AND facing direction), then that segment admits no hull.
	#        | Otherwise, record this point as start and predecessor, and build graph by walking
	#          clockwise.
	#            ! Don't add edges if present in graph already.
	#            ! Hull is closed upon return to start point. End result may be a single point.
	#        | Next segment.
	# \-> Check if any hulls (polys or points) have a shared region "a" in nhood over all pointels.
	#     This implies that this hull is a cut from region "a".

	G = nx.Graph()

	# Find first pixel of each segment by above criteria.
	firsts = [image.shape[:2] for x in pointels_by_region]
	it = np.nditer(preseg_real, flags=['multi_index'], op_flags=['readonly'])
	while not it.finished:
		coord = (it.multi_index[0], it.multi_index[1])
		segc = it[0]
		if coord < firsts[segc]:
			firsts[segc] = coord
		it.iternext()

	# Now walk from each starting point, building graph and polygon hulls.
	polygons = []
	poly_nodes = []

	met_pointels = set()

	plt.imshow(image)
	plt.show()
	plt.imshow(preseg_real_c)
	plt.show()
	plt.axis('on')
	feat.plot_matches(plt, bound_img, preseg_real_c, kp_set_to_np(keep), kp_set_to_np(pointel_list), np.array([]), (1.0, 0.0, 0.0))
	plt.show()

	print firsts

	for (region_n, start_pointel) in enumerate(firsts):
		print "loop started for", region_n
		# Pointel to top-left of chosen pixel is start
		poly_list = []
		# Interest pointels
		first_found_pointel = None
		prev_found_pointel = None

		# Generic pointels
		prev_pointel = None
		curr_pointel = None

		history = set()
		past = set()

		done = False

		# Loop ends if either back at start pointel
		while (first_found_pointel is None and curr_pointel != start_pointel) or not done:
			# Start the process.
			if curr_pointel is None:
				curr_pointel = start_pointel

			(cy, cx) = curr_pointel
			# print curr_pointel

			# Check if curr is an interest pointel
			if curr_pointel in pointel_ids:
				if curr_pointel not in past or curr_pointel == first_found_pointel:

					past.add(curr_pointel)

					if first_found_pointel is None:
						history = set()
						first_found_pointel = curr_pointel

					# if region_n ==0:
					# 	print curr_pointel

					# Do stuff to connect curr to prev here
					if prev_found_pointel is not None:
						G.add_edge(pointel_ids[prev_found_pointel], pointel_ids[curr_pointel])
						# End if back at start...
						if curr_pointel == first_found_pointel:
							done = True
							break
					poly_list.append(curr_pointel)
					met_pointels.add(curr_pointel)

					prev_found_pointel = curr_pointel

			# Identify next point
			#
			# Choose a pointel from 4 neighbours s.t. the
			# connecting linel touches a pixel from region_n and another,
			# but ISN'T the previous pointel.
			local_pxs = get_pointel_pxs(preseg_real, cx, cy)
			local_pnts = [
				# N, E, S, W
				(cy-1,cx), (cy,cx+1), (cy+1,cx), (cy,cx-1)
			]

			next_pointel = None
			for i in xrange(0,4):
				target = local_pnts[i]
				neighbours = array_rotate(local_pxs, i)[0:2]

				if (curr_pointel, i) in history:
					continue

				if target != prev_pointel and region_n in neighbours and len(np.unique(neighbours)) == 2:
					next_pointel = target
					history.add((curr_pointel, i))
					history.add((next_pointel, (i+2)%4))
					break

			# Move on
			prev_pointel = curr_pointel
			curr_pointel = next_pointel

		# Push completed polygons
		poly_nodes.append(poly_list)
		polygons.append(Polygon(poly_list))
		print "loop terminated for", region_n

	# Convert to plot space
	flip_coord = [(x,y) for (y,x) in pointel_list]

	if format == IMG or format == SEG:
		# Flip pointel coords vert to convert from raster order
		flip_coord = [(x,image.shape[0]-y) for (x,y) in flip_coord]
	else:
		# Flip pointel coords horiz if needed
		flip_coord = [(image.shape[1]-x,y) for (x,y) in flip_coord]

	colors = [np.array(fetch(image, x, y, val=[0,0,0]), dtype=np.float64)/255 for (y,x) in pointel_list]

	nx.draw(G, flip_coord, node_color=colors)
	plt.show()

	# Perform delaunay triangulation over each polygon's set of nodes.
	# Add each edge generated which intersects the current face and NO OTHERS
	# (I know I can do this faster, but I'm REALLY lazy)
	for region_n in pointels_by_region:#poly_nodes):
		nodes = list(met_pointels & pointels_by_region[region_n])
		d = Delaunay(nodes)
		edges = set()

		#convert triangles to edges
		for tri in d.simplices:
			tri.sort()
			[a,b,c] = tri
			edges.add((nodes[a], nodes[b]))
			edges.add((nodes[a], nodes[c]))
			edges.add((nodes[b], nodes[c]))

		# check if edge contained in main poly, not contained in any other
		for e in edges:
			good = True

			for poly_n, poly in enumerate(polygons):
				if not good:
					break
				good = LineString(e).within(poly) if poly_n == region_n else not LineString(e).crosses(poly)

			if good:
				G.add_edge(pointel_ids[e[0]], pointel_ids[e[1]])

	print len(G.edges())
	print len(G.nodes())

	node_map = {}
	for i, el in enumerate(G.nodes()):
		node_map[el] = i

	nx.draw(G, flip_coord, node_color=colors)
	plt.show()

	# Write the output graph file
	count = len(G.nodes())
	out.write(str(count) + "\n")

	for node in G.nodes():
		relevant_edges = [r for (l,r) in G.edges() if l == node]
		out.write(str(len(relevant_edges)))

		for edge in relevant_edges:
			out.write(" {}".format(node_map[edge]))

		out.write(" @ {} {}\n".format(*flip_coord[node]))

	out.close()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Turn an image (or segment file) into a graph.')
	parser.add_argument("input", help="Filename to read in")
	parser.add_argument('out', type=argparse.FileType('w'),
	                    help='a filename to write out the graph representation to')
	parser.add_argument("-f", "--format", type=int, default=IMG,
	                    help="file input format. 0=image, 1=image, rotate 180, 2=segmentation file. Seg file must be used with -s setting")
	parser.add_argument("-s", "--seg-file", default="",
	                    help="use with '-f 2'. Path to segment file")
	args = parser.parse_args()
	main(args.input, args.out, format=args.format)