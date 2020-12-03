"""
================
Set Jenkins Jobs
================

This jobs is used to add jobs to a :epkg:`Jenkins` server in order
to build packages on Windows. The :epkg:`YAML` definition is located
at `pymyinstall/whl <https://github.com/sdpython/pymyinstall/tree/master/whl>`_
and it defines the jobs in this folder
`pymyinstall/whl/windows <https://github.com/sdpython/pymyinstall/tree/master/whl/windows>`_.

"""
################################################
# imports
import sys
import os
import warnings

from pyquickhelper.jenkinshelper import setup_jenkins_server_yml, JenkinsExt
from pyquickhelper.loghelper import fLOG, get_user

#################################
# Starts logging.
fLOG(OutputPrint=True)
fLOG("start")

#################################
# password
with warnings.catch_warnings():
    warnings.simplefilter('ignore', DeprecationWarning)
    import keyring
user = keyring.get_password("jenkins", "user")
pwd = keyring.get_password("jenkins", "pwd")

#################################
# local path
key = "Python%d%d" % sys.version_info[:2]
engines = {key: os.path.abspath(os.path.dirname(sys.executable))}
if sys.platform.startswith("win"):
    folder = "C:\\%s\\github\\_whl" % get_user()
    location = "c:\\jenkins\\pymy"
    suf = "win"
else:
    folder = "/home/%s/github/_whl" % get_user()
    location = "/usr/local/Python%d.%d" % sys.version_info[:2]
    suf = "lin"

#################################
if not os.path.exists("build"):
    os.mkdir("build")

#################################
# Loads the yml template.
yml = os.path.join(folder, ".local.jenkins.%s.yml" % suf)
with open(yml, "r", encoding="utf-8") as f:
    content = f.read()

#################################
# Starts the Jenkins server.
js = JenkinsExt('http://localhost:8080/', user,
                pwd, fLOG=fLOG, engines=engines)

#################################
# Defines the Jenkins job.
ymls = []
for mod in ["polylearn", "dynd-python"]:
    new_content = content.replace("__MODULE__", mod)
    yml = os.path.join("build", ".local.jenkins.{1}.{0}.yml".format(mod, "lin"))
    with open(yml, "w", encoding="utf-8") as f:
        f.write(new_content)
    batch = os.path.join(folder, "windows", "build_{0}.bat".format(mod))
    with open(batch, "r", encoding="utf-8") as f:
        cbat = f.read()
    with open(yml, "w", encoding="utf-8") as f:
        f.write(new_content)
    toadd = [dict(name="build_{0}.bat".format(mod),
                  content=cbat)]
    ymls.append(("yml", yml, dict(scripts=toadd)))

#################################
# Update the Jenkins jobs for the given set of modules
fLOG("Update jenkins")
setup_jenkins_server_yml(js, github=None, modules=ymls,
                         overwrite=True, location=location, prefix="",
                         delete_first=False, disable_schedule=False, fLOG=fLOG)
fLOG("Done")
