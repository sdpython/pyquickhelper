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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.jenkinshelper.jenkins_server import JenkinsExt
from src.pyquickhelper.jenkinshelper.yaml_helper import enumerate_processed_yml

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestYamlJenkins(unittest.TestCase):

    def test_jenkins(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_jenkins_yml")
        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "..", "..", ".local.jenkins.win.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python34="c:\\Python34_x64",
                       Python35=os.path.dirname(sys.executable),
                       Python36=os.path.dirname(sys.executable),
                       Python27="c:\\Python27_x64",
                       Anaconda3="c:\\Anaconda3", Anaconda2="c:\\Anaconda2",
                       WinPython36="c:\\PythonENSAE",
                       root_path="d:\\jenkins\\yml")
        git_repo = "https://github.com/sdpython/pyquickhelper.git"
        srv = JenkinsExt("http://localhost:8080/", "user", "password",
                         mock=True, fLOG=fLOG, engines=context)
        for i, tuconv in enumerate(enumerate_processed_yml(yml, server=srv,
                                                           context=context, git_repo=git_repo, yml_platform="win")):
            conv, name, var = tuconv
            c = "conda" if "c:\\Anaconda" in conv else 'win'
            with open(os.path.join(temp, "yml-%s-%d.xml" % (c, i)), "w") as f:
                f.write(conv)

    def test_jenkins_ext_setup_server_yaml(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        self.private_tst_jenkins_ext_setup_server_yaml(False, None)

    def test_jenkins_ext_setup_server_yaml_disabled(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        self.private_tst_jenkins_ext_setup_server_yaml(True, None)

    def test_jenkins_ext_setup_server_yaml_cred(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        self.private_tst_jenkins_ext_setup_server_yaml(True, "FFFF")

    def private_tst_jenkins_ext_setup_server_yaml(self, disable_schedule, credentials):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "..", "..", ".local.jenkins.win.yml"))
        yml_url = "https://raw.githubusercontent.com/sdpython/python3_module_template/master/.local.jenkins.win.yml"

        github = "https://github.com/sdpython/"

        modules = [("yml", yml, "H H(10-11) * * 0"),
                   ("yml", yml_url, "H H(10-11) * * 0")]

        if sys.version_info[0] == 2:
            modules = modules[:1]
            warnings.warn(
                "We don't test the url way on Python 2.7, too annoying.")

        engines = dict(Python34="c:\\Python34_x64",
                       Python35=os.path.dirname(sys.executable),
                       Python36=os.path.dirname(sys.executable),
                       Python27="c:\\Python27_x64",
                       Anaconda3="c:\\Anaconda3", Anaconda2="c:\\Anaconda2",
                       WinPython36="c:\\PythonENSAE",
                       root_path="d:\\jenkins\\yml")

        srv = JenkinsExt(
            "http://localhost:8080/", "user", "password", mock=True,
            engines=engines, fLOG=fLOG, platform="win")

        if not sys.platform.startswith("win"):
            # not yet implemented
            return

        fLOG("---------------------")
        res = srv.setup_jenkins_server(github=github, modules=modules,
                                       overwrite=True, add_environ=False,
                                       location="anything", disable_schedule=disable_schedule,
                                       credentials=credentials)
        reg = re.compile("<description>(.*)</description>")
        nb = 0
        sch = 0
        desc = 0
        to = 0
        nb_jen = 0
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
            if "anything\\python3_module_template\\%NAME_JENKINS%" not in conf:
                nb_jen += 1
            if "python3_module_template_UT_36_std" in conf:
                nb += 1
            if "H H(20-21) * * 0" in conf:
                sch += 1
            if "H H(16-17) * * 0" in conf:
                sch += 1
            if "0101 - H H(20-21) * * 0" in conf:
                desc += 1
            if "0101 - H H(16-17) * * 0" in conf:
                desc += 1
            if "<timeoutSecondsString>900</timeoutSecondsString>" in conf:
                to += 1

        if sys.version_info[0] != 2:
            self.assertTrue(i > 0)
            self.assertTrue(nb > 0)
            self.assertTrue(nb_jen > 0)
            self.assertTrue(to > 0)
            if disable_schedule:
                self.assertEqual(sch, 0)
                self.assertEqual(desc, 0)
            else:
                self.assertEqual(sch, 2)
                self.assertEqual(desc, 2)
            fLOG(to)
            if credentials:
                if "credentialsId" not in conf:
                    raise Exception(conf)
            else:
                if "<credentialsId>None" not in conf:
                    raise Exception(conf)
        else:
            warnings.warn("disable the test on Python 2.7")


if __name__ == "__main__":
    unittest.main()
