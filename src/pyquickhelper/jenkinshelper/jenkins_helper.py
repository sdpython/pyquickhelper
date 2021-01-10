"""
@file
@brief Helpers to prepare a local Jenkins server.
"""
import sys
from ..loghelper import noLOG


def get_platform(platform=None):
    """
    Returns *platform* if not *None*, ``sys.platform`` otherwise.

    @param      platform    default values for which OS or
                            ``sys.platform``.
    @return                 platform

    This documentation was generated with a machine using the
    following *OS* (among the
    `possible values <https://docs.python.org/3/library/sys.html#sys.platform>`_).

    .. runpython::
        :showcode:

        from pyquickhelper.jenkinshelper.jenkins_helper import get_platform
        print(get_platform())

    .. versionadded:: 1.8
    """
    return platform or sys.platform


def default_engines(platform=None):
    """
    Returns a dictionary with default values for Jenkins server,
    you should update the path if the proposed path are not good.

    @param      platform    default values for which OS or
                            ``get_platform(platform)``.
    @return                 dictionary

    .. warning::

        Virtual environment with conda must be created on the same disk
        as the original interpreter. The other scenario is not supported
        by Anaconda.

    It returns:

    .. runpython::

        from pyquickhelper.jenkinshelper import default_engines
        print(default_engines())
    """
    platform = get_platform(platform)
    if platform == "win32":
        res = dict(Anaconda3="d:\\Anaconda3",
                   Python39="c:\\Python39_x64",
                   Python38="c:\\Python38_x64",
                   Python37="c:\\Python37_x64",
                   WinPython39="c:\\APythonENSAE\\python39",
                   WinPython38="c:\\APythonENSAE\\python38",
                   WinPython37="c:\\APythonENSAE\\python37")
    elif platform == "linux":
        res = dict(Anaconda3="/usr/local/miniconda3",
                   Python39="/usr/local/python39",
                   Python38="/usr/local/python38",
                   Python37="/usr/local/python37",
                   Python36="/usr/local/python36",
                   WinPython39="ERROR",
                   WinPython38="ERROR",
                   WinPython37="ERROR")
    else:
        raise ValueError(  # pragma: no cover
            "Unknown value for platform '{0}'.".format(platform))

    return res


def default_jenkins_jobs(platform=None, github_owner="sdpython",
                         module_name="pyquickhelper"):
    """
    Example of a list of jobs for parameter *module*
    of function @see fn setup_jenkins_server_yml.

    @param      platform        platform
    @param      github_owner     GitHub user
    @param      module_name     module name or list of modules names
    @return                     tuple

    It returns:

    .. runpython::

        from pyquickhelper.jenkinshelper import default_jenkins_jobs
        print(default_jenkins_jobs())
    """
    platform = get_platform(platform)
    plat = "win" if platform.startswith("win") else "lin"
    pattern = "https://raw.githubusercontent.com/{1}/%s/master/.local.jenkins.{0}.yml".format(
        plat, github_owner)
    yml = []
    if not isinstance(module_name, list):
        module_name = [module_name]
    for i, c in enumerate(module_name):
        yml.append(('yml', pattern % c, 'H H(5-6) * * %d' % (i % 7)))
    return yml


def setup_jenkins_server_yml(js, github="sdpython", modules=None,
                             overwrite=False, location=None, prefix="",
                             delete_first=False, disable_schedule=False,
                             fLOG=noLOG, **kwargs):
    """
    Sets up many jobs on :epkg:`Jenkins`.

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
    @param      disable_schedule        disable scheduling for all jobs
    @param      fLOG                    logging function
    @param      kwargs                  see method @see me setup_jenkins_server
    @return                             list of created jobs

    Example::

        from pyquickhelper.jenkinshelper (
            import JenkinsExt, setup_jenkins_server_yml,
            default_jenkins_jobs, default_engines)

        user = "<user>"
        password = "<password>"
        modules = default_jenkins_jobs()
        engines = default_engines()
        js = JenkinsExt('http://localhost:8080/', user, password, engines=engines)
        setup_jenkins_server_yml(js, github="sdpython", modules=modules, fLOG=print,
                                 overwrite=True, delete_first=False,
                                 location="d:\\\\jenkins\\\\pymy")

    See `.local.jenkins.win.yml
    <https://github.com/sdpython/pyquickhelper/blob/
    master/.local.jenkins.win.yml>`_ (Windows) or
    `.local.jenkins.lin.yml
    <https://github.com/sdpython/pyquickhelper/blob/
    master/.local.jenkins.lin.yml>`_ (Linux)
    about the syntax of a :epkg:`yml` job description.
    If *modules* is None, it is replaced by the results of
    @see fn default_jenkins_jobs.
    The platform is stored in *srv*.
    """
    if modules is None:
        modules = default_jenkins_jobs(js.platform)
    if delete_first:
        js.delete_all_jobs()
    r = js.setup_jenkins_server(
        github=github, modules=modules, overwrite=overwrite,
        location=location, prefix=prefix, disable_schedule=disable_schedule,
        **kwargs)
    return r


def jenkins_final_postprocessing(xml_job, py27):
    """
    Postprocesses a job produced by :epkg:`Jenkins`.

    @param      xml_job     :epkg:`xml` definition
    @param      py27        is it for :epkg:`Python` 27
    @return                 new xml job
    """
    if py27:
        # options are not allowed
        xml_job = xml_job.replace(
            "python -X faulthandler -X showrefcount", "python")
    return xml_job
