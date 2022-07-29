"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import (
    get_default_extensions, get_default_standard_extensions)
from pyquickhelper.helpgen.utils_sphinx_doc import private_migrating_doxygen_doc
from pyquickhelper.helpgen._fake_function_to_documentation import (
    f1, f2, f3, f4, f5, f6)


class TestStyleDoc(ExtTestCase):

    def test_docstyle(self):
        extensions = get_default_standard_extensions() + get_default_extensions()
        extensions = [_ for _ in extensions if "matplotlib" not in _ and
                      "images" not in _ and "IPython" not in _ and
                      "nbsphinx" not in _ and "jupyter" not in _ and
                      "inheritance_diagram" not in _]
        external_docnames = [
            "_modules/src/pyquickhelper/helpgen/_fake_function_to_documentation"]
        funcs = [None, f1, f2, f3, f4, f5, f6]

        exps = [" * **a** -- parameter a",
                ":param      a:",
                ":param a:",
                "a: parameter a"]

        for i in range(1, 7):
            content = ".. autofunction:: pyquickhelper.helpgen._fake_function_to_documentation.f{0}".format(
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
                if len(filt) == 0 and __name__ == '__main__':
                    print("\n---- ORIGINAL", i, "\n", funcs[i].__doc__,
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
