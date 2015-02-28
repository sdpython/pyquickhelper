"""
@brief      test log(time=8s)
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.helpgen.convert_doc_helper import rst2html, docstring2html
from src.pyquickhelper import df2rst

from IPython.core.display import HTML
import pandas


class TestConvertDocHelper(unittest.TestCase):

    def test_rst2html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        rst = """
            run the server

            :param      server:      if None, it becomes ``HTTPServer(('localhost', 8080), DocumentationHandler)``
            :param      mappings:    prefixes with local folders (dictionary)
            :param      thread:      if True, the server is run in a thread
                                    and the function returns right away,
                                    otherwise, it runs the server.

            :param      port:        port to use
            :return:                 server if thread is False, the thread otherwise (the thread is started)



            .. _le-documentation_server-l551:

            .. _le-runalocalserverwhichservesthedocumentation:

            **Example: run a local server which serves the documentation**

            .. example(run a local server which serves the documentation;;le-documentation_server-l551).

            The following code will create a local server: `http://localhost:8079/pyquickhelper/ <http://localhost:8079/pyquickhelper/>`_.

            ::


                this_fold = os.path.dirname(pyquickhelper.serverdoc.documentation_server.__file__)
                this_path = os.path.abspath( os.path.join( this_fold, "..", "..", "..", "dist", "html") )
                run_doc_server(None, mappings = { "pyquickhelper": this_path } )


            The same server can serves more than one project.
            More than one mappings can be sent.
            .. endexample.
        """
        html = rst2html(rst, fLOG=fLOG)
        assert len(html) > 0
        assert "example(run a local server which serves" in html

    def test_doctring2html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        html = docstring2html(df2rst, False, fLOG=fLOG)
        assert len(html) > 0
        assert "<p>&#64;code" not in html
        html = docstring2html(df2rst, True, fLOG=fLOG)
        assert isinstance(html, HTML)

    def test_doctring2html_pandas(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        html = docstring2html(pandas.read_csv, False, fLOG=fLOG)
        assert len(html) > 0

    def test_doctring2html_sklearn(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        try:
            import sklearn.linear_model
        except ImportError:
            return
        html = docstring2html(
            sklearn.linear_model.LogisticRegression,
            False,
            fLOG=fLOG)
        assert len(html) > 0
        if '<div class="system-message">' in html:
            raise Exception(html)


if __name__ == "__main__":
    unittest.main()
