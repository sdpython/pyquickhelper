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
from ..loghelper.flog import noLOG


from ..pycode.windows_scripts import windows_jenkins, windows_jenkins_27, windows_jenkins_any
from ..pycode.build_helper import private_script_replacements, choose_path

_default_engine_paths = {
    "windows": {
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


class JenkinsExtException(Exception):

    """
    exception for the class JenkinsExt
    """
    pass


class JenkinsExtPyException(Exception):

    """
    exception for the class JenkinsExt, when a distribution is not available
    """
    pass


class JenkinsExt(jenkins.Jenkins):

    """
    extension for the `Jenkins <https://jenkins-ci.org/>`_ server
    """

    def __init__(self, url,
                 username=None,
                 password=None,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 mock=False):
        """
        constructor

        @param      url         url of the server
        @param      username    username
        @param      password    password
        @param      timeout     timeout
        @param      mock        True by default, if False, avoid talking to the server
        """
        jenkins.Jenkins.__init__(self, url, username, password)
        self._mock = mock

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

    _config_job = """
            <?xml version='1.0' encoding='UTF-8'?>
            <project>
              <actions/>
              <description>__DESCRIPTION__</description>
              <logRotator class="hudson.tasks.LogRotator">
                <daysToKeep>__KEEP__</daysToKeep>
                <numToKeep>__KEEP__</numToKeep>
                <artifactDaysToKeep>-1</artifactDaysToKeep>
                <artifactNumToKeep>-1</artifactNumToKeep>
              </logRotator>
              <keepDependencies>false</keepDependencies>
              <properties/>
              __GITREPOXML__
              <canRoam>true</canRoam>
              <disabled>false</disabled>
              <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
              <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
              __TRIGGER__
              <concurrentBuild>false</concurrentBuild>
              __LOCATION__
              <builders>
              __TASKS__
              </builders>
              <publishers/>
              <buildWrappers/>
            </project>
        """.replace("            ", "")

    _trigger_up = """
              <triggers>
                <jenkins.triggers.ReverseBuildTrigger>
                  <spec></spec>
                  <upstreamProjects>__UP__</upstreamProjects>
                  <threshold>
                    <name>FAILURE</name>
                    <ordinal>2</ordinal>
                    <color>RED</color>
                    <completeBuild>true</completeBuild>
                  </threshold>
                </jenkins.triggers.ReverseBuildTrigger>
              </triggers>
              """.replace("            ", "")

    _trigger_time = """
              <triggers>
                <hudson.triggers.TimerTrigger>
                  <spec>__SCHEDULER__</spec>
                </hudson.triggers.TimerTrigger>
              </triggers>
              """.replace("            ", "")

    _git_repo = """
              <scm class="hudson.plugins.git.GitSCM" plugin="git@2.3.4">
                <configVersion>2</configVersion>
                <userRemoteConfigs>
                  <hudson.plugins.git.UserRemoteConfig>
                    <url>__GITREPO__</url>
                    __CRED__
                  </hudson.plugins.git.UserRemoteConfig>
                </userRemoteConfigs>
                <branches>
                  <hudson.plugins.git.BranchSpec>
                    <name>*/master</name>
                  </hudson.plugins.git.BranchSpec>
                </branches>
                <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
                <submoduleCfg class="list"/>
                <extensions>
                  <hudson.plugins.git.extensions.impl.WipeWorkspace/>
                </extensions>
              </scm>
              """.replace("            ", "")

    _task_batch = """
                <hudson.tasks.BatchFile>
                  <command>__SCRIPT__
                  </command>
                </hudson.tasks.BatchFile>
                """.replace("            ", "")

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
                            platform=sys.platform,
                            py27=False,
                            description=None,
                            default_engine_paths=None
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
        @param      platform                win, linux, ...
        @param      py27                    python 2.7 (True) or Python 3 (False)
        @param      description             add a description to the job
        @param      default_engine_paths    define the default location for python engine, should be dictionary *{ engine: path }*, see below.

        The job can be modified on Jenkins. To add a time trigger::

            H H(13-14) * * *

        Same trigger but once every week and not every day (Sunday for example)::

            H H(13-14) * * 0

        """
        if script is None:
            if platform.startswith("win"):
                script = private_script_replacements(
                    windows_jenkins, "____", None, "____", raise_exception=False,
                    platform=platform,
                    default_engine_paths=default_engine_paths)
            else:
                raise JenkinsExtException("no default script for linux")

        if upstreams is not None and len(upstreams) > 0 and scheduler is not None:
            raise JenkinsExtException(
                "upstreams and scheduler cannot be not null at the same time: {0}".format(name))

        if upstreams is not None and len(upstreams) > 0:
            trigger = JenkinsExt._trigger_up.replace(
                "__UP__", ",".join(upstreams))
        elif scheduler is not None:
            trigger = JenkinsExt._trigger_time.replace(
                "__SCHEDULER__", scheduler)
        else:
            trigger = ""

        if dependencies is None:
            dependencies = {}

        cmd = "set" if sys.platform.startswith("win") else "export"

        if not isinstance(script, list):
            script = [script]

        # we modify the scripts
        script_mod = []
        for scr in script:
            if "__PYTHON__" in scr:
                scr = scr.replace("__PYTHON__", choose_path(
                    os.path.dirname(sys.executable), "c:\\Python34_x64", "c:\\Anaconda3"))

            if "__PYTHON27__" in scr:
                raise NotImplementedError()

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
        else:
            return self.create_job(name, conf.encode("utf-8"))

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

    @staticmethod
    def get_jenkins_job_name(job):
        """
        infer a name for the jenkins job

        @param      job     str
        @return             name
        """
        for prefix in ["doc", "anaconda", "anaconda2", "winpython"]:
            p = "[%s]" % prefix
            if p in job:
                job = p + " " + job.replace(" " + p, "")
        return job.replace(" ", "_").replace("[", "").replace("]", "")

    @staticmethod
    def get_cmd_standalone(job, pythonexe, winpython, anaconda, anaconda2, platform, port):
        """
        Custom command for jenkins (such as updating conda)

        @param      job             module and options
        @param      pythonexe       unused
        @param      anaconda        location of anaconda (3)
        @param      anaconda2       location of anaconda 2
        @param      winpython       location of winpython
        @param      platform        platform, Windows or Linux or ...
        @param      port            port for the local pypi server
        @return                     script
        """
        spl = job.split()
        if spl[0] != "standalone":
            raise JenkinsExtException(
                "the job should start by standalone: " + job)

        if platform.startswith("win"):
            # windows
            if "[conda_update]" in spl:
                cmd = "%s\\Scripts\\conda update -y --all" % anaconda
            elif "[conda_update27]" in spl:
                cmd = "%s\\Scripts\\conda update -y --all" % anaconda2
            elif "[local_pypi]" in spl:
                cmd = "if not exist ..\\local_pypi_server mkdir ..\\local_pypi_server"
                cmd += "\necho __PYTHON__\\Scripts\\pypi-server.exe -u -v -p __PORT__ --disable-fallback ..\\local_pypi_server > ..\\local_pypi_server\\start_local_pypi.bat"
                cmd = cmd.replace("__PYTHON__", os.path.dirname(sys.executable)) \
                         .replace("__PORT__", str(port))
            else:
                raise JenkinsExtException("cannot interpret job: " + job)
            return cmd
        else:
            raise NotImplementedError()

    @staticmethod
    def hash_string(s, l=5):
        """
        hash a string

        @param      s       string
        @param      l       cut the string to the first *l* character
        @return             hashed string
        """
        m = hashlib.md5()
        m.update(s.encode("ascii"))
        r = m.hexdigest().upper()
        return r if l == -1 else r[:l]

    @staticmethod
    def get_jenkins_script(job, pythonexe, winpython, anaconda, anaconda2, platform, port):
        """
        build the jenkins script for a module and its options

        @param      job             module and options
        @param      pythonexe       unused
        @param      anaconda        location of anaconda (3)
        @param      anaconda2       location of anaconda 2
        @param      winpython       location of winpython
        @param      platform        platform, Windows or Linux or ...
        @param      port            port for the local pypi server
        @return                     script

        Method @see me setup_jenkins_server describes which tags
        this method can interpret.

        The method allow command such as ``[custom...]``, they will be
        run in a virtual environment as ``setup.py custom...``.
        """
        spl = job.split()
        module_name = spl[0]
        job_hash = JenkinsExt.hash_string(job)

        def replacements(cmd, python, suffix):
            res = cmd.replace("__PYTHON__", python) \
                     .replace("__SUFFIX__", suffix + "_" + job_hash)  \
                     .replace("__PORT__", str(port))  \
                     .replace("__MODULE__", module_name)  # suffix for the virtual environment and module name

            # patch to avoid installing pyquickhelper when testing
            # pyquickhelper
            if module_name == "pyquickhelper":
                lines = res.split("\n")
                for i, line in enumerate(lines):
                    if "/simple/ pyquickhelper" in line and "install --extra-index-url http://localhost" in line:
                        lines[i] = ""
                res = "\n".join(lines)

            return res

        if platform.startswith("win"):
            # windows
            py = choose_path(os.path.dirname(sys.executable),
                             "c:\\Python34_x64",
                             anaconda,
                             winpython,
                             ".")

            if len(spl) == 1:
                script = modified_windows_jenkins
                if not isinstance(script, list):
                    script = [script]
                return [replacements(s, os.path.join(py, "python"), "A0") for s in script]

            elif len(spl) == 0:
                raise ValueError("job is empty")

            elif spl[0] == "standalone":
                # conda update
                return JenkinsExt.get_cmd_standalone(
                    job, pythonexe, winpython, anaconda, anaconda2, platform, port)

            elif len(spl) in [2, 3, 4]:
                # step 1: define the script

                if "[test_local_pypi]" in spl:
                    cmd = "auto_setup_test_local_pypi.bat __PYTHON__"
                elif "[LONG]" in spl:
                    cmd = modified_windows_jenkins_any.replace(
                        "__COMMAND__", "unittests_LONG")
                elif "[SKIP]" in spl:
                    cmd = modified_windows_jenkins_any.replace(
                        "__COMMAND__", "unittests_SKIP")
                elif "[27]" in spl:
                    cmd = modified_windows_jenkins_27
                elif "[doc]" in spl:
                    # documentation
                    cmd = modified_windows_jenkins_any.replace(
                        "__COMMAND__", "build_sphinx")
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
                    if "[anaconda]" in spl:
                        if anaconda is not None:
                            cmd = replacements(
                                cmd, os.path.join(anaconda, "python"), "A3")
                        else:
                            raise JenkinsExtPyException(
                                "anaconda is not available")

                    elif "[anaconda2]" in spl:
                        if anaconda2 is not None:
                            cmd = replacements(cmd, os.path.join(py, "python"), "A2") \
                                .replace("__PYTHON27__", os.path.join(anaconda2, "python"))
                        else:
                            raise JenkinsExtPyException(
                                "anaconda2 is not available")
                    elif "[winpython]" in spl:
                        if winpython is not None:
                            # with WinPython, nb_convert has some trouble when called
                            # from the command line within Python
                            # the job might fail
                            cmd = replacements(
                                cmd, os.path.join(winpython, "python"), "WP")
                        else:
                            raise JenkinsExtPyException(
                                "winpython is not available")
                    else:
                        py = choose_path(
                            os.path.dirname(sys.executable), "c:\\Python34_x64", "c:\\Anaconda3", ".")
                        cmd = replacements(
                            cmd, os.path.join(py, "python"), "DF")

                    res.append(cmd)

                return res
            else:
                raise ValueError("unable to interpret: " + job)
        else:
            # linux
            spl = job.split()
            if len(spl) == 1:
                return "build_setup_help_on_linux.sh"
            elif len(spl) == 0:
                raise ValueError("job is empty")
            elif spl[0] == "standalone":
                # conda update
                cmd = JenkinsExt.get_cmd_standalone(
                    job, pythonexe, winpython, anaconda, anaconda2, platform, port)
                return cmd
            elif len(spl) in [2, 3]:
                if "[all]" in spl:
                    cmd = "bunittest_all.sh"
                elif "[notebooks]" in spl:
                    cmd = "bunittest_notebooks.sh"
                elif "[27]" in spl:
                    cmd = "build_setup_help_on_linux_27.sh"
                else:
                    cmd = "build_setup_help_on_linux.sh"

                if "[anaconda]" in spl:
                    if anaconda is not None:
                        cmd += " " + os.path.join(anaconda, "python")
                elif "[anaconda2]" in spl:
                    if anaconda2 is not None:
                        cmd += " " + os.path.join(anaconda2, "python")
                elif "[winpython]" in spl:
                    raise JenkinsExtException(
                        "unable to use WinPython on Linux")
                return cmd
            else:
                raise ValueError("unable to interpret: " + job)

    def setup_jenkins_server(self,
                             github,
                             modules,
                             get_jenkins_script=None,
                             pythonexe=os.path.dirname(sys.executable),
                             winpython=r"C:\WinPython-64bit-3.4.3.2FlavorRfull\python-3.4.3.amd64",
                             anaconda=r"c:\Anaconda3",
                             anaconda2=r"c:\Anaconda2",
                             overwrite=False,
                             location=None,
                             no_dep=False,
                             prefix="",
                             fLOG=noLOG,
                             dependencies=None,
                             platform=sys.platform,
                             port=8067,
                             default_engine_paths=None):
        """
        Set up many jobs on Jenkins

        @param      js_url                  url or jenkins server (specially if you need credentials)
        @param      github                  github account if it does not start with *http://*,
                                            the link to git repository of the project otherwise
        @param      modules                 modules for which to generate the
        @param      get_jenkins_script      see @see me get_jenkins_script (default value if this parameter is None)
        @param      pythonexe               location of Python (unused)
        @param      winpython               location of WinPython (or None to skip)
        @param      anaconda                location of Anaconda (or None to skip)
        @param      overwrite               do not create the job if it already exists
        @param      location                None for default or a local folder
        @param      no_dep                  if True, do not add dependencies
        @param      prefix                  add a prefix to the name
        @param      dependencies            some modules depend on others also being tested,
                                            this parameter gives the list
        @param      platform                platform of the Jenkins server
        @param      port                    port for the local pypi server
        @param      default_engine_paths    define the default location for python engine, should be dictionary *{ engine: path }*, see below.
        @param      fLOG                    logging function
        @return                             list of created jobs

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

        * ``[anaconda]``: use Anaconda as python engine
        * ``[anaconda2]``: use Anaconda 2.7 as python engine
        * ``[winpython]``: use WinPython as python engine
        * ``[27]``: run with python 2.7
        * ``[-nodep]``: do not check dependencies
        * ``[LONG]``: run longer unit tests (files start by ``test_LONG``)
        * ``[SKIP]``: run skipped unit tests (files start by ``test_SKIP``)
        * ``[custom.+]``: run ``setup.py <custom.+>`` in a virtual environment

        Others tags:

        * ``[conda_update]``: update conda distribution
        * ``[conda_update27]``: update conda distribution for python 2.7
        * ``[local_pypi]``: write a script to run a local pypi server on port 8067 (default option)

        *modules* is a list defined as follows:

            * each element can be a string or a tuple (string, schedule time) or a list
            * if it is a list, it contains a list of elements defined as previously
            * the job at position i is not scheduled, it will start after the last
              job at position i-1 whether or not it fails

        Example ::

             modules=[  # update anaconda
                        ("standalone [conda_update]", "H H(8-9) * * 0"),
                        "standalone [conda_update27]",
                        "standalone [local_pypi]",
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

            js = JenkinsExt('http://machine:8080/', "user", "password")

            if True:
                js.setup_jenkins_server(github="sdpython",
                                    modules=modules,
                                    anaconda=r"C:\\Anaconda3",
                                    anaconda2=r"C:\\Anaconda2",
                                    winpython=r"C:\WinPython-64bit-3.4.3.2FlavorRfull\python-3.4.3.amd64",
                                    fLOG=print,
                                    overwrite = True,
                                    location = r"c:\\jenkins\\pymy")


        For WinPython, version 3.4.3+ is mandatory to get the latest version of IPython (3).

        Another example::

            import sys
            sys.path.append(r"C:\<path>\ensae_teaching_cs\src")
            sys.path.append(r"C:\<path>\pyquickhelper\src")
            sys.path.append(r"C:\<path>\pyensae\src")
            sys.path.append(r"C:\<path>\pyrsslocal\src")
            from ensae_teaching_cs.automation.jenkins_helper import setup_jenkins_server, JenkinsExt
            js = JenkinsExt("http://<machine>:8080/", <user>, <password>)
            js.setup_jenkins_server(location=r"c:\jenkins\pymy",
                    overwrite=True,
                    fLOG=print)
        """
        if anaconda == anaconda2:
            raise JenkinsExtException("same paths:\n{0}".format(
                "\n".join([pythonexe, winpython, anaconda, anaconda2])))

        if get_jenkins_script is None:
            get_jenkins_script = JenkinsExt.get_jenkins_script

        if dependencies is None:
            dependencies = {}

        js = self

        if "https://" not in github:
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
                    job, scheduler = job
                    order = 1
                    if counts.get(dozen, 0) > 0:
                        dozen = chr(ord(dozen) + 1)
                else:
                    scheduler = None
                    if i == 0:
                        order += 1

                counts[dozen] = counts.get(dozen, 0) + 1

                mod = job.split()[0]
                name = JenkinsExt.get_jenkins_job_name(job)
                jname = prefix + name

                try:
                    j = js.get_job_config(jname) if not js._mock else None
                except jenkins.NotFoundException:
                    j = None
                except jenkins.JenkinsException as e:
                    raise JenkinsExtException(
                        "unable to retrieve job config for job={0}, name={1}".format(job, jname)) from e

                if overwrite or j is None:

                    if j is not None:
                        fLOG("delete job", jname)
                        js.delete_job(jname)

                    script = get_jenkins_script(
                        job, pythonexe, winpython, anaconda, anaconda2, platform, port)

                    if script is not None and len(script) > 0:
                        new_dep.append(name)
                        upstreams = [] if (
                            no_dep or scheduler is not None) else dep[-1:]
                        fLOG("create job", jname, " - ", job,
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

                        if mod == "standalone":
                            gpar = None
                        else:
                            gpar = github + "%s/" % mod

                        # create the template
                        r = js.create_job_template(jname,
                                                   git_repo=gpar,
                                                   upstreams=upstreams,
                                                   script=script,
                                                   location=loc,
                                                   dependencies=deps,
                                                   scheduler=scheduler,
                                                   platform=platform,
                                                   py27="[27]" in job,
                                                   description=description,
                                                   default_engine_paths=default_engine_paths)

                        # check some inconsistencies
                        if "[27]" in job and "Anaconda3" in script:
                            raise JenkinsExtException(
                                "incoherence for job {0}, script:\n{1}\npaths:\n{2}".format(job, script,
                                                                                            "\n".join([pythonexe, winpython, anaconda, anaconda2])))

                        locations.append((job, loc))
                        created.append((job, name, loc, job, r))
                    else:
                        # skip the job
                        loc = None if location is None else os.path.join(
                            location, jname)
                        locations.append((job, loc))
                        fLOG("skipping", job, "location", loc)

                elif j is not None:
                    new_dep.append(name)

            dep = new_dep

        return created

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
            pattern = "lower number of dependencies, requested:\n{0}\nFOUND:\n{1}\nLOCATIONS:\n{2}"
            raise Exception(pattern.format(", ".join(dependencies), "\n".join(
                "{0} : {1}".format(k, v) for k, v in sorted(res.items())),
                "\n".join("{0} : {1}".format(k, v) for k, v in locations)))

        return res
