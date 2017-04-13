from config import *
from subprocess import call
import os.path as path
import os
import shutil

style_base = "../paper/"
style_files = [
	"gnuplot-lua-tikz.sty",
	"gnuplot-lua-tikz.tex",
	"gnuplot-lua-tikz-common.tex",
	"t-gnuplot-lua-tikz.tex",
]

def copy_files(dir):
	for file in style_files:
		shutil.copyfile(style_base + file, dir + file)

def del_files(dir):
	for file in style_files:
		os.remove(dir + file)

def pdf_plots(dir):
	files = os.listdir(dir)
	copy_files(dir)
	for file in files:
		curr = dir + file
		if path.isdir(curr):
			pdf_plots(curr+"/")
		else:
			if file[-4:] == ".tex":
				call(["pdflatex", "-output-directory", dir, curr])
	del_files(dir)

def top_pdf():
	roots = [tables_dir, plots_dir]

	for root in roots:
		pdf_plots(root)

if __name__ == '__main__':
	top_pdf()