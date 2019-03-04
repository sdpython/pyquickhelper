"""
@brief      test log(time=6s)
"""

import sys
import os
import unittest
import re
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

from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase
from src.pyquickhelper.jenkinshelper.jenkins_server import JenkinsExt
from src.pyquickhelper.jenkinshelper.yaml_helper import enumerate_processed_yml


class TestYamlJenkinsBug(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_jenkins_bug_quote(self):
        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "data", ".local.jenkins.lin.bug.yml"))
        self.assertExists(yml)

        github = "https://github.com/sdpython/"

        modules = [("yml", yml, "H H(10-11) * * 0")]

        engines = dict(Python37="/usr/bin/python3.7",
                       Python36="/usr/bin/python3.6",
                       root_path="./rootpath/")
        vers = "%d%d" % sys.version_info[:2]

        srv = JenkinsExt(
            "http://localhost:8080/", "user", "password", mock=True,
            engines=engines, platform="linux")

        res = srv.setup_jenkins_server(github=github, modules=modules,
                                       overwrite=True, add_environ=False,
                                       location="anything", disable_schedule=False,
                                       credentials="")
        res = list(res)
        self.assertEqual(len(res), 4)
        scripts = [''.join(s) for s in res]
        for sc in scripts:
            self.assertNotIn("Python370_x64", sc)
        nb = 0
        for last in scripts:
            self.assertNotIn(
                "$PYINT -c \"from sphinx.cmd.build import build_main\n'", last)
            if "3.6" in last:
                self.assertIn(
                    "export LD_LIBRARY_PATH=/usr/local/Python-3.6.8", last)
            elif "3.7" in last:
                self.assertIn(
                    "export LD_LIBRARY_PATH=/usr/local/Python-3.7.2", last)
            else:
                raise Exception(
                    "Unknown python in job\n----------\n" + last + "\n-------")
            if "NAME=UT" in last:
                self.assertIn(
                    "build_main(['-j2','-v','-T','-b','html','-d','dist/doctrees','_doc','dist/html']", last)
                nb += 1
        self.assertEqual(nb, 1)


if __name__ == "__main__":
    unittest.main()
