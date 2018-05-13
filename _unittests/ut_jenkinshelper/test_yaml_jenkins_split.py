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
from src.pyquickhelper.jenkinshelper.jenkins_helper import setup_jenkins_server_yml

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestYamlJenkinsSplit(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_jenkins_ext_setup_server_yaml_split(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        engines = {'Python36': 'c:\\Python36_x64',
                   'Python35': 'c:\\Python35_x64'}
        srv = JenkinsExt(
            "http://localhost:8080/", "user", "password", mock=True,
            engines=engines, fLOG=fLOG, platform="win")

        this = os.path.abspath(os.path.dirname(__file__))
        localyml = os.path.abspath(os.path.join(
                                   this, "data", "local.yml"))

        fLOG("---------------------")
        modules = [('yml', localyml, 'H H(5-6) * * 0')]
        res = setup_jenkins_server_yml(srv, github="sdpython", modules=modules,
                                       overwrite=True, add_environ=False,
                                       location="anything")
        reg = re.compile("<description>(.*)</description>")
        assert len(res) > 0
        for i, r in enumerate(res):
            conf = r[-1]

            if not conf.startswith("<?xml version='1.0' encoding='UTF-8'?>"):
                raise Exception(conf)

            search = reg.search(conf)
            if not search:
                raise Exception(conf)

            job = r[0]
            fLOG(search.groups()[0], "--", job, "--", r[1])

            conf = conf.replace("\n", "")
            exp = "</hudson.tasks.BatchFile><hudson.tasks.BatchFile>"
            if exp not in conf:
                raise Exception(conf)

    def test_jenkins_ext_setup_server_yaml_split2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        engines = dict(Python35="py35", Python36="C:\\Python36_x64",
                       Python27="py27", Anaconda3="ana3", Anaconda2="ana2",
                       project_name="pyquickhelper", root_path="ROOT")
        srv = JenkinsExt(
            "http://localhost:8080/", "user", "password", mock=True,
            engines=engines, fLOG=fLOG, platform="win")

        this = os.path.abspath(os.path.dirname(__file__))
        localyml = os.path.abspath(os.path.join(
                                   this, "data", "local2.yml"))

        fLOG("---------------------")
        modules = [('yml', localyml, 'H H(5-6) * * 0')]
        res = setup_jenkins_server_yml(srv, github="sdpython", modules=modules,
                                       overwrite=True, add_environ=False,
                                       location="anything")
        reg = re.compile("<description>(.*)</description>")
        assert len(res) > 0
        for i, r in enumerate(res):
            conf = r[-1]

            if not conf.startswith("<?xml version='1.0' encoding='UTF-8'?>"):
                raise Exception(conf)

            search = reg.search(conf)
            if not search:
                raise Exception(conf)

            job = r[0]
            fLOG(search.groups()[0], "--", job, "--", r[1])

            confno = conf.replace("\n", "")
            exp = "</hudson.tasks.BatchFile><hudson.tasks.BatchFile>"
            if exp not in confno:
                raise Exception(confno)


if __name__ == "__main__":
    unittest.main()
