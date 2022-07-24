"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.jenkinshelper.yaml_helper import enumerate_processed_yml


class TestYamlCondition(ExtTestCase):

    def test_jenkins_job_verif(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(this, "data", "local_linux.yml"))
        context = dict(Python37=os.path.dirname(sys.executable),
                       Python38=os.path.dirname(sys.executable),
                       Python39=os.path.dirname(sys.executable),
                       project_name="pyquickhelper",
                       root_path="ROOT")
        vers = "%d%d" % sys.version_info[:2]
        context[f"Python{vers}"] = os.path.dirname(sys.executable)
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
