import os
import string

# Configure me!
fontpaths = [
	"DejaVuSans.ttf",
	"Alegreya.ttf"
]
fonts     = [
	"dejavu-sans",
	"alegreya"
]
params    = [
	("",               "edgecountinc"),
	("--edge-overlap", "edgecountdec"),
	("--induced",      "induced")
]
timelimit = 300
num_cores = 8

img_dir     = "../imgs/"
graph_dir   = "../graphs/"
gviz_dir    = "../graphviz/"
results_dir = "../results/mcs/"
tables_dir  = "../tables/"
font_dir    = "../resources/"
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