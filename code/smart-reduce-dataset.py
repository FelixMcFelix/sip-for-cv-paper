import argparse
import csv
import numpy as np
from config import *

def smart_reduce_dataset(low_symbol=0, high_symbol=1500):
	for dset in datasets:
		rows_sets = []
		total_len = 0

		for split in splits:
			points = []

			with open("{}{}/{}.csv".format(img_dir, dset, split)) as csvfile:
				rdr = csv.reader(csvfile)
				for row in rdr:
					clss = int(row[1])
					if clss >= low_symbol and clss <= high_symbol:
						points.append(row)
						total_len += 1

			rows_sets.append((split, points))

		for size in dataset_sizes:
			ratio = float(size) / total_len

			for split, rows in rows_sets:
				with open("{}{}/{}-{}-smrt.csv".format(img_dir, dset, split, size), "wb") as csvfile:
					wrt = csv.writer(csvfile)
					perm_size = len(rows)
					to_take = int(ratio * perm_size)

					print split, perm_size, to_take

					for row in np.random.permutation(rows)[:to_take+1]:
						wrt.writerow(row)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="Narrow down test/train datasets, preserving label frequencies"
	)
	parser.add_argument("-ls", "--low-symbol", default=0, type=int)
	parser.add_argument("-hs", "--high-symbol", default=1500, type=int)
	args = parser.parse_args()
	smart_reduce_dataset(low_symbol=args.low_symbol, high_symbol=args.high_symbol)