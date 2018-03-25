"""
@brief      test log(time=3s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import shutil

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

from src.pyquickhelper.helpgen.post_process import post_process_rst_output
from src.pyquickhelper.pycode import ExtTestCase, get_temp_folder


if sys.version_info[0] == 2:
    from codecs import open


class TestNotebookPostProcess(ExtTestCase):

    def test_notebook_post_process_audio(self):
        temp = get_temp_folder(__file__, "temp_notebook_post_process_audio")
        data = os.path.join(temp, '..', "data", "exemple_div.rst")
        shutil.copy(data, temp)
        source = os.path.join(temp, "exemple_div.rst")
        post_process_rst_output(source, False, False, False, False, False,
                                is_notebook=True, exc=True, github=False,
                                notebook=None, nblinks=None)
        with open(source, "r", encoding="utf-8") as f:
            content = f.read()
        nb = 0
        for i, line in enumerate(content.split('\n')):
            if line.startswith('<div'):
                raise AssertionError(
                    "Issue with line {0}\n{1}".format(i, line))
            else:
                nb += 1
        self.assertGreater(nb, 0)


if __name__ == "__main__":
    unittest.main()
