"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest


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
from src.pyquickhelper.pycode import ExtTestCase
from src.pyquickhelper.jenkinshelper.yaml_helper import enumerate_processed_yml

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestYamlCondition(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_jenkins_job_verif(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(this, "data", "local_linux.yml"))
        context = dict(Python37=os.path.dirname(sys.executable),
                       project_name="pyquickhelper",
                       root_path="ROOT")
        vers = "%d%d" % sys.version_info[:2]
        context["Python%s" % vers] = os.path.dirname(sys.executable)
        res = list(enumerate_processed_yml(
            yml, context=context, platform="linux"))
        found = 0
        for script in res:
            for sc in script:
                if sc is None:
                    continue
                for s in sc:
                    for v in s.split('\n'):
                        if "if [ -f dist ];" in v:
                            found += 1
                        if "if [ -f distscript ];" in v:
                            found += 1
                        if "if [ -f distinst ];" in v:
                            found += 1
        self.assertEqual(found, 3)


if __name__ == "__main__":
    unittest.main()
