"""
@brief
@file Batch file use to automate some of the tasks (setup, unit tests, help, pypi).
"""
import sys


def _sversion():
    return "PY%d%d" % sys.version_info[:2]

#################
#: stop if error
#################


linux_error = "if [ $? -ne 0 ]; then exit $?; fi"

#################
#: call the setup
#################
jenkins_linux_setup = "$PYINT -u setup.py"


#################
#: script for Jenkins
#################
linux_jenkins = "echo SCRIPT: linux_jenkins\nexport jenkinspython=__PYTHON__\necho ~EXPORT jenkinspython=__PYTHON__\n" + \
    "\n__PACTHPQb__\n" + \
    jenkins_linux_setup + " build_script\n" + \
    "\n__PACTHPQe__\n" + \
    linux_error + "\nbash auto_unittest_setup_help.sh $jenkinspython __SUFFIX__\n" + \
    linux_error

linux_jenkins_any = "echo SCRIPT: linux_jenkins_any\nexport jenkinspython=__PYTHON__\necho ~EXPORT jenkinspython=__PYTHON__\n" + \
    "\n__PACTHPQb__\n" + \
    jenkins_linux_setup + " build_script\n" + \
    "\n__PACTHPQe__\n" + \
    linux_error + "\nbash auto_cmd_any_setup_command.sh $jenkinspython __SUFFIX__ __COMMAND__\n" + \
    linux_error
