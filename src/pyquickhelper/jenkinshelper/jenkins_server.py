"""
@file
@brief Extends Jenkins Server from `python-jenkins <http://python-jenkins.readthedocs.org/en/latest/>`_

.. versionadded:: 1.1
"""

import os
import sys
import jenkins
import socket
from ..loghelper.flog import noLOG


class JenkinsExtException(Exception):

    """
    exception for the class JenkinsExt
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
              <description></description>
              <logRotator class="hudson.tasks.LogRotator">
                <daysToKeep>__KEEP__</daysToKeep>
                <numToKeep>__KEEP__</numToKeep>
                <artifactDaysToKeep>-1</artifactDaysToKeep>
                <artifactNumToKeep>-1</artifactNumToKeep>
              </logRotator>
              <keepDependencies>false</keepDependencies>
              <properties/>
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
              <canRoam>true</canRoam>
              <disabled>false</disabled>
              <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
              <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
              __TRIGGER__
              <concurrentBuild>false</concurrentBuild>
              __LOCATION__
              <builders>
                <hudson.tasks.BatchFile>
                  <command>__SCRIPT__
                  </command>
                </hudson.tasks.BatchFile>
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

    def create_job_template(self,
                            name,
                            git_repo,
                            credentials="",
                            upstreams=None,
                            script="build_setup_help_on_windows.bat",
                            location=None,
                            keep=30,
                            dependencies=None,
                            scheduler=None,
                            platform=sys.platform,
                            py27=False,
                            ):
        """
        add a job to the jenkins server

        @param      name            name
        @param      credentials     credentials
        @param      git_repo        git repository
        @param      upstreams       the build must run after... (even if failures),
                                    must be None in that case
        @param      script          script to execute
        @param      keep            number of buils to keep
        @param      location        location of the build
        @param      dependencies    to add environment variable before
                                    and to set them to empty after the script is done
        @param      scheduler       add a schedule time (upstreams must be None in that case)
        @param      platform        win, linux, ...
        @param      py27            python 2.7 (True) or Python 3 (False)

        The job can be modified on Jenkins. To add a time trigger::

            H H(13-14) * * *

        Same trigger but once every week and not every day (Sunday for example)::

            H H(13-14) * * 0

        """
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
            rows.append(script)
            rows.extend(end)
            script_mod = "\n".join(rows)
        else:
            script_mod = script

        location = "" if location is None else "<customWorkspace>%s</customWorkspace>" % location
        conf = JenkinsExt._config_job
        rep = dict(__KEEP__=str(keep),
                   __GITREPO__=git_repo,
                   __SCRIPT__=script_mod,
                   __TRIGGER__=trigger,
                   __LOCATION__=location,
                   __CRED__="<credentialsId>%s</credentialsId>" % credentials)

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
        return job.replace(" ", "_").replace("[", "").replace("]", "")

    @staticmethod
    def get_jenkins_script(job, pythonexe, winpython, anaconda, anaconda2, platform):
        """
        build the jenkins script for a module and its options

        @param      job             module and options
        @param      pythonexe       unused
        @param      anaconda        location of anaconda
        @param      anaconda2       location of anaconda 2
        @param      winpython       location of winpython
        @param      platform        platform, Windows or Linux or ...
        @return                     script
        """
        if platform.startswith("win"):
            # windows
            spl = job.split()
            if len(spl) == 1:
                return "build_setup_help_on_windows.bat"
            elif len(spl) == 0:
                raise ValueError("job is empty")

            elif len(spl) in [2, 3]:
                if "[all]" in spl:
                    cmd = "bunittest_all.bat"
                elif "[notebooks]" in spl:
                    cmd = "bunittest_notebooks.bat"
                elif "[update]" in spl:
                    cmd = "update_anaconda.bat"
                elif "[update27]" in spl:
                    cmd = "update_anaconda_27.bat"
                elif "[27]" in spl:
                    cmd = "build_setup_help_on_windows_27.bat"
                else:
                    cmd = "build_setup_help_on_windows.bat"

                if "[anaconda]" in spl:
                    if anaconda is not None:
                        cmd += " " + os.path.join(anaconda, "python")
                elif "[anaconda2]" in spl:
                    if anaconda2 is not None:
                        cmd += " " + os.path.join(anaconda2, "python")
                elif "[winpython]" in spl:
                    if winpython is not None:
                        # with WinPython, nb_convert has some trouble when called
                        # from the command line within Python
                        # we skip for the time being
                        cmd += " " + \
                            os.path.join(winpython, "python") + " skip_sphinx"

                return cmd
            else:
                raise ValueError("unable to interpret: " + job)
        else:
            # linux
            spl = job.split()
            if len(spl) == 1:
                return "build_setup_help_on_linux.sh"
            elif len(spl) == 0:
                raise ValueError("job is empty")

            elif len(spl) in [2, 3]:
                if "[all]" in spl:
                    cmd = "bunittest_all.sh"
                elif "[notebooks]" in spl:
                    cmd = "bunittest_notebooks.sh"
                elif "[update]" in spl:
                    cmd = "update_anaconda.sh"
                elif "[update27]" in spl:
                    cmd = "update_anaconda_27.sh"
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
                             platform=sys.platform):
        """
        Set up many jobs on Jenkins

        @param      js_url              url or jenkins server (specially if you need credentials)
        @param      github              github account if it does not start with *http://*,
                                        the link to git repository of the project otherwise
        @param      modules             modules for which to generate the
        @param      get_jenkins_script  see @see me get_jenkins_script (default value if this parameter is None)
        @param      pythonexe           location of Python (unused)
        @param      winpython           location of WinPython (or None to skip)
        @param      anaconda            location of Anaconda (or None to skip)
        @param      overwrite           do not create the job if it already exists
        @param      location            None for default or a local folder
        @param      no_dep              if True, do not add dependencies
        @param      prefix              add a prefix to the name
        @param      dependencies        some modules depend on others also being tested,
                                        this parameter gives the list
        @param      platform            platform of the Jenkins server
        @param      fLOG                logging function
        @return                         list of created jobs

        *modules* is a list defined as follows:

            * each element can be a string or a tuple (string, schedule time) or a list
            * if it is a list, it contains a list of elements defined as previously
            * the job at position i is not scheduled, it will start after the last
              job at position i-1 whether or not it fails

        Example ::

             modules=[ ("pyquickhelper", "H H(10-11) * * 0"),
                      ["pymyinstall", ],
                      ["pymyinstall [anaconda] [update]",
                          "pymyinstall [anaconda2] [update27]"],
                      ["pyquickhelper [anaconda]", "pyquickhelper [winpython]",
                          "pyquickhelper [27] [anaconda2]"],
                      ["pyensae", ],
                      ["pymmails", "pysqllike", "pyrsslocal", "pymyinstall [27] [anaconda2]",
                       "python3_module_template", "pyensae [anaconda]", "pyensae [winpython]"],
                      ["pymmails [anaconda]", "pysqllike [anaconda]", "pyrsslocal [anaconda]",
                       "python3_module_template [anaconda]", "python3_module_template [27] [anaconda]",
                       "pymyinstall [all]"],
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
                      "ensae_teaching_cs [notebooks]",
                      ["ensae_teaching_cs [winpython] [notebooks]",
                       "ensae_teaching_cs [anaconda] [notebooks]", ],
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
        for jobs in modules:

            if not isinstance(jobs, list):
                jobs = [jobs]

            new_dep = []
            for job in jobs:

                if isinstance(job, tuple):
                    job, scheduler = job
                else:
                    scheduler = None

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
                        job, pythonexe, winpython, anaconda, anaconda2, platform)
                    if script is not None:
                        new_dep.append(name)
                        upstreams = [] if (
                            no_dep or scheduler is not None) else dep[-1:]
                        fLOG("create job", jname, " - ", job,
                             " : ", scheduler, " / ", upstreams)
                        loc = None if location is None else os.path.join(
                            location, jname)

                        deps = JenkinsExt.get_dependencies_path(
                            job, locations, dependencies.get(mod, None))

                        r = js.create_job_template(jname,
                                                   git_repo=github +
                                                   "%s/" % mod,
                                                   upstreams=upstreams,
                                                   script=script,
                                                   location=loc,
                                                   dependencies=deps,
                                                   scheduler=scheduler,
                                                   platform=platform,
                                                   py27="[27]" in job)

                        locations.append((job, loc))
                        created.append((job, name, loc, job, r))
                    else:
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

        if len(dependencies) != len(res):
            pattern = "lower number of dependencies, requested:\n{0}\nFOUND:\n{1}\nLOCATIONS:\n{2}"
            raise Exception(pattern.format(", ".join(dependencies), "\n".join(
                "{0} : {1}".format(k, v) for k, v in sorted(res.items())),
                "\n".join("{0} : {1}".format(k, v) for k, v in locations)))

        return res
