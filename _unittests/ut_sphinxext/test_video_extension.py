"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
import warnings
import logging
import shutil
from io import StringIO
from docutils.parsers.rst import directives

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase, is_travis_or_appveyor
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import VideoDirective
from pyquickhelper.helpgen.sphinxm_custom_app import CustomSphinxApp
from pyquickhelper.helpgen.sphinx_main_helper import compile_latex_output_final
from pyquickhelper.helpgen.conf_path_tools import find_latex_path


class TestVideoExtension(ExtTestCase):

    def setUp(self):
        logger = logging.getLogger('gdot')
        logger.disabled = True

    def test_post_parse_sn(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("video", VideoDirective)

    def test_video(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. video:: myvideo.mp4
                        :width: 10
                        :height: 20

                    after

                    this code shoud appear
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        logger2 = logging.getLogger("video")

        log_capture_string = StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.DEBUG)
        logger2.addHandler(ch)
        with warnings.catch_warnings(record=True):
            html = rst2html(content,  # fLOG=fLOG,
                            writer="custom", keep_warnings=True,
                            directives=None)

        warns = log_capture_string.getvalue().strip("\n\r\t ")
        if len(warns) != 0 and 'Unable to find' not in warns:
            raise Exception("warnings '{0}'".format(warns))

        t1 = "this code shoud not appear"
        if t1 in html:
            raise Exception(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "myvideo.mp4"
        if t1 not in html:
            raise Exception(html)

        t1 = "linkedin"
        if t1 in html:
            raise Exception(html)

        t1 = "unable to find"
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_video")
        with open(os.path.join(temp, "out_video.html"), "w", encoding="utf8") as f:
            f.write(html)

    def setup_format(self, temp):
        src_ = os.path.join(temp, "..", "data", "video")
        v1 = os.path.join(temp, "..", "data", "video", "mur.mp4")
        v2 = os.path.join(temp, "..", "data", "video", "jol", "mur2.mp4")
        if not os.path.exists(v2):
            shutil.copy(v1, v2)
        fold = os.path.join(temp, "..", "data", "video", "jol", 'im')
        if not os.path.exists(fold):
            os.mkdir(fold)
        v3 = os.path.join(temp, "..", "data", "video", "jol", 'im', "mur3.mp4")
        if not os.path.exists(v3):
            shutil.copy(v1, v3)
        return src_

    def test_sphinx_ext_video_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_sphinx_ext_video_html")

        src_ = self.setup_format(temp)
        app = CustomSphinxApp(src_, temp)
        app.build()

        index = os.path.join(temp, "index.html")
        self.assertExists(index)
        with open(index, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("unable to find", content)
        index = os.path.join(temp, "mur.mp4")
        self.assertExists(index)
        index = os.path.join(temp, "jol", "mur2.mp4")
        self.assertExists(index)
        index = os.path.join(temp, "jol", 'im', "mur3.mp4")
        self.assertExists(index)

    def test_sphinx_ext_video_rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_sphinx_ext_video_rst")

        src_ = self.setup_format(temp)
        app = CustomSphinxApp(src_, temp, buildername="rst")
        app.build()

        index = os.path.join(temp, "index.rst")
        self.assertExists(index)
        with open(index, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("unable to find", content)
        self.assertIn('.. video', content)
        index = os.path.join(temp, "mur.mp4")
        self.assertExists(index)
        index = os.path.join(temp, "jol", "mur2.mp4")
        self.assertExists(index)
        index = os.path.join(temp, "jol", 'im', "mur3.mp4")
        self.assertExists(index)

    def test_sphinx_ext_video_latex(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_sphinx_ext_video_latex")

        fLOG('custom app init')
        src_ = self.setup_format(temp)
        app = CustomSphinxApp(src_, temp, buildername="latex")
        fLOG('custom app build')
        app.build()
        fLOG('custom app done')

        index = os.path.join(temp, "pyq-video.tex")
        self.assertExists(index)
        with open(index, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("unable to find", content)
        self.assertIn('mur.mp4}', content)
        index = os.path.join(temp, "mur.mp4")
        self.assertExists(index)
        index = os.path.join(temp, "jol", "mur2.mp4")
        self.assertExists(index)
        index = os.path.join(temp, "jol", 'im', "mur3.mp4")
        self.assertExists(index)

        if is_travis_or_appveyor() not in ('travis', 'appveyor'):
            latex = find_latex_path()
            fLOG("latex-compile", latex)
            compile_latex_output_final(temp, latex, doall=True)
            fLOG("compilatione done")
            index = os.path.join(temp, "pyq-video.pdf")
            self.assertExists(index)

    def test_sphinx_ext_video_text(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_sphinx_ext_video_text")
        src_ = self.setup_format(temp)
        app = CustomSphinxApp(src_, temp, buildername="text")
        app.build()

        index = os.path.join(temp, "index.txt")
        self.assertExists(index)
        with open(index, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("unable to find", content)
        self.assertIn('mur.mp4', content)
        index = os.path.join(temp, "mur.mp4")
        self.assertExists(index)
        index = os.path.join(temp, "jol", "mur2.mp4")
        self.assertExists(index)
        index = os.path.join(temp, "jol", 'im', "mur3.mp4")
        self.assertExists(index)

    def test_video_url(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. video:: http://www.xavierdupre.fr/ensae/video_hackathon_ensae_ey_label_emmaus_2017.mp4
                        :width: 300

                    after

                    this code shoud appear
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        logger2 = logging.getLogger("video")

        log_capture_string = StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.DEBUG)
        logger2.addHandler(ch)
        with warnings.catch_warnings(record=True):
            html = rst2html(content,  # fLOG=fLOG,
                            writer="custom", keep_warnings=True,
                            directives=None)

        warns = log_capture_string.getvalue().strip("\n\r\t ")
        if len(warns) != 0 and 'Unable to find' not in warns:
            raise Exception("warnings '{0}'".format(warns))

        t1 = "this code shoud not appear"
        if t1 in html:
            raise Exception(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "video_hackathon_ensae_ey_label_emmaus_2017.mp4"
        if t1 not in html:
            raise Exception(html)

        t1 = "unable to find"
        if t1 in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_video_url")
        with open(os.path.join(temp, "out_video.html"), "w", encoding="utf8") as f:
            f.write(html)


if __name__ == "__main__":
    unittest.main()
