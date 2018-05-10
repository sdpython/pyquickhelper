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
from src.pyquickhelper.jenkinshelper.yaml_helper import load_yaml, enumerate_convert_yaml_into_instructions, evaluate_condition, convert_sequence_into_batch_file
from src.pyquickhelper.jenkinshelper.jenkins_helper import jenkins_final_postprocessing

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
            this, "..", "..", ".local.jenkins.win.yml"))
        if not os.path.exists(yml):
            yml = os.path.abspath(os.path.join(
                this, "..", "..", "..", ".local.jenkins.win.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python34=None, Python35=os.path.dirname(sys.executable),
                       Python36=os.path.dirname(sys.executable),
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython36=None, project_name="pyquickhelper",
                       root_path="ROOT")
        obj, name = load_yaml(yml, context=context)
        for k, v in obj.items():
            fLOG(k, type(v), v)
        self.assertTrue("python" in obj)
        self.assertTrue(isinstance(obj["python"], list))
        self.assertTrue(name is not None)

    def test_evaluate_condition(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        r = evaluate_condition('[ ${PYTHON} == "C:\\\\Python35_x64\\\\pythonw.exe" ]',
                               dict(python="C:\\\\Python35_x64\\\\pythonw.exe"))
        self.assertTrue(r)
        self.assertTrue(isinstance(r, bool))
        r = evaluate_condition('${PYTHON} == "C:\\\\Python35_x64\\\\pythonw.exe"',
                               dict(python="C:\\\\Python35_x64\\\\pythonw.exe"))
        self.assertTrue(r)
        self.assertTrue(isinstance(r, bool))
        r = evaluate_condition('${PYTHON} != "C:\\\\Python35_x64\\\\pythonw.exe"',
                               dict(python="C:\\\\Python35_x64\\\\pythonw.exe"))
        self.assertTrue(not r)
        self.assertTrue(isinstance(r, bool))
        r = evaluate_condition('[${PYTHON} != "C:\\\\Python35_x64\\\\pythonw.exe", ${PYTHON} == "C:\\\\Python35_x64\\\\pythonw.exe"]',
                               dict(python="C:\\\\Python35_x64\\\\pythonw.exe"))
        self.assertTrue(not r)
        self.assertTrue(isinstance(r, bool))

    def test_jenkins_job_multiplication(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "..", "..", ".local.jenkins.win.yml"))
        if not os.path.exists(yml):
            yml = os.path.abspath(os.path.join(
                this, "..", "..", "..", ".local.jenkins.win.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python34="fake", Python35=os.path.dirname(sys.executable) + "35",
                       Python36=os.path.dirname(sys.executable) + "36",
                       Python27="fake2", Anaconda3=None, Anaconda2=None,
                       WinPython36=None, root_path="ROOT", project_name="pyquickhelper")
        obj, name = load_yaml(yml, context=context, platform="win")
        self.assertTrue(name is not None)
        res = list(enumerate_convert_yaml_into_instructions(
            obj, add_environ=False))

        for r, v in res:
            if None in r:
                raise Exception(r)
            if r[1][0] != "python" and r[1][0] != "INFO":
                raise Exception(r)
        if len(res) != 7:
            rows = [str(_) for _ in res]
            raise Exception("len(res)={0}\n{1}".format(
                len(res), "\n".join(rows)))

        doc = [[s[0] for s in seq if s[1] is not None] for seq, _ in res]
        fLOG(doc)
        doc = [s for s in doc if "documentation" in s]
        if len(doc) != 1:
            raise Exception("len(doc)={0}\n{1}".format(
                len(doc), "\n".join(str(_) for _ in doc)))
        else:
            fLOG("**", doc)

    def test_jconvert_sequence_into_batch_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        try:
            self.zz_st_jconvert_sequence_into_batch_file("linux")
        except NotImplementedError as e:
            pass
        self.zz_st_jconvert_sequence_into_batch_file("win")

    def zz_st_jconvert_sequence_into_batch_file(self, platform):
        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "..", "..", ".local.jenkins.win.yml"))
        if not os.path.exists(yml):
            yml = os.path.abspath(os.path.join(
                this, "..", "..", "..", ".local.jenkins.win.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python34="fake", Python35="C:\\Python35_x64",
                       Python36="C:\\Python36_x64",
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython36=None, project_name="pyquickhelper",
                       root_path="ROOT")
        obj, name = load_yaml(yml, context=context, platform=platform)
        self.assertTrue(name is not None)
        res = list(enumerate_convert_yaml_into_instructions(
            obj, add_environ=False))
        convs = []
        for r, v in res:
            conv = convert_sequence_into_batch_file(
                r, variables=v, platform=platform)
            convs.append(conv)
            typstr = str  # unicode#
            self.assertTrue(isinstance(conv, typstr))
        self.assertTrue(len(res) > 0)

        conv = [
            _ for _ in convs if "SET NAME=UT" in _ and "VERSION=3.6" in _ and '-g' not in _]
        if len(conv) != 2:
            rows = [str(_) for _ in conv]
            raise Exception("len(conv)={0}\n----\n{1}\n-----\n{2}".format(
                len(conv), "\n".join(conv), "\n".join(rows)))
        conv = conv[0]
        if platform.startswith("win"):
            expected = """
            @echo off
            set PATH0=%PATH%
            SET DIST=std
            SET VERSION=3.6
            SET NAME=UT
            SET TIMEOUT=900

            @echo AUTOMATEDSETUP
            set current=ROOT\\pyquickhelper\\%NAME_JENKINS%

            @echo interpreter=C:\\Python36_x64\\python

            @echo CREATE VIRTUAL ENVIRONMENT in ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv
            if not exist "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv" mkdir "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv"
            set KEEPPATH=%PATH%
            set PATH=%PATH%;C:\\Python36_x64
            "C:\\Python36_x64\\Scripts\\virtualenv" --system-site-packages "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv"
            set PATH=%KEEPPATH%
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo INSTALL
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            pip install --no-cache-dir --no-deps --index http://localhost:8067/simple/ jyquickhelper --extra-index-url=https://pypi.python.org/simple/
            if %errorlevel% neq 0 exit /b %errorlevel%
            pip install -r requirements.txt
            if %errorlevel% neq 0 exit /b %errorlevel%
            python --version
            if %errorlevel% neq 0 exit /b %errorlevel%
            pip freeze
            if %errorlevel% neq 0 exit /b %errorlevel%
            pip freeze > pip_freeze.txt
            if %errorlevel% neq 0 exit /b %errorlevel%
            set JOB_NAME=UT

            @echo SCRIPT
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            python -u setup.py unittests
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo AFTER_SCRIPT
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            python -u setup.py bdist_wheel
            if %errorlevel% neq 0 exit /b %errorlevel%
            copy dist\\*.whl ROOT\\pyquickhelper\\..\\..\\local_pypi\\local_pypi_server
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo DOCUMENTATION
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            python -u setup.py build_sphinx
            if %errorlevel% neq 0 exit /b %errorlevel%
            xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\html dist\\html
            if %errorlevel% neq 0 exit /b %errorlevel%
            """.replace("            ", "").strip("\n \t\r")
            val = conv.strip("\n \t\r")
            if expected != val:
                mes = "EXP:\n{0}\n###########\nGOT:\n{1}".format(expected, val)
                for a, b in zip(expected.split("\n"), val.split("\n")):
                    if a != b:
                        raise Exception(
                            "error on line:\nEXP:\n{0}\nGOT:\n{1}\n#######\n{2}".format(a, b, mes))
                raise Exception(mes)

        conv = [_ for _ in convs if "SET NAME=DOC" in _]
        if len(conv) != 1:
            raise Exception(
                "################################\n{0}".format(conv))
        conv = conv[0]
        if platform.startswith("win"):
            expected = """
            @echo off
            set PATH0=%PATH%
            SET DIST=std
            SET VERSION=3.6
            SET NAME=DOC

            @echo AUTOMATEDSETUP
            set current=ROOT\\pyquickhelper\\%NAME_JENKINS%

            @echo interpreter=C:\\Python36_x64\\python

            @echo CREATE VIRTUAL ENVIRONMENT in ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv
            if not exist "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv" mkdir "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv"
            set KEEPPATH=%PATH%
            set PATH=%PATH%;C:\\Python36_x64
            "C:\\Python36_x64\\Scripts\\virtualenv" --system-site-packages "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv"
            set PATH=%KEEPPATH%
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo INSTALL
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            pip install --no-cache-dir --no-deps --index http://localhost:8067/simple/ jyquickhelper --extra-index-url=https://pypi.python.org/simple/
            if %errorlevel% neq 0 exit /b %errorlevel%
            pip install -r requirements.txt
            if %errorlevel% neq 0 exit /b %errorlevel%
            python --version
            if %errorlevel% neq 0 exit /b %errorlevel%
            pip freeze
            if %errorlevel% neq 0 exit /b %errorlevel%
            pip freeze > pip_freeze.txt
            if %errorlevel% neq 0 exit /b %errorlevel%
            set JOB_NAME=DOC

            @echo SCRIPT
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            python -u setup.py build_sphinx
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo AFTER_SCRIPT
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            python -u setup.py bdist_wheel
            if %errorlevel% neq 0 exit /b %errorlevel%
            """.replace("            ", "").strip("\n \t\r")
            val = conv.strip("\n \t\r")
            if expected != val:
                mes = "EXP:\n{0}\n###########\nGOT:\n{1}".format(expected, val)
                for a, b in zip(expected.split("\n"), val.split("\n")):
                    if a != b:
                        raise Exception(
                            "error on line:\nEXP:\n{0}\nGOT:\n{1}\n#######\n{2}".format(a, b, mes))
                raise Exception(mes)

    def test_jconvert_sequence_into_batch_file27(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        platform = "win"
        this = os.path.abspath(os.path.dirname(__file__))
        yml = os.path.abspath(os.path.join(
            this, "..", "..", ".local.jenkins.win.yml"))
        if not os.path.exists(yml):
            yml = os.path.abspath(os.path.join(
                this, "..", "..", "..", ".local.jenkins.win.yml"))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python34=None, Python35="C:\\Python35_x64",
                       Python36="C:\\Python36_x64",
                       Python27="C:\\Python27_x64", Anaconda3=None, Anaconda2=None,
                       WinPython36=None, project_name="pyquickhelper",
                       root_path="ROOT")
        obj, name = load_yaml(yml, context=context, platform=platform)
        self.assertTrue(name is not None)
        res = list(enumerate_convert_yaml_into_instructions(
            obj, add_environ=False))
        convs = []
        for r, v in res:
            conv = convert_sequence_into_batch_file(
                r, variables=v, platform=platform)
            typstr = str  # unicode#
            if not isinstance(conv, typstr):
                raise TypeError(type(conv))
            convs.append(conv)
        fLOG("number of jobs", len(res))
        convs = [jenkins_final_postprocessing(
            _, True) for _ in convs if "VERSION=2.7" in _]
        self.assertTrue(len(convs) > 0)
        conv = convs[0]

        if platform.startswith("win"):
            expected = """
            @echo off
            set PATH0=%PATH%
            SET DIST=std
            SET VERSION=2.7
            SET NAME=UT
            SET TIMEOUT=900

            @echo AUTOMATEDSETUP
            set current=ROOT\\pyquickhelper\\%NAME_JENKINS%

            @echo interpreter=C:\\Python27_x64\\python

            @echo CREATE VIRTUAL ENVIRONMENT in ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv
            if not exist "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv" mkdir "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv"
            set KEEPPATH=%PATH%
            set PATH=%PATH%;C:\\Python27_x64
            "C:\\Python27_x64\\Scripts\\virtualenv" --system-site-packages "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv"
            set PATH=%KEEPPATH%
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo INSTALL
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            pip install --no-cache-dir --no-deps --index http://localhost:8067/simple/ jyquickhelper --extra-index-url=https://pypi.python.org/simple/
            if %errorlevel% neq 0 exit /b %errorlevel%
            pip install -r requirements.txt
            if %errorlevel% neq 0 exit /b %errorlevel%
            python --version
            if %errorlevel% neq 0 exit /b %errorlevel%
            pip freeze
            if %errorlevel% neq 0 exit /b %errorlevel%
            pip freeze > pip_freeze.txt
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo BEFORE_SCRIPT
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            pip uninstall jyquickhelper
            if %errorlevel% neq 0 exit /b %errorlevel%
            pip install bin\\jyquickhelper-0.2-py2-none-any.whl
            if %errorlevel% neq 0 exit /b %errorlevel%
            C:\\Python36_x64\\python -u setup.py copy27
            if %errorlevel% neq 0 exit /b %errorlevel%
            cd dist_module27
            if %errorlevel% neq 0 exit /b %errorlevel%
            set JOB_NAME=UT

            @echo SCRIPT
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            python -u setup.py unittests
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo AFTER_SCRIPT
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            python -u setup.py bdist_wheel
            if %errorlevel% neq 0 exit /b %errorlevel%
            copy dist\\*.whl ROOT\\pyquickhelper\\..\\..\\local_pypi\\local_pypi_server
            if %errorlevel% neq 0 exit /b %errorlevel%
            cd ..
            if %errorlevel% neq 0 exit /b %errorlevel%
            """.replace("            ", "").strip("\n \t\r")
            val = conv.strip("\n \t\r")
            if expected != val:
                mes = "EXP:\n{0}\n###########\nGOT:\n{1}".format(expected, val)
                for a, b in zip(expected.split("\n"), val.split("\n")):
                    if a != b:
                        raise Exception(
                            "error on line:\nEXP:\n{0}\nGOT:\n{1}\n#######\n{2}".format(a, b, mes))
                raise Exception(mes)


if __name__ == "__main__":
    unittest.main()
