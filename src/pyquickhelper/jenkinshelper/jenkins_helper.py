"""
@file
@brief Helpers to prepare a local Jenkins server.
"""
from ..loghelper import noLOG


def default_engines():
    """
    returns a dictionary with default values for Jenkins server,
    you should update the path if the proposed path are not good.

    @return     dictionary

    .. warning::

        Virtual environment with conda must be created on the same disk
        as the original interpreter. The other scenario is not supported
        by Anaconda.

    It returns:

    .. runpython::

        from pyquickhelper.jenkinshelper import default_engines
        print(default_engines())
    """
    res = dict(Anaconda2="d:\\Anaconda",
               Anaconda3="d:\\Anaconda3",
               Python35="c:\\Python35_x64",
               Python34="c:\\Python34_x64",
               Python27="c:\\Python27",
               WinPython35="c:\\APythonENSAE\\python")
    return res


def default_jenkins_jobs():
    """
    example of a list of jobs for parameter *module*
    of function @see fn setup_jenkins_server_yml

    It returns:

    .. runpython::

        from pyquickhelper.jenkinshelper import default_jenkins_jobs
        print(default_jenkins_jobs())
    """
    pattern = "https://raw.githubusercontent.com/sdpython/%s/master/.local.jenkins.win.yml"
    yml = []
    for i, c in enumerate(["pyquickhelper"]):
        yml.append(('yml', pattern % c, 'H H(5-6) * * %d' % (i % 7)))
    return yml


def setup_jenkins_server_yml(js, github="sdpython", modules=default_jenkins_jobs(),
                             overwrite=False, location=None, prefix="",
                             delete_first=False, fLOG=noLOG, **kwargs):
    """
    Set up many jobs on Jenkins

    @param      js                      @see cl JenkinsExt, jenkins server
    @param      github                  github account if it does not start with *http://*,
                                        the link to git repository of the project otherwise,
                                        we assume the job comes from the same repository,
                                        otherwise the function will have to called several times
    @param      modules                 modules for which to generate the Jenkins job (see @see fn default_jenkins_jobs)
    @param      overwrite               do not create the job if it already exists
    @param      location                None for default or a local folder
    @param      prefix                  add a prefix to the name
    @param      delete_first            removes all jobs before adding new ones
    @param      fLOG                    logging function
    @param      kwargs                  see method @see me setup_jenkins_server
    @return                             list of created jobs

    Example::

        from pyquickhelper.jenkinshelper import JenkinsExt, setup_jenkins_server_yml, default_jenkins_jobs, default_engines

        js = JenkinsExt('http://localhost:8080/', None, None)
        modules = default_jenkins_jobs()
        engines = default_engines()
        setup_jenkins_server_yml(js, github="sdpython", modules=modules, fLOG=print,
                            overwrite = True, delete_first=True, engines=engines,
                            location = "d:\\\\jenkins\\\\pymy")
    """
    if delete_first:
        js.delete_all_jobs()
    r = js.setup_jenkins_server(github=github, modules=modules, overwrite=overwrite, 
                                location=location, prefix=prefix, **kwargs)
    return r
