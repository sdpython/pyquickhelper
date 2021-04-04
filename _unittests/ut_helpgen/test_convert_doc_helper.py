"""
@brief      test log(time=2s)
@author     Xavier Dupre

For some reason, the test fails if it is run after another one:
*test_app_sphinx*.
"""

import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.helpgen.rst_converters import rst2html, docstring2html
from pyquickhelper.pandashelper import df2rst

from IPython.core.display import HTML
import pandas


class TestConvertDocHelper(ExtTestCase):
    """
    Tests function rst2html.
    """

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


                this_fold = os.path.dirname(pyquickhelper.server.documentation_server.__file__)
                this_path = os.path.abspath( os.path.join( this_fold, "..", "..", "..", "dist", "html") )
                run_doc_server(None, mappings = { "pyquickhelper": this_path } )


            The same server can serves more than one project.
            More than one mappings can be sent.

            .. endexample.
        """
        html = rst2html(rst)
        self.assertNotEmpty(html)
        if ".. endexample." in html:
            raise Exception(html)
        if ".. example" in html:
            raise Exception(html)
        if "</pre>" not in html:
            raise Exception(html)

    def test_doctring2html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        html = docstring2html(df2rst, "rawhtml")
        self.assertNotEmpty(html)
        self.assertNotIn("<p>&#64;code", html)
        html = docstring2html(df2rst, "html")
        self.assertIsInstance(html, HTML)

    def test_object(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        class AA:
            """one doc"""

            def __init__(self):
                """constructor"""
                pass

            @property
            def g(self):
                """g"""
                return ""

            @staticmethod
            def st():
                """st"""
                return ""

        rst = docstring2html(pandas)
        self.assertNotEmpty(rst)
        rst = docstring2html(AA)
        self.assertNotEmpty(rst)
        rst = docstring2html(3)
        self.assertNotEmpty(rst)
        rst = docstring2html(AA().__class__)
        self.assertNotEmpty(rst)
        rst = docstring2html(AA.__init__)
        self.assertNotEmpty(rst)
        rst = docstring2html(AA.g)
        self.assertNotEmpty(rst)
        rst = docstring2html(AA.st)
        self.assertNotEmpty(rst)
        rst = docstring2html(self)
        self.assertNotEmpty(rst)


if __name__ == "__main__":
    unittest.main()
