"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import datetime


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
from src.pyquickhelper.filehelper.synchelper import explore_folder
from src.pyquickhelper.loghelper.pyrepo_helper import SourceRepository
import src.pyquickhelper.helpgen.utils_sphinx_doc as utils_sphinx_doc

if sys.version_info[0] == 2:
    from codecs import open


class TestSphinxDoc (unittest.TestCase):

    def test_svn_version(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            return
        s = SourceRepository()
        ver = s.version()
        fLOG("version", ver)
        assert isinstance(ver, int) or isinstance(ver, str)

        try:
            import pysvn
        except ImportError:
            return

        if isinstance(ver, int) and ver <= 3:
            raise Exception("version should be > 100 : " + str(ver))

    def test_svn_logs(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        try:
            import pysvn
        except ImportError:
            return

        src = SourceRepository()
        ver = src.log()
        assert len(ver) > 0
        assert isinstance(ver, list)
        assert len(ver[0]) >= 4
        assert isinstance(ver[0][1], int) or isinstance(ver[0][1], str)
        assert isinstance(ver[0][2], datetime.datetime)
        ver.sort(reverse=True)
        fLOG("logs", "\n" + "\n".join(map(str, ver[:10])))

    def test_sphinx_doc(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.split(__file__)[0]
        file = os.path.join(
            path,
            "..",
            "..",
            "src",
            "pyquickhelper",
            "helpgen",
            "utils_sphinx_doc.py")
        assert os.path.exists(file)

        with open(file, "r", encoding="utf8") as f:
            content = f.read()
        stats, newc = utils_sphinx_doc.migrating_doxygen_doc(content, file)
        snewc = newc[:len(newc) // 2]
        assert "pass" in newc
        assert ":param" in newc
        assert "@param" not in snewc
        assert "docrows" in stats

    def test_sphinx_doc_all(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.split(__file__)[0]
        file = os.path.join(path, "..", "..", "src", "pyquickhelper")
        files = explore_folder(file, pattern=".*[.]py$")[1]
        assert len(files) > 10

        if sys.version_info[0] == 2:
            return

        nb = []
        issue = []
        for fi in files:
            if "run_setup_pause.py" in fi:
                continue
            if "setup.py" not in fi \
                    and utils_sphinx_doc.validate_file_for_help(fi, lambda f: "_externals" in f and ("/test" in f or "\\test" in f)):
                well = fi.replace("\\", "/")
                well = well[well.find("src"):]
                well = os.path.splitext(well)[0]
                well = well.replace("/", ".")

                try:
                    __import__(well)
                except Exception as e:
                    message = [
                        "issues while importing file:" + well + "(" + fi + ")"]
                    message.append(
                        "  File \"%s\", line 1" %
                        os.path.abspath(fi))
                    message.append("if it fails, you should add these lines:")
                    message.append("""
                            try :
                                import rpy2
                            except ImportError :
                                import os,sys
                                path = os.path.normpath(os.path.abspath( \
                                             os.path.join(os.path.split(__file__)[0],"..","..")))
                                sys.path.insert(0,path)
                                import rpy2
                            """.replace("                            ", ""))
                    raise Exception(
                        "error\n" +
                        "\n".join(message) +
                        "\n" +
                        str(e))

            try:
                with open(fi, "r", encoding="utf8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                fLOG("ut: unable to read utf8, file:", fi)
                try:
                    with open(fi, "r") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(fi, "r", encoding="latin1") as f:
                        content = f.read()

            try:
                newc = utils_sphinx_doc.migrating_doxygen_doc(
                    content,
                    fi,
                    silent=True)
            except SyntaxError as e:
                issue.append(
                    ("  File \"%s\", line 1," %
                     fi) +
                    "    issue 1 (unable to migrate through doxygen)")

            if "@param" in newc:
                if "utils_sphinx_doc.py" in fi:
                    continue
                if r"pdf.py" in fi:
                    continue
                if r"_externals\xlrd" in fi or r"_externals/xlrd" in fi:
                    continue
                fLOG("issue with file", fi)
                nb.append(
                    ("  File \"%s\", line 1," %
                     fi) +
                    "    issue 2 (contains @param)")

        for i in issue:
            fLOG("issue (1) with ", i)
            #utils_sphinx_doc.migrating_doxygen_doc(content, i)
        for i in nb:
            fLOG("issue (2) with ", i)
        if len(nb) != 0:
            fLOG("***** issues ", "\n".join(nb))
            raise Exception("issue:\n" + "\n".join(nb))
        if len(issue) != 0:
            fLOG("***** issues ", "\n".join(issue))
            raise Exception("issue:\n" + "\n".join(issue))


if __name__ == "__main__":
    unittest.main()
