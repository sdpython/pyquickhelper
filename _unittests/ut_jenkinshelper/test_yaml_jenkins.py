"""
@brief      test log(time=2s)
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

from src.pyquickhelper.loghelper import fLOG, run_cmd
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
                       Python27="c:\\Python27_x64",
                       Anaconda3="c:\\Anaconda3", Anaconda2="c:\\Anaconda2",
                       WinPython35="c:\\PythonENSAE",
                       root_path="d:\\jenkins\\yml")
        git_repo = "https://github.com/sdpython/pyquickhelper.git"
        srv = JenkinsExt("http://localhost:8080/", "user", "password",
                         mock=True, fLOG=fLOG, engines=context)
        for i, conv in enumerate(enumerate_processed_yml(yml, server=srv,
                                                         context=context, git_repo=git_repo, platform="win")):
            c = "conda" if "c:\\Anaconda" in conv else 'win'
            with open(os.path.join(temp, "yml-%s-%d.xml" % (c, i)), "w") as f:
                f.write(conv)


if __name__ == "__main__":
    unittest.main()
