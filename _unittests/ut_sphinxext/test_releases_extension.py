"""
@brief      test log(time=4s)
@author     Xavier Dupre
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.helpgen import rst2html

if sys.version_info[0] == 2:
    from codecs import open


class TestReleasesExtension(unittest.TestCase):

    def test_releases(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_sharenet not run on Python 2.7")
            return

        from docutils import nodes as skip_

        content = """
                    =======
                    History
                    =======

                    * :release:`1.5.2050 <2017-09-01>`
                    * :bug:`46`: update to Sphinx 1.6
                    * :bug:`54`: fix searchbox for `sphinx_rtd_theme <https://github.com/rtfd/sphinx_rtd_theme>`_
                    * :feature:`56`: support function for role epkg
                    * :feature:`36`: add support for sphinx-gallery
                    * :feature:`53`: handle history, converts the file into something usable by module releases
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="html", keep_warnings=True,
                        directives=None, layout="sphinx",
                        releases_release_uri="https://pypi.python.org/pypi/pyquickhelper/%s",
                        releases_issue_uri="https://github.com/sdpython/pyquickhelper/issues/%s",
                        releases_document_name="<<string>>")

        t1 = "this code shoud not appear"
        if t1 in html:
            raise Exception(html)

        t1 = 'href="https://github.com/rtfd/sphinx_rtd_theme'
        if t1 not in html:
            raise Exception(html)

        t1 = "update to Sphinx 1.6</p></li>"
        if t1 not in html:
            raise Exception(html)

        t1 = "https://github.com/sdpython/pyquickhelper/issues/53"
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_releases")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)


if __name__ == "__main__":
    unittest.main()
