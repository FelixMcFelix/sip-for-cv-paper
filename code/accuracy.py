from config import *
import argparse

def get_accuracy(filename, print_ans=False):
	total = 0
	correct = 0

	truth_labels = {}
	observe_labels = {}

	def incc(labels):
		maps = [truth_labels, observe_labels]
		for l, m in zip(labels, maps):
			if l not in m:
				m[l] = 1
			else:
				m[l] += 1

	def sync(src, targ):
		for label in src:
			if label not in targ:
				targ[label] = 0

	with open(filename) as infile:
		for line in infile:
			total += 1
			line = line.strip()

			[real, observed, good] = [int(x) for x in line.split(" ")[1:]]

			incc([real, observed])

			correct += good

	ans = float(correct)/total

	# kappa stuff
	expt = 0
	sync(truth_labels, observe_labels)
	sync(observe_labels, truth_labels)

	for label in truth_labels:
		truth_occr = truth_labels[label]
		obs_occr = observe_labels[label]

		# print truth_occr, obs_occr

		expt += (truth_occr * obs_occr) / float(total)

	expt /= float(total)

	kappa = (ans - expt) / (1 - expt)

	if print_ans:
		print ans, "k=", kappa

	return ans, kappa

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="")
	parser.add_argument("input",
						help="Filename of classifier output.")
	args = parser.parse_args()
	get_accuracy(args.input, True)