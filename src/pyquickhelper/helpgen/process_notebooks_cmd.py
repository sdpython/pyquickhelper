"""
@file
@brief Calls :epkg:`nbconvert` in command line for latex and pdf.
"""
import sys
try:
    from nbconvert.nbconvertapp import main as nbconvert_main
except AttributeError as e:
    raise ImportError("Unable to import nbconvert") from e


def run_nbconvert(argv):
    nbconvert_main(argv=argv)


def main():
    run_nbconvert(sys.argv[1:])


if __name__ == "__main__":
    main()
