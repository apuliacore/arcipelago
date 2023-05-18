from arcipelago.db import init_db
from arcipelago.config import development
import os


def init_poster_folder():
	poster_folder_name = "./locandine/"
	if not os.path.exists(poster_folder_name):
		os.makedirs(poster_folder_name)
		print("Initialized posters folder.")


def main():
	init_db(development)
	print("Initialized database.")
	init_poster_folder()


if __name__ == '__main__':
	main()
