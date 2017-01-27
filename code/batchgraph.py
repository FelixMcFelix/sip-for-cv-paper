import makegraph as m
import os

from subprocess import call

def mkdirnotex(filename):
	folder=os.path.dirname(filename)
	if not os.path.exists(folder):
		os.makedirs(folder)

categories = [
	"dejavu-sans"
]

base = ".."
img_dir = "/imgs/"
graphs_dir = "/graphs/"
graphviz_dir = "/graphviz/"

for cat in categories:
	in_path = base + img_dir + cat
	dot_base = base + graphviz_dir + cat + "/"
	dot_img_base = dot_base + "img/"

	mkdirnotex(base + graphs_dir + cat)
	mkdirnotex(dot_base)
	mkdirnotex(dot_img_base)

	for filename in os.listdir(in_path):
		no_ext = filename.split(".")[0]
		out = open(base + graphs_dir + cat + "/" + no_ext, "w+")

		dot_out = dot_base + no_ext + ".dot"
		dot_img = dot_img_base + no_ext + ".png"

		m.makegraph(
			in_path + "/" + filename, output=out,
			dotfile=dot_out)
		call(["dot", "-Tpng", "-o", dot_img, dot_out])