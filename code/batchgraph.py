import makegraph as m
import os
from config import *
from subprocess import call

base = ".."

for font in fonts:
	in_path = img_dir + font
	dot_base = gviz_dir + font + "/"
	dot_img_base = dot_base + "img/"

	mkdirnotex(graph_dir + font + "/")
	mkdirnotex(dot_base)
	mkdirnotex(dot_img_base)

	for filename in os.listdir(in_path):
		no_ext = filename.split(".")[0]
		with open(graph_dir + font + "/" + no_ext, "w+") as out:
			dot_out = dot_base + no_ext + ".gv"
			dot_img = dot_img_base + no_ext + ".png"

			print "making", font, "--", no_ext
			m.makegraph(
				in_path + "/" + filename, output=out,
				dotfile=dot_out)
			call(["dot", "-Tpng", "-o", dot_img, dot_out])