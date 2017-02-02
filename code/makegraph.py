
import argparse
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import skimage.color as color
import skimage.data as data
import skimage.draw as draw
import skimage.filters as filters
import skimage.morphology as morph

# from networkx.drawing.nx_agraph import graphviz_layout
from networkx.drawing.nx_pydot import write_dot

LINE = 1
CURVE = 2
NEIGHBOUR = 3
NORTH = 4

COLOR_LINE = "red"
COLOR_CURVE = "green"
COLOR_NEIGHBOUR = "blue"
COLOR_NORTH = "purple"

def makegraph(input, output=None, plot=False, dotfile=None):
	G = nx.MultiGraph()

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
	# print starts, keyp_sets

	##
	# Step 6: Line/Path detection
	##
	# walk graph to find all paths.
	# from start point, check all values in 3x3 nhood for next place to go.
	# upon hitting another keypoint, queue it up to visit after the current kp
	# is exhausted.
	for start, keyps in zip(starts, keyp_sets):
		# print "new component"
		work_queue = [start]
		visited = set()
		while len(work_queue) > 0:
			curr = work_queue.pop(0)
			# print "took", curr, "now", work_queue
			(y, x) = curr

			local_pts = get_nhood_pts(x, y)

			for direction, (ly, lx) in enumerate(local_pts):
				pt   = (ly, lx)
				last = curr
				seg  = cc[pt] - 1

				if seg >= 0 and pt not in visited:
					pathim = np.zeros_like(cc)
					pathlen = 0
					first = pt

					while pt not in keyps and pt is not None:
						search_pts = get_nhood_pts(pt[1], pt[0])
						visited.add(pt)
						# print "visited", pt

						# Mark the current path to perform fitting.
						pathim[pt[0], pt[1]] = 1
						pathlen += 1

						# Find first point, and first keypoint
						next_nhood = None
						next_keyp  = None

						for (sy, sx) in search_pts:
							if not (next_nhood is None or next_keyp is None):
								break

							if (cc[sy, sx] - 1) >= 0 and (sy, sx) not in visited and (sy, sx) != last:
								if next_nhood is None:
									next_nhood = (sy, sx)
								if next_keyp is None and (sy, sx) in keyps:
									next_keyp = (sy, sx)

						# Move to next point
						# Prefer choosing keypoints over neighbours
						last = pt
						if next_keyp is not None:
							pt = next_keyp
						else:
							pt = next_nhood

					# might have ended up in a dead end
					if pt is None: break

					# path completed now.
					if pt not in work_queue:
						work_queue.append(pt)

					# now establish if this is a line or curve
					lineim = np.zeros_like(cc)
					rr, ll = draw.line(first[0], first[1], last[0], last[1])
					lineim[rr, ll] = 1
					len_line = np.sum(lineim)
					in_line = np.sum(lineim & pathim)

					label = LINE
					col = COLOR_LINE
					thres = 1.5
					# print pathlen, len_line, in_line
					if thres * len_line < pathlen:
						label = CURVE
						col = COLOR_CURVE

					show(plot, pathim)
					show(plot, lineim)

					# print "path from", curr, "to", pt, ": dir", direction, "label", label
					G.add_edge(curr, pt, weight=label, color=col)

			visited.add(curr)


	##
	# Step 7: North and Component connection
	##
	zero = (0,0)
	closest = None
	for pt in G.nodes():
		if closest is None or sqdist(zero, pt) < sqdist(zero, closest):
			closest = pt
	if closest is not None:
		G.add_edge(zero, closest, weight=NORTH, color=COLOR_NORTH)
		# print "path from", zero, "to", closest, "label", NORTH

	for i, eps in enumerate(endpoints):
		if len(eps) == 0:
			eps = inters[i]
			# print eps
		if len(eps) == 0:
			eps = [starts[i]]
			# print eps

		for ep in eps:
			best = None
			for j, keyps in enumerate(keyp_sets):
				if i != j:
					for kp in keyps:
						if best is None or sqdist(ep, kp) < sqdist(ep, best):
							best = kp
			if best is not None:
				v1 = (ep, best)
				v2 = (best, ep)
				edges = G.edges()
				if not (v1 in edges or v2 in edges):
					G.add_edge(ep, best, weight=NEIGHBOUR, color=COLOR_NEIGHBOUR)
					# print "path from", ep, "to", best, "label", NEIGHBOUR

	if dotfile is not None:
		write_dot(G, dotfile)

	node_code = {}
	for i, node in enumerate(G.nodes()):
		node_code[node] = i

	##
	# Step 8: Output
	##
	def graph_out(text):
		if output is None:
			print text
		else:
			output.write(text+"\n")

	graph_out(str(len(node_code)) + " " + str(len(G.edges())))

	for n1, n2, d in G.edges(data=True):
		graph_out(
			str(node_code[n1]) + " " +
			str(node_code[n2]) + " " +
			str(d["weight"])
		)

def sqdist(pt1, pt2):
	out = 0
	for c_0, c_1 in zip(pt1, pt2):
		out += (c_0 - c_1) ** 2
	return out

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

	skel_col = color.gray2rgb(skel)

	# Find endpoints and intersections in each shape.
	it = np.nditer(cc, flags=["multi_index"])
	while not it.finished:
		# Operate only on foreground
		if it[0] > 0:
			[y,x] = it.multi_index

			# Take nhood from skel (since binary) -- this allows
			# some nice tricks.
			nh = get_nhood(skel, x, y)
			nh_flat = get_nhood_pts(x, y)

			# Count neighbours (non-centre)
			# degree = np.sum(nh) - 1
			degree = 0
			first = skel[nh_flat[0]]
			last = 0
			for p in nh_flat:
				val = skel[p]
				# increment degree on rise
				if val > last:
					degree += 1
				last = val

			if first == True and first == last:
				degree -= 1

			seg = cc[y, x] - 1

			if degree != 2:
				# print degree, seg, y, x

				im = np.array(skel_col)
				im[y,x] = [255,0,0]

				# show(True, im, grey=False)

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
	parser.add_argument("-df", "--dotfile",
						default=None,
						help="Path of graph dot file. "+
							"Used with Graphviz for representation.")
	parser.add_argument("-p", "--plots", action='store_true',
						default=False,
						help="Show plots of intermediate steps.")
	args = parser.parse_args()
	makegraph(
		args.input, output=args.output,
		plot=args.plots, dotfile=args.dotfile)