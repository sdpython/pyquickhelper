"""
@file
@brief Calls nbconvert in command line for latex and pdf
"""
import sys
from sphinx import build_main


def run_sphinx_build(argv):
    build_main(argv=argv)


def main():
    run_sphinx_build(sys.argv)


if __name__ == "__main__":
    main()
