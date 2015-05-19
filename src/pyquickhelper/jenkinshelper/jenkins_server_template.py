"""
@file
@brief Job templates

.. versionadded:: 1.1
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
    <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
    <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
    __TRIGGER__
    <concurrentBuild>false</concurrentBuild>
    __LOCATION__
    <builders>
    __TASKS__
    </builders>
    <publishers />
    <buildWrappers />
</project>
"""

#: when to trigger
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
"""

#: scheduler
_trigger_time = """
<triggers>
    <hudson.triggers.TimerTrigger>
        <spec>__SCHEDULER__</spec>
    </hudson.triggers.TimerTrigger>
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
    <extensions>
        <hudson.plugins.git.extensions.impl.WipeWorkspace />
    </extensions>
</scm>
"""

#: for the script
_task_batch = """
<hudson.tasks.BatchFile>
    <command>__SCRIPT__
    </command>
</hudson.tasks.BatchFile>
"""
