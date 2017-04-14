import os
import stat
import sys
import glob

from config import *

mcs_res_dir = results_dir + "mcs/"
mcs_job_folder = job_folder + "mcs/"
prog_name   = "sip-mcs/solve_subgraph_isomorphism"

#-----------------------------------------------
def addjobs(chars, font, params, subtask_name, tasks, chars2=None, font2=None):
	seen = set()
	outloc = "{}{}-{}/".format(mcs_res_dir, font, subtask_name)
	ds = dual_suffix[:-1]
	outloc_dual = "{}{}{}-{}/".format(mcs_res_dir, dual_suffix, font, subtask_name)

	if chars2 is None:
		chars2 = chars
	if font2 is not None:
		outloc = "{}{}-{}-{}/".format(mcs_res_dir, font, font2, subtask_name)
		outloc_dual = "{}{}{}-{}-{}/".format(mcs_res_dir, dual_suffix, font, font2, subtask_name)

	for char1 in chars:
		c1 = nix(char1)
		n1 = c1.split("/")[-1]
		for char2 in chars2:
			c2 = nix(char2)
			n2 = c2.split("/")[-1]

			# if (n2, n1) not in seen:
			outfile = "{}{}.{}".format(outloc, n1, n2)
			outfile_dual = "{}{}.{}".format(outloc_dual, n1, n2)

			# quick fix

			# string surgery to get dual graphs going.
			c1_dual = "/".join(map(str, c1.split("/")[:-2] + [ds] + c1.split("/")[-2:]))
			c2_dual = "/".join(map(str, c2.split("/")[:-2] + [ds] + c2.split("/")[-2:]))

			tasks.append("{} --format umg_attr --timeout {} {} sequentialix {} {} > {}".format(prog_name, timelimit, params, c1, c2, outfile))
			tasks.append("{} --format umg_attr_lab --timeout {} {} sequentialix {} {} > {}".format(prog_name, timelimit, params, c1_dual, c2_dual, outfile_dual))
			seen.add((n1, n2))

def job_gen_mcs():
	# Store tasks as they arrive
	tasks = []

	top_tasks = [
		"mkdir -p ../../{}".format(mcs_res_dir)
	]

	per_file = [
		'cd ../..'
	]

	# create tasks
	for font in fonts:
		chars = glob.glob("{}{}/*".format(graph_dir, font))
		for param, param_name in params:
			addjobs(chars, font, param, param_name, tasks)
			top_tasks.append("mkdir -p ../../{}{}-{}".format(mcs_res_dir, font, param_name))
			top_tasks.append("mkdir -p ../../{}{}{}-{}".format(mcs_res_dir, dual_suffix, font, param_name))

	for font1, font2 in font_comp:
		chars = glob.glob("{}{}/*".format(graph_dir, font1))
		chars2 = glob.glob("{}{}/*".format(graph_dir, font2))
		for param, param_name in params:
			addjobs(chars, font1, param, param_name, tasks, chars2, font2)
			top_tasks.append("mkdir -p ../../{}{}{}-{}-{}".format(mcs_res_dir, dual_suffix, font1, font2, param_name))

	# now divide tasks up by how many cores there are.
	taskdiv = []
	for i in range(0, num_cores):
		taskdiv.append([])

	print len(tasks)

	for i, task in enumerate(tasks):
		taskdiv[i%num_cores].append(task)

	mkdirnotex(mcs_job_folder)

	for i in range(0, num_cores):
		file = "job_{}.sh".format(i)
		filep = "{}{}".format(mcs_job_folder, file)
		print filep, len(taskdiv[i])
		f = open(filep, "wb")
		f.writelines(liney(per_file))
		f.writelines(liney(taskdiv[i]))
		top_tasks.append("./{} &".format(file))
		make_exec(filep)
		f.close()

	finalout = "{}run_tests.sh".format(mcs_job_folder)

	f = open(finalout, "wb")
	f.writelines(liney(top_tasks))

	make_exec(finalout)


if __name__ == '__main__':
	job_gen_mcs()