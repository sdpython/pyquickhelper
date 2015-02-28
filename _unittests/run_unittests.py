"""
@file
@brief run all unit tests
"""

import unittest
import os
import sys
import io


def main():
    try:
        import pyquickhelper
    except ImportError:
        sys.path.append(
            os.path.normpath(
                os.path.abspath(
                    os.path.join(
                        os.path.split(__file__)[0],
                        "..",
                        "src"))))
        import pyquickhelper

    from pyquickhelper import fLOG, main_wrapper_tests
    fLOG(OutputPrint=True)
    main_wrapper_tests(__file__)

if __name__ == "__main__":
    main()
