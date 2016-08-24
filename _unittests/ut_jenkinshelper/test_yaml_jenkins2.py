"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import re


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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.jenkinshelper.jenkins_server import JenkinsExt
from src.pyquickhelper.jenkinshelper.jenkins_helper import default_engines, default_jenkins_jobs, setup_jenkins_server_yml

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestYamlJenkins2(unittest.TestCase):

    def test_jenkins_ext_setup_server_yaml2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        srv = JenkinsExt(
            "http://localhost:8080/", "user", "password", mock=True,
            engines=default_engines(), fLOG=fLOG)

        fLOG("---------------------")
        res = setup_jenkins_server_yml(srv, github="sdpython", modules=default_jenkins_jobs(),
                                       overwrite=True, add_environ=False,
                                       location="anything", yml_platform="win")
        reg = re.compile("<description>(.*)</description>")
        nb = 0
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
            if "anything\\%NAME_JENKINS%" not in conf:
                raise Exception(conf)
            if "pyquickhelper_UT_35_std" in conf:
                nb += 1
            if "H H(5-6) * * 0" in conf:
                sch += 1
            if "H H(6-7) * * 0" in conf:
                sch += 1

        assert i > 0
        assert nb > 0
        self.assertEqual(sch, 2)


if __name__ == "__main__":
    unittest.main()
