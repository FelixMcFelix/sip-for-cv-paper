import makegraph as m
import os
import csv
from config import *
from subprocess import call

def make_graphs():
	print "Font graphs:"
	for font in fonts:
		in_path = img_dir + font

		dot_base = gviz_dir + font + "/"
		dot_img_base = dot_base + "img/"

		dual_dot_base = gviz_dir + dual_suffix + font + "/"
		dual_dot_img_base = dual_dot_base + "img/"

		mkdirnotex(graph_dir + font + "/")
		mkdirnotex(graph_dir + dual_suffix + font + "/")
		mkdirnotex(dot_base)
		mkdirnotex(dot_img_base)
		mkdirnotex(dual_dot_base)
		mkdirnotex(dual_dot_img_base)

		for filename in os.listdir(in_path):
			no_ext = filename.split(".")[0]
			with open(graph_dir + font + "/" + no_ext, "w+") as out:
				with open(graph_dir + dual_suffix + font + "/" + no_ext, "w+") as dual_out:
					dot_out = dot_base + no_ext + ".gv"
					dot_img = dot_img_base + no_ext + ".png"

					dual_dot_out = dual_dot_base + no_ext + ".gv"
					dual_dot_img = dual_dot_img_base + no_ext + ".png"

					print "making", font, "--", no_ext
					m.makegraph(
						in_path + "/" + filename, output=out, dual_output=dual_out,
						dotfile=dot_out, dual_dotfile=dual_dot_out)

					call(["dot", "-Tpng", "-o", dot_img, dot_out])
					call(["dot", "-Tpng", "-o", dual_dot_img, dual_dot_out])

	print "Online Data Graphs:"
	for dset in datasets:
		for r in pen_rads:
			for split in splits:
				in_path = "{}{}/r-{}/{}/".format(img_dir, dset, r, split)

				dot_base = "{}{}/r-{}/{}/".format(gviz_dir, dset, r, split)
				dot_img_base = dot_base + "img/"

				dual_dot_base = "{}{}{}/r-{}/{}/".format(gviz_dir, dual_suffix, dset, str(r), split)
				dual_dot_img_base = dual_dot_base + "img/"

				mkdirnotex(graph_dir + dset + "/r-" + str(r) + "/" + split + "/")
				mkdirnotex(graph_dir + dual_suffix + dset + "/r-" + str(r) + "/" + split + "/")
				mkdirnotex(dot_base)
				mkdirnotex(dot_img_base)
				mkdirnotex(dual_dot_base)
				mkdirnotex(dual_dot_img_base)

				for size in dataset_sizes:
					with open("{}{}/{}-{}-smrt.csv".format(img_dir, dset, split, size)) as csvfile:
						rdr = csv.reader(csvfile)

						for filename, classification in rdr:
							no_ext = filename.split(".")[0]
							with open(graph_dir + dset + "/r-" + str(r) + "/" + split + "/" + no_ext, "w+") as out:
								with open(graph_dir + dual_suffix + dset + "/r-" + str(r) + "/" + split + "/" + no_ext, "w+") as dual_out:
									dot_out = dot_base + no_ext + ".gv"
									dot_img = dot_img_base + no_ext + ".png"

									dual_dot_out = dual_dot_base + no_ext + ".gv"
									dual_dot_img = dual_dot_img_base + no_ext + ".png"

									print "making", "{}-{}/{}/".format(dset,r,split), "--", no_ext
									m.makegraph(
										in_path + "/" + filename, output=out, dual_output=dual_out,
										dotfile=dot_out, dual_dotfile=dual_dot_out)

									call(["dot", "-Tpng", "-o", dot_img, dot_out])
									call(["dot", "-Tpng", "-o", dual_dot_img, dual_dot_out])


if __name__ == "__main__":
	make_graphs()