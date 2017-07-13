"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.sphinxext import get_default_extensions, get_default_standard_extensions
from src.pyquickhelper.helpgen.utils_sphinx_doc import private_migrating_doxygen_doc
from src.pyquickhelper.helpgen._fake_function_to_documentation import f1, f2, f3, f4, f5, f6


class TestStyleDoc(unittest.TestCase):

    def test_docstyle(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        extensions = get_default_standard_extensions() + get_default_extensions()
        external_docnames = [
            "_modules/src/pyquickhelper/helpgen/_fake_function_to_documentation"]
        funcs = [None, f1, f2, f3, f4, f5, f6]

        exps = [" * **a** -- parameter a",
                ":param      a:",
                ":param a:",
                "a: parameter a"]

        for i in range(1, 7):
            content = ".. autofunction:: src.pyquickhelper.helpgen._fake_function_to_documentation.f{0}".format(
                i)
            text = rst2html(content,  # fLOG=fLOG,
                            writer="rst", keep_warnings=True,
                            layout="sphinx", extensions=extensions,
                            external_docnames=external_docnames)
            filt = list(filter(lambda s: s in text, exps))
            if len(filt) == 0:
                doc = funcs[i].__doc__
                rows = doc.split("\n")
                conv = private_migrating_doxygen_doc(rows, 0, "f%d" % i)
                content = "\n".join(conv)
                text2 = rst2html(content,  # fLOG=fLOG,
                                 writer="rst", keep_warnings=True,
                                 layout="sphinx", extensions=extensions,
                                 external_docnames=external_docnames)
                filt = list(filter(lambda s: s in text2, exps))
                if len(filt) == 0:
                    fLOG("\n---- ORIGINAL", i, "\n", funcs[i].__doc__,
                         "\n---- RESULT", i, "\n", text,
                         "\n**** CONVERTED\n", content,
                         "\n**** FINAL", i, "\n", text2,
                         "\n*************** END")
                else:
                    rep = text2.strip("\n ")
                    if not rep.startswith(".."):
                        raise Exception("\n" + text2)


if __name__ == "__main__":
    unittest.main()
