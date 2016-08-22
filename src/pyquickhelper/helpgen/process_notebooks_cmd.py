"""
@file
@brief Calls nbconvert in command line for latex and pdf
"""
import sys
from nbconvert.nbconvertapp import main as nbconvert_main


def run_nbconvert(argv):
    nbconvert_main(argv=argv)


def main():
    run_nbconvert(sys.argv[1:])


if __name__ == "__main__":
    main()
