"""
@file
@brief Calls :epkg:`nbconvert` in command line for latex and pdf.
"""
import sys
import warnings

try:
    from nbconvert.nbconvertapp import main as nbconvert_main
except AttributeError as e:
    raise ImportError("Unable to import nbconvert") from e


def run_nbconvert(argv):
    try:
        nbconvert_main(argv=argv)
    except Exception as e:
        warnings.warn(
            "[run_nbconvert-ERROR] Unable to to convert a notebook with "
            "args=%r due to %r." % (argv, e), RuntimeWarning)


def main():
    run_nbconvert(sys.argv[1:])


if __name__ == "__main__":
    main()
