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

curve_thr = [
	1.2,
	1.35,
	1.5,
	1.65
	# 1.7
]

dsets_inf = [
	# font name, split names, automated split names, size?, curve_thres?, seperate folders?
	("hwrt", ["test", "train"], ["test", "train"], 2000, False, True),
	("washington", ["test", "valid", "train"], ["valid", "train"], None, True, False)
]

dataset_sizes = [
	500,
	1000,
	2000,
	4000
]

pen_rads  = range(1+4*0, 2 + 4*2, 4)

pen_to_start = {
	# 5: 142741
}

timelimit = 300
search_timelimit = 30
num_cores = 8

base = ".."

img_dir     = "../imgs/"
graph_dir   = "../graphs/"
gviz_dir    = "../graphviz/"
dual_suffix = "dual/"
results_dir = "../results/"
tables_dir  = "../tables/"
font_dir    = "../resources/"
job_folder  = "jobs/"

washington     = "washington/"
washington_img = "Data/Word_Images_Binarised/01_Skew"
washington_set = "Set/"
washington_spl = "newset/"

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

def nix(string):
	return string.replace("\\", "/")

def liney(arr):
	return [x + "\n" for x in arr]