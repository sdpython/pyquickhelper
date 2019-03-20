"""
@brief      test log(time=2s)
"""

import os
import unittest
import sys
from pyquickhelper.loghelper import fLOG  # pylint: disable=E0401
from pyquickhelper.jenkinshelper.yaml_helper import load_yaml, enumerate_convert_yaml_into_instructions  # pylint: disable=E0401
from pyquickhelper.jenkinshelper.yaml_helper import evaluate_condition, convert_sequence_into_batch_file  # pylint: disable=E0401
from pyquickhelper.jenkinshelper.jenkins_helper import jenkins_final_postprocessing  # pylint: disable=E0401


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
                       Python37=os.path.dirname(sys.executable),
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython36=None, project_name="pyquickhelper",
                       root_path="ROOT")
        vers = "%d%d" % sys.version_info[:2]
        context["Python%s" % vers] = os.path.dirname(sys.executable)
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
                       Python37=os.path.dirname(sys.executable) + "37",
                       Python27="fake2", Anaconda3=None, Anaconda2=None,
                       WinPython36=None, root_path="ROOT", project_name="pyquickhelper")
        obj, name = load_yaml(yml, context=context, platform="win32")
        self.assertTrue(name is not None)
        res = list(enumerate_convert_yaml_into_instructions(
            obj, add_environ=False))

        for r, v in res:
            if None in r:
                raise Exception(r)
            if r[1][0] != "python" and r[1][0] != "INFO":
                raise Exception(r)
        if len(res) != 9:
            rows = [str(_) for _ in res]
            raise Exception("len(res)={0}\n{1}".format(
                len(res), "\n".join(rows)))

        doc = [[s[0] for s in seq if s[1] is not None] for seq, _ in res]
        fLOG(doc)
        doc = [s for s in doc if "documentation" in s]
        if len(doc) != 1:
            raise Exception("len(doc)={0}\n{1}".format(
                len(doc), "\n".join(str(_) for _ in doc)))
        fLOG("**", doc)

    def test_jconvert_sequence_into_batch_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.zz_st_jconvert_sequence_into_batch_file("win")
        self.zz_st_jconvert_sequence_into_batch_file("linux")

    def zz_st_jconvert_sequence_into_batch_file(self, platform):
        this = os.path.abspath(os.path.dirname(__file__))
        plat = "win" if platform.startswith("win") else "lin"
        yml = os.path.abspath(os.path.join(
            this, "..", "..", ".local.jenkins.%s.yml" % plat))
        if not os.path.exists(yml):
            yml = os.path.abspath(os.path.join(
                this, "..", "..", "..", ".local.jenkins.%s.yml" % plat))
        if not os.path.exists(yml):
            raise FileNotFoundError(yml)
        context = dict(Python34="fake", Python35="C:/Python35_x64",
                       Python36="C:/Python36_x64",
                       Python37="C:/Python37_x64",
                       Python27=None, Anaconda3=None, Anaconda2=None,
                       WinPython36=None, project_name="pyquickhelper",
                       root_path="ROOT")
        vers = "%d%d" % sys.version_info[:2]
        context["Python%s" % vers] = "C:/Python%s_x64" % vers
        if platform.startswith("win"):
            for k in context:
                if context[k] is not None:
                    context[k] = context[k].replace("/", "\\")
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

        set_name = "SET" if platform.startswith("win") else "export"
        vers_ = "%d.%d" % sys.version_info[:2]
        conv = [
            _ for _ in convs if set_name + " NAME=UT" in _ and "VERSION=%s" % vers_ in _ and '-g' not in _]
        if len(conv) != 3:
            vers_ = "3.7"
            vers = "37"
            conv = [
                _ for _ in convs if set_name + " NAME=UT" in _ and "VERSION=%s" % vers_ in _ and '-g' not in _]
        if len(conv) not in (3, 5, 4, 6):
            rows = [str(_) for _ in conv]
            raise Exception("len(convs)={3}-len(conv)={0}\n----\n{1}\n-----\n{2}\n***\n{4}".format(
                len(conv), "\n".join(conv), "\n".join(rows), len(convs), "\n*****\n".join(convs)))
        conv = conv[0]
        if platform.startswith("win"):
            expected = """
            @echo off
            set PATH0=%PATH%
            SET DIST=std
            SET VERSION=__VERSP__
            SET NAME=UT
            SET TIMEOUT=899

            @echo AUTOMATEDSETUP
            set current=ROOT\\pyquickhelper\\%NAME_JENKINS%

            @echo interpreter=C:\\Python__VERS___x64\\python

            @echo CREATE VIRTUAL ENVIRONMENT in ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv
            if not exist "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv" mkdir "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv"
            set KEEPPATH=%PATH%
            set PATH=C:\\Python__VERS___x64;%PATH%
            "C:\\Python__VERS___x64\\python" -c "from virtualenv import create_environment;create_environment(\\"ROOT\\\\pyquickhelper\\\\%NAME_JENKINS%\\\\_venv\\", site_packages=True)"
            set PATH=%KEEPPATH%
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo INSTALL
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            pip install --no-cache-dir --no-deps --index http://localhost:8067/simple/ jyquickhelper tkinterquickhelper --extra-index-url=https://pypi.python.org/simple/
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
            expected = expected.replace("__VERS__", vers)
            expected = expected.replace("__VERSP__", vers_)
            val = conv.strip("\n \t\r")
            if expected != val:
                mes = "EXP:\n{0}\n###########\nGOT:\n{1}".format(expected, val)
                for a, b in zip(expected.split("\n"), val.split("\n")):
                    if a != b:
                        raise Exception(
                            "error on line:\nEXP:\n{0}\nGOT:\n{1}\n#######\n{2}".format(a, b, mes))
                raise Exception(mes)

        conv = [_ for _ in convs if set_name +
                " DIST=std" in _ and "TIMEOUT=899" in _]
        if len(conv) != 1:
            raise Exception(
                "################################\nlen(conv)={0}\n{1}".format(len(conv), conv))
        conv = conv[0]
        if platform.startswith("win"):
            expected = """
            @echo off
            set PATH0=%PATH%
            SET DIST=std
            SET VERSION=__VERSP__
            SET NAME=UT
            SET TIMEOUT=899

            @echo AUTOMATEDSETUP
            set current=ROOT\\pyquickhelper\\%NAME_JENKINS%

            @echo interpreter=C:\\Python__VERS___x64\\python

            @echo CREATE VIRTUAL ENVIRONMENT in ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv
            if not exist "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv" mkdir "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv"
            set KEEPPATH=%PATH%
            set PATH=C:\\Python__VERS___x64;%PATH%
            "C:\\Python__VERS___x64\\python" -c "from virtualenv import create_environment;create_environment(\\"ROOT\\\\pyquickhelper\\\\%NAME_JENKINS%\\\\_venv\\", site_packages=True)"
            set PATH=%KEEPPATH%
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo INSTALL
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            pip install --no-cache-dir --no-deps --index http://localhost:8067/simple/ jyquickhelper tkinterquickhelper --extra-index-url=https://pypi.python.org/simple/
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
            expected = expected.replace("__VERS__", vers)
            expected = expected.replace("__VERSP__", vers_)
            val = conv.strip("\n \t\r")
            if expected != val:
                mes = "EXP:\n{0}\n###########\nGOT:\n{1}".format(expected, val)
                for a, b in zip(expected.split("\n"), val.split("\n")):
                    if a != b:
                        raise Exception(
                            "error on line:\nEXP:\n{0}\nGOT:\n{1}\n#######\n{2}".format(a, b, mes))
                raise Exception(mes)
        else:
            expected = """
            export DIST=std
            export PYINT=python__VERSP__
            export VERSION=__VERSP__
            export NAME=UT
            export TIMEOUT=899

            echo AUTOMATEDSETUP
            export current=ROOT/pyquickhelper/$NAME_JENKINS

            echo interpreter=C:/Python__VERS___x64/$PYINT

            echo CREATE VIRTUAL ENVIRONMENT in ROOT/pyquickhelper/$NAME_JENKINS/_venv
            if [-f ROOT/pyquickhelper/$NAME_JENKINS/_venv]; then mkdir "ROOT/pyquickhelper/$NAME_JENKINS/_venv"; fi
            export KEEPPATH=$PATH
            export PATH=C:/Python__VERS___x64:$PATH
            "C:/Python__VERS___x64/$PYINT" -c "from virtualenv import create_environment;create_environment(\\"ROOT/pyquickhelper/$NAME_JENKINS/_venv\\", site_packages=True)"
            export PATH=$KEEPPATH
            if [ $? -ne 0 ]; then exit $?; fi

            echo INSTALL
            export PATH=ROOT/pyquickhelper/$NAME_JENKINS/_venv/bin:$PATH
            $PYINT -c "from pip._internal import main;main(\\"install --no-cache-dir --no-deps --index http://localhost:8067/simple/ jyquickhelper tkinterquickhelper --extra-index-url=https://pypi.python.org/simple/\\".split())"
            if [ $? -ne 0 ]; then exit $?; fi
            $PYINT -c "from pip._internal import main;main(\\"install -r requirements.txt\\".split())"
            if [ $? -ne 0 ]; then exit $?; fi
            $PYINT --version
            if [ $? -ne 0 ]; then exit $?; fi
            $PYINT -c "from pip._internal import main;main([\\"freeze\\"])"
            if [ $? -ne 0 ]; then exit $?; fi
            export JOB_NAME=UT

            echo SCRIPT
            export PATH=ROOT/pyquickhelper/$NAME_JENKINS/_venv/bin:$PATH
            $PYINT -u setup.py unittests
            if [ $? -ne 0 ]; then exit $?; fi

            echo AFTER_SCRIPT
            export PATH=ROOT/pyquickhelper/$NAME_JENKINS/_venv/bin:$PATH
            $PYINT -u setup.py bdist_wheel
            if [ $? -ne 0 ]; then exit $?; fi
            cp dist/*.whl ROOT/pyquickhelper/../local_pypi/local_pypi_server
            if [ $? -ne 0 ]; then exit $?; fi

            echo DOCUMENTATION
            export PATH=ROOT/pyquickhelper/$NAME_JENKINS/_venv/bin:$PATH
            $PYINT -u setup.py build_sphinx
            if [ $? -ne 0 ]; then exit $?; fi
            cp -R -f _doc/sphinxdoc/build/html dist/html
            if [ $? -ne 0 ]; then exit $?; fi
            """.replace("            ", "").strip("\n \t\r")
            expected = expected.replace("__VERS__", vers)
            expected = expected.replace("__VERSP__", vers_)
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
                       Python37="C:\\Python37_x64",
                       Python27="C:\\Python27_x64", Anaconda3=None, Anaconda2=None,
                       WinPython36=None, project_name="pyquickhelper",
                       root_path="ROOT")
        vers = "%d%d" % sys.version_info[:2]
        context["Python%s" % vers] = "C:\\Python%s_x64" % vers
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
            SET TIMEOUT=899

            @echo AUTOMATEDSETUP
            set current=ROOT\\pyquickhelper\\%NAME_JENKINS%

            @echo interpreter=C:\\Python27_x64\\python

            @echo CREATE VIRTUAL ENVIRONMENT in ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv
            if not exist "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv" mkdir "ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv"
            set KEEPPATH=%PATH%
            set PATH=C:\\Python27_x64;%PATH%
            "C:\\Python27_x64\\python" -c "from virtualenv import create_environment;create_environment(\\"ROOT\\\\pyquickhelper\\\\%NAME_JENKINS%\\\\_venv\\", site_packages=True)"
            set PATH=%KEEPPATH%
            if %errorlevel% neq 0 exit /b %errorlevel%

            @echo INSTALL
            set PATH=ROOT\\pyquickhelper\\%NAME_JENKINS%\\_venv\\Scripts;%PATH%
            pip install --no-cache-dir --no-deps --index http://localhost:8067/simple/ jyquickhelper tkinterquickhelper --extra-index-url=https://pypi.python.org/simple/
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
            C:\\Python37_x64\\python -u setup.py copy27
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
