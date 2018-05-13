"""
@brief      test log(time=6s)
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

from src.pyquickhelper.loghelper import fLOG, CustomLog
from src.pyquickhelper.helpgen import process_notebooks
from src.pyquickhelper.pycode import skipif_travis, skipif_appveyor, get_temp_folder, ExtTestCase


if sys.version_info[0] == 2:
    from codecs import open


class TestNoteBooksBugVideo(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    @skipif_travis('latex')
    @skipif_appveyor('latex')
    def test_notebook_video(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # does not work on Python 2
            return
        formats = ["pdf", "rst"]
        temp = get_temp_folder(__file__, "temp_nb_bug_video")
        nbs = [os.path.join(temp, '..', 'data', 'video_notebook.ipynb')]
        clog = CustomLog(temp)
        clog("test_notebook_rst_audio")

        clog("process_notebooks: begin")
        process_notebooks(nbs, temp, temp, formats=formats, fLOG=clog)
        clog("process_notebooks: end")

        name = os.path.join(temp, "video_notebook.tex")
        clog("final checking", name)
        with open(name, "r", encoding="utf8") as f:
            content = f.read()
        clog("final read", name)
        exp = "<moviepy.video.io.html\\_tools.HTML2 object>"
        if exp not in content:
            raise Exception(content)

        name = os.path.join(temp, "video_notebook.rst")
        clog("final checking", name)
        with open(name, "r", encoding="utf8") as f:
            content = f.read()
        clog("final read", name)
        exp = ".. raw:: html"
        if exp not in content:
            raise Exception(content)
        clog("done")


if __name__ == "__main__":
    unittest.main()
