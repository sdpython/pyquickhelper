"""
@brief      test log(time=4s)

"""


import sys
import os
import unittest

if sys.version_info[0] == 2:
    pass
else:
    from http.server import HTTPServer as skip_

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

    from pyquickhelper.loghelper import fLOG, get_url_content
    from pyquickhelper.serverdoc import run_doc_server
    from pyquickhelper.pycode import is_travis_or_appveyor


class TestDocumentationServer(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_server_start_run(self):
        if sys.version_info[0] == 2:
            return
        if is_travis_or_appveyor() == "appveyor":
            return

        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        data = os.path.join(path, "data")

        server = 'localhost'
        thread = run_doc_server(
            server, {
                "pyquickhelper": data}, True, port=8094)

        url = "http://localhost:8094/pyquickhelper/"
        cont = get_url_content(url)
        assert len(cont) > 0
        assert "GitHub/pyquickhelper</a>" in cont
        fLOG("-------")
        url = "http://localhost:8094/pyquickhelper/search.html?q=flog&check_keywords=yes&area=default"
        cont = get_url_content(url)
        assert len(cont) > 0
        assert "Please activate JavaScript to enable the search" in cont
        assert "http://sphinx.pocoo.org/" in cont

        cont = get_url_content(url, True)
        assert len(cont) > 0
        assert "Please activate JavaScript to enable the search" in cont
        assert "http://sphinx.pocoo.org/" in cont

        thread.shutdown()
        if thread.is_alive():
            fLOG("thread is still alive?", thread.is_alive())
            assert False


if __name__ == "__main__":
    unittest.main()
