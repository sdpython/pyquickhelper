"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.jenkinshelper.yaml_helper import load_yaml, enumerate_convert_yaml_into_instructions, convert_sequence_into_batch_file


class TestYamlSplit(unittest.TestCase):

    def test_jconvert_sequence_into_batch_file_split(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.zz_st_jconvert_sequence_into_batch_file_split("win")

    def zz_st_jconvert_sequence_into_batch_file_split(self, platform):
        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "data", "local.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python35="fake", Python36="C:\\Python36_x64",
                       Python38="C:\\Python38_x64",
                       Python39="C:\\Python39_x64",
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
                raise TypeError(type(conv))
            convs.append(conv)
        assert len(res) > 0

        self.assertEqual(len(convs), 2)
        conv = convs[0]
        assert conv
        assert isinstance(conv, list)
        fr = 0
        for c in conv:
            if "JENKINS_SPLIT" in c:
                raise Exception(c)
            if "pip freeze" in c:
                fr += 1
            fLOG("-------------------------------")
            fLOG(c)
        self.assertEqual(fr, 1)


if __name__ == "__main__":
    unittest.main()
