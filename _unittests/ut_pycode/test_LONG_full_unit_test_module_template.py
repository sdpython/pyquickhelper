"""
@brief      test log(time=600s)
@author     Xavier Dupre
"""
import os
import sys
import unittest
import time
from io import StringIO

import pyquickhelper
from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.loghelper import sys_path_append
from pyquickhelper.pycode import (
    get_temp_folder, process_standard_options_for_setup, is_travis_or_appveyor)
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pycode.utils_tests import TestWrappedException
from pyquickhelper.pycode.utils_tests_helper import PEP8Exception
from pyquickhelper.loghelper import git_clone
from pyquickhelper import __file__ as pyq_location


class TestUnitTestFullModuleTemplate(ExtTestCase):

    def test_full_unit_test(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if __name__ != "__main__" or not os.path.exists("temp2_full_unit_test"):
            temp_ = get_temp_folder(__file__, "temp2_full_unit_test")
            temp = os.path.join(temp_, "python3_module_template")
            if not os.path.exists(temp):
                os.mkdir(temp)
            git_clone(temp, "github.com", "sdpython",
                      "python3_module_template")
            wait = 0
            while not os.path.exists(os.path.join(temp, "python3_module_template")) and wait < 5:
                fLOG("wait", wait)
                time.sleep(1000)
                wait += 1
        else:
            temp = os.path.abspath(os.path.join(
                "temp2_full_unit_test", "python3_module_template"))
        root = temp

        with sys_path_append(os.path.join(root, "src")):
            setup = os.path.join(root, "setup.py")
            pyq = os.path.join(os.path.dirname(pyquickhelper.__file__), "..")

            def skip_function(name, code, duration):
                return "test_example" not in name

            pyq_folder = os.path.normpath(os.path.abspath(
                os.path.join(os.path.dirname(pyq_location), '..')))

            blog_list = """
                <?xml version="1.0" encoding="UTF-8"?>
                <opml version="1.0">
                    <head>
                        <title>blog</title>
                    </head>
                    <body>
                        <outline text="python3_module_template"
                            title="python3_module_template"
                            type="rss"
                            xmlUrl="http://www.xavierdupre.fr/app/pyquickhelper/python3_module_template/_downloads/rss.xml"
                            htmlUrl="http://www.xavierdupre.fr/app/pyquickhelper/python3_module_template/blog/main_0000.html" />
                    </body>
                </opml>
                """

            stdout = StringIO()
            stderr = StringIO()
            fLOG("setup", setup)
            thispath = os.path.abspath(os.path.dirname(__file__))
            thispath = os.path.normpath(
                os.path.join(thispath, "..", "..", "src"))
            import jyquickhelper

            fLOG("unit tests", root)
            for command in ["version", "write_version", "clean_pyd",
                            "build_script", "copy27",
                            "run_pylint .*((myex)|(example_ext)).*[.]py$ "
                            "-iC0103 -iC0123 -iC0111 -iW0611 -iE0401 -iE0611 -iE0401",
                            "unittests -e .*code_style.*",
                            "unittests -g .*((ext)|(code_style)|(run_notebooks)).*",
                            "unittests_LONG", "unittests_SKIP",
                            "build_sphinx"]:
                if command == "build_sphinx" and is_travis_or_appveyor() in ('travis', 'appveyor'):
                    # InkScape not installed for AppVeyor or travis.
                    continue
                if command == "build_sphinx" and is_travis_or_appveyor() in ('azurepip', ):
                    # AttributeError: type object 'Callable' has no attribute '_abc_registry'
                    continue

                fLOG("#######################################################")
                fLOG("#######################################################")
                fLOG(command)
                fLOG("#######################################################")
                rem = False
                PYTHONPATH = os.environ.get("PYTHONPATH", "")
                sep = ";" if sys.platform.startswith("win") else ":"
                new_val = PYTHONPATH + sep + thispath
                new_val_src = new_val + sep + 'src'
                if os.path.exists(new_val_src):
                    new_val = new_val_src
                os.environ["PYTHONPATH"] = new_val.strip(sep)
                if command == "build_sphinx":
                    if thispath not in sys.path:
                        sys.path.append(thispath)
                        fLOG("UT add", thispath)
                        rem = True
                log_lines = []

                def logging_custom(*args, **kwargs):
                    log_lines.append(args)
                lcmd = command.split() if ' ' in command else [command]
                stdout2 = StringIO()
                stderr2 = StringIO()

                pos_remove = None
                if command == "unittests -e .*code_style.*":
                    if pyq_folder not in sys.path:
                        pos_remove = len(sys.path)
                        sys.path.append(pyq_folder)
                        fLOG("ADD='{0}'".format(pyq_folder))

                try:
                    r = process_standard_options_for_setup(
                        lcmd, setup, "python3_module_template",
                        port=8067, requirements=["pyquickhelper"],
                        blog_list=blog_list,
                        fLOG=logging_custom,
                        additional_ut_path=[pyq, (root, True)],
                        skip_function=skip_function,
                        coverage_options={"disable_coverage": True},
                        stdout=stdout2, stderr=stderr2,
                        use_run_cmd=True)
                    goon = True
                except PEP8Exception as e:
                    lines = str(e).split('\n')[1:]
                    lines = [line for line in lines
                             if "should be placed before" not in line and
                             'C0209' not in line]
                    content = "\n".join(lines).strip("\n\r\t ")
                    if len(content) > 0:
                        raise AssertionError(
                            "Remaining style issues.\n{}".format(content)) from e
                except TestWrappedException as e:
                    if "test_coverage_combine.py" in str(e):
                        goon = False
                    else:
                        raise e
                except NotImplementedError:
                    # Maybe not implemented on linux or windows.
                    goon = False

                if goon:
                    if command == "unittests -e .*code_style.*" and pos_remove:
                        if sys.path[pos_remove] != pyq_folder:
                            raise Exception(
                                "sys.path has changed at position {0}".format(pos_remove))
                        del sys.path[pos_remove]
                        fLOG("REMOVE='{0}'".format(pyq_folder))
                elif pos_remove:
                    del sys.path[pos_remove]

                vout = stdout2.getvalue()
                stdout.write(vout)
                verr = stderr2.getvalue()
                stderr.write(verr)

                if "unittests" in command:
                    if not r:
                        raise Exception("{0}-{1}".format(r, command))
                    for line in log_lines:
                        fLOG("  ", line)
                    if len(log_lines) == 0:
                        raise Exception(
                            "command1={0}\n--OUT--\n{1}\n--ERR--\n{2}".format(command, vout, verr))
                    if "-e" in command and "running test   1, ut_module/test_convert_notebooks.py" in vout:
                        raise Exception(vout)
                    if "-e" in command and "_ext" not in vout and "code_style" not in command:
                        raise Exception(
                            "command3={0}\n--OUT--\n{1}".format(command, vout))
                    if "LONG" in command and "running test   1, ut_module/test_convert_notebooks.py" in vout:
                        raise Exception(vout)
                if rem:
                    del sys.path[sys.path.index(thispath)]
                os.environ["PYTHONPATH"] = PYTHONPATH

            fLOG("#######################################################")
            fLOG("#######################################################")
            fLOG("OUT:\n", stdout.getvalue())
            fLOG("ERR:\n", stderr.getvalue())

            out = os.path.join(temp, "_unittests", "unittests.out")
            if not os.path.exists(out):
                raise Exception("not found: " + out)


if __name__ == "__main__":
    unittest.main()
