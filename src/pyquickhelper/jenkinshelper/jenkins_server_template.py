"""
@file
@brief Job templates.
"""

#: main template: the full job
_config_job = """<?xml version='1.0' encoding='UTF-8'?>
<project>
    <actions />
    <description>__DESCRIPTION__</description>
    <logRotator class="hudson.tasks.LogRotator">
        <daysToKeep>__KEEP__</daysToKeep>
        <numToKeep>__KEEP__</numToKeep>
        <artifactDaysToKeep>-1</artifactDaysToKeep>
        <artifactNumToKeep>-1</artifactNumToKeep>
    </logRotator>
    <keepDependencies>false</keepDependencies>
    <properties />
    __GITREPOXML__
    <canRoam>true</canRoam>
    <disabled>false</disabled>
    <blockBuildWhenDownstreamBuilding>true</blockBuildWhenDownstreamBuilding>
    <blockBuildWhenUpstreamBuilding>true</blockBuildWhenUpstreamBuilding>
    __TRIGGER__
    <concurrentBuild>false</concurrentBuild>
    __LOCATION__
    <builders>
    __TASKS__
    </builders>
    <publishers>
    __PUBLISHERS__
    </publishers>
    <buildWrappers>
        <hudson.plugins.build__timeout.BuildTimeoutWrapper plugin="build-timeout@1.19">
            <strategy class="hudson.plugins.build_timeout.impl.NoActivityTimeOutStrategy">
                <timeoutSecondsString>__TIMEOUT__</timeoutSecondsString>
            </strategy>
            <operationList>
                <hudson.plugins.build__timeout.operations.AbortOperation/>
                <hudson.plugins.build__timeout.operations.FailOperation/>
            </operationList>
        </hudson.plugins.build__timeout.BuildTimeoutWrapper>
        __BUILDWRAPPERS__
    </buildWrappers>
</project>
"""

#: when to trigger
_trigger_up = """
<triggers>
    <jenkins.triggers.ReverseBuildTrigger>
        <spec></spec>
        <upstreamProjects>__UP__</upstreamProjects>
        <threshold>
            <name>__FAILURE__</name>
            <ordinal>__ORDINAL__</ordinal>
            <color>__COLOR__</color>
            <completeBuild>true</completeBuild>
        </threshold>
    </jenkins.triggers.ReverseBuildTrigger>
</triggers>
"""

#: scheduler
_trigger_time = """
<triggers>
    <hudson.triggers.TimerTrigger>
        <spec>__SCHEDULER__</spec>
    </hudson.triggers.TimerTrigger>
</triggers>
"""

#: trigger startup
_trigger_startup = """
<triggers>
    <org.jvnet.hudson.plugins.triggers.startup.HudsonStartupTrigger plugin="startup-trigger-plugin">
        <quietPeriod>0</quietPeriod>
        <runOnChoice>ON_BOTH</runOnChoice>
    </org.jvnet.hudson.plugins.triggers.startup.HudsonStartupTrigger>
</triggers>
"""

#: git repository
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
    <submoduleCfg class="list" />
    __WIPE__
</scm>
"""

_wipe_repo = """
    <extensions>
        <hudson.plugins.git.extensions.impl.WipeWorkspace />
    </extensions>
"""

#: for the script
_task_batch_win = """
<hudson.tasks.BatchFile>
    <command>__SCRIPT__
    </command>
</hudson.tasks.BatchFile>
"""

_task_batch_lin = """
<hudson.tasks.Shell>
    <command>__SCRIPT__
    </command>
</hudson.tasks.Shell>
"""

#: mails
_publishers = """
<hudson.tasks.Mailer plugin="mailer">
    <recipients>__MAIL__</recipients>
    <dontNotifyEveryUnstableBuild>false</dontNotifyEveryUnstableBuild>
    <sendToIndividuals>true</sendToIndividuals>
</hudson.tasks.Mailer>
"""

#: creation of a file
_file_creation = """
<com.etas.jenkins.plugins.CreateTextFile.CreateFileBuilder plugin="text-file-operations">
  <textFilePath>__FILENAME__</textFilePath>
  <textFileContent>
__CONTENT__
  </textFileContent>
  <fileOption>overWrite</fileOption>
  <useWorkspace>true</useWorkspace>
</com.etas.jenkins.plugins.CreateTextFile.CreateFileBuilder>
"""

#: artifacts
_artifacts = """
    <hudson.tasks.ArtifactArchiver>
      <artifacts>__PATTERN__</artifacts>
      <allowEmptyArchive>true</allowEmptyArchive>
      <onlyIfSuccessful>true</onlyIfSuccessful>
      <fingerprint>false</fingerprint>
      <defaultExcludes>true</defaultExcludes>
      <caseSensitive>true</caseSensitive>
    </hudson.tasks.ArtifactArchiver>
"""

#: cleanup
_cleanup_repo = """
<hudson.plugins.ws__cleanup.PreBuildCleanup plugin="ws-cleanup@0.37">
  <deleteDirs>true</deleteDirs>
  <cleanupParameter></cleanupParameter>
  <externalDelete></externalDelete>
  <disableDeferredWipeout>true</disableDeferredWipeout>
</hudson.plugins.ws__cleanup.PreBuildCleanup>
"""
