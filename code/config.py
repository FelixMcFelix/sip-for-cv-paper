import os
import string

# Configure me!
fontpaths = [
	"DejaVuSans.ttf",
	"Alegreya.ttf",
	"OpenSans.ttf"
]
fonts     = [
	"dejavu-sans",
	"alegreya",
	"open-sans"
]
font_comp = [
	("dejavu-sans", "alegreya"),
	("alegreya",    "dejavu-sans"),
	("dejavu-sans", "open-sans"),
	("open-sans",    "dejavu-sans")
]
params    = [
	("",               "edgecountinc"),
	("--edge-overlap", "edgecountdec"),
	("--induced",      "induced")
]

datasets  = [
	"hwrt"
]

splits    = [
	"test",
	"train"
]

dataset_sizes = [
	500,
	1000
]

pen_rads  = range(1+4*1, 2 + 4*2, 4)

pen_to_start = {
	# 5: 142741
}

timelimit = 300
num_cores = 8

base = ".."

img_dir     = "../imgs/"
graph_dir   = "../graphs/"
gviz_dir    = "../graphviz/"
dual_suffix = "dual/"
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