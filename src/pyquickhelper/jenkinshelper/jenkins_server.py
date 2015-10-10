"""
@file
@brief Extends Jenkins Server from `python-jenkins <http://python-jenkins.readthedocs.org/en/latest/>`_

.. versionadded:: 1.1
"""

import os
import sys
import jenkins
import socket
import hashlib
import re
from ..loghelper.flog import noLOG
from ..pycode.windows_scripts import windows_jenkins, windows_jenkins_27, windows_jenkins_any
from ..pycode.build_helper import private_script_replacements
from .jenkins_exceptions import JenkinsExtException, JenkinsJobException
from .jenkins_server_template import _config_job, _trigger_up, _trigger_time, _git_repo, _task_batch


_default_engine_paths = {
    "windows": {
        "__PY35__": "__PY35__",
        "__PY35_X64__": "__PY35_X64__",
        "__PY34__": "__PY34__",
        "__PY34_X64__": "__PY34_X64__",
        "__PY27_X64__": "__PY27_X64__",
    },
}

modified_windows_jenkins = private_script_replacements(
    windows_jenkins, "__MODULE__", None, "__PORT__", raise_exception=False,
    default_engine_paths=_default_engine_paths)
modified_windows_jenkins_27 = private_script_replacements(
    windows_jenkins_27, "__MODULE__", None, "__PORT__", raise_exception=False,
    default_engine_paths=_default_engine_paths)
modified_windows_jenkins_any = windows_jenkins_any \
    .replace("virtual_env_suffix=%2", "virtual_env_suffix=___SUFFIX__")


class JenkinsExt(jenkins.Jenkins):

    """
    extensions for the `Jenkins <https://jenkins-ci.org/>`_ server
    based on module `python-jenkins <http://pythonhosted.org/python-jenkins/>`_

    .. index:: Jenkins, Jenkins extensions

    some useful Jenkins extensions:

    * `Credentials Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Credentials+Plugin>`_
    * `Extrea Column Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Extra+Columns+Plugin>`_
    * `Git Client Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Git+Client+Plugin>`_
    * `GitHub Client Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Github+Plugin>`_
    * `GitLab Client Plugin <https://wiki.jenkins-ci.org/display/JENKINS/GitLab+Plugin>`_
    * `Matrix Project Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Matrix+Project+Plugin>`_
    * `Build Pipeline Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Build+Pipeline+Plugin>`_

    .. versionchanged:: 1.3
        The whole class was changed to defined many different engines.
    """

    _config_job = _config_job
    _trigger_up = _trigger_up
    _trigger_time = _trigger_time
    _git_repo = _git_repo
    _task_batch = _task_batch

    def __init__(self, url,
                 username=None,
                 password=None,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 mock=False,
                 engines=None,
                 platform=sys.platform,
                 pypi_port=8067,
                 fLOG=noLOG):
        """
        constructor

        @param      url         url of the server
        @param      username    username
        @param      password    password
        @param      timeout     timeout
        @param      mock        True by default, if False, avoid talking to the server
        @param      engines     list of Python engines *{name: path to python.exe}*
        @param      platform    platform of the Jenkins server
        @param      pypi_port   pypi port used for the documentation server
        @param      fLOG        logging function

        .. versionchanged:: 1.3
            Parameter *engines*, *fLOG* were added to rationalize Python engines.
        """
        jenkins.Jenkins.__init__(self, url, username, password)
        self._mock = mock
        self.platform = platform
        self.pypi_port = pypi_port
        self.fLOG = fLOG
        if engines is None:
            engines = {"default": os.path.dirname(sys.executable)}
        self.engines = engines
        for k, v in self.engines.items():
            if v.endswith(".exe"):
                raise FileNotFoundError("{}:{} is not a folder".format(k, v))
            if " " in v:
                raise JenkinsJobException(
                    "No space allowed in engine path: " + v)

    @property
    def Engines(self):
        """
        @return the available engines
        """
        return self.engines

    def jenkins_open(self, req, add_crumb=True):
        '''
        Overloads the same method from module jenkins to replace string by bytes

        @param      req             see `jenkins API <https://python-jenkins.readthedocs.org/en/latest/api.html>`_
        @param      add_crumb       see `jenkins API <https://python-jenkins.readthedocs.org/en/latest/api.html>`_
        '''
        if self._mock:
            raise JenkinsExtException("mocking server, cannot be open")

        try:
            if self.auth:
                req.add_header('Authorization', self.auth)
            if add_crumb:
                self.maybe_add_crumb(req)
            with jenkins.urlopen(req, timeout=self.timeout) as u:
                response = u.read()
            if response is None:
                raise jenkins.EmptyResponseException(
                    "Error communicating with server[%s]: "
                    "empty response" % self.server)
            response = str(response, encoding="utf-8")  # change for Python 3
            return response
        except jenkins.HTTPError as e:
            # Jenkins's funky authentication means its nigh impossible to
            # distinguish errors.
            if e.code in [401, 403, 500]:
                # six.moves.urllib.error.HTTPError provides a 'reason'
                # attribute for all python version except for ver 2.6
                # Falling back to HTTPError.msg since it contains the
                # same info as reason
                raise jenkins.JenkinsException(
                    'Error in request. ' +
                    'Possibly authentication failed [%s]: %s' % (
                        e.code, e.msg)
                )
            elif e.code == 404:
                raise jenkins.NotFoundException(
                    'Requested item could not be found')
            else:
                raise
        except jenkins.URLError as e:
            raise jenkins.JenkinsException('Error in request: %s' % (e.reason))

    def delete_job(self, name):
        '''Delete Jenkins job permanently.

        :param name: Name of Jenkins job, ``str``
        '''
        if self._mock:
            return

        self.jenkins_open(jenkins.Request(
            self.server + jenkins.DELETE_JOB % self._get_encoded_params(locals()), b''))
        if self.job_exists(name):
            raise JenkinsExtException('delete[%s] failed' % (name))

    def get_jobs(self):
        """
        Get list of all jobs recursively to the given folder depth,
        see `get_all_jobs <https://python-jenkins.readthedocs.org/en/latest/api.html#jenkins.Jenkins.get_all_jobs>`_.

        @return                     list of jobs, ``[ { str: str} ]``

        .. versionadded:: 1.3
        """
        return jenkins.Jenkins.get_jobs(self)

    def delete_all_jobs(self):
        """
        delete all jobs permanently.

        @param      fLOG        logging function
        @return                 list of deleted jobs

        .. versionadded:: 1.3
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
        infer a name for the jenkins job

        @param      job     str
        @return             name
        """
        if job.startswith("custom "):
            return job.replace(" ", "_").replace("[", "").replace("]", "")
        else:
            def_prefix = ["doc", "setup", "setup_big"]
            def_prefix.extend(self.engines.keys())
            for prefix in def_prefix:
                p = "[%s]" % prefix
                if p in job:
                    job = p + " " + job.replace(" " + p, "")
            return job.replace(" ", "_").replace("[", "").replace("]", "")

    def get_engine_from_job(self, job, return_key=False):
        """
        extract the engine from the job definition,
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
            raise JenkinsJobException("unable to find engine in job {}, available: {}".format(
                job, ", ".join(self.engines.keys())))
        else:
            # self.fLOG("    {}={}   ---  {}                   --- {}".format(key, res, job, ",".join(self.engines.keys())))
            return (res, key) if return_key else res

    def get_cmd_standalone(self, job):
        """
        Custom command for jenkins (such as updating conda)

        @param      job             module and options
        @return                     script
        """
        spl = job.split()
        if spl[0] != "standalone":
            raise JenkinsExtException(
                "the job should start by standalone: " + job)

        if self.platform.startswith("win"):
            # windows
            if "[conda_update]" in spl:
                cmd = "__ENGINE__\\Scripts\\conda update -y --all"
            elif "[local_pypi]" in spl:
                cmd = "if not exist ..\\local_pypi mkdir ..\\local_pypi"
                cmd += "\nif not exist ..\\..\\local_pypi\\local_pypi_server mkdir ..\\..\\local_pypi\\local_pypi_server"
                cmd += "\necho __ENGINE__\\..\\Scripts\\pypi-server.exe -u -p __PORT__ --disable-fallback ..\\..\\local_pypi\\local_pypi_server > ..\\..\\local_pypi\\local_pypi_server\\start_local_pypi.bat"
                cmd = cmd.replace("__PORT__", str(self.pypi_port))
            elif "[update]" in spl:
                cmd = "__ENGINE__\\python -u -c \"from pymyinstall.packaged import update_all;update_all(temp_folder='build/update_modules', verbose=True)\""
            elif "[install]" in spl:
                cmd = "__ENGINE__\\python -u -c \"from pymyinstall.packaged import install_all;install_all(temp_folder='build/update_modules', verbose=True)\""
            else:
                raise JenkinsExtException("cannot interpret job: " + job)

            engine = self.get_engine_from_job(job)
            cmd = cmd.replace("__ENGINE__", engine)
            return cmd
        else:
            raise NotImplementedError()

    @staticmethod
    def get_cmd_custom(job):
        """
        Custom script for jenkins

        @param      job             module and options
        @return                     script

        .. versionadded:: 1.2
        """
        spl = job.split()
        if spl[0] != "custom":
            raise JenkinsExtException(
                "the job should start by custom: " + job)
        # we expect __SCRIPTOPTIONS__ to be replaced by a script later on
        return "__SCRIPTOPTIONS__"

    @staticmethod
    def hash_string(s, l=10):
        """
        hash a string

        @param      s       string
        @param      l       cut the string to the first *l* character
        @return             hashed string
        """
        m = hashlib.md5()
        m.update(s.encode("ascii"))
        r = m.hexdigest().upper()
        return r if (l == -1 or len(r) <= l) else r[:l]

    def get_jenkins_script(self, job):
        """
        build the jenkins script for a module and its options

        @param      job             module and options
        @return                     script

        Method @see me setup_jenkins_server describes which tags
        this method can interpret.

        The method allow command such as ``[custom...]``, they will be
        run in a virtual environment as ``setup.py custom...``.

        job can be ``empty``, in that case, this function returns an empty string.
        """
        def replacements(cmd, engine, python, suffix):
            res = cmd.replace("__ENGINE__", engine) \
                     .replace("__PYTHON__", python) \
                     .replace("__SUFFIX__", suffix + "_" + job_hash)  \
                     .replace("__PORT__", str(self.pypi_port))  \
                     .replace("__MODULE__", module_name)  # suffix for the virtual environment and module name
            if "[27]" in job:
                res = res.replace("__PYTHON27__", python)
                if "__DEFAULTPYTHON__" in res:
                    if "default" not in self.engines:
                        raise JenkinsExtException(
                            "a default engine (Python 3.4) must be defined for script using Python 27, job={}".format(job))
                res = res.replace("__DEFAULTPYTHON__",
                                  os.path.join(self.engines["default"], "python"))

            if "__" in res:
                raise JenkinsJobException(
                    "uanble to interpret command line: {}\n{}".format(cmd, res))

            # patch to avoid installing pyquickhelper when testing
            # pyquickhelper
            if module_name == "pyquickhelper":
                lines = res.split("\n")
                for i, line in enumerate(lines):
                    if "/simple/ pyquickhelper" in line and "--find-links http://localhost" in line:
                        lines[i] = ""
                res = "\n".join(lines)

            return res

        spl = job.split()
        module_name = spl[0]
        job_hash = JenkinsExt.hash_string(job)

        if self.platform.startswith("win"):
            # windows
            engine, namee = self.get_engine_from_job(job, True)
            python = os.path.join(engine, "python.exe")

            if len(spl) == 1:
                script = modified_windows_jenkins
                if not isinstance(script, list):
                    script = [script]
                return [replacements(s, engine, python, namee + "_" + job_hash) for s in script]

            elif len(spl) == 0:
                raise ValueError("job is empty")

            elif spl[0] == "standalone":
                # conda update
                return self.get_cmd_standalone(job)

            elif spl[0] == "custom":
                # custom script
                return JenkinsExt.get_cmd_custom(job)

            elif spl[0] == "empty":
                return ""

            elif len(spl) in [2, 3, 4]:
                # step 1: define the script

                if "[test_local_pypi]" in spl:
                    cmd = "auto_setup_test_local_pypi.bat __PYTHON__"
                elif "[update_modules]" in spl:
                    cmd = "__PYTHON__ setup.py build_script\nauto_update_modules.bat __PYTHON__"
                elif "[LONG]" in spl:
                    cmd = modified_windows_jenkins_any.replace(
                        "__COMMAND__", "unittests_LONG")
                elif "[SKIP]" in spl:
                    cmd = modified_windows_jenkins_any.replace(
                        "__COMMAND__", "unittests_SKIP")
                elif "[27]" in spl:
                    cmd = modified_windows_jenkins_27
                    if not isinstance(cmd, list):
                        cmd = [cmd]
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
                    cmd = modified_windows_jenkins_any.replace(
                        "__COMMAND__", "build_sphinx")
                elif "[setup]" in spl:
                    # setup
                    cmd = "__PYTHON__ setup.py build_script\nauto_cmd_build_dist.bat __PYTHON__"
                elif "[setup_big]" in spl:
                    # setup + [big]
                    cmd = "__PYTHON__ setup.py build_script\nauto_cmd_build_dist.bat __PYTHON__ [big]"
                else:
                    cmd = modified_windows_jenkins
                    for pl in spl[1:]:
                        if pl.startswith("[custom_") and pl.endswith("]"):
                            cus = pl.strip("[]")
                            cmd = modified_windows_jenkins_any.replace(
                                "__COMMAND__", cus)

                # step 2: replacement (python __PYTHON__, virtual environnement
                # __SUFFIX__)

                cmds = cmd if isinstance(cmd, list) else [cmd]
                res = []
                for cmd in cmds:
                    cmd = replacements(cmd, engine, python,
                                       namee + "_" + job_hash)
                    res.append(cmd)

                return res
            else:
                raise ValueError("unable to interpret: " + job)
        else:
            # linux
            raise NotImplementedError("On Linux, unable to interpret: " + job)

    @staticmethod
    def get_dependencies_path(job, locations, dependencies):
        """
        return the depeencies to add to the job based on the name and the past locations

        @param      job             job description
        @param      locations       list of 2-uple ( job description, location )
        @param      dependencies    None or list of dependencies
        @return                     dictionary { module, location }
        """
        if dependencies is None:
            return {}

        py27 = "[27]" in job

        res = {}
        for dep in dependencies:
            for j, loc in locations:

                if loc is None:
                    raise JenkinsExtException("location is None for job {0}, dependency {1}".format(job, j) +
                                              "\nyou need to set up the location if there are dependencies")
                n = j.split()[0]
                p27 = "[27]" in j

                if n == dep and p27 == py27:
                    if not p27:
                        res[dep] = os.path.join(loc, "src")
                    else:
                        res[dep] = os.path.join(loc, "dist_module27", "src")
                    break

        if len(dependencies) != len(res) and "[-nodep]" not in job:
            pattern = "lower number of dependencies for job: {3}\nrequested:\n{0}\nFOUND:\n{1}\nLOCATIONS:\n{2}"
            raise Exception(pattern.format(", ".join(dependencies), "\n".join(
                "{0} : {1}".format(k, v) for k, v in sorted(res.items())),
                "\n".join("{0} : {1}".format(k, v) for k, v in locations),
                job))

        return res

    def create_job_template(self,
                            name,
                            git_repo,
                            credentials="",
                            upstreams=None,
                            script=None,
                            location=None,
                            keep=30,
                            dependencies=None,
                            scheduler=None,
                            py27=False,
                            description=None,
                            default_engine_paths=None,
                            success_only=False,
                            update=False
                            ):
        """
        add a job to the jenkins server

        @param      name                    name
        @param      credentials             credentials
        @param      git_repo                git repository
        @param      upstreams               the build must run after... (even if failures),
                                            must be None in that case
        @param      script                  script to execute or list of scripts
        @param      keep                    number of buils to keep
        @param      location                location of the build
        @param      dependencies            to add environment variable before
                                            and to set them to empty after the script is done
        @param      scheduler               add a schedule time (upstreams must be None in that case)
        @param      py27                    python 2.7 (True) or Python 3 (False)
        @param      description             add a description to the job
        @param      default_engine_paths    define the default location for python engine, should be dictionary *{ engine: path }*, see below.
        @param      success_only            only triggers the job if the previous one was successful
        @param      update                  update the job instead of creating it

        The job can be modified on Jenkins. To add a time trigger::

            H H(13-14) * * *

        Same trigger but once every week and not every day (Sunday for example)::

            H H(13-14) * * 0

        .. versionchanged:: 1.2
            Parameter *success_only* was added to prevent a job from running if the previous one failed.
            Options *success_only* must be specified.
            Parameter *update* was added to update a job instead of creating it.

        """
        if script is None:
            if self.platform.startswith("win"):
                if default_engine_paths is None and "default" in self.engines:
                    ver = "__PY%d%d__" % sys.version_info[:2]
                    pat = os.path.join(self.engines["default"], "python")
                    default_engine_paths = dict(
                        windows={ver: pat, "__PYTHON__": pat})

                script = private_script_replacements(
                    windows_jenkins, "____", None, "____", raise_exception=False,
                    platform=self.platform,
                    default_engine_paths=default_engine_paths)

                hash = JenkinsExt.hash_string(script)
                script = script.replace("__SUFFIX__", hash)
            else:
                raise JenkinsExtException("no default script for linux")

        if upstreams is not None and len(upstreams) > 0 and scheduler is not None:
            raise JenkinsExtException(
                "upstreams and scheduler cannot be not null at the same time: {0}".format(name))

        if upstreams is not None and len(upstreams) > 0:
            trigger = JenkinsExt._trigger_up \
                .replace("__UP__", ",".join(upstreams)) \
                .replace("__FAILURE__", "SUCCESS" if success_only else "FAILURE") \
                .replace("__ORDINAL__", "0" if success_only else "2") \
                .replace("__COLOR__", "BLUE" if success_only else "RED")
        elif scheduler is not None:
            trigger = JenkinsExt._trigger_time.replace(
                "__SCHEDULER__", scheduler)
        else:
            trigger = ""

        if dependencies is None:
            dependencies = {}

        cmd = "set" if self.platform.startswith("win") else "export"

        if not isinstance(script, list):
            script = [script]

        underscore = re.compile("(__[A-Z_]+__)")

        # we modify the scripts
        script_mod = []
        for scr in script:
            search = underscore.search(scr)
            if search:
                mes = "script still contains __\ndefault_engine_paths: {}\nfound: {}\nscr:\nSCRIPT:\n{}\n".format(
                    default_engine_paths, search.groups()[0], scr, str(script))
                raise ValueError(mes)

            if len(dependencies) > 0:
                rows = []
                end = []
                for k, v in sorted(dependencies.items()):
                    if py27:
                        rows.append("{0} {1}27={2}".format(cmd, k.upper(), v))
                        rows.append("{0} {1}=".format(cmd, k.upper()))
                        end.append("{0} {1}27=".format(cmd, k.upper()))
                    else:
                        rows.append("{0} {1}={2}".format(cmd, k.upper(), v))
                        rows.append("{0} {1}27=".format(cmd, k.upper()))
                        end.append("{0} {1}=".format(cmd, k.upper()))
                rows.append(scr)
                rows.extend(end)
                scr = "\n".join(rows)
            else:
                pass

            script_mod.append(scr)

        # repo
        if git_repo is None:
            git_repo_xml = ""
        else:
            git_repo_xml = JenkinsExt._git_repo \
                .replace("__GITREPO__", git_repo) \
                .replace("__CRED__", "<credentialsId>%s</credentialsId>" % credentials)

        # scripts
        tasks = [JenkinsExt._task_batch.replace(
            "__SCRIPT__", s) for s in script_mod]

        # location
        location = "" if location is None else "<customWorkspace>%s</customWorkspace>" % location

        # replacements
        conf = JenkinsExt._config_job
        rep = dict(__KEEP__=str(keep),
                   __TASKS__="\n".join(tasks),
                   __TRIGGER__=trigger,
                   __LOCATION__=location,
                   __DESCRIPTION__="" if description is None else description,
                   __GITREPOXML__=git_repo_xml)

        for k, v in rep.items():
            conf = conf.replace(k, v)

        if self._mock:
            return conf
        elif update:
            return self.reconfig_job(name, conf)
        else:
            return self.create_job(name, conf)

    def process_options(self, script, options):
        """
        post process a script inserted in a job definition

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
                script = [v + "\n" + _ for _ in script]
            elif k == "post_set":
                script = [_ + "\n" + v for _ in script]
            elif k == "script":
                script = [_.replace("__SCRIPTOPTIONS__", v) for _ in script]
            else:
                raise JenkinsJobException(
                    "unable to interpret options: " + str(options))
        return script

    def setup_jenkins_server(self,
                             github,
                             modules,
                             get_jenkins_script=None,
                             overwrite=False,
                             location=None,
                             no_dep=False,
                             prefix="",
                             dependencies=None,
                             credentials="",
                             update=True):
        """
        Set up many jobs on Jenkins

        @param      js_url                  url or jenkins server (specially if you need credentials)
        @param      github                  github account if it does not start with *http://*,
                                            the link to git repository of the project otherwise
        @param      modules                 modules for which to generate the
        @param      get_jenkins_script      see @see me get_jenkins_script (default value if this parameter is None)
        @param      overwrite               do not create the job if it already exists
        @param      location                None for default or a local folder
        @param      no_dep                  if True, do not add dependencies
        @param      prefix                  add a prefix to the name
        @param      dependencies            some modules depend on others also being tested, this parameter gives the list
        @param      credentials             credentials to use for the job (string or dictionary)
        @param      update                  update job instead of deleting it if the job already exists
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
        * `Python <https://wiki.jenkins-ci.org/display/JENKINS/Python+Plugin>`_
        * `Python Wrapper Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Python+Wrapper+Plugin>`_


        Tag description:

        * ``[engine]``: to use this specific engine (Python path)
        * ``[27]``: run with python 2.7
        * ``[-nodep]``: do not check dependencies
        * ``[LONG]``: run longer unit tests (files start by ``test_LONG``)
        * ``[SKIP]``: run skipped unit tests (files start by ``test_SKIP``)
        * ``[custom.+]``: run ``setup.py <custom.+>`` in a virtual environment

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
                        ("standalone [conda_update]", "H H(8-9) * * 0"),
                        "standalone [conda_update27]",
                        "standalone [local_pypi]",
                        "standalone [install]",
                        "standalone [update]",
                        # pyquickhelper and others,
                       ("pyquickhelper", "H H(10-11) * * 0"),
                        "pymyinstall",
                        ["pyquickhelper [anaconda]", "pyquickhelper [winpython]",
                        "pyquickhelper [27] [anaconda2]"],
                      ["pyensae", ],
                      ["pymmails", "pysqllike", "pyrsslocal", "pymyinstall [27] [anaconda2]",
                       "python3_module_template", "pyensae [anaconda]", "pyensae [winpython]"],
                      ["pymmails [anaconda]", "pysqllike [anaconda]", "pyrsslocal [anaconda]",
                       "python3_module_template [anaconda]", "python3_module_template [27] [anaconda2]",
                       "pymyinstall [LONG]"],
                      # update modules
                      ("pymyinstall [update_modules]", "H H(10-11) * * 5"),
                      # actuariat
                      [("actuariat_python", "H H(12-13) * * 0")],
                      ["actuariat_python [winpython]",
                       "actuariat_python [anaconda]"],
                      # code_beatrix
                      ("code_beatrix", "H H(14-15) * * 0"),
                      ["code_beatrix [winpython]",
                       "code_beatrix [anaconda]"],
                      # teachings
                      ("ensae_teaching_cs", "H H(15-16) * * 0"),
                      ["ensae_teaching_cs [winpython]",
                       "ensae_teaching_cs [anaconda]"],
                      "ensae_teaching_cs [custom_left]",
                      ["ensae_teaching_cs [winpython] [custom_left]",
                       "ensae_teaching_cs [anaconda] [custom_left]", ],
                      ],

        Example::

            from ensae_teaching_cs.automation.jenkins_helper import setup_jenkins_server
            from pyquickhelper.jenkinshelper import JenkinsExt

            engines = dict(Anaconda2=r"C:\\Anaconda2",
                           Anaconda3=r"C:\\Anaconda3",
                           py34=r"c:\\Python34_x64",
                           py35=r"c:\\Python35_x64",
                           custom=r"c:\\CustomPython")

            js = JenkinsExt('http://machine:8080/', "user", "password", engines=engines)

            if True:
                js.setup_jenkins_server(github="sdpython",
                                    overwrite = True,
                                    location = r"c:\\jenkins\\pymy")


        For WinPython, version 3.4.3+ is mandatory to get the latest version of IPython/Jupyter.

        Another example::

            import sys
            sys.path.append(r"C:\\<path>\\ensae_teaching_cs\\src")
            sys.path.append(r"C:\\<path>\\pyquickhelper\\src")
            sys.path.append(r"C:\\<path>\\pyensae\\src")
            sys.path.append(r"C:\\<path>\\pyrsslocal\\src")
            from ensae_teaching_cs.automation.jenkins_helper import setup_jenkins_server, JenkinsExt
            js = JenkinsExt("http://<machine>:8080/", <user>, <password>)
            js.setup_jenkins_server(location=r"c:\\jenkins\\pymy",
                    overwrite=True,
                    engines=engines)

        .. versionchanged:: 1.2
            Parameter *update* was added.

        .. versionchanged:: 1.3
            Parameter *credential* can be a dictionary where the key is
            the git repository.
        """
        if get_jenkins_script is None:
            get_jenkins_script = JenkinsExt.get_jenkins_script

        if dependencies is None:
            dependencies = {}

        js = self

        if github is not None and "https://" not in github:
            github = "https://github.com/" + github + "/"

        dep = []
        created = []
        locations = []
        order = 0
        dozen = "A"
        counts = {}
        for jobs in modules:

            if not isinstance(jobs, list):
                jobs = [jobs]

            unit = 0
            new_dep = []
            for i, job in enumerate(jobs):
                unit += 1

                if isinstance(job, tuple):
                    if len(job) < 2:
                        raise JenkinsJobException(
                            "the tuple must contain at least two elements:\nJOB:\n" + str(job))

                    # we extract options if any
                    if len(job) == 3:
                        options = job[2]
                        if not isinstance(options, dict):
                            raise JenkinsJobException(
                                "the last element of the tuple must be a dictionary:\nJOB:\n" + str(options))
                    else:
                        options = {}

                    # job and scheduler
                    job, scheduler = job[:2]
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

                counts[dozen] = counts.get(dozen, 0) + 1

                mod = job.split()[0]
                name = self.get_jenkins_job_name(job)
                jname = prefix + name

                try:
                    j = js.get_job_config(jname) if not js._mock else None
                except jenkins.NotFoundException:
                    j = None
                except jenkins.JenkinsException as e:
                    raise JenkinsExtException(
                        "unable to retrieve job config for job={0}, name={1}".format(job, jname)) from e

                if overwrite or j is None:

                    update_job = False
                    if j is not None:
                        if update:
                            update_job = True
                        else:
                            self.fLOG("[jenkins] delete job", jname)
                            js.delete_job(jname)

                    # success_only
                    if "success_only" in options:
                        success_only = options["success_only"]
                        del options["success_only"]
                    else:
                        success_only = False

                    # script
                    script = get_jenkins_script(self, job)

                    # we process the repository
                    if "repo" in options:
                        gitrepo = options["repo"]
                        options = options.copy()
                        del options["repo"]
                    else:
                        gitrepo = github

                    # we post process the script
                    script = self.process_options(script, options)

                    # if there is a script
                    if script is not None and len(script) > 0:
                        new_dep.append(name)
                        upstreams = [] if (
                            no_dep or scheduler is not None) else dep[-1:]
                        self.fLOG("[jenkins] create job", jname, " - ", job,
                                  " : ", scheduler, " / ", upstreams)
                        loc = None if location is None else os.path.join(
                            location, jname)

                        deps = JenkinsExt.get_dependencies_path(
                            job, locations, dependencies.get(mod, None))

                        # add a description to the job
                        description = ["%s%02d%02d" % (dozen, order, unit)]
                        if scheduler is not None:
                            description.append(scheduler)
                        description = " - ".join(description)

                        if mod in ("standalone", "custom"):
                            gpar = None
                        elif gitrepo is None:
                            raise JenkinsJobException(
                                "gitrepo cannot be none if standalone is not defined,\njob=" + str(job))
                        elif gitrepo.endswith(".git"):
                            gpar = gitrepo
                        else:
                            gpar = gitrepo + "%s/" % mod

                        if isinstance(credentials, dict):
                            cred = credentials.get(gitrepo, None)
                            if cred is None:
                                cred = credentials.get("default", "")
                        else:
                            cred = credentials

                        # create the template
                        r = js.create_job_template(jname,
                                                   git_repo=gpar,
                                                   upstreams=upstreams,
                                                   script=script,
                                                   location=loc,
                                                   dependencies=deps,
                                                   scheduler=scheduler,
                                                   py27="[27]" in job,
                                                   description=description,
                                                   credentials=cred,
                                                   success_only=success_only,
                                                   update=update_job)

                        # check some inconsistencies
                        if "[27]" in job and "Anaconda3" in script:
                            raise JenkinsExtException(
                                "incoherence for job {0}, script:\n{1}\npaths:\n{2}".format(job, script))

                        locations.append((job, loc))
                        created.append((job, name, loc, job, r))
                    else:
                        # skip the job
                        loc = None if location is None else os.path.join(
                            location, jname)
                        locations.append((job, loc))
                        self.fLOG("[jenkins] skipping", job, "location", loc)

                elif j is not None:
                    new_dep.append(name)

            dep = new_dep

        return created
