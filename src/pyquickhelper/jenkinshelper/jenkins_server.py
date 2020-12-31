"""
@file
@brief Extends Jenkins Server from :epkg:`python-jenkins`.
"""

import os
import sys
import socket
import hashlib
import re
from xml.sax.saxutils import escape
import requests
import jenkins
from ..loghelper.flog import noLOG
from ..pycode.windows_scripts import windows_jenkins, windows_jenkins_any
from ..pycode.windows_scripts import windows_jenkins_27_conda, windows_jenkins_27_def
from ..pycode.linux_scripts import linux_jenkins, linux_jenkins_any
from ..pycode.build_helper import private_script_replacements
from .jenkins_exceptions import JenkinsExtException, JenkinsJobException
from .jenkins_server_template import _config_job, _trigger_up, _trigger_time, _git_repo, _task_batch_win, _task_batch_lin
from .jenkins_server_template import _trigger_startup, _publishers, _file_creation, _wipe_repo, _artifacts, _cleanup_repo
from .yaml_helper import enumerate_processed_yml
from .jenkins_helper import jenkins_final_postprocessing, get_platform

_timeout_default = 1200

_default_engine_paths = {
    "windows": {
        "__PY36__": "__PY36__",
        "__PY37__": "__PY37__",
        "__PY38__": "__PY38__",
        "__PY39__": "__PY39__",
        "__PY36_X64__": "__PY36_X64__",
        "__PY37_X64__": "__PY37_X64__",
        "__PY38_X64__": "__PY38_X64__",
        "__PY39_X64__": "__PY39_X64__",
    },
}


def _modified_windows_jenkins(requirements_local, requirements_pypi, module="__MODULE__",
                              port="__PORT__", platform=None):
    return private_script_replacements(
        linux_jenkins, module,
        (requirements_local, requirements_pypi),
        port, raise_exception=False,
        default_engine_paths=_default_engine_paths,
        platform=get_platform(platform))


def _modified_linux_jenkins(requirements_local, requirements_pypi, module="__MODULE__",
                            port="__PORT__", platform=None):
    return private_script_replacements(
        windows_jenkins, module,
        (requirements_local, requirements_pypi),
        port, raise_exception=False,
        default_engine_paths=_default_engine_paths,
        platform=get_platform(platform))


def _modified_windows_jenkins_27(requirements_local, requirements_pypi, module="__MODULE__",
                                 port="__PORT__", anaconda=True, platform=None):
    return private_script_replacements(
        windows_jenkins_27_conda if anaconda else windows_jenkins_27_def,
        module, (requirements_local, requirements_pypi),
        port, raise_exception=False,
        default_engine_paths=_default_engine_paths,
        platform=get_platform(platform))


def _modified_windows_jenkins_any(requirements_local, requirements_pypi, module="__MODULE__",
                                  port="__PORT__", platform=None):
    res = private_script_replacements(
        windows_jenkins_any, module,
        (requirements_local, requirements_pypi),
        port, raise_exception=False,
        default_engine_paths=_default_engine_paths,
        platform=get_platform(platform))
    return res.replace("virtual_env_suffix=%2", "virtual_env_suffix=___SUFFIX__")


def _modified_linux_jenkins_any(requirements_local, requirements_pypi, module="__MODULE__",
                                port="__PORT__", platform=None):
    res = private_script_replacements(
        linux_jenkins_any, module,
        (requirements_local, requirements_pypi),
        port, raise_exception=False,
        default_engine_paths=_default_engine_paths,
        platform=get_platform(platform))
    return res.replace("virtual_env_suffix=%2", "virtual_env_suffix=___SUFFIX__")


class JenkinsExt(jenkins.Jenkins):

    """
    Extensions for the :epkg:`Jenkins` server
    based on module :epkg:`python-jenkins`.

    .. index:: Jenkins, Jenkins extensions

    Some useful :epkg:`Jenkins` extensions:

    * `Credentials Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Credentials+Plugin>`_
    * `Extra Column Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Extra+Columns+Plugin>`_
    * `Git Client Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Git+Client+Plugin>`_
    * `GitHub Client Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Github+Plugin>`_
    * `GitLab Client Plugin <https://wiki.jenkins-ci.org/display/JENKINS/GitLab+Plugin>`_
    * `Matrix Project Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Matrix+Project+Plugin>`_
    * `Build Pipeline Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Build+Pipeline+Plugin>`_

    The whole class can define many different engines.
    A job can send a mail at the end of the job execution.
    """

    _config_job = _config_job  # pylint: disable=W0127
    _trigger_up = _trigger_up  # pylint: disable=W0127
    _trigger_time = _trigger_time  # pylint: disable=W0127
    _trigger_startup = _trigger_startup  # pylint: disable=W0127
    _git_repo = _git_repo  # pylint: disable=W0127
    _task_batch_win = _task_batch_win  # pylint: disable=W0127
    _task_batch_lin = _task_batch_lin  # pylint: disable=W0127
    _publishers = _publishers  # pylint: disable=W0127
    _wipe_repo = _wipe_repo  # pylint: disable=W0127
    _artifacts = _artifacts  # pylint: disable=W0127
    _cleanup_repo = _cleanup_repo  # pylint: disable=W0127

    def __init__(self, url, username=None, password=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 mock=False, engines=None, platform=None, pypi_port=8067, fLOG=noLOG,
                 mails=None):
        """
        @param      url         url of the server
        @param      username    username
        @param      password    password
        @param      timeout     timeout
        @param      mock        True by default, if False, avoid talking to the server
        @param      engines     list of Python engines *{name: path to python.exe}*
        @param      platform    platform of the Jenkins server
        @param      pypi_port   pypi port used for the documentation server
        @param      mails       (str) list of mails to contact in case of a mistaje
        @param      fLOG        logging function

        If *platform* is None, it is replace by the value returned
        by @see fn get_platform.
        """
        if platform is None:
            platform = get_platform(platform)
        jenkins.Jenkins.__init__(
            self, url, username, password, timeout=timeout)
        self._mock = mock
        self.platform = platform
        self.pypi_port = pypi_port
        self.mails = mails
        self.fLOG = fLOG
        if engines is None:
            engines = {"default": os.path.dirname(sys.executable)}
        self.engines = engines
        for k, v in self.engines.items():
            if v.endswith(".exe"):
                raise FileNotFoundError(  # pragma: no cover
                    "{}:{} is not a folder".format(k, v))
            if " " in v:
                raise JenkinsJobException(  # pragma: no cover
                    "No space allowed in engine path: " + v)

    @property
    def Engines(self):
        """
        @return the available engines
        """
        return self.engines

    def jenkins_open(self, req, add_crumb=True, resolve_auth=True):  # pragma: no cover
        '''
        Overloads the same method from module :epkg:`python-jenkins`
        to replace string by bytes.

        @param      req             see :epkg:`Jenkins API`
        @param      add_crumb       see :epkg:`Jenkins API`
        @param      resolve_auth    see :epkg:`Jenkins API`
        '''
        if self._mock:
            raise JenkinsExtException("mocking server, cannot be open")

        response = self.jenkins_request(
            req=req, add_crumb=add_crumb, resolve_auth=resolve_auth)
        if response is None:
            raise jenkins.EmptyResponseException(
                "Error communicating with server[%s]: "
                "empty response" % self.server)
        return response.content

    def delete_job(self, name):  # pragma: no cover
        '''
        Deletes :epkg:`Jenkins` job permanently.

        :param name: name of :epkg:`Jenkins` job, ``str``
        '''
        if self._mock:
            return
        r = self._get_job_folder(name)
        if r is None:
            raise JenkinsExtException('delete[%s] failed (no job)' % (name))

        folder_url, short_name = self._get_job_folder(name)
        if folder_url is None:
            raise ValueError("folder_url is None for job '{0}'".format(name))
        self.jenkins_open(requests.Request(
            'POST', self._build_url(jenkins.DELETE_JOB, locals())
        ))
        if self.job_exists(name) or self.job_exists(short_name):
            raise jenkins.JenkinsException('delete[%s] failed' % (name))

    def get_jobs(self, folder_depth=0, folder_depth_per_request=10, view_name=None):
        """
        Gets the list of all jobs recursively to the given folder depth,
        see `get_all_jobs
        <https://python-jenkins.readthedocs.org/en/latest/api.html
        #jenkins.Jenkins.get_all_jobs>`_.

        @return                     list of jobs, ``[ { str: str} ]``
        """
        return jenkins.Jenkins.get_jobs(self, folder_depth=folder_depth,
                                        folder_depth_per_request=folder_depth_per_request,
                                        view_name=view_name)

    def delete_all_jobs(self):  # pragma: no cover
        """
        Deletes all jobs permanently.

        @return                 list of deleted jobs
        """
        jobs = self.get_jobs()
        res = []
        for k in jobs:
            self.fLOG("[jenkins] remove job", k["name"])
            self.delete_job(k["name"])
            res.append(k["name"])
        return res

    def get_jenkins_job_name(self, job):
        """
        Infers a name for the jenkins job.

        @param      job     str
        @return             name
        """
        if "<--" in job:
            job = job.split("<--")[0]
        if job.startswith("custom "):
            return job.replace(" ", "_").replace("[", "").replace("]", "").strip("_")
        def_prefix = ["doc", "setup", "setup_big"]
        def_prefix.extend(self.engines.keys())
        for prefix in def_prefix:
            p = "[%s]" % prefix
            if p in job:
                job = p + " " + job.replace(" " + p, "")
        return job.replace(" ", "_").replace("[", "").replace("]", "").strip("_")

    def get_engine_from_job(self, job, return_key=False):
        """
        Extracts the engine from the job definition,
        it should be like ``[engine]``.

        @param      job         job string
        @param      return_key  return the engine name too
        @return                 engine or tuple(engine, name)

        If their is no engine definition, the system
        uses the default one (key=*default*) if it was defined.
        Otherwise, it raises an exception.
        """
        res = None
        spl = job.split()
        for s in spl:
            t = s.strip(" []")
            if t in self.engines:
                res = self.engines[t]
                key = t
                break
        if res is None and "default" in self.engines:
            res = self.engines["default"]
            key = "default"
        if res is None:
            raise JenkinsJobException(  # pragma: no cover
                "Unable to find engine in job '{}', available: {}".format(
                    job, ", ".join(self.engines.keys())))
        if "[27]" in job and "python34" in res.lower():  # pragma: no cover
            mes = "\n".join("  {0}={1}".format(k, v)
                            for k, v in sorted(self.engines.items()))
            raise ValueError(
                "Python mismatch in version:\nJOB = {0}\nRES = {1}\nENGINES\n{2}"
                "".format(job, res, mes))
        return (res, key) if return_key else res

    def get_cmd_standalone(self, job):
        """
        Custom command for :epkg:`Jenkins` (such as updating conda)

        @param      job             module and options
        @return                     script
        """
        spl = job.split()
        if spl[0] != "standalone":
            raise JenkinsExtException(  # pragma: no cover
                "the job should start by standalone: " + job)

        if self.platform.startswith("win"):
            # windows
            if "[conda_update]" in spl:
                cmd = "__ENGINE__\\Scripts\\conda update -y --all"
            elif "[local_pypi]" in spl:
                cmd = "if not exist ..\\..\\local_pypi mkdir ..\\local_pypi"
                cmd += "\nif not exist ..\\..\\local_pypi\\local_pypi_server mkdir ..\\..\\local_pypi\\local_pypi_server"
                cmd += "\necho __ENGINE__\\..\\Scripts\\pypi-server.exe -v -u -p __PORT__ --disable-fallback "
                cmd += "..\\..\\local_pypi\\local_pypi_server > ..\\..\\local_pypi\\local_pypi_server\\start_local_pypi.bat"
                cmd = cmd.replace("__PORT__", str(self.pypi_port))
            elif "[update]" in spl:
                cmd = "__ENGINE__\\python -u -c \"from pymyinstall.packaged import update_all;"
                cmd += "update_all(temp_folder='build/update_modules', "
                cmd += "verbose=True, source='2')\""
            elif "[install]" in spl:
                cmd = "__ENGINE__\\python -u -c \"from pymyinstall.packaged import install_all;install_all"
                cmd += "(temp_folder='build/update_modules', "
                cmd += "verbose=True, source='2')\""
            else:
                raise JenkinsExtException(
                    "cannot interpret job: " + job)  # pragma: no cover

            engine = self.get_engine_from_job(job)
            cmd = cmd.replace("__ENGINE__", engine)
            return cmd
        else:  # pragma: no cover
            if "[conda_update]" in spl:
                cmd = "__ENGINE__/bin/conda update -y --all"
            elif "[local_pypi]" in spl:
                cmd = 'if [-f ../local_pypi ]; then mkdir "../local_pypi"; fi'
                cmd += '\nif [-f ../local_pypi/local_pypi_server]; then mkdir "../local_pypi/local_pypi_server"; fi'
                cmd += "\necho pypi-server -v -u -p __PORT__ --disable-fallback "
                cmd += "../local_pypi/local_pypi_server > ../local_pypi/local_pypi_server/start_local_pypi.sh"
                cmd = cmd.replace("__PORT__", str(self.pypi_port))
            elif "[update]" in spl:
                cmd = "__ENGINE__/python -u -c \"from pymyinstall.packaged import update_all;"
                cmd += "update_all(temp_folder='build/update_modules', "
                cmd += "verbose=True, source='2')\""
            elif "[install]" in spl:
                cmd = "__ENGINE__/python -u -c \"from pymyinstall.packaged import install_all;install_all"
                cmd += "(temp_folder='build/update_modules', "
                cmd += "verbose=True, source='2')\""
            else:
                raise JenkinsExtException("cannot interpret job: " + job)

            engine = self.get_engine_from_job(job)
            cmd = cmd.replace("__ENGINE__", engine)
            return cmd

    @staticmethod
    def get_cmd_custom(job):
        """
        Custom script for :epkg:`Jenkins`.

        @param      job             module and options
        @return                     script
        """
        spl = job.split()
        if spl[0] != "custom":
            raise JenkinsExtException(
                "the job should start by custom: " + job)
        # we expect __SCRIPTOPTIONS__ to be replaced by a script later on
        return "__SCRIPTOPTIONS__"

    @staticmethod
    def hash_string(s, le=4):
        """
        Hashes a string.

        @param      s       string
        @param      le      cut the string to the first *l* character
        @return             hashed string
        """
        m = hashlib.md5()
        m.update(s.encode("ascii"))
        r = m.hexdigest().upper()
        if len(r) < le:
            return r  # pragma: no cover
        m = le // 2
        return r[:m] + r[len(r) - le + m:]

    def extract_requirements(self, job):
        """
        Extracts the requirements for a job.

        @param      job     job name
        @return             3-tuple job, local requirements, pipy requirements

        Example::

            "pyensae <-- pyquickhelper <---- qgrid"

        The function returns::

            (pyensae, ["pyquickhelper"], ["qgrid"])
        """
        if "<--" in job:
            spl = job.split("<--")
            job = spl[0]
            rl, rp = None, None
            for o in spl[1:]:
                if o.startswith("--"):
                    rp = [_.strip("- ") for _ in o.split(",")]
                else:
                    rl = [_.strip() for _ in o.split(",")]
            return job, rl, rp
        return job, None, None

    def get_jenkins_script(self, job):
        """
        Builds the :epkg:`Jenkins` script for a module and its options.

        @param      job             module and options
        @return                     script

        Method @see me setup_jenkins_server describes which tags this method can interpret.
        The method allow command such as ``[custom...]``, they will be
        run in a virtual environment as ``setup.py custom...``.
        Parameter *job* can be ``empty``, in that case, this function returns an empty string.
        Requirements local and from pipy can be specified by added in the job name:

        * ``<-- module1, module2`` for local requirements
        """
        job_verbose = job

        def replacements(cmd, engine, python, suffix, module_name):
            res = cmd.replace("__ENGINE__", engine) \
                     .replace("__PYTHON__", python) \
                     .replace("__SUFFIX__", suffix + "_" + job_hash)  \
                     .replace("__PORT__", str(self.pypi_port))  \
                     .replace("__MODULE__", module_name)  # suffix for the virtual environment and module name
            if "[27]" in job:
                res = res.replace("__PYTHON27__", python)
                if "__DEFAULTPYTHON__" in res:
                    if "default" not in self.engines:
                        raise JenkinsExtException(  # pragma: no cover
                            "a default engine (Python 3.4) must be defined for script using Python 27, job={}".format(job))
                res = res.replace("__DEFAULTPYTHON__",
                                  os.path.join(self.engines["default"], "python"))

            # patch for pyquickhelper
            if "PACTHPQ" in res:
                if hasattr(self, "PACTHPQ"):
                    if not hasattr(self, "pyquickhelper"):
                        raise RuntimeError(  # pragma: no cover
                            "this should not happen:\n{0}\n---\n{1}".format(job_verbose, res))
                    if "pyquickhelper" in module_name:
                        repb = "@echo ~~SET set PYTHONPATH=src\nset PYTHONPATH=src"
                    else:
                        repb = "@echo ~~SET set PYTHONPATH={0}\nset PYTHONPATH={0}".format(self.pyquickhelper.replace(
                            "\\\\", "\\"))
                    repe = "@echo ~~SET set PYTHONPATH=\nset PYTHONPATH="
                else:
                    repb = ""
                    repe = ""
                res = res.replace("__PACTHPQb__", repb).replace(
                    "__PACTHPQe__", repe)

            if "__" in res:
                raise JenkinsJobException(  # pragma: no cover
                    "unable to interpret command line: {}\nCMD: {}\nRES:\n{}".format(job_verbose, cmd, res))

            # patch to avoid installing pyquickhelper when testing
            # pyquickhelper
            if module_name == "pyquickhelper":
                lines = res.split("\n")
                for i, line in enumerate(lines):
                    if "/simple/ pyquickhelper" in line and "--find-links http://localhost" in line:
                        lines[i] = ""  # pragma: no cover
                res = "\n".join(lines)

            return res

        # job hash
        job_hash = JenkinsExt.hash_string(job)

        # extact requirements
        job, requirements_local, requirements_pypi = self.extract_requirements(
            job)
        spl = job.split()
        module_name = spl[0]

        if self.platform.startswith("win"):
            # windows
            engine, namee = self.get_engine_from_job(job, True)
            python = os.path.join(engine, "python.exe")

            if len(spl) == 1:
                script = _modified_windows_jenkins(
                    requirements_local, requirements_pypi, platform=self.platform)
                if not isinstance(script, list):
                    script = [script]
                return [replacements(s, engine, python, namee + "_" + job_hash, module_name) for s in script]

            if len(spl) == 0:
                raise ValueError("job is empty")  # pragma: no cover

            if spl[0] == "standalone":
                # conda update
                return self.get_cmd_standalone(job)

            if spl[0] == "custom":
                # custom script
                return JenkinsExt.get_cmd_custom(job)

            if spl[0] == "empty":
                return ""  # pragma: no cover

            if len(spl) in [2, 3, 4, 5]:
                # step 1: define the script

                if "[test_local_pypi]" in spl:  # pragma: no cover
                    cmd = """__PYTHON__ -u setup.py test_local_pypi"""
                    cmd = "auto_setup_test_local_pypi.bat __PYTHON__"
                elif "[update_modules]" in spl:
                    cmd = """__PYTHON__ -u -c "import sys;sys.path.append('src');from pymyinstall.packaged import update_all;""" + \
                          """update_all(temp_folder='build/update_modules', verbose=True, source='2')" """
                elif "[UT]" in spl:
                    parameters = [_ for _ in spl if _.startswith(
                        "{") and _.endswith("}")]
                    if len(parameters) != 1:
                        raise ValueError(  # pragma: no cover
                            "Unable to extract parameters for the unittests:"
                            "\n{0}".format(" ".join(spl)))
                    p = parameters[0].replace("_", " ").strip("{}")
                    cmd = _modified_windows_jenkins_any(requirements_local, requirements_pypi, platform=self.platform).replace(
                        "__COMMAND__", "unittests " + p)
                elif "[LONG]" in spl:
                    cmd = _modified_windows_jenkins_any(requirements_local, requirements_pypi, platform=self.platform).replace(
                        "__COMMAND__", "unittests_LONG")
                elif "[SKIP]" in spl:
                    cmd = _modified_windows_jenkins_any(  # pragma: no cover
                        requirements_local, requirements_pypi, platform=self.platform).replace(
                            "__COMMAND__", "unittests_SKIP")
                elif "[GUI]" in spl:
                    cmd = _modified_windows_jenkins_any(  # pragma: no cover
                        requirements_local, requirements_pypi, platform=self.platform).replace(
                            "__COMMAND__", "unittests_GUI")
                elif "[27]" in spl:
                    cmd = _modified_windows_jenkins_27(
                        requirements_local, requirements_pypi, anaconda=" [anaconda" in job, platform=self.platform)
                    if not isinstance(cmd, list):
                        cmd = [cmd]  # pragma: no cover
                    else:
                        cmd = list(cmd)
                    if spl[0] == "pyquickhelper":
                        # exception for this job, we don't want to import pyquickhelper
                        # c:/jenkins/pymy/anaconda2_pyquickhelper_27/../virtual/pyquickhelper_conda27vir/Scripts/pip
                        # install --no-cache-dir --index
                        # http://localhost:8067/simple/ pyquickhelper
                        for i in range(0, len(cmd)):
                            lines = cmd[i].split("\n")
                            lines = [
                                (_ if "simple/ pyquickhelper" not in _ else "rem do not import pyquickhelper") for _ in lines]
                            cmd[i] = "\n".join(lines)
                elif "[doc]" in spl:
                    # documentation
                    cmd = _modified_windows_jenkins_any(requirements_local, requirements_pypi, platform=self.platform).replace(
                        "__COMMAND__", "build_sphinx")
                else:
                    cmd = _modified_windows_jenkins(
                        requirements_local, requirements_pypi, platform=self.platform)
                    for pl in spl[1:]:
                        if pl.startswith("[custom_") and pl.endswith("]"):
                            cus = pl.strip("[]")
                            cmd = _modified_windows_jenkins_any(requirements_local, requirements_pypi,
                                                                platform=self.platform).replace("__COMMAND__", cus)

                # step 2: replacement (python __PYTHON__, virtual environnement
                # __SUFFIX__)

                cmds = cmd if isinstance(cmd, list) else [cmd]
                res = []
                for cmd in cmds:
                    cmdn = replacements(cmd, engine, python,
                                        namee + "_" + job_hash, module_name)
                    if "run27" in cmdn and (
                            "Python34" in cmdn or "Python35" in cmdn or
                            "Python36" in cmdn or "Python37" in cmdn or
                            "Python38" in cmdn or "Python39" in cmdn):
                        raise ValueError(  # pragma: no cover
                            "Python version mismatch\nENGINE\n{2}\n----BEFORE"
                            "\n{0}\n-----\nAFTER\n-----\n{1}".format(cmd, cmdn, engine))
                    res.append(cmdn)

                return res
            else:
                raise ValueError("unable to interpret: " +
                                 job)  # pragma: no cover
        else:  # pragma: no cover
            # linux
            engine, namee = self.get_engine_from_job(job, True)
            if engine is None:
                python = "python%d.%d" % sys.version_info[:2]
            elif namee.startswith('py'):
                vers = (int(namee[2:3]), int(namee[3:]))
                python = "python%d.%d" % vers
            else:
                raise ValueError(
                    "Unable to handle engine ='{}', namee='{}'.".format(engine, namee))

            if len(spl) == 1:
                script = _modified_linux_jenkins(
                    requirements_local, requirements_pypi, platform=self.platform)
                if not isinstance(script, list):
                    script = [script]
                return [replacements(s, engine, python, namee + "_" + job_hash, module_name) for s in script]

            elif len(spl) == 0:
                raise ValueError("job is empty")

            elif spl[0] == "standalone":
                # conda update
                return self.get_cmd_standalone(job)

            elif spl[0] == "empty":
                return ""

            elif len(spl) in [2, 3, 4, 5]:
                # step 1: define the script

                if "[test_local_pypi]" in spl:
                    cmd = """__PYTHON__ -u setup.py test_local_pypi"""
                    cmd = "auto_setup_test_local_pypi.bat __PYTHON__"
                elif "[update_modules]" in spl:
                    cmd = """__PYTHON__ -u -c "import sys;sys.path.append('src');from pymyinstall.packaged import update_all;""" + \
                          """update_all(temp_folder='build/update_modules', verbose=True, source='2')" """

                else:
                    cmd = _modified_linux_jenkins(
                        requirements_local, requirements_pypi, platform=self.platform)
                    for pl in spl[1:]:
                        if pl.startswith("[custom_") and pl.endswith("]"):
                            cus = pl.strip("[]")
                            cmd = _modified_linux_jenkins_any(requirements_local, requirements_pypi,
                                                              platform=self.platform).replace("__COMMAND__", cus)

                # step 2: replacement (python __PYTHON__, virtual environnement
                # __SUFFIX__)

                cmds = cmd if isinstance(cmd, list) else [cmd]
                res = []
                for cmd in cmds:
                    cmdn = replacements(cmd, engine, python,
                                        namee + "_" + job_hash, module_name)
                    if "run27" in cmdn and (
                            "Python34" in cmdn or "Python35" in cmdn or
                            "Python36" in cmdn or "Python37" in cmdn or
                            "Python38" in cmdn or "Python39" in cmdn):
                        raise ValueError(
                            "Python version mismatch\nENGINE\n{2}\n----BEFORE\n{0}\n-----\nAFTER\n-----\n{1}".format(cmd, cmdn, engine))
                    res.append(cmdn)

                return res

            # other possibilities
            raise NotImplementedError("On Linux, unable to interpret: " + job)

    def adjust_scheduler(self, scheduler, adjust_scheduler=True):
        """
        Adjusts the scheduler to avoid having two jobs starting at the same time,
        jobs are delayed by an hour, two hours, three hours...

        @param      scheduler           existing scheduler
        @param      adjust_scheduler    True to change it
        @return                         new scheduler (only hours are changed)

        The function uses member ``_scheduled_jobs``.
        It creates it if it does not exist.
        """
        if not adjust_scheduler:
            return scheduler  # pragma: no cover
        if scheduler is None:
            raise ValueError("scheduler is None")  # pragma: no cover
        if not hasattr(self, "_scheduled_jobs"):
            self._scheduled_jobs = {}
        if scheduler not in self._scheduled_jobs:
            self._scheduled_jobs[scheduler] = 1
            return scheduler
        else:
            if "H(" in scheduler:
                cp = re.compile("H[(]([0-9]+-[0-9]+)[)]")
                f = cp.findall(scheduler)
                if len(f) != 1:
                    raise ValueError(  # pragma: no cover
                        "Unable to find hours in the scheduler '{0}', expects 'H(a-b)'".format(scheduler))
                a, b = f[0].split('-')
                a0 = a
                a = int(a)
                b = int(b)
                new_value = scheduler
                rep = 'H(%s)' % f[0]
                iter = 0
                while iter < 100 and (new_value in self._scheduled_jobs or (a0 == a)):
                    a += 1
                    b += 1
                    if a >= 24 or b > 24:
                        a = 0  # pragma: no cover
                        b = 1 + iter // 24  # pragma: no cover
                    r = 'H(%d-%d)' % (a, b)
                    new_value = scheduler.replace(rep, r)
                    iter += 1
                scheduler = new_value
            self._scheduled_jobs[
                scheduler] = self._scheduled_jobs.get(scheduler, 0) + 1
            return scheduler

    def create_job_template(self, name, git_repo, credentials="", upstreams=None, script=None,
                            location=None, keep=30, scheduler=None, py27=False, description=None,
                            default_engine_paths=None, success_only=False, update=False,
                            timeout=_timeout_default, additional_requirements=None,
                            return_job=False, adjust_scheduler=True, clean_repo=True, **kwargs):
        """
        Adds a job to the :epkg:`Jenkins` server.

        @param      name                        name
        @param      credentials                 credentials
        @param      git_repo                    git repository
        @param      upstreams                   the build must run after... (even if failures),
                                                must be None in that case
        @param      script                      script to execute or list of scripts
        @param      keep                        number of buils to keep
        @param      location                    location of the build
        @param      scheduler                   add a schedule time (upstreams must be None in that case)
        @param      py27                        python 2.7 (True) or Python 3 (False)
        @param      description                 add a description to the job
        @param      default_engine_paths        define the default location for python engine,
                                                should be dictionary ``{ engine: path }``, see below.
        @param      success_only                only triggers the job if the previous one was successful
        @param      update                      update the job instead of creating it
        @param      additional_requirements     requirements for this module built by this Jenkins server,
                                                otherthise, we assume they are available
                                                on the installed distribution
        @param      timeout                     specify a timeout
        @param      kwargs                      additional parameters
        @param      adjust_scheduler            adjust the scheduler of a job so that it is delayed if this spot
                                                is already taken
        @param      return_job                  return job instead of submitting the job
        @param      clean_repo                  clean the repository before building (default is yes)

        The job can be modified on Jenkins. To add a time trigger::

            H H(13-14) * * *

        Same trigger but once every week and not every day (Sunday for example)::

            H H(13-14) * * 0

        Parameter *success_only* prevents a job from running if the previous one failed.
        Options *success_only* must be specified.
        Parameter *update* updates a job instead of creating it.
        """
        if 'platform' in kwargs:
            raise NameError(  # pragma: no cover
                "Parameter 'platform' should be set up in the constructor.")
        if script is None:
            if self.platform.startswith("win"):
                if default_engine_paths is None and "default" in self.engines:
                    ver = "__PY%d%d__" % sys.version_info[:2]
                    pat = os.path.join(self.engines["default"], "python")
                    default_engine_paths = dict(
                        windows={ver: pat, "__PYTHON__": pat})

                script = private_script_replacements(
                    windows_jenkins, "____", additional_requirements, "____",
                    raise_exception=False, platform=self.platform,
                    default_engine_paths=default_engine_paths)

                hash = JenkinsExt.hash_string(script)
                script = script.replace("__SUFFIX__", hash)
            else:
                raise JenkinsExtException(
                    "no default script for linux")  # pragma: no cover

        if upstreams is not None and len(upstreams) > 0 and scheduler is not None:
            raise JenkinsExtException(
                "upstreams and scheduler cannot be not null at the same time: {0}".format(name))

        # overwrite parameters with job_options
        job_options = kwargs.get('job_options', None)
        if job_options is not None:
            job_options = job_options.copy()
            if "scheduler" in job_options:
                scheduler = job_options["scheduler"]
                del job_options["scheduler"]
            if "git_repo" in job_options:
                git_repo = job_options["git_repo"]
                del job_options["git_repo"]
            if "credentials" in job_options:
                credentials = job_options["credentials"]
                del job_options["credentials"]

        if upstreams is not None and len(upstreams) > 0:
            trigger = JenkinsExt._trigger_up \
                .replace("__UP__", ",".join(upstreams)) \
                .replace("__FAILURE__", "SUCCESS" if success_only else "FAILURE") \
                .replace("__ORDINAL__", "0" if success_only else "2") \
                .replace("__COLOR__", "BLUE" if success_only else "RED")
        elif scheduler is not None:
            if scheduler.lower() == "startup":
                trigger = JenkinsExt._trigger_startup
            elif scheduler.lower() == "NONE":
                trigger = ""  # pragma: no cover
            else:
                new_scheduler = self.adjust_scheduler(
                    scheduler, adjust_scheduler)
                trigger = JenkinsExt._trigger_time.replace(
                    "__SCHEDULER__", new_scheduler)
                if description is not None:
                    description = description.replace(scheduler, new_scheduler)
                scheduler = new_scheduler
        else:
            trigger = ""

        if not isinstance(script, list):
            script = [script]

        underscore = re.compile("(__[A-Z_]+__)")

        # we modify the scripts
        script_mod = []
        for scr in script:
            search = underscore.search(scr)
            if search:
                raise ValueError(  # pragma: no cover
                    "script still contains __\ndefault_engine_paths: {}\n"
                    "found: {}\nscr:\n{}\nSCRIPT:\n{}\n".format(
                        default_engine_paths, search.groups()[0],
                        scr, str(script)))
            script_mod.append(scr)

        # wrappers
        bwrappers = []

        # repo
        if clean_repo:
            wipe = JenkinsExt._wipe_repo
            bwrappers.append(JenkinsExt._cleanup_repo)
        else:
            wipe = ""
        if git_repo is None:
            git_repo_xml = ""
        else:
            if not isinstance(git_repo, str):
                raise TypeError(  # pragma: no cover
                    "git_repo must be str not '{0}'".format(git_repo))
            git_repo_xml = JenkinsExt._git_repo \
                .replace("__GITREPO__", git_repo) \
                .replace("__WIPE__", wipe) \
                .replace("__CRED__", "<credentialsId>%s</credentialsId>" % credentials)

        # additional scripts
        before = []
        if job_options is not None:
            if 'scripts' in job_options:
                lscripts = job_options['scripts']
                for scr in lscripts:
                    au = _file_creation.replace("__FILENAME__", scr["name"]) \
                                       .replace("__CONTENT__", scr["content"])
                    if "__" in au:
                        raise Exception(
                            "Unable to fully replace expected string in:\n{0}".format(au))
                    before.append(au)
                del job_options['scripts']
            if len(job_options) > 0:
                keys = ", ".join(
                    ["credentials", "git_repo", "scheduler", "scripts"])
                raise ValueError(  # pragma: no cover
                    "Unable to process options\n{0}\nYou can specify the "
                    "following options:\n{1}".format(job_options, keys))

        # scripts
        # tasks is XML, we need to encode s into XML format
        if self.platform.startswith("win"):
            scr = JenkinsExt._task_batch_win
        else:
            scr = JenkinsExt._task_batch_lin
        tasks = before + [scr.replace("__SCRIPT__", escape(s))
                          for s in script_mod]

        # location
        if location is not None and "<--" in location:
            raise Exception(  # pragma: no cover
                "this should not happen")
        location = "" if location is None else "<customWorkspace>%s</customWorkspace>" % location

        # emailing
        publishers = []
        mails = kwargs.get("mails", None)
        if mails is not None:
            publishers.append(  # pragma: no cover
                JenkinsExt._publishers.replace("__MAIL__", mails))
        publishers.append(JenkinsExt._artifacts.replace(
            "__PATTERN__", "dist/*.whl,dist/*.zip"))

        # replacements
        conf = JenkinsExt._config_job
        rep = dict(__KEEP__=str(keep),
                   __TASKS__="\n".join(tasks),
                   __TRIGGER__=trigger,
                   __LOCATION__=location,
                   __DESCRIPTION__="" if description is None else description,
                   __GITREPOXML__=git_repo_xml,
                   __TIMEOUT__=str(timeout),
                   __PUBLISHERS__="\n".join(publishers),
                   __BUILDWRAPPERS__="\n".join(bwrappers))

        for k, v in rep.items():
            conf = conf.replace(k, v)

        # final processing
        conf = jenkins_final_postprocessing(conf, py27)

        if self._mock or return_job:
            return conf
        if update:
            return self.reconfig_job(name, conf)  # pragma: no cover
        return self.create_job(name, conf)  # pragma: no cover

    def process_options(self, script, options):
        """
        Postprocesses a script inserted in a job definition.

        @param      script      script to execute (in a list)
        @param      options     dictionary with options
        @return                 new script
        """
        if not isinstance(script, list):
            script = [script]
        for k, v in options.items():
            if k == "pre":
                script.insert(0, v)
            elif k == "post":
                script.append(v)
            elif k == "pre_set":
                script = [v + "\n" + _ for _ in script]  # pragma: no cover
            elif k == "post_set":
                script = [_ + "\n" + v for _ in script]  # pragma: no cover
            elif k == "script":
                script = [_.replace("__SCRIPTOPTIONS__", v) for _ in script]
            else:
                raise JenkinsJobException(  # pragma: no cover
                    "unable to interpret options: " + str(options))
        return script

    def setup_jenkins_server(self, github, modules, get_jenkins_script=None, overwrite=False,
                             location=None, prefix="", credentials="", update=True, yml_engine="jinja2",
                             add_environ=True, disable_schedule=False, adjust_scheduler=True):
        """
        Sets up many jobs in :epkg:`Jenkins`.

        @param      github                  github account if it does not start with *http://*,
                                            the link to git repository of the project otherwise,
                                            we assume all jobs in *modules* are located on the same
                                            account otherwise the function will have to called twice with
                                            different parameters
        @param      modules                 modules for which to generate the
        @param      get_jenkins_script      see @see me get_jenkins_script (default value if this parameter is None)
        @param      overwrite               do not create the job if it already exists
        @param      location                None for default or a local folder
        @param      prefix                  add a prefix to the name
        @param      credentials             credentials to use for the job (string or dictionary)
        @param      update                  update job instead of deleting it if the job already exists
        @param      yml_engine              templating engine used to process yaml config files
        @param      add_environ             use of local environment variables to interpret the job
        @param      adjust_scheduler        adjust the scheduler of a job so that it is delayed if this spot is already taken
        @param      disable_schedule        disable scheduling for all jobs
        @return                             list of created jobs

        If *credentials* are a dictionary, the function looks up
        into it by using the git repository as a key. If it does not find
        it, it looks for default key. If there is not found,
        the function assumes, there is not credentials for this git repository.

        The function *get_jenkins_script* is called with the following parameters:

        * job

        The extension
        `Extra Columns Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Extra+Columns+Plugin>`_
        is very useful to add extra columns to a view (the description, the output of the
        last execution). Here is a list of useful extensions:

        * `Build Graph View Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Build+Graph+View+Plugin>`_
        * `Build Pipeline Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Build+Pipeline+Plugin>`_
        * `Credentials Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Credentials+Plugin>`_
        * `Extra Columns Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Extra+Columns+Plugin>`_
        * `Git Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Git+Plugin>`_
        * `GitHub Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Github+Plugin>`_
        * `GitLab Plugin <https://wiki.jenkins-ci.org/display/JENKINS/GitLab+Plugin>`_
        * :epkg:`Python`
        * `Python Wrapper Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Python+Wrapper+Plugin>`_
        * `Build timeout plugin <https://wiki.jenkins-ci.org/display/JENKINS/Build-timeout+Plugin>`_

        Tag description:

        * ``[engine]``: to use this specific engine (Python path)
        * ``[27]``: run with python 2.7
        * ``[LONG]``: run longer unit tests (files start by ``test_LONG_``)
        * ``[SKIP]``: run skipped unit tests (files start by ``test_SKIP_``)
        * ``[GUI]``: run skipped unit tests (files start by ``test_GUI_``)
        * ``[custom.+]``: run ``setup.py <custom.+>`` in a virtual environment
        * ``[UT] {-d_10}``: run ``setup.py unittests -d 10`` in a virtual environment, ``-d 10`` is one of the possible parameters

        Others tags:

        * ``[conda_update]``: update conda distribution
        * ``[update]``: update distribution
        * ``[install]``: update distribution
        * ``[local_pypi]``: write a script to run a local pypi server on port 8067 (default option)
        * ``pymyinstall [update_modules]``: run a script to update all modules
          (might have to be ran a couple of times before being successful)

        *modules* is a list defined as follows:

        * each element can be a string or a tuple (string, schedule time) or a list
        * if it is a list, it contains a list of elements defined as previously
        * if the job at position i is not scheduled, it will start after the last
          job at position i-1 whether or not it fails
        * the job can be defined as a tuple of 3 elements, the last one contains options

        The available options are:

        * pre: defines a string to insert at the beginning of a job
        * post: defines a string to insert at the end of a job
        * script: defines a full script if the job to execute is ``custom``

        Example ::

            modules=[  # update anaconda
                    ("standalone [conda_update] [anaconda3]",
                     "H H(0-1) * * 0"),
                    "standalone [conda_update] [anaconda2] [27]",
                    "standalone [local_pypi]",
                    #"standalone [install]",
                    #"standalone [update]",
                    #"standalone [install] [py34]",
                    #"standalone [update] [py34]",
                    #"standalone [install] [winpython]",
                    #"standalone [update] [winpython]",
             # pyquickhelper and others,
             ("pyquickhelper", "H H(2-3) * * 0"),
             ("pysqllike <-- pyquickhelper", None, dict(success_only=True)),
             ["python3_module_template <-- pyquickhelper",
                 "pyquickhelper [27] [anaconda2]"],
             ["pyquickhelper [winpython]",
                 "python3_module_template [27] [anaconda2] <-- pyquickhelper", ],
             ["pymyinstall <-- pyquickhelper", "pyensae <-- pyquickhelper"],
             ["pymmails <-- pyquickhelper", "pyrsslocal <-- pyquickhelper, pyensae"],
             ["pymyinstall [27] [anaconda2] <-- pyquickhelper", "pymyinstall [LONG] <-- pyquickhelper"],
             # update, do not move, it depends on pyquickhelper
             ("pyquickhelper [anaconda3]", "H H(2-3) * * 1"),
             ["pyquickhelper [winpython]", "pysqllike [anaconda3]",
                        "pysqllike [winpython] <-- pyquickhelper",
                        "python3_module_template [anaconda3] <-- pyquickhelper",
                        "python3_module_template [winpython] <-- pyquickhelper",
                        "pymmails [anaconda3] <-- pyquickhelper",
                        "pymmails [winpython] <-- pyquickhelper",
                        "pymyinstall [anaconda3] <-- pyquickhelper",
                        "pymyinstall [winpython] <-- pyquickhelper"],
             ["pyensae [anaconda3] <-- pyquickhelper",
                        "pyensae [winpython] <-- pyquickhelper",
                        "pyrsslocal [anaconda3] <-- pyquickhelper, pyensae",
                        "pyrsslocal [winpython] <-- pyquickhelper"],
             ("pymyinstall [update_modules]",
                        "H H(0-1) * * 5"),
             "pymyinstall [update_modules] [winpython]",
             "pymyinstall [update_modules] [py34]",
             "pymyinstall [update_modules] [anaconda2]",
             "pymyinstall [update_modules] [anaconda3]",
             # py35
             ("pyquickhelper [py34]", "H H(2-3) * * 2"),
             ["pysqllike [py34]",
                        "pymmails [py34] <-- pyquickhelper",
                        "python3_module_template [py34] <-- pyquickhelper",
                        "pymyinstall [py34] <-- pyquickhelper"],
             "pyensae [py34] <-- pyquickhelper",
             "pyrsslocal [py34] <-- pyquickhelper, pyensae",
            ],

        Example::

            from ensae_teaching_cs.automation.jenkins_helper import setup_jenkins_server
            from pyquickhelper.jenkinshelper import JenkinsExt

            engines = dict(Anaconda2=r"C:\\Anaconda2",
                           Anaconda3=r"C:\\Anaconda3",
                           py35=r"c:\\Python35_x64",
                           py36=r"c:\\Python36_x64",
                           default=r"c:\\Python36_x64",
                           custom=r"c:\\CustomPython")

            js = JenkinsExt('http://machine:8080/', "user", "password", engines=engines)

            if True:
                js.setup_jenkins_server(github="sdpython", overwrite = True,
                                        location = r"c:\\jenkins\\pymy")


        Another example::

            import sys
            sys.path.append(r"C:\\<path>\\ensae_teaching_cs\\src")
            sys.path.append(r"C:\\<path>\\pyquickhelper\\src")
            sys.path.append(r"C:\\<path>\\pyensae\\src")
            sys.path.append(r"C:\\<path>\\pyrsslocal\\src")
            from ensae_teaching_cs.automation.jenkins_helper import setup_jenkins_server, JenkinsExt
            js = JenkinsExt("http://<machine>:8080/", <user>, <password>)
            js.setup_jenkins_server(location=r"c:\\jenkins\\pymy", overwrite=True, engines=engines)

        Parameter *credentials* can be a dictionary where the key is
        the git repository. Parameter *dependencies* and *no_dep*
        were removed. Dependencies are now specified
        in the job name using ``<--`` and they exclusively rely
        on pipy (local or remote). Add options for module
        *Build Timeout Plugin*.
        """
        # we do a patch for pyquickhelper
        all_jobs = []
        for jobs in modules:
            jobs = jobs if isinstance(jobs, list) else [jobs]
            for job in jobs:
                if isinstance(job, tuple):
                    job = job[0]
                job = job.split("<--")[0]
                name = self.get_jenkins_job_name(job)
                all_jobs.append(name)
        all_jobs = set(all_jobs)
        if "pyquickhelper" in all_jobs:
            self.PACTHPQ = True
            self.pyquickhelper = os.path.join(
                location, "_pyquickhelper", "src")

        # rest of the function
        if get_jenkins_script is None:
            get_jenkins_script = JenkinsExt.get_jenkins_script

        if github is not None and "https://" not in github:
            github = "https://github.com/" + github + "/"

        deps = []
        created = []
        locations = []
        indexes = dict(order=0, dozen="A")
        counts = {}
        for jobs in modules:
            if isinstance(jobs, tuple):
                if len(jobs) == 0:
                    raise ValueError(
                        "Empty jobs in the list.")  # pragma: no cover
                if jobs[0] == "yml" and len(jobs) != 3:
                    raise ValueError(  # pragma: no cover
                        "If it is a yml jobs, the tuple should contain 3 elements: ('yml', filename, schedule or None or dictionary).\n" +
                        "Not: {0}".format(jobs))

            cre, ds, locs = self._setup_jenkins_server_modules_loop(
                jobs=jobs, counts=counts,
                get_jenkins_script=get_jenkins_script,
                location=location, adjust_scheduler=adjust_scheduler,
                add_environ=add_environ, yml_engine=yml_engine,
                overwrite=overwrite, prefix=prefix,
                credentials=credentials, github=github,
                disable_schedule=disable_schedule, jenkins_server=self,
                update=update, indexes=indexes, deps=deps)
            created.extend(cre)
            locations.extend(locs)
            deps.extend(ds)
        return created

    def _setup_jenkins_server_modules_loop(self, jobs, counts, get_jenkins_script, location, adjust_scheduler,
                                           add_environ, yml_engine, overwrite, prefix, credentials, github,
                                           disable_schedule, jenkins_server, update, indexes, deps):
        if not isinstance(jobs, list):
            jobs = [jobs]
        indexes["unit"] = 0
        new_dep = []
        created = []
        locations = []
        for i, job in enumerate(jobs):
            indexes["unit"] += 1
            cre, dep, loc = self._setup_jenkins_server_job_iteration(
                job, counts=counts,
                get_jenkins_script=get_jenkins_script,
                location=location, adjust_scheduler=adjust_scheduler,
                add_environ=add_environ, yml_engine=yml_engine,
                overwrite=overwrite, prefix=prefix,
                credentials=credentials, github=github,
                disable_schedule=disable_schedule,
                jenkins_server=jenkins_server,
                update=update, indexes=indexes,
                deps=deps, i=i)
            created.extend(cre)
            new_dep.extend(dep)
            locations.extend(loc)
            if len(new_dep) > 20000:
                raise JenkinsExtException(  # pragma: no cover
                    "unreasonable number of dependencies: {0}".format(len(new_dep)))
        return created, new_dep, locations

    def _setup_jenkins_server_job_iteration(self, job, get_jenkins_script, location, adjust_scheduler,
                                            add_environ, yml_engine, overwrite, prefix, credentials, github,
                                            disable_schedule, jenkins_server, update, indexes, deps, i, counts):
        order = indexes["order"]
        dozen = indexes["dozen"]
        unit = indexes["unit"]
        new_dep = []
        created = []
        locations = []

        if isinstance(job, tuple):
            if len(job) < 2:
                raise JenkinsJobException(  # pragma: no cover
                    "the tuple must contain at least two elements:\nJOB:"
                    "\n" + str(job))

            if job[0] == "yml":
                is_yml = True
                job = job[1:]
            else:
                is_yml = False

            # we extract options if any
            if len(job) == 3:
                options = job[2]
                if not isinstance(options, dict):
                    raise JenkinsJobException(  # pragma: no cover
                        "The last element of the tuple must be a dictionary:\nJOB:\n" + str(options))
            else:
                options = {}

            # job and scheduler
            job, scheduler_options = job[:2]
            if isinstance(scheduler_options, dict):
                scheduler = scheduler_options.get('scheduler', None)
            else:
                scheduler = scheduler_options
                scheduler_options = None
            if scheduler is not None:
                order = 1
                if counts.get(dozen, 0) > 0:
                    dozen = chr(ord(dozen) + 1)
            else:
                if i == 0:
                    order += 1
        else:
            scheduler = None
            if i == 0:
                order += 1
            options = {}
            is_yml = False

        # all schedule are disabled if disable_schedule is True
        if disable_schedule:
            scheduler = None
        counts[dozen] = counts.get(dozen, 0) + 1

        # success_only
        if "success_only" in options:
            success_only = options["success_only"]
            del options["success_only"]
        else:
            success_only = False

        # timeout
        if "timeout" in options:
            timeout = options["timeout"]
            del options["timeout"]
        else:
            timeout = _timeout_default

        # script
        if not is_yml:
            script = get_jenkins_script(self, job)

        # we process the repository
        if "repo" in options:
            gitrepo = options["repo"]
            options = options.copy()
            del options["repo"]
        else:
            gitrepo = github

        # add a description to the job
        description = ["%s%02d%02d" % (dozen, order, unit)]
        if scheduler is not None:
            description.append(scheduler)
        try:
            description = " - ".join(description)
        except TypeError as e:  # pragma: no cover
            raise TypeError("Issue with {}.".format(description)) from e

        # credentials
        if isinstance(credentials, dict):  # pragma: no cover
            cred = credentials.get(gitrepo, None)
            if cred is None:
                cred = credentials.get("default", "")
        else:
            cred = credentials

        if not is_yml:
            mod = job.split()[0]
            name = self.get_jenkins_job_name(job)
            jname = prefix + name

            try:
                j = jenkins_server.get_job_config(
                    jname) if not jenkins_server._mock else None
            except jenkins.NotFoundException:  # pragma: no cover
                j = None
            except jenkins.JenkinsException as e:  # pragma: no cover
                raise JenkinsExtException(
                    "unable to retrieve job config for job={0}, name={1}".format(job, jname)) from e

            if overwrite or j is None:

                update_job = False
                if j is not None:  # pragma: no cover
                    if update:
                        update_job = True
                    else:
                        self.fLOG("[jenkins] delete job", jname)
                        jenkins_server.delete_job(jname)

                # we post process the script
                script = self.process_options(script, options)

                # if there is a script
                if script is not None and len(script) > 0:
                    new_dep.append(name)
                    upstreams = [] if (
                        scheduler is not None) else deps[-1:]
                    self.fLOG("[jenkins] create job", jname, " - ", job,
                              " : ", scheduler, " / ", upstreams)

                    # set up location
                    if location is None:
                        loc = None  # pragma: no cover
                    else:
                        if "_" in jname:
                            loc = os.path.join(location, name, jname)
                        else:
                            loc = os.path.join(location, name, "_" + jname)

                    if mod in ("standalone", "custom"):
                        gpar = None
                    elif gitrepo is None:
                        raise JenkinsJobException(  # pragma: no cover
                            "gitrepo cannot must not be None if standalone or "
                            "custom is not defined,\njob=" + str(job))
                    elif gitrepo.endswith(".git"):
                        gpar = gitrepo
                    else:
                        gpar = gitrepo + "%s/" % mod

                    # create the template
                    r = jenkins_server.create_job_template(jname, git_repo=gpar, upstreams=upstreams, script=script,
                                                           location=loc, scheduler=scheduler, py27="[27]" in job,
                                                           description=description, credentials=cred, success_only=success_only,
                                                           update=update_job, timeout=timeout, adjust_scheduler=adjust_scheduler,
                                                           mails=self.mails)

                    # check some inconsistencies
                    if "[27]" in job and "Anaconda3" in script:
                        raise JenkinsExtException(  # pragma: no cover
                            "incoherence for job {0}, script:\n{1}".format(job, script))

                    locations.append((job, loc))
                    created.append((job, name, loc, job, r))
                else:  # pragma: no cover
                    # skip the job
                    loc = None if location is None else os.path.join(
                        location, jname)
                    locations.append((job, loc))
                    self.fLOG("[jenkins] skipping",
                              job, "location", loc)
            elif j is not None:
                new_dep.append(name)

        else:
            # yml file
            if location is not None:
                options["root_path"] = location
            for k, v in self.engines.items():
                if k not in options:
                    options[k] = v
            jobdef = job[0] if isinstance(job, tuple) else job

            done = {}
            for aj, name, var in enumerate_processed_yml(
                    jobdef, context=options, engine=yml_engine,
                    add_environ=add_environ, server=self, git_repo=gitrepo,
                    scheduler=scheduler, description=description, credentials=cred,
                    success_only=success_only, timeout=timeout, platform=self.platform,
                    adjust_scheduler=adjust_scheduler, overwrite=overwrite,
                    build_location=location, mails=self.mails,
                    job_options=scheduler_options):
                if name in done:
                    s = "A name '{0}' was already used for a job, from:\n{1}\nPROCESS:\n{2}"  # pragma: no cover
                    raise ValueError(  # pragma: no cover
                        s.format(name, jobdef, "\n".join(sorted(set(done.keys())))))
                done[name] = (aj, name, var)
                loc = None if location is None else os.path.join(
                    location, name)
                self.fLOG("[jenkins] adding i={2}: '{0}' var='{1}'".format(
                    name, var, len(created)))
                created.append((job, name, loc, job, aj))

        indexes["order"] = order
        indexes["dozen"] = dozen
        indexes["unit"] = unit
        return created, new_dep, locations
