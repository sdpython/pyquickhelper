"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG, run_cmd
from pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor
from pyquickhelper.jenkinshelper.yaml_helper import load_yaml, enumerate_convert_yaml_into_instructions, convert_sequence_into_batch_file


class TestYamlExe(unittest.TestCase):

    def test_bug_exe(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        command = "dir" if sys.platform.startswith("win32") else "ls"
        yml = """
        language: python
        python:
            - {{Python35}}
        before:
            - %s
        after_script:
            - %s {{PLATFORM}}
        script:
            - %s
        """.replace("        ", "") % (command, command, command)
        context = dict(Python34="fake", Python35=os.path.dirname(sys.executable),
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython35=None, project_name="pyquickhelper",
                       root_path="ROOT", PLATFORM="win32")
        obj, name = load_yaml(yml, context=context)
        self.assertTrue(name is not None)
        try:
            res = list(enumerate_convert_yaml_into_instructions(
                obj, variables=context))
            self.assertTrue(False)
            self.assertTrue(res)
        except ValueError as e:
            self.assertTrue("'before'" in str(e))

    def test_exe(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        command = "dir" if sys.platform.startswith("win32") else "ls"
        yml = """
        language: python
        python:
            - {{Python35}}
        before_script:
            - %s
        after_script:
            - %s {{PLATFORM}}
        script:
            - %s
        """.replace("        ", "") % (command, command, command)
        temp = get_temp_folder(__file__, "temp_yaml_exe")
        context = dict(Python34="fake", Python35=os.path.dirname(sys.executable),
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython35=None, project_name="pyquickhelper",
                       root_path="ROOT", PLATFORM="win32")
        obj, name = load_yaml(yml, context=context)
        self.assertTrue(name is not None)
        res = list(enumerate_convert_yaml_into_instructions(
            obj, variables=context))
        for r, var in res:
            conv = convert_sequence_into_batch_file(r, variables=var)
            if (f"{command} ") not in conv:
                raise Exception(f"{command}\n--\n{conv}")
            fLOG("####", conv)
            ext = "bat" if command == "dir" else "sh"
            name = os.path.join(temp, f"yml.{ext}")
            with open(name, "w") as f:
                f.write(conv)
            if is_travis_or_appveyor() == "__travis":
                # linux, unable to test TestYamlExe.test_exe.
                pass
            else:
                if sys.platform.startswith("win"):
                    cmd = name
                else:
                    cmd = "bash " + name
                try:
                    out, err = run_cmd(cmd, wait=True)
                except PermissionError as e:
                    raise Exception(
                        f"Unable to execute '{name}' which contains\n{conv}") from e
                fLOG("###")
                fLOG(out)
                if "BEFORE_SCRIPT" not in out:
                    raise Exception(
                        f"{out}\nERR\n{err}\n#########\n{conv}")
                if "AFTER_SCRIPT" not in out:
                    raise Exception(
                        f"{out}\nERR\n{err}\n#########\n{conv}")
                if "SCRIPT" not in out:
                    raise Exception(
                        f"{out}\nERR\n{err}\n#########\n{conv}")


if __name__ == "__main__":
    unittest.main()
