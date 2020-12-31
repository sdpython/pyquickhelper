"""
@brief      test log(time=2s)
"""
import sys
import os
import unittest
import re

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import skipif_appveyor
from pyquickhelper.jenkinshelper.jenkins_server import JenkinsExt
from pyquickhelper.jenkinshelper.jenkins_helper import (
    default_engines, default_jenkins_jobs, setup_jenkins_server_yml)


class TestYamlJenkins2(unittest.TestCase):

    @skipif_appveyor("discrepencies with python 3.8 on windows")
    def test_jenkins_ext_setup_server_yaml2_url(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self._jenkins_ext_setup_server_yaml2(True, "win32")

    def test_jenkins_ext_setup_server_yaml2_url_linux(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self._jenkins_ext_setup_server_yaml2(True, "linux")

    def test_jenkins_ext_setup_server_yaml2_local(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self._jenkins_ext_setup_server_yaml2(False, "win32")

    def _jenkins_ext_setup_server_yaml2(self, use_url, platform):
        srv = JenkinsExt(
            "http://localhost:8080/", "user", "password", mock=True,
            engines=default_engines(platform="win32"), fLOG=fLOG, platform=platform)

        fLOG("---------------------")
        modules = default_jenkins_jobs()
        if not use_url:
            this = os.path.abspath(os.path.dirname(__file__))
            if platform == 'win32':
                local_file = os.path.join(
                    this, "data", ".local.jenkins.win.yml")
            else:
                local_file = os.path.join(
                    this, "data", ".local.jenkins.lin.yml")
            modules = [('yml', local_file, 'H H(5-6) * * 0')]
        fLOG("[modules]", modules)
        res = setup_jenkins_server_yml(srv, github="sdpython", modules=modules,
                                       overwrite=True, add_environ=False,
                                       location="anything")
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

            if platform == 'win32':
                if "SET VERSION=" not in conf:
                    raise Exception(conf)
                if "SET NAME=" not in conf:
                    raise Exception(conf)
                if "SET DIST=" not in conf:
                    raise Exception(conf)
            else:
                if "export VERSION=" not in conf:
                    raise Exception(conf)
                if "export NAME=" not in conf:
                    raise Exception(conf)
                if "export DIST=" not in conf:
                    raise Exception(conf)
            if use_url:
                if platform == 'win32' and "anything\\pyquickhelper\\%NAME_JENKINS%" not in conf:
                    raise Exception(conf)
                if platform == 'linux' and "anything/pyquickhelper/$NAME_JENKINS" not in conf:
                    raise Exception(conf)
            if "pyquickhelper_UT_%d%d_std" % sys.version_info[:2] in conf:
                nb += 1
            if "H H(5-6) * * 0" in conf:
                sch += 1
            if "H H(6-7) * * 0" in conf:
                sch += 1

        self.assertTrue(i > 0)
        if use_url:
            if nb == 0:
                raise AssertionError(
                    "############# %s\n#############\n%s" % (
                        "pyquickhelper_UT_%d%d_std" % sys.version_info[:2],
                        "\n##############\n".join(r[-1] for r in res)))
        self.assertEqual(sch, 2)


if __name__ == "__main__":
    TestYamlJenkins2().test_jenkins_ext_setup_server_yaml2_url_linux()
    unittest.main()
