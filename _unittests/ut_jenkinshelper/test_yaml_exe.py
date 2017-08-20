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

from src.pyquickhelper.loghelper import fLOG, run_cmd
from src.pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor
from src.pyquickhelper.jenkinshelper.yaml_helper import load_yaml, enumerate_convert_yaml_into_instructions, convert_sequence_into_batch_file

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


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
                       root_path="ROOT", PLATFORM="win")
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
                       root_path="ROOT", PLATFORM="win")
        obj, name = load_yaml(yml, context=context)
        self.assertTrue(name is not None)
        res = list(enumerate_convert_yaml_into_instructions(
            obj, variables=context))
        for r, var in res:
            conv = convert_sequence_into_batch_file(r, variables=var)
            self.assertTrue(("%s " % command) in conv)
            fLOG("####", conv)
            ext = "bat" if command == "dir" else "sh"
            name = os.path.join(temp, "yml.%s" % ext)
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
                        "Unable to execute '{0}' which contains\n{1}".format(name, conv)) from e
                fLOG("###")
                fLOG(out)
                if "BEFORE_SCRIPT" not in out:
                    raise Exception(
                        "{0}\nERR\n{2}\n#########\n{1}".format(out, conv, err))
                if "AFTER_SCRIPT" not in out:
                    raise Exception(
                        "{0}\nERR\n{2}\n#########\n{1}".format(out, conv, err))
                if "SCRIPT" not in out:
                    raise Exception(
                        "{0}\nERR\n{2}\n#########\n{1}".format(out, conv, err))


if __name__ == "__main__":
    unittest.main()
