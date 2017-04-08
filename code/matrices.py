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

def write_matrix(path, filename, matrix, negate=False):
	outname = path + filename
	mkdirnotex(outname)
	with open(outname + ".csv", "wb") as f:
		out = csv.writer(f)
		out.writerow([""] + labels)
		for label, row in zip(labels, matrix):
			out.writerow([label] + row.tolist())

	outext = ".png"
	neg_var = "; ged='defined'" if negate else ""
	call(["gnuplot", "-e", "filename='{0}.csv'; outpng='{0}{1}'; outtikz='{0}.tex'{2}".format(outname, outext, neg_var), "heatmap.gp"])

def process_font(font, font2=None, path_append=""):
	# find all graph sizes
	sizes  = []
	sizes2 = []
	for char in chars:
		with open(graph_dir + path_append + font + "/" + char, "r") as f:
			sizes.append(int(f.readline().split(" ")[0]))

		if font2 is not None:
			with open(graph_dir + path_append + font2 + "/" + char, "r") as f:
				sizes2.append(int(f.readline().split(" ")[0]))

	if font2 is None:
		sizes2 = sizes

	name_append = path_append.replace("/", "-")

	w = len(sizes)
	nrms = np.zeros((w,w))
	ps = np.zeros((w,w))
	ts = np.zeros((w,w))

	for param, param_name in params:
		vals = np.zeros((w,w))
		# Fill matrix with observed values
		for p, t in ((p, t) for p in chars for t in chars):
			path = "{}mcs/{}{}-{}/{}.{}".format(results_dir, path_append, font, param_name, p, t) if font2 is None else "{}mcs/{}{}-{}-{}/{}.{}".format(results_dir,  path_append, font, font2, param_name, p, t)
			with open(path) as f:
				# print param_name, p, t
				interm = f.readlines()[-1].strip().split("SIZE=")
				vals[back_chars[p], back_chars[t]] = int(interm[1]) if len(interm) > 1 else 0

		# normalisation factors
		for i, size_p in enumerate(sizes):
			for j, size_t in enumerate(sizes2):
				el = max(size_t, size_p)
				nrms[i, j] = el
				ps[i, j] = size_p
				ts[i, j] = size_t

		# print vals
		out_p = "{}{}/{}".format(name_append, font, param_name) if font2 is None else "{}{}-{}/{}".format(name_append, font, font2, param_name)

		ged = np.abs(vals-ps)+np.abs(vals-ts)

		write_matrix(tables_dir, "{}-conf-reg".format(out_p), vals.astype(np.int_))
		write_matrix(tables_dir, "{}-conf-nrm".format(out_p), vals/nrms)
		write_matrix(tables_dir, "{}-conf-ged".format(out_p), ged.astype(np.int_), negate=True)

for font in fonts:
	process_font(font)
	process_font(font, path_append=dual_suffix)

for font1, font2 in font_comp:
	process_font(font1, font2)
	process_font(font1, font2, dual_suffix)