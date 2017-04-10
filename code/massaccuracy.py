from config import *
from accuracy import *
import os.path as path
import os

def massaccuracy(dir):
	files = os.listdir(dir)
	for file in files:
		curr = dir + file
		if path.isdir(curr):
			massaccuracy(curr+"/")
		else:
			(acc, kappa) = get_accuracy(curr)
			print "{0}: {1:.2f}%, k={2:.4f}".format(curr, acc * 100, kappa)


if __name__ == '__main__':
	massaccuracy(results_dir + "search/")