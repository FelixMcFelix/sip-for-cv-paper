from config import *
from subprocess import call

for font, name in zip(fonts, fontpaths):
	mkdirnotex("{}{}/".format(img_dir, font))
	for char in chars:
		call([
			"magick",
			"-background", "white",
			"-fill", "black",
			"-font", font_dir + name,
			"-pointsize", "300",
			"label:{}".format(char.split("-up")[0]),
			"{}{}/{}.png".format(img_dir, font, char)])