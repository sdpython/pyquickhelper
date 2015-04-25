"""
extends Jenkins Server from `python-jenkins <http://python-jenkins.readthedocs.org/en/latest/>`_
"""

import sys
import jenkins
import socket
from jenkins import JenkinsException


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
            raise JenkinsException("mocking server, cannot be open")

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

    def create_job_template(self,
                            name,
                            git_repo,
                            credentials="",
                            upstreams=None,
                            script="build_setup_help_on_windows.bat",
                            location=None,
                            keep=30,
                            dependencies=None
                            ):
        """
        add a job to the jenkins server

        @param      name            name
        @param      credentials     credentials
        @param      git_repo        git repository
        @param      upstreams       the build must run after... (even if failures)
        @param      script          script to execute
        @param      keep            number of buils to keep
        @param      location        location of the build
        @param      dependencies    to add environment variable before
                                    and to set them to empty after the script is done

        The job can be modified on Jenkins. To add a time trigger::

            H H(13-14) * * *

        Same trigger but once every week and not every day (Sunday for example)::

            H H(13-14) * * 0

        """
        if upstreams is None:
            upstreams = []

        if dependencies is None:
            dependencies = {}

        cmd = "set" if sys.platform.startswith("win") else "export"

        if len(dependencies) > 0:
            rows = []
            end = []
            for k, v in sorted(dependencies.items()):
                rows.append("{0} {1}={2}".format(cmd, k, v))
                end.append("{0} {1}=".format(cmd, k))
            rows.append(script)
            rows.extend(end)
            script_mod = "\n".join(rows)

        location = "" if location is None else "<customWorkspace>%s</customWorkspace>" % location
        conf = JenkinsExt._config_job
        rep = dict(__KEEP__=str(keep),
                   __GITREPO__=git_repo,
                   __SCRIPT__=script_mod,
                   __UP__=",".join(upstreams),
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
            raise JenkinsException('delete[%s] failed' % (name))
