from config import *
import os.path as path
import os
import numpy as np
from plots import process_graph

def graphstats(dir):
	files = os.listdir(dir)

	if "test" in files and "train" in files and path.isdir(dir+"test") and path.isdir(dir+"train"):
		parsedir(dir, [dir+"test/", dir+"train/"])
	else:
		is_leaf = True
		for file in files:
			curr = dir + file
			if path.isdir(curr):
				graphstats(curr+"/")
				is_leaf = False
		
		if is_leaf:
			parsedir(dir, [dir]) #print "{0}: {1:.2f}%".format(curr, get_accuracy(curr) * 100)


def parsedir(printdir, dirs):
	sizes = []
	orders = []
	degrees = []

	for dir in dirs:
		files = os.listdir(dir)
		for file in files:
			[order, sz, deg, lns, crvs, rat] = process_graph(dir+file)
			sizes.append(int(sz))
			orders.append(int(order))
			if(not np.isnan(deg)):
				degrees.append(deg)

	print "{0}:".format(printdir)

	def statify(name, arr):
		print "\t{0} min: {1} max: {2} median: {3} mean: {4}".format(name, np.min(arr), np.max(arr), np.median(arr), np.mean(arr))

	statify("order", orders)
	statify("size", sizes)
	statify("degree", degrees)

if __name__ == '__main__':
	graphstats(graph_dir)