import os
import stat
import sys
import glob

from config import *

search_res_dir = results_dir + "search/"
search_job_folder = job_folder + "search/"
prog_name   = "./search_subgraph_isomorphism"

#-----------------------------------------------
def job_gen_search():
	# Store tasks as they arrive
	tasks = []

	top_tasks = [
		"mkdir -p ../../{}".format(search_res_dir)
	]

	per_file = [
		'cd ../../sip-mcs'
	]

	# create tasks
	for font, all_splits, used_splits, size, curve_thres, sep_folders in dsets_inf:
		for param, param_name in params:
			pat_folder = ""
			targ_folder = ""

			if sep_folders:
				# work out pattern locations
				[pat_folder, targ_folder] = [x for x in used_splits]

			csv_p_name = "{}.csv".format(used_splits[0]) if size is None else "{}-{}-smrt.csv".format(used_splits[0], size)
			csv_t_name = "{}.csv".format(used_splits[1]) if size is None else "{}-{}-smrt.csv".format(used_splits[1], size)

			outdir = "{}{}-{}".format(search_res_dir, font, param_name)
			outdir_d = "{}{}{}-{}".format(search_res_dir, dual_suffix, font, param_name)

			if curve_thres:
				csv_loc = "{}{}{}".format(font_dir, washington, washington_spl)
				for t in curve_thr:
					folder = "{}-{}/".format(font, t)
					dual_f = dual_suffix + folder

					# ./search_subgraph_isomorphism ../../graphs/dual/hwrt/r-1/test ../../imgs/hwrt/test-4000-smrt.csv ../../graphs/dual/hwrt/r-1/train ../../imgs/hwrt/train-4000-smrt.csv --format umg_attr_lab --induced --timeout 10 > test-r1-4000-dual-smrt.out &
					# Add these jobs!

					p_csv = csv_loc + csv_p_name
					p_loc = graph_dir + folder + pat_folder
					p_loc_d = graph_dir + dual_f + pat_folder

					t_csv = csv_loc + csv_t_name
					t_loc = graph_dir + folder + targ_folder
					t_loc_d = graph_dir + dual_f + targ_folder

					out = "{}/{}-{}.out".format(outdir, t, used_splits[0])
					out_d = "{}/{}-{}.out".format(outdir_d, t, used_splits[0])

					tasks.append('{} "../{}" "../{}" "../{}" "../{}" --format umg_attr --timeout {} {} > "../{}"'.format(prog_name, p_loc, p_csv, t_loc, t_csv, search_timelimit, param, out))
					tasks.append('{} "../{}" "../{}" "../{}" "../{}" --format umg_attr_lab --timeout {} {} > "../{}"'.format(prog_name, p_loc_d, p_csv, t_loc_d, t_csv, search_timelimit, param, out_d))
			else:
				csv_loc = "{}{}/".format(img_dir, font)
				for p in pen_rads:
					folder = "{}/r-{}/".format(font, p)
					dual_f = dual_suffix + folder

					# ./search_subgraph_isomorphism ../../graphs/dual/hwrt/r-1/test ../../imgs/hwrt/test-4000-smrt.csv ../../graphs/dual/hwrt/r-1/train ../../imgs/hwrt/train-4000-smrt.csv --format umg_attr_lab --induced --timeout 10 > test-r1-4000-dual-smrt.out &
					# Add these jobs!

					p_csv = csv_loc + csv_p_name
					p_loc = graph_dir + folder + pat_folder
					p_loc_d = graph_dir + dual_f + pat_folder

					t_csv = csv_loc + csv_t_name
					t_loc = graph_dir + folder + targ_folder
					t_loc_d = graph_dir + dual_f + targ_folder

					out = "{}/r{}-{}.out".format(outdir, p, size)
					out_d = "{}/r{}-{}.out".format(outdir_d, p, size)

					tasks.append('{} "../{}" "../{}" "../{}" "../{}" --format umg_attr --timeout {} {} > "../{}"'.format(prog_name, p_loc, p_csv, t_loc, t_csv, search_timelimit, param, out))
					tasks.append('{} "../{}" "../{}" "../{}" "../{}" --format umg_attr_lab --timeout {} {} > "../{}"'.format(prog_name, p_loc_d, p_csv, t_loc_d, t_csv, search_timelimit, param, out_d))
			# addjobs(font, param, param_name, tasks)
			top_tasks.append("mkdir -p ../../{}".format(outdir))
			top_tasks.append("mkdir -p ../../{}".format(outdir_d))

	# now divide tasks up by how many cores there are.
	taskdiv = []
	for i in range(0, num_cores):
		taskdiv.append([])

	for i, task in enumerate(tasks):
		taskdiv[i%num_cores].append(task)

	mkdirnotex(search_job_folder)

	for i in range(0, num_cores):
		file = "job_{}.sh".format(i)
		filep = "{}{}".format(search_job_folder, file)
		f = open(filep, "wb")
		f.writelines(liney(per_file))
		f.writelines(liney(taskdiv[i]))
		top_tasks.append("./{} &".format(file))
		make_exec(filep)
		f.close()

	finalout = "{}run_tests.sh".format(search_job_folder)

	f = open(finalout, "wb")
	f.writelines(liney(top_tasks))

	make_exec(finalout)


if __name__ == '__main__':
	job_gen_search()