import csv
import numpy as np
from config import *
from subprocess import call

labels      = [c.split("-up")[0] for c in chars]
back_labels = {}
back_chars  = {}

for i, (label, char) in enumerate(zip(labels, chars)):
	back_labels[label] = i
	back_chars[char]  = i


# out = np.zeros((len(labels)+1, len(labels)+1), dtype=np.string_)

# out[0, 1:] = labels
# out[1:, 0] = labels.T

def write_matrix(path, filename, matrix):
	outname = path + filename
	mkdirnotex(outname)
	with open(outname + ".csv", "wb") as f:
		out = csv.writer(f)
		out.writerow([""] + labels)
		for label, row in zip(labels, matrix):
			out.writerow([label] + row.tolist())

	outext = ".png"
	call(["gnuplot", "-e", "filename='{0}.csv'; outpng='{0}{1}'; outtikz='{0}.tex'".format(outname, outext), "heatmap.gp"])

for font in fonts:
	# find all graph sizes
	sizes = []
	for char in chars:
		with open(graph_dir + font + "/" + char, "r") as f:
			sizes.append(int(f.readline().split(" ")[0]))

	w = len(sizes)
	nrms = np.zeros((w,w))

	for param, param_name in params:
		vals = np.zeros((w,w))
		# Fill matrix with observed values
		for p, t in ((p, t) for p in chars for t in chars):
			with open("{}{}-{}/{}.{}".format(results_dir, font, param_name, p, t)) as f:
				vals[back_chars[p], back_chars[t]] = int(f.readlines()[-1].strip().split("SIZE=")[1])

		# normalisation factors
		for i, size_p in enumerate(sizes):
			for j, size_t in enumerate(sizes[i:]):
				el = max(size_t, size_p)
				nrms[i, i+j] = nrms[i+j, i] = el

		# print vals
		write_matrix(tables_dir, "{}-{}.conf-reg".format(font, param_name), vals.astype(np.int_))
		write_matrix(tables_dir, "{}-{}.conf-nrm".format(font, param_name), vals/nrms)