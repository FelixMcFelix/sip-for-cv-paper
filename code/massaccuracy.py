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
			print "{0}: {1:.2f}%".format(curr, get_accuracy(curr) * 100)


if __name__ == '__main__':
	massaccuracy(results_dir + "search/")