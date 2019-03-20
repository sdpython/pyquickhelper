"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import re

from pyquickhelper.loghelper import fLOG
from pyquickhelper.jenkinshelper.jenkins_server import JenkinsExt
from pyquickhelper.jenkinshelper.jenkins_helper import default_engines, setup_jenkins_server_yml


class TestYamlJenkins2Scheduler(unittest.TestCase):

    def test_jenkins_ext_setup_server_yaml2_url_scheduler(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self._jenkins_ext_setup_server_yaml2()

    def _jenkins_ext_setup_server_yaml2(self):
        srv = JenkinsExt(
            "http://localhost:8080/", "user", "password", mock=True,
            engines=default_engines(platform="win32"), fLOG=fLOG, platform="win32")

        fLOG("---------------------")
        this = os.path.abspath(os.path.dirname(__file__))
        local_file = os.path.join(this, "data", ".local.jenkins.win2.yml")
        modules = [('yml', local_file, None)]

        fLOG("[modules]", modules)
        res = setup_jenkins_server_yml(srv, github="sdpython", modules=modules,
                                       overwrite=True, add_environ=False,
                                       location="anything")
        reg = re.compile("<description>(.*)</description>")
        sch = 0
        for i, r in enumerate(res):
            conf = r[-1]

            if not conf.startswith("<?xml version='1.0' encoding='UTF-8'?>"):
                raise Exception(conf)

            search = reg.search(conf)
            if not search:
                raise Exception(conf)

            job = r[0]
            fLOG(search.groups()[0], "--", job, "--", r[1])

            if "PYQUICKHELPER27" in conf:
                raise Exception(conf)

            if "SET VERSION=" not in conf:
                raise Exception(conf)
            if "SET NAME=" not in conf:
                raise Exception(conf)
            if "SET DIST=" not in conf:
                raise Exception(conf)
            if "10 10 * * *" in conf:
                sch += 1

        self.assertEqual(sch, 1)


if __name__ == "__main__":
    unittest.main()
