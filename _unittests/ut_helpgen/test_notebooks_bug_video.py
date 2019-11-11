"""
@brief      test log(time=6s)
@author     Xavier Dupre
"""

import os
import unittest
import shutil
from pyquickhelper.loghelper import fLOG, CustomLog
from pyquickhelper.helpgen.sphinx_main import process_notebooks
from pyquickhelper.pycode import skipif_travis, skipif_appveyor, get_temp_folder, ExtTestCase


class TestNoteBooksBugVideo(ExtTestCase):

    @skipif_travis('latex')
    @skipif_appveyor('latex')
    def test_notebook_video(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        formats = ["pdf", "rst"]
        temp = get_temp_folder(__file__, "temp_nb_bug_video")
        nbs = [os.path.join(temp, '..', 'data', 'video_notebook.ipynb')]
        clog = CustomLog(temp)
        clog("test_notebook_rst_audio")

        fold = 'static'
        if not os.path.exists(fold):
            os.mkdir(fold)
        for tpl in ['article']:
            sty = os.path.join(fold, '%s.tplx' % tpl)
            sr = os.path.join(temp, '..', 'data', '%s.tplx' % tpl)
            if not os.path.exists(sr):
                raise FileNotFoundError(sr)
            if not os.path.exists(sty):
                shutil.copy(sr, fold)
            if not os.path.exists('%s.tplx' % tpl):
                shutil.copy(sr, '.')

        clog("process_notebooks: begin")
        process_notebooks(nbs, temp, temp, formats=formats, fLOG=clog)
        clog("process_notebooks: end")

        name = os.path.join(temp, "video_notebook.rst")
        clog("final checking", name)
        with open(name, "r", encoding="utf8") as f:
            content = f.read()
        clog("final read", name)
        exp = ".. raw:: html"
        if exp not in content:
            raise Exception(content)

        clog("done")
        name = os.path.join(temp, "video_notebook.tex")
        clog("final checking", name)
        with open(name, "r", encoding="utf8") as f:
            content = f.read()
        clog("final read", name)
        exp = "<moviepy.video.io.html\\_tools.HTML2 object>"
        if exp not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
