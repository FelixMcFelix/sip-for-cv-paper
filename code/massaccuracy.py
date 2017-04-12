from config import *
from accuracy import *
import os.path as path
import os
import csv

totrack = []

def topcall(dir):
	massaccuracy(dir)

	# Now write out the plot data, and make dat plot?
	out_file = plots_dir + "ct/vals.csv"

	mkdirnotex(out_file)

	with open(out_file, "wb") as f:
		wrt = csv.writer(f)
		for row in totrack:
			wrt.writerow(row)

def massaccuracy(dir):
	files = os.listdir(dir)
	for file in files:
		curr = dir + file
		if path.isdir(curr):
			massaccuracy(curr+"/")
		else:
			(acc, kappa) = get_accuracy(curr)
			print "{0}: {1:.2f}%, k={2:.4f}".format(curr, acc * 100, kappa)

			# haxx
			if "hwrt-induced/t" in curr and "-r1-" in curr and "dual" not in curr:
				t = float(
					curr.split("hwrt-induced/t")[1].split("-r1-")[0]
				)

				totrack.append((t, acc))

if __name__ == '__main__':
	topcall(results_dir + "search/")