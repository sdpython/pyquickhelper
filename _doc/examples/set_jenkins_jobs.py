"""
================
Set Jenkins Jobs
================

This jobs is used to add jobs to a Jenkins server in order
to build packages on Windows. The YAML definition is located
at `pymyinstall/whl <https://github.com/sdpython/pymyinstall/tree/master/whl>`_
and it defines the jobs in this folder
`pymyinstall/whl/windows <https://github.com/sdpython/pymyinstall/tree/master/whl/windows>`_.

"""
################################################
# imports
import os
try:
    import pyquickhelper
except ImportError:
    import sys
    sys.path.append("src")
    import pyquickhelper

from pyquickhelper.jenkinshelper import setup_jenkins_server_yml, JenkinsExt
from pyquickhelper.loghelper import fLOG

#################################
# Starts logging.
fLOG(OutputPrint=True)
fLOG("start")

#################################
# password
import keyring
user = keyring.get_password("jenkins", os.environ["COMPUTERNAME"] + "user")
pwd = keyring.get_password("jenkins", os.environ["COMPUTERNAME"] + "pwd")

#################################
# local path
engines = dict(Python35="c:\\Python35_x64",
               Python36="c:\\Python36_x64")
folder = "C:\\%s\github\\pymyinstall\\whl" % os.environ["USERNAME"]
location = "d:\\jenkins\\pymy"

#################################
if not os.path.exists("build"):
    os.mkdir("build")

#################################
# Loads the yml template.
yml = os.path.join(folder, ".local.jenkins.win.yml")
with open(yml, "r", encoding="utf-8") as f:
    content = f.read()

#################################
# Starts the Jenkins server.
js = JenkinsExt('http://localhost:8080/', user,
                pwd, fLOG=fLOG, engines=engines)

#################################
# Defiens the Jenkins job.
ymls = []
for mod in ["polylearn", "dynd-python"]:
    new_content = content.replace("__MODULE__", mod)
    yml = os.path.join("build", ".local.jenkins.win.{0}.yml".format(mod))
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
