import csv
import numpy as np
from config import *

def reduce_dataset():
	for dset in datasets:
		rows_sets = []
		total_len = 0

		for split in splits:
			points = []

			with open("{}{}/{}.csv".format(img_dir, dset, split)) as csvfile:
				rdr = csv.reader(csvfile)
				for row in rdr:
					points.append(row)
					total_len += 1

			rows_sets.append((split, points))

		for size in dataset_sizes:
			ratio = float(size) / total_len

			for split, rows in rows_sets:
				with open("{}{}/{}-{}.csv".format(img_dir, dset, split, size), "wb") as csvfile:
					wrt = csv.writer(csvfile)
					perm_size = len(rows)
					to_take = int(ratio * perm_size)

					print split, perm_size, to_take

					for row in np.random.permutation(rows)[:to_take+1]:
						wrt.writerow(row)

if __name__ == "__main__":
	reduce_dataset()