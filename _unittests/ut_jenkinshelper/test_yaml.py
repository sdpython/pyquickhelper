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
from src.pyquickhelper.jenkinshelper.yaml_helper import load_yaml

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestYaml(unittest.TestCase):

    def test_jenkins_job_verif(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "..", "..", ".local_jenkins.win.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python34=None, Python35=sys.executable,
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython35=None, project_name="pyquickhelper")
        obj = load_yaml(yml, context=context)
        for k, v in obj.items():
            fLOG(k, type(v), v)
        assert "python" in obj
        assert isinstance(obj["python"], list)


if __name__ == "__main__":
    unittest.main()
