"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "This file should not be imported in that location: '{0}'.".format(
            os.path.abspath(__file__)))

from pyquickhelper.filehelper import FileTreeNode
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.helpgen.utils_sphinx_doc import filecontent_to_rst, replace_relative_import_fct


class TestFileNodeTree(ExtTestCase):

    def test_file_tree_node(self):
        this = os.path.abspath(os.path.dirname(__file__))
        folder = os.path.normpath(os.path.join(this, "..", "..", "src"))

        def filter(root, path, f, d):
            return "__pycache__" not in path and "__pycache__" not in f

        ftn = FileTreeNode(folder, log=True, log1=True,
                           filter=filter)
        if len(ftn) == 2:
            raise Exception("%d" % len(ftn))
        nb = 0
        nrst = 0
        for f in ftn:
            if f.isfile():
                hash = f.hash_md5_readfile()
                s = str(f)
                self.assertNotEmpty(s)
                self.assertNotEmpty(hash)
                nb += 1
                if nb > 15:
                    break
                if "cli_helper.py" in f.name:
                    continue

                if "__init__" not in f.name and ".py" in f.name and ".pyc" not in f.name \
                        and "__main__" not in f.name:
                    content = f.get_content()
                    rst = filecontent_to_rst(f.fullname, content)
                    contr, doc = rst
                    nrst += 1
                    self.assertNotIn("no documentation", doc)
                    self.assertIn(".. _f-", contr)

                    try:
                        cont2 = replace_relative_import_fct(f.fullname)
                    except ValueError as e:
                        raise ValueError(
                            "Unable to process '{}'.".format(f.fullname)) from e
                    lines = cont2.split("\n")
                    condition = "# replace # from ." in cont2
                    if not condition:
                        for line in lines:
                            if "from ." in line and "import" in line:
                                doc = "\n-------------DOC--------\n" + doc
                                raise Exception(
                                    "{0}\nLINE:\n{1}\n-------CONT---------:\n{2}{3}".format(
                                        f.fullname, line, cont2, doc))

        self.assertGreater(nb, 0)
        self.assertGreater(nrst, 0)


if __name__ == "__main__":
    unittest.main()
