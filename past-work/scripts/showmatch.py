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

def match_map(match):
	line = match.readlines()[1]
	match.close()

	lmap = {}
	rmap = {}

	# now parse the line
	for pair in line.split(")"):
		if "->" in pair:
			nums = [int(x) for x in pair.split("(")[1].split(" -> ")]
			if nums[1] > -1:
				lmap[nums[0]] = nums[1]
				rmap[nums[1]] = nums[0]

	return (lmap, rmap)

def get_graph(file, match_map, first=None):
	lines = file.readlines()[1:]
	file.close()

	coords = []
	G = nx.Graph()

	for i, line in enumerate(lines):
		parts = line.split(" @ ")

		# read coords in graph-space
		coords.append([int(x) for x in parts[1].split(" ")])

		# add edges if relevant
		if i in match_map:
			G.add_node(i)
			partners = [int(x) for x in parts[0].split(" ")[1:]]
			for p in partners:
				if p in match_map:
					if first is None:
						G.add_edge(i, p)
					else:
						edges = first.edges()
						(il, pl) = (match_map[i], match_map[p])
						if (il,pl) in edges or (pl,il) in edges:
							G.add_edge(i, p)


	return (G, coords)

def draw_graph(graph, coords):
	nx.draw(graph, coords)
	plt.show()

def math_to_raster(coords_list, shape):
	return np.array([(shape[0]-y, x) for (x,y) in coords_list])

def map_to_np_match(map):
	out = []
	for l in map:
		out.append([l, map[l]])
	
	return np.array(out, dtype=np.uint32)

def main(match, pattern, target, image_path, image_path_2):
	image = data.imread(image_path)
	image2 = data.imread(image_path_2)

	# extract info from the match file
	(lmap, rmap) = match_map(match)

	(pGraph, pCoords) = get_graph(pattern, lmap)
	(tGraph, tCoords) = get_graph(target, rmap, pGraph)

	# draw the graphs

	draw_graph(pGraph, pCoords)
	draw_graph(tGraph, tCoords)

	# now draw the "keypoint matching"
	pCoords_prime = math_to_raster(pCoords, image.shape)
	tCoords_prime = math_to_raster(tCoords, image2.shape)

	match = map_to_np_match(lmap)
	print len(pGraph.nodes()), len(tGraph.nodes()), len(match)

	for j, k in match:
		(xp, yp) = pCoords_prime[j]
		(xt, yt) = tCoords_prime[k]

		if (xp-xt)**2 + (yp-yt)**2 > 25:
			print j, pCoords[j], pCoords_prime[j]
			print k, tCoords[k], tCoords_prime[k]
			print (xp-xt)**2 + (yp-yt)**2

			(xp, yp) = pCoords[j]
			(xt, yt) = tCoords[k]

			print (xp-xt)**2 + (yp-yt)**2


	feat.plot_matches(plt, image, image2, pCoords_prime, tCoords_prime, map_to_np_match(lmap), (1.0, 0.0, 0.0), only_matches=False)
	plt.show()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('match', type=argparse.FileType('r'),
	                    help='a file containing the match result')
	parser.add_argument('pattern', type=argparse.FileType('r'),
	                    help='a file containing the pattern graph')
	parser.add_argument('target', type=argparse.FileType('r'),
	                    help='a file containing the target graph')
	parser.add_argument('image_path',
	                    help='a file containing the image, to demonstrate matching')
	parser.add_argument('image_path_2', nargs='?', default=None,
						help='a file containing a second image')
	args = parser.parse_args()

	im2 = args.image_path_2 if args.image_path_2 is not None else args.image_path

	main(args.match, args.pattern, args.target, args.image_path, im2)