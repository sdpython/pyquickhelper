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
    from pyquickhelper.pycode import skipif_appveyor, ExtTestCase


class TestDocumentationServer(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    @skipif_appveyor("does not end")
    def test_server_start_run(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        data = os.path.join(path, "data")

        server = 'localhost'
        thread = run_doc_server(server, {"pyquickhelper": data},
                                True, port=8094)

        url = "http://localhost:8094/pyquickhelper/"
        cont = get_url_content(url)
        self.assertNotEmpty(cont)
        self.assertIn("GitHub/pyquickhelper</a>", cont)
        fLOG("-------")
        url = "http://localhost:8094/pyquickhelper/search.html?q=flog&check_keywords=yes&area=default"
        cont = get_url_content(url)
        self.assertNotEmpty(cont)
        self.assertIn("Please activate JavaScript to enable the search", cont)
        self.assertIn("http://sphinx.pocoo.org/", cont)

        cont = get_url_content(url, True)
        self.assertNotEmpty(cont)
        self.assertIn("Please activate JavaScript to enable the search", cont)
        self.assertIn("http://sphinx.pocoo.org/", cont)

        thread.shutdown()
        if thread.is_alive():
            fLOG("thread is still alive?", thread.is_alive())
            assert False


if __name__ == "__main__":
    unittest.main()
