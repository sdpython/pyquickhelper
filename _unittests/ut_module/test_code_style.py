"""
@brief      test log(time=0s)
"""

import sys
import os
import unittest
import warnings


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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import check_pep8


class TestCodeStyle(unittest.TestCase):

    def test_style_src(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2 or "Anaconda" in sys.executable \
                or "condavir" in sys.executable:
            warnings.warn(
                "skipping test_code_style because of Python 2 or " + sys.executable)
            return

        thi = os.path.abspath(os.path.dirname(__file__))
        src_ = os.path.normpath(os.path.join(thi, "..", "..", "src"))
        check_pep8(src_, fLOG=fLOG, skip=["ftp_transfer_files.py:373: [E731]",
                                          "_nbconvert_config.py:",
                                          "convert_doc_sphinx_helper.py:31: [E402]",
                                          "magic_class.py:12: [E402]"])

    def test_style_test(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2 or "Anaconda" in sys.executable \
                or "condavir" in sys.executable:
            warnings.warn(
                "skipping test_code_style because of Python 2 or " + sys.executable)
            return

        thi = os.path.abspath(os.path.dirname(__file__))
        test = os.path.normpath(os.path.join(thi, "..", ))
        check_pep8(test, fLOG=fLOG, neg_filter="temp_.*",
                   skip=["src' imported but unused",
                         "skip_' imported but unused",
                         "skip__' imported but unused",
                         "skip___' imported but unused",
                         "2test_download_pip.py",
                         "[E402] module ",
                         ])


if __name__ == "__main__":
    unittest.main()
