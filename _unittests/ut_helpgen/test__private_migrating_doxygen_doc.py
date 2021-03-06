"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.helpgen.utils_sphinx_doc import _private_migrating_doxygen_doc


class TestHelpGenPrivate(unittest.TestCase):
    """First line.
    Second line.
    """

    def test__private_migrating_doxygen_doc(self):
        """First line.
        Second line.

        @param  self        self
        """
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        doc = TestHelpGenPrivate.__doc__.split("\n")
        res = _private_migrating_doxygen_doc(doc, 0, "<test>")
        exp = """
                First line.
                Second line.


                :githublink:`%|py|0`
                """.replace("            ", "")
        self.assertEqual("\n".join(res).strip("\n "), exp.strip("\n "))

        doc = TestHelpGenPrivate.test__private_migrating_doxygen_doc.__doc__.split(
            "\n")
        res = _private_migrating_doxygen_doc(doc, 0, "<test>")
        exp = """
                    First line.
                    Second line.

                    :param  self:        self


                    :githublink:`%|py|0`
                """.replace("            ", "")
        self.assertEqual("\n".join(res).strip("\n "), exp.strip("\n "))


if __name__ == "__main__":
    unittest.main()
