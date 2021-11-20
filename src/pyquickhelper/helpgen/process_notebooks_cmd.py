"""
@file
@brief Calls :epkg:`nbconvert` in command line for latex and pdf.
"""
import sys
import warnings
import traceback

try:
    from nbconvert.nbconvertapp import main as nbconvert_main
except AttributeError as e:
    raise ImportError("Unable to import nbconvert") from e


def run_nbconvert(argv):
    try:
        nbconvert_main(argv=argv)
    except Exception as ee:
        warnings.warn(
            "[run_nbconvert-ERROR] Unable to convert a notebook with "
            "args=%r due to %r\n--CALL-STACK--\n%s." % (
                argv, ee, traceback.format_exc()), RuntimeWarning)


def main():
    run_nbconvert(sys.argv[1:])


if __name__ == "__main__":
    main()
