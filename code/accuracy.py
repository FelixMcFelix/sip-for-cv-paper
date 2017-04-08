from config import *
import argparse

def get_accuracy(filename, print_ans=False):
	total = 0
	correct = 0

	with open(filename) as infile:
		for line in infile:
			total += 1
			line = line.strip()

			correct += int(line.split(" ")[-1])

	ans = float(correct)/total

	if print_ans:
		print ans

	return ans

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="")
	parser.add_argument("input",
						help="Filename of classifier output.")
	args = parser.parse_args()
	get_accuracy(args.input, True)