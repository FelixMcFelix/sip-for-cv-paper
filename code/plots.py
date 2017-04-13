from config import *
from makegraph import LINE, CURVE, NEIGHBOUR, NORTH
import csv
import numpy as np
from subprocess import call

def makeplots():
	# Only doing HWRT because I'm fabulously lazy (fight me)
	base = results_dir + "search/"

	out_all_dir = plots_dir + "allclass/"
	out_all = out_all_dir + "vals.csv"
	mkdirnotex(out_all)

	with open(out_all, "wb") as outf:
		wrt = csv.writer(outf)

		for blah, pname in params:
			result_folder = "{}hwrt-{}/".format(base, pname)
			result_folder_d = "{}dual/hwrt-{}/".format(base, pname)
			for r in pen_rads:
				for t in curve_thr:
					outdir = "{}search/{}-t{}-r{}/".format(plots_dir, pname, t, r)
					outdir_d = "{}search/dual-{}-t{}-r{}/".format(plots_dir, pname, t, r)
					mkdirnotex(outdir)
					mkdirnotex(outdir_d)

					send = wrt if pname == "induced" else None

					base_graph_dir = "{}hwrt-{}/r-{}/".format(graph_dir, t, r)
					base_graph_dir_d = "{}dual/hwrt-{}/r-{}/".format(graph_dir, t, r)
					make_plot_set(
						["../imgs/hwrt/test-2000-smrt.csv", "../imgs/hwrt/train-2000-smrt.csv"],
						[base_graph_dir + "test/", base_graph_dir + "train/"],
						"{}t{}-r{}-2000.out".format(result_folder, t, r),
						outdir,
						# None
						send
						)

					make_plot_set(
						["../imgs/hwrt/test-2000-smrt.csv", "../imgs/hwrt/train-2000-smrt.csv"],
						[base_graph_dir_d + "test/", base_graph_dir_d + "train/"],
						"{}t{}-r{}-2000.out".format(result_folder_d, t, r),
						outdir_d,
						None
						# send
						)

		out_dir = plots_dir + "ct/"
		dat_file = out_dir + "vals.csv"

		call(["gnuplot", "-e",
				"filename='{0}'; outpng='{3}{2}{1}'; outtikz='{3}{2}.tex'".format(
					dat_file, ".png", "ct", out_dir
				),
				"plot_thres.gp"])

	plot_csv(out_all, out_all_dir)

def make_plot_csv(split_files, graph_folders, result_file, out_folder, overall_csv):
	label_stats = {}
	label_counts = {}
	label_goods = {}
	label_accs = {}

	all_good = 0
	all_count = 0

	all_stats = []

	def app(lab, store, val):
		if lab not in store:
			store[lab] = [val]
		else:
			store[lab].append(val)

	def increm(lab, store, do=True):
		val = 1 if do else 0

		if lab not in store:
			store[lab] = val
		else:
			store[lab] += val

	for split_loc, graph_loc in zip(split_files, graph_folders):
		with open(split_loc) as split_csv:
			rdr = csv.reader(split_csv)
			for filename, label in rdr:
				no_ext = filename.split(".")[0]
				this_stat = process_graph(graph_loc +"/"+ no_ext)
				app(label, label_stats, this_stat)

				all_stats.append(this_stat)

	with open(result_file) as filey:
		for ln in filey.readlines():
			[truth, observed, correct] = [int(x.strip()) for x in ln.split(" ")[1:]]
			increm(truth, label_counts)
			increm(truth, label_goods, correct==1)
			all_count += 1
			all_good += correct

	for label in label_counts:
		label_accs[label] = label_goods[label] / float(label_counts[label])

	out_path = out_folder + "/vals.csv"

	with open(out_path, "wb") as outf:
		wrt = csv.writer(outf)

		for label in label_accs:
			acc = label_accs[label]

			# [orders, sizes, degrees, line_counts, curve_counts, ratios] = label_stats[label]
			stats = np.array(label_stats[str(label)])

			# take mean over each column
			wrt.writerow([label, acc] + list(stats.mean(axis=0)))

	acc = all_good / float(all_count)

	# print list(np.array(all_stats).mean(axis=0)) #all_stats

	if overall_csv is not None:
		overall_csv.writerow([0, acc] + list(np.array(all_stats).mean(axis=0)))

	# Okay, now worry about plots eventually...
	return out_path

def make_plot_set(split_files, graph_folders, result_file, out_folder, overall_csv):
	csv_dir = make_plot_csv(split_files, graph_folders, result_file, out_folder, overall_csv)
	plot_csv(csv_dir, out_folder)

def plot_csv(csv_dir, out_folder):
	# [label, acc, order, size, np.mean(degrees), line_count, curve_count, ratio]
	y = ("Accuracy", 1)

	xs = [
		("Order", 2),
		("Size", 3),
		("Mean Degree", 4),
		("Line Count", 5),
		("Curve Count", 6),
		("Line-Curve Ratio", 7),
	]

	outext = ".png"

	(yl, yc) = y

	for (label_name, column) in xs:
		call(["gnuplot", "-e",
			"filename='{0}'; outpng='{4}{2}{1}'; outtikz='{4}{2}.tex'; xl='{2}'; xc={3}; yl='{5}'; yc={6}".format(
				csv_dir, outext, label_name.replace(" ", "-"), column+1, out_folder, yl, yc+1
			),
			"plotty.gp"])

def process_graph(graph_path):
	with open(graph_path) as f:
		lns = [x.strip() for x in f.readlines()]
		[order, size] = [int(x) for x in lns[0].split(" ")]
		edge_start = 1
		use_edge_labels = True

		degrees = [0 for x in xrange(order)]
		line_count = 0
		curve_count = 0

		# def reg_label(lab):
		# 	if lab == LINE:
		# 		line_count += 1
		# 	elif lab == CURVE:
		# 		curve_count += 1

		if "dual" in graph_path:
			edge_start += order
			use_edge_labels = False
			for line in lns[1:edge_start]:
				lab = int(line)
				# reg_label(lab)
				if lab == LINE:
					line_count += 1
				elif lab == CURVE:
					curve_count += 1

		for ln in lns[edge_start:]:
			[start, end, lab] = [int(x) for x in ln.split(" ")]
			if use_edge_labels:
				# reg_label(lab)
				if lab == LINE:
					line_count += 1
				elif lab == CURVE:
					curve_count += 1
			degrees[start] += 1
			degrees[end] += 1

		ratio = line_count / float(max(curve_count, 1e-6))

		return [order, size, np.mean(degrees), line_count, curve_count, ratio]

if __name__ == '__main__':
	makeplots()