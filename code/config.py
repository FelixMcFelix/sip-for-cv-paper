import os
import string

# Configure me!
fonts     = ["dejavu-sans"]
params    = [
	("",               "edgecountinc"),
	("--edge-overlap", "edgecountdec"),
	("--induced",      "induced")
]
timelimit = 300
num_cores = 8

graph_dir   = "../graphs/"
results_dir = "../results/mcs/"
tables_dir  = "../tables/"
prog_name   = "sip-mcs/solve_subgraph_isomorphism"
job_folder  = "jobs/mcs/"

chars = list(string.lowercase) + [c + "-up" for c in string.uppercase]

# ---------------------------------------------------------------------------- #
# Shared functions -- not for config.                                          #
# ---------------------------------------------------------------------------- #

def make_exec(filename):
		st = os.stat(filename)
		os.chmod(filename, st.st_mode | 0111)

def mkdirnotex(filename):
	folder = os.path.dirname(filename)
	if not os.path.exists(folder):
		os.makedirs(folder)