import argparse

def main(input, output):
	print input, output;

	# Step 1: read input image
	# Step 2: threshold
	# Step 3: skeletonize
	# Step 4: connected component analysis
	# Step 5: endpoints, keypoints
	# Step 6: Line/Path detection
	# Step 7: North and Component connection

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="")
	parser.add_argument("input", type=argparse.FileType("r"),
						help="filename of an input character image")
	parser.add_argument("output", nargs="?",
						default=None, type=argparse.FileType("w"),
						help="path of graph output file.")
	args = parser.parse_args()
	main(args.input, args.output)