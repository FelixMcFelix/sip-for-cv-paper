from config import *
import os
import csv

def washington_split():
	loc = font_dir + washington + washington_set
	outloc = font_dir + washington + washington_spl

	mkdirnotex(outloc)

	label_map = {}
	labels = []

	for filename in os.listdir(loc):
		with open(loc + filename) as f:
			with open(outloc + filename.lower().replace(".txt", ".csv"), "wb+") as outf:
				lns = [x.strip() for x in f.readlines()]
				wrt = csv.writer(outf)
				for ln in lns:
					[label, img] = ln.split(" ")
					if label not in label_map:
						l_code = len(labels)
						labels.append(label)
						label_map[label] = l_code
					wrt.writerow(["{}.png".format(img), label_map[label]])

	with open(outloc+"labels.csv", "wb+") as outf:
		wrt = csv.writer(outf)
		for tup in enumerate(labels):
			wrt.writerow(tup)

if __name__ == '__main__':
	washington_split()