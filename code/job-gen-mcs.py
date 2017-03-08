import os
import stat
import sys
import glob

from config import *

#-----------------------------------------------
def addjobs(chars, font, params, subtask_name, tasks, chars2=None, font2=None):
	seen = set()
	outloc = "{}{}-{}/".format(results_dir, font, subtask_name)

	if chars2 is None:
		chars2 = chars
	if font2 is not None:
		outloc = "{}{}-{}-{}/".format(results_dir, font, font2, subtask_name)

	for char1 in chars:
		n1 = char1.split("\\")[-1]
		for char2 in chars2:
			n2 = char2.split("\\")[-1]
			# if (n2, n1) not in seen:
			outfile = "{}{}.{}".format(outloc, n1, n2)
			tasks.append("{} --format umg_attr --timeout {} {} sequentialix {} {} > {}\n".format(prog_name, timelimit, params, nix(char1), nix(char2), outfile))
			seen.add((n1, n2))

def nix(string):
	return string.replace("\\", "/")

# Store tasks as they arrive
tasks = []

top_tasks = [
	"mkdir -p ../../{}\n".format(results_dir)
]

per_file = [
	'cd ../..\n'
]

# create tasks
for font in fonts:
	chars = glob.glob("{}{}\\*".format(graph_dir, font))
	for param, param_name in params:
		addjobs(chars, font, param, param_name, tasks)
		top_tasks.append("mkdir -p ../../{}{}-{}\n".format(results_dir, font, param_name))

for font1, font2 in font_comp:
	chars = glob.glob("{}{}\\*".format(graph_dir, font1))
	chars2 = glob.glob("{}{}\\*".format(graph_dir, font2))
	for param, param_name in params:
		addjobs(chars, font1, param, param_name, tasks, chars2, font2)
		top_tasks.append("mkdir -p ../../{}{}-{}-{}\n".format(results_dir, font1, font2, param_name))

# now divide tasks up by how many cores there are.
taskdiv = []
for i in range(0, num_cores):
	taskdiv.append([])

for i, task in enumerate(tasks):
	taskdiv[i%num_cores].append(task)

mkdirnotex(job_folder)

for i in range(0, num_cores):
	file = "job_{}.sh".format(i)
	filep = "{}{}".format(job_folder, file)
	f = open(filep, "wb")
	f.writelines(per_file)
	f.writelines(taskdiv[i])
	top_tasks.append("./{} &\n".format(file))
	make_exec(filep)
	f.close()

finalout = "{}run_tests.sh".format(job_folder)

f = open(finalout, "wb")
f.writelines(top_tasks)

make_exec(finalout)
