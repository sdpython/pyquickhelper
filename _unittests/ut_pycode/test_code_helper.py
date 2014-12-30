"""
@brief      test tree node (time=5s)
"""


import sys, os, unittest, re, shutil, warnings

try :
    import src
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    import src

from src.pyquickhelper import fLOG, remove_extra_spaces, create_visual_diff_through_html_files

class TestCodeHelper(unittest.TestCase):

    def test_synchro_hash (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")

        try :
            import pymyinstall
        except ImportError :
            path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..", "..", "pymyinstall", "src")))
            if path not in sys.path : sys.path.append (path)
            try:
                import pymyinstall
            except ImportError :
                # we skip
                warnings.warn("unable to test TestCodeHelper.test_synchro_hash")
                return

        fold = os.path.abspath(os.path.split(__file__)[0])
        data = os.path.join(fold, "data")
        filename = os.path.join(data, "setup.py.test")
        temp = os.path.join(fold, "temp_code_helper")
        if not os.path.exists(temp) : os.mkdir(temp)
        dest = os.path.join(temp, "setup.py.test")
        if os.path.exists(dest) : os.remove(dest)
        shutil.copy(filename, dest)
        d = remove_extra_spaces(dest)
        fLOG("removed", d)
        assert d > 0
        assert d < 100
        if __name__ == "__main__":
            create_visual_diff_through_html_files(filename, dest,
                        page = os.path.join(temp, "page_diff.html"),
                        encoding=None, browser = True)


if __name__ == "__main__"  :
    unittest.main ()