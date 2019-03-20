"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import re
import requests
import jenkins

from pyquickhelper.loghelper import fLOG
from pyquickhelper.jenkinshelper.jenkins_server import JenkinsExt, JenkinsExtException
from pyquickhelper.pycode import ExtTestCase


class TestJenkinsExt(ExtTestCase):

    def test_jenkins_job_verif(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        for platform in {'win', 'linux'}:
            TestJenkinsExt.zz_st_jenkins_job_verif(self, platform)

    def zz_st_jenkins_job_verif(self, platform):
        engines_default = dict(anaconda2="c:\\Anaconda",
                               anaconda3="c:\\Anaconda3",
                               py35="c:\\Python35_x64",
                               default="c:\\Python34_x64",
                               winpython="c:\\APythonENSAE\\python")

        srv = JenkinsExt(
            "http://localhost:8080/", "user", "password",
            mock=True, fLOG=fLOG, engines=engines_default, platform=platform)

        if platform == "win":
            job = "standalone [conda_update] [anaconda3]"
            cmd = srv.get_cmd_standalone(job)
            self.assertIn("Anaconda3", cmd)

        if platform == "win":
            job = "pyrsslocal [py35] <-- pyquickhelper, pyensae"
            cmd = "\n".join(srv.get_jenkins_script(job))
            self.assertNotIn("Python34", cmd)
        else:
            try:
                job = "pyrsslocal [py35] <-- pyquickhelper, pyensae"
            except NotImplementedError:
                fLOG("OK FOR", platform)

    def test_jenkins_ext(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        srv = JenkinsExt(
            "http://localhost:8080/", "user", "password",
            mock=True, fLOG=fLOG, platform="win32")
        github = "https://github.com/sdpython/"

        conf = srv.create_job_template("pyquickhelper",
                                       git_repo=github +
                                       "%s/" % "pyquickhelper",
                                       upstreams=None,
                                       location=r"/home/username/jenkins/")

        self.assertIn("auto_unittest_setup_help.bat", conf)

        conf = srv.create_job_template("pyquickhelper",
                                       git_repo=github +
                                       "%s/" % "pyquickhelper",
                                       upstreams=None,
                                       location=r"/home/username/jenkins/",
                                       scheduler="H H(13-14) * * *")
        self.assertIn("H H(13-14) * * *", conf)

        try:
            conf = srv.create_job_template("pyquickhelper",
                                           git_repo=github +
                                           "%s/" % "pyquickhelper",
                                           upstreams=["pyquickhelper"],
                                           location=r"/home/username/jenkins/",
                                           scheduler="H H(13-14) * * *")
            raise Exception("should not happen")
        except JenkinsExtException:
            pass

        conf = srv.create_job_template("pyquickhelper",
                                       git_repo=github +
                                       "%s/" % "pyquickhelper",
                                       upstreams=["pyquickhelper"],
                                       location=r"/home/username/jenkins/",
                                       scheduler=None)
        self.assertIn("pyquickhelper", conf)

    def test_jenkins_ext_setup_server(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        github = "https://github.com/sdpython/"

        modules = [  # update anaconda
            ("standalone [conda_update] [Anaconda3]", "H H(8-9) * * 0"),
            "standalone [conda_update] [Anaconda2]",
            "standalone [local_pypi]",
            "standalone [update] [Anaconda3]",
            "standalone [update] [WinPython]",
            "standalone [update]",
            "standalone [install] [Anaconda2]",
            # pyquickhelper,
            ("pyquickhelper", "H H(10-11) * * 0"),
            ("pymyinstall <-- pyquickhelper", None, dict(success_only=True)),
            ["pyquickhelper [Anaconda3]",
             "pyquickhelper [WinPython]",
             "pyquickhelper [27] [Anaconda2]",
             "pyquickhelper [py35]"],
            ["pyensae <-- pyquickhelper <---- qgrid"],
            ["pymmails <-- pyquickhelper",
             "pysqllike <-- pyquickhelper",
             "pyrsslocal <-- pyquickhelper, pyensae",
             "pymyinstall [27] [Anaconda2] <-- pyquickhelper <---- qgrid",
             "python3_module_template <-- pyquickhelper",
             "pyensae [Anaconda3] <-- pyquickhelper",
             "pyensae [WinPython] <-- pyquickhelper"],
            ["pymmails [Anaconda3] <-- pyquickhelper",
             "pysqllike [Anaconda3] <-- pyquickhelper",
             "pyrsslocal [Anaconda3] <-- pyquickhelper, pensae",
             "python3_module_template [Anaconda3] <-- pyquickhelper",
             "python3_module_template [27] [Anaconda2] <-- pyquickhelper",
             "pymyinstall [LONG] <-- pyquickhelper"],
            # update
            ("pymyinstall [update_modules] <-- pyquickhelper",
             "H H(10-11) * * 5"),
            # actuariat
            [("actuariat_python <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall", "H H(12-13) * * 0")],
            ["actuariat_python [WinPython] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall",
             "actuariat_python [Anaconda3] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall"],
            # code_beatrix
            ("code_beatrix <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall",
             "H H(14-15) * * 0"),
            "code_beatrix [WinPython] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall",
            "code_beatrix [Anaconda3] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall",
            # teachings
            ("ensae_teaching_cs <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall",
             "H H(15-16) * * 0", dict(timeout=4799)),
            [("ensae_teaching_cs [WinPython] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall", None, dict(timeout=4800)),
             ("ensae_teaching_cs [Anaconda3] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall", None, dict(timeout=4801))],
            ("ensae_teaching_cs [custom_left] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall",
             None, dict(timeout=4802)),
            ("ensae_teaching_cs [WinPython] [custom_left] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall",
             None, dict(timeout=4803)),
            ("ensae_teaching_cs [Anaconda3] [custom_left] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall",
             None, dict(timeout=4804)),
            # documentation
            ("pyquickhelper [doc] <-- pyquickhelper", "H H(3-4) * * 1"),
            ["pymyinstall [doc] <-- pyquickhelper",
             "pysqllike [doc] <-- pyquickhelper",
             "pymmails [doc] <-- pyquickhelper",
             "pyrsslocal [doc] <-- pyquickhelper",
             "pyensae [doc] <-- pyquickhelper"],
            ["actuariat_python [doc] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall",
             "code_beatrix [doc] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall"],
            ("ensae_teachings_cs [doc] <-- pyquickhelper, pyensae, pymmails, pyrsslocal, pymyinstall",
             None, dict(pre="rem pre", post="rem post", timeout=4805)),
            ("custom [any_name]", "H H(3-4) * * 1",
             dict(script="any_script.bat")),
            ["pyensae [UT] {-d_10} <-- pyquickhelper <---- qgrid"],
        ]

        engines = dict(Anaconda2="C:\\Anaconda2",
                       Anaconda3="C:\\Anaconda3",
                       WinPython="C:\\WinPython\\Python",
                       default="c:\\Python34_x64",
                       py35="c:\\Python35_x64")

        srv = JenkinsExt(
            "http://localhost:8080/", "user", "password", mock=True,
            platform="win32", engines=engines, fLOG=fLOG)

        fLOG("---------------------")
        res = srv.setup_jenkins_server(github=github, modules=modules,
                                       overwrite=True,
                                       location="anything/")
        reg = re.compile("<description>(.*)</description>")
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

            if "notebook" in conf:
                raise Exception(conf)

            if "pymyinstall" in r[0].split("<--")[0] and "[" not in r[0]:
                if "FAILURE" in conf:
                    raise Exception("{0}\n----\n{1}".format(r[0], conf))
                if "SUCCESS" not in conf:
                    raise Exception(conf)

            if "[UT]" in job:
                if "-d 10" not in conf:
                    raise Exception("{0}\n-----------\n{1}".format(job, conf))
                if "%1" in conf:
                    raise Exception("{0}\n-----------\n{1}".format(job, conf))
                if " -d 10" not in conf:
                    raise Exception("{0}\n-----------\n{1}".format(job, conf))

            if i == 0:
                if "conda update" not in conf:
                    raise Exception(conf)
                if "H H(8-9) * * 0" not in conf:
                    raise Exception(conf)
                if "A0101" not in conf:
                    raise Exception(conf)
                if "github" in conf:
                    raise Exception(conf)

            if i == 7:
                if "pyquickhelper" not in conf:
                    raise Exception(conf)
                if "H H(10-11) * * 0" not in conf:
                    raise Exception(conf)
                if "B0101" not in conf:
                    raise Exception(conf)
                if "github" not in conf:
                    raise Exception(conf)

            if "python3_module_template [27]" in r[0]:
                if "PYQUICKHELPER27=" in conf:
                    raise Exception(conf)
                if "PYQUICKHELPER=" in conf:
                    raise Exception(conf)
                if "PYQUICKHELPER27=a" in conf:
                    raise Exception(conf)
                if "dist_module27" not in conf:
                    raise Exception(conf)
                if "Anaconda3" in conf:
                    raise Exception(conf)

            if "[27]" not in r[0] and "update" not in conf:
                if "PYQUICKHELPER27=a" in conf:
                    raise Exception(conf)
                if "dist_module27" in conf:
                    raise Exception(conf)

            if "_LONG" in conf and "build_script" not in conf:
                raise Exception(conf)

            if "custom_left" in conf:
                if "auto_cmd_any_setup_command.bat %jenkinspythonexe% default_87E5_87E5 custom_left" not in conf and \
                        "auto_cmd_any_setup_command.bat %jenkinspythonexe% WinPython_0640_0640 custom_left" not in conf and \
                        "auto_cmd_any_setup_command.bat %jenkinspythonexe% Anaconda3_3279_3279 custom_left" not in conf:
                    raise Exception(conf)

            if ">G0" in conf:
                exp = re.compile(
                    "auto_cmd_any_setup_command.bat %jenkinspythonexe% default_([A-Z0-9_]+) build_sphinx")
                ser = exp.search(conf)
                if not ser:
                    raise Exception(conf)

            if "ensae_teachings_cs [doc]" in conf:
                if "rem pre" not in conf or "rem post" not in conf:
                    raise Exception(conf)

            if "[Anaconda3]" in job:
                if "C:\\Anaconda3" not in conf:
                    raise Exception(conf)

            if "[Anaconda2]" in job:
                if "C:\\Anaconda2" not in conf:
                    raise Exception(conf)

            if "[py35]" in job:
                if "c:\\Python35_x64" not in conf:
                    raise Exception(conf)

            if "pymyinstall" in job and "[27]" in job:
                if sys.version_info[:2] == (3, 5):
                    s1 = '''%jenkinspythonexe% -u -c "import pip;pip.main('install --no-cache-dir''' + \
                         ''' --index http://localhost:8067/simple/ pyquickhelper'.split())"'''
                    s2 = '''%jenkinspythonexe% -u -c "import pip;pip.main('install qgrid'.split())"'''
                    if s1 not in conf:
                        raise Exception(conf)
                    if s2 not in conf:
                        raise Exception(conf)
                else:
                    if "%jenkinspythonpip% install --no-cache-dir --index http://localhost:8067/simple/ pyquickhelper" not in conf:
                        raise Exception(conf)
                    if "%jenkinspythonpip% install qgrid" not in conf:
                        raise Exception(conf)

            if "ensae_teaching" in job:
                if "<timeoutSecondsString>4799" not in conf and "<timeoutSecondsString>480" not in conf:
                    raise Exception(conf)

            if "[doc]" in job:
                if "%jenkinspythonexe% -u %current%setup.py build_script" not in conf:
                    raise Exception(conf)

        self.assertGreater(i, 0)

    def test_python_jenkins_request(self):
        req = requests.Request
        self.assertNotEmpty(req)


if __name__ == "__main__":
    unittest.main()
