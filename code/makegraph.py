import argparse
import math
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

def makegraph(input, output=None, plot=False, dotfile=None, dual_output=None, dual_dotfile=None):
	G = nx.MultiGraph()
	G2 = nx.MultiGraph()

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

	# NOTE: need this for construction of the dual graph.
	label_map = []
	edges_for_pt = {}
	special_edges_for_pt = {}

	def base_register(edge, label, descriptors, collection, col):
		index = len(label_map)
		label_map.append(label)

		for pt, descriptor in zip(edge, descriptors):
			tu = (index, descriptor)
			if pt not in collection:
				collection[pt] = [tu]
			else:
				collection[pt].append(tu)

		G.add_edge(*edge, attr_dict={"weight":label, "color":col})
		G2.add_node(index, attr_dict={"weight":label, "color":col})

	def reg_edge(edge, label, descriptors, color):
		base_register(edge, label, descriptors, edges_for_pt, color)

	def reg_special(edge, label, color):
		base_register(edge, label, [0]*len(edge), special_edges_for_pt, color)

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
					rest = []

					while pt not in keyps and pt is not None:
						search_pts = get_nhood_pts(pt[1], pt[0])
						visited.add(pt)
						rest.append(pt)
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

					my_d_min = 7
					my_d_max = my_d_min + 2

					goods = path_keyps(rest, d_min = my_d_min, d_max = my_d_max, a_max = math.radians(150))

					history = [curr] + rest + [pt]
					path_subdivs = [curr] + [rest[i] for i in goods] + [pt]

					if plot: "working between", curr, "and", pt
					show(plot, pathim)

					lastgood = 0

					# For each point and the next point along
					for p1, p2 in zip(path_subdivs, path_subdivs[1:]):
						# now establish if this is a line or curve
						lineim = np.zeros_like(cc)
						rr, ll = draw.line(p1[0], p1[1], p2[0], p2[1])
						lineim[rr, ll] = 1
						len_line = np.sum(lineim)
						in_line = np.sum(lineim & pathim)

						h_sub = history[lastgood:]

						currgood = h_sub.index(p2) if p1 != p2 else len(h_sub) - 1
						subpathlen = currgood
						lastgood += currgood

						label = LINE
						col = COLOR_LINE
						thres = 1.5
						# print pathlen, len_line, in_line
						if thres * len_line < subpathlen:
							label = CURVE
							col = COLOR_CURVE
						
						# G.add_edge(p1, p2, weight=label, color=col)
						edge = (p1, p2)
						mods = [1, -1]

						# print edge
						# print history
						# print [
						# 	history[history.index(pt)+mod]
						# 	# history[history.index(pt)+mod]
						# 	# get_nhood_pts(*pt)
						# 	for pt, mod in zip(edge, mods)
						# ]

						descriptors = [
							get_nhood_pts(*pt, img_order=False).index(h[h.index(pt)+mod])
							# history[history.index(pt)+mod]
							# get_nhood_pts(*pt)
							for pt, mod, h in zip(edge, mods, [h_sub, h_sub[(p1==p2):]])
						]
						reg_edge(edge, label, descriptors, col)

						if plot:
							print "path from", p1, "to", p2, "label", label

						show(plot, lineim)

					# Testing
					# if plot: print goods
					# can = color.gray2rgb(np.array(pathim))

					# for index in goods:
					# 	can[rest[index]] = [1,0,0]

					# show(plot, can, grey=False)
					# End testing

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
		reg_special((zero, closest), NORTH, COLOR_NORTH)
		# G.add_edge(zero, closest, weight=NORTH, color=COLOR_NORTH)
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
					reg_special((ep, best), NEIGHBOUR, COLOR_NEIGHBOUR)
					# G.add_edge(ep, best, weight=NEIGHBOUR, color=COLOR_NEIGHBOUR)
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

	##
	# Step 9: Dual Graph
	##
	# Only make it if we need it.

	# print edges_for_pt, special_edges_for_pt

	if dual_output is None and dual_dotfile is None:
		return

	for pt in edges_for_pt:
		l = edges_for_pt[pt]
		for i, (dex1, attr1) in enumerate(l):
			for dex2, attr2 in l[i+1:]:
				G2.add_edge(dex1, dex2, label=abs(attr1-attr2))

	for pt in special_edges_for_pt:
		l = special_edges_for_pt[pt]
		for i, (dex1, attr1) in enumerate(l):
			for dex2, attr2 in l[i+1:]:
				G2.add_edge(dex1, dex2, label=abs(attr1-attr2))

			if pt in edges_for_pt:
				for dex_far, _ in edges_for_pt[pt]:
					G2.add_edge(dex1, dex_far, label=8)					

	# print G2.nodes(data=True)
	if dual_dotfile is not None:
		# nx.to_agraph(G2).write(dual_dotfile)
		write_dot(G2, dual_dotfile)

	if dual_output is not None:
		dual_output.write("{} {}\n".format(len(label_map), len(G2.edges())))

		for label in label_map:
			dual_output.write("{}\n".format(label))

		for n1, n2, d in G2.edges(data=True):
			dual_output.write("{} {} {}\n".format(n1, n2, d["label"]))


def sqdist(pt1, pt2):
	out = 0
	for c_0, c_1 in zip(pt1, pt2):
		out += (c_0 - c_1) ** 2
	return out

def manh_dist(pt1, pt2):
	out = 0
	for c_0, c_1 in zip(pt1, pt2):
		diff = (c_0 - c_1)
		out += diff if diff >= 0 else -diff
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

def get_nhood_pts(x, y, img_order=True):
	out = [
		# N, NE,
		# E, SE,
		# S, SW,
		# W, NW
		(y-1,x), (y-1,x+1),
		(y,x+1), (y+1,x+1),
		(y+1,x), (y+1,x-1),
		(y,x-1), (y-1,x-1),
	]
	return out if img_order else [(x, y) for (y, x) in out]

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

def reverse_enumerate(L):
	for index in reversed(xrange(len(L))):
		yield index, L[index]

DEFAULT_A_MAX = math.radians(150)
def path_keyps(path, d_min=7, d_max=None, a_max=DEFAULT_A_MAX):
	# Take a set of locations on a path, return a list of interest point indices
	# (locations w high curvature) by the IPAN algorithm.
	# (Chetverikov, 2003)
	# based on https://www.lemoda.net/algorithms/high-curvature/index.html
	if d_max is None:
		d_max = d_min+2

	d_max_2 = d_max * d_max
	d_min_2 = d_min * d_min

	cos_min = math.cos(a_max)

	candidates = []
	out = []

	# First pass -- find candidates
	for i, p in enumerate(path):
		sharpness = None
		cos_max = -1
		seen_valid_up = False
		for j, p_plus in enumerate(path[i+1:]):
			true_j = j + i + 1
			side_a = sqdist(path[i], path[true_j])

			if seen_valid_up and side_a > d_max_2:
				break
			if side_a < d_min_2:
				continue

			seen_valid_up = True
			seen_valid_down = False
			for k, p_minus in reverse_enumerate(path[:i]):
				side_b = sqdist(path[i], path[k])

				if seen_valid_down and side_b > d_max_2:
					break
				if side_b < d_min_2:
					continue

				seen_valid_down = True
				side_c = sqdist(path[k], path[true_j])

				top = side_a + side_b - side_c
				bottom = 2 * math.sqrt(side_a * side_b)

				cos = top/bottom if bottom != 0.0 else -2

				if cos < cos_min:
					break
				if cos_max < cos:
					cos_max = cos
					sharpness = (i, true_j, k, cos)

		if sharpness is not None: candidates.append(sharpness)

	# Second pass -- clean up.
	# examine all other candidates under d_max_2 to find better maxima.
	last_found = -1
	lf_cos = -2
	for (index, plus, minus, cos) in candidates:

		## ORIGINAL PAPER ##
		# Modified to stop equality from ruining maxima
		beaten = False
		for (index_v, plus_v, minus_v, cos_v) in candidates:
			if beaten:
				break
			if index_v == index or sqdist(path[index],path[index_v]) > d_max_2:
				continue

			# point is worth considering (valid), do sharpness test.
			beaten = cos < cos_v or (cos == cos_v and index_v in out)
			# if beaten: print index, "denied by", index_v

		if not beaten:
			out.append(index)
		# out.append(index)

		## INTERNET WEIRD ONE ##
		# found = False
		# remove_last = False
		# src = ""
		# if cos > cos_min:
		# 	if last_found > 0:
		# 		d = sqdist(path[index], path[last_found])
		# 		if d > d_max_2:
		# 			src = "dist constraint"
		# 			found = True
		# 		elif cos > lf_cos:
		# 			src = "better cos"
		# 			remove_last = True
		# 			found = True
		# 	else:
		# 		src = "first pt"
		# 		found = True

		# if found:
		# 	if remove_last:
		# 		del out[-1]
		# 	out.append(index)
		# 	lf_cos = cos
		# 	last_found = index
		# 	print "marked", index, "with", src

	# done
	return out




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
	parser.add_argument("-ddf", "--dual-dotfile",
						default=None,
						help="Path of dual graph dot file. "+
							"Used with Graphviz for representation.")
	parser.add_argument("-do", "--dual-output",
						default=None, type=argparse.FileType("w"),
						help="Path of dual-graph output file. "+
							"If not present, graph is not produced.")
	parser.add_argument("-p", "--plots", action='store_true',
						default=False,
						help="Show plots of intermediate steps.")
	args = parser.parse_args()
	makegraph(
		args.input, output=args.output, dual_output=args.dual_output,
		plot=args.plots, dotfile=args.dotfile, dual_dotfile=args.dual_dotfile)