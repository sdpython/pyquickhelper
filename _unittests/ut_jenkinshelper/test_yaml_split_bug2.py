"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.jenkinshelper.yaml_helper import load_yaml, enumerate_convert_yaml_into_instructions, convert_sequence_into_batch_file


class TestYamlSplit2(ExtTestCase):

    def test_jconvert_sequence_into_batch_file_split2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.zz_st_jconvert_sequence_into_batch_file_split2("win")

    def zz_st_jconvert_sequence_into_batch_file_split2(self, platform):
        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "data", "local2.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python35="py35", Python36="C:\\Python36_x64",
                       Python27="py27", Anaconda3="ana3", Anaconda2="ana2",
                       project_name="pyquickhelper", root_path="ROOT")
        obj, name = load_yaml(yml, context=context, platform=platform)
        assert name is not None
        res = list(enumerate_convert_yaml_into_instructions(
            obj, add_environ=False))
        convs = []
        for r, v in res:
            conv = convert_sequence_into_batch_file(
                r, variables=v, platform=platform)
            if not isinstance(conv, list):
                raise TypeError(str(type(conv)) + "\n" + str(conv))
            convs.append(conv)
        self.assertNotEmpty(res)

        self.assertEqual(len(convs), 17)
        for conv in convs:
            assert conv
            assert isinstance(conv, list)
            fr = 0
            for c in conv:
                if "JENKINS_SPLIT" in c:
                    raise Exception(c)
                if "pip freeze" in c:
                    fr += 1
            self.assertEqual(fr, 2)


if __name__ == "__main__":
    unittest.main()
