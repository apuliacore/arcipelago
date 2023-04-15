import argparse
from arcipelago.db import init_db
from arcipelago.config import development


def main():
	init_db(development)
	print("Initialized database.")


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--dummy', action='store_true')
	args = parser.parse_args()
	main(args)
