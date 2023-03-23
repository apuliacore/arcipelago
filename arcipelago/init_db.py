import argparse
from db import init_db


def main(args):
	init_db(args.dummy)
	print("Initialized database.")


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--dummy', action='store_true')
	args = parser.parse_args()
	main(args)
