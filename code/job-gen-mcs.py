import os
import stat
import sys
import glob

def make_exec(filename):
		st = os.stat(filename)
		os.chmod(filename, st.st_mode | 0111)

def mkdirnotex(filename):
	folder = os.path.dirname(filename)
	if not os.path.exists(folder):
		os.makedirs(folder)

# Configure me!
fonts     = ["dejavu-sans"]
timelimit = 300
num_cores = 8

file_dir    = "../graphs/"
results_dir = "../results/mcs/"
prog_name   = "sip-mcs/solve_subgraph_isomorphism"
job_folder  = "jobs/mcs/"

#-----------------------------------------------
def addjobs(chars, font, tasks):
	seen = set()
	outloc = "{}{}/".format(results_dir, font)
	for char1 in chars:
		n1 = char1.split("\\")[-1]
		for char2 in chars:
			n2 = char2.split("\\")[-1]
			if (n2, n1) not in seen:
				outfile = "{}{}.{}".format(outloc, n1, n2)
				tasks.append("{} --format umg_attr --timeout {} sequentialix {} {} > {}\n".format(prog_name, timelimit, nix(char1), nix(char2), outfile))
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
	chars = glob.glob("{}{}\\*".format(file_dir, font))
	addjobs(chars, font, tasks)
	top_tasks.append("mkdir -p ../../{}{}\n".format(results_dir, font))

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

finalout = "{}run_tests.sh".format(job_folder)

f = open(finalout, "wb")
f.writelines(top_tasks)

make_exec(finalout)
