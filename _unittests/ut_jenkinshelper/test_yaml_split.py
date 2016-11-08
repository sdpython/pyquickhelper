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
from src.pyquickhelper.jenkinshelper.yaml_helper import load_yaml, enumerate_convert_yaml_into_instructions, convert_sequence_into_batch_file

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestYamlSplit(unittest.TestCase):

    def test_jconvert_sequence_into_batch_file_split(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.a_test_jconvert_sequence_into_batch_file_split("win")

    def a_test_jconvert_sequence_into_batch_file_split(self, platform):
        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "data", "local.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python35="fake", Python36="C:\\Python35_x64",
                       project_name="pyquickhelper", root_path="ROOT")
        obj, name = load_yaml(yml, context=context, platform=platform)
        assert name is not None
        res = list(enumerate_convert_yaml_into_instructions(
            obj, add_environ=False))
        convs = []
        for r, v in res:
            conv = convert_sequence_into_batch_file(
                r, variables=v, platform=platform)
            convs.append(conv)
            typstr = str  # unicode#
            assert isinstance(conv, typstr)
        assert len(res) > 0

        conv = [_ for _ in convs if "SET NAME=UT" in _ and "VERSION=3.5" in _]
        self.assertEqual(len(conv), 1)
        conv = conv[0]
        assert conv
        fLOG(conv)


if __name__ == "__main__":
    unittest.main()
