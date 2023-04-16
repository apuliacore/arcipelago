from arcipelago.db import init_db
from arcipelago.config import development


def main():
	init_db(development)
	print("Initialized database.")


if __name__ == '__main__':
	main()
