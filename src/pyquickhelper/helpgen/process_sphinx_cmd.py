"""
@file
@brief Calls nbconvert in command line for latex and pdf
"""
import sys

try:
    from sphinx.cmd.build import main as build_main
except ImportError:
    # Sphinx >= 1.7
    from sphinx import build_main


def run_sphinx_build(argv):
    build_main(argv=argv[1:])


def main():
    run_sphinx_build(sys.argv)


if __name__ == "__main__":
    main()
