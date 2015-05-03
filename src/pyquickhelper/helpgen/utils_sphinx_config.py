"""
@file
@brief Check various settings.

"""

import sys
import os
import site
from distutils.sysconfig import get_python_lib

if sys.version_info[0] == 2:
    from codecs import open


def getsitepackages():
    """
    overwrites function `getsitepackages <https://docs.python.org/3.4/library/site.html#site.getsitepackages>`_
    which does not work for a virtual environment

    @return         site-package somewhere
    """
    try:
        return site.getsitepackages()
    except AttributError:
        return [get_python_lib()]


def ie_layout_html():
    """
    The layout produced by sphinx does not always work with Internet Explorer.
    See `Issue with some Sphinx themes and Internet Explorer <http://www.xavierdupre.fr/blog/2014-10-30_nojs.html>`_.

    @return         boolean

    If False, raises an exception.
    """
    tofind = '<meta http-equiv="X-UA-Compatible" content="IE=edge" />'

    sitep = [_ for _ in getsitepackages() if "packages" in _]
    if len(sitep) == 1:
        sitep = sitep[0]
    else:
        raise FileNotFoundError(
            "unable to find site-packages\n{1}".format("\n".join(site.getsitepackages())))

    if not os.path.exists(sitep):
        raise FileNotFoundError("unable to find site-packages, tried: {0}\nALL:\n{1}".format(sitep,
                                                                                             "\n".join(site.getsitepackages())))

    layout = os.path.join(sitep, "sphinx", "themes", "basic", "layout.html")
    if os.path.exists(layout):
        with open(layout, "r", encoding="utf-8") as f:
            content = f.read()
        if tofind not in content:
            alls = ["unable to find: " + tofind + " in ",
                    '  File "{0}", line 1'.format(layout),
                    'see http://www.xavierdupre.fr/blog/2014-10-30_nojs.html']
            raise Exception("\n".join(alls))
        return True
    else:
        raise FileNotFoundError(
            "Sphinx is not properly installed, unable to find: " + layout)


def locate_image_documentation(image_name):
    """
    tries to local an image in the module for help generation in a folder ``_doc``

    @param      image_name      path
    @return                     local file
    """
    folder, filename = os.path.split(image_name)
    while len(folder) > 0 and "_doc" not in os.listdir(folder):
        folder = os.path.split(folder)[0]
    doc = os.path.join(folder, "_doc")
    for root, dirs, files in os.walk(doc):
        for name in files:
            t = os.path.join(root, name)
            fn = os.path.split(t)[-1]
            if filename == fn:
                return t
    raise FileNotFoundError(image_name)


def NbImage(name, repository=None, force_github=False, width=None):
    """
    retrieve a name or a url of the image if it is not found in the local folder

    @param      name            image name (name.png)
    @param      force_github    force the system to retrieve the image from GitHub
    @param      repository      repository, see below
    @param      width           to modify the width
    @return                     an `Image object <http://ipython.org/ipython-doc/2/api/generated/IPython.core.display.html#IPython.core.display.Image>`_

    We assume the image is retrieved from a notebook.
    This function will display an image even though the notebook is not run
    from the sources. IPython must be installed.

    if *repository* is None, then the function will use the variable ``module.__github__`` to
    guess the location of the image.

    .. versionadded:: 0.9
    """
    from IPython.core.display import Image
    local = os.path.abspath(name)
    if not force_github and os.path.exists(local):
        return Image(local, width=width)

    local_split = local.replace("\\", "/").split("/")
    if "notebooks" not in local_split:
        local = locate_image_documentation(local)
        return Image(local, width=width)

    # otherwise --> github
    paths = local.replace("\\", "/").split("/")
    try:
        pos = paths.index("notebooks") - 1
    except IndexError as e:
        # we are looking for the right path
        raise IndexError(
            "the image is not retrieve from a notebook from a folder ``_docs/notebooks`` or you changed the current folder:\n{0}".format(local)) from e
    except ValueError as ee:
        # we are looking for the right path
        raise IndexError(
            "the image is not retrieve from a notebook from a folder ``_docs/notebooks`` or you changed the current folder:\n{0}".format(local)) from ee

    if repository is None:
        module = paths[pos - 1]
        if module not in sys.modules:
            if "ensae_teaching_cs" in local:
                # for some specific modules, we add the location
                repository = "https://github.com/sdpython/ensae_teaching_cs/"
            else:
                raise ImportError(
                    "the module {0} was not imported, cannot guess the location of the repository".format(module))
        else:
            repository = sys.modules[module].__github__
        repository = repository.strip("/")

    loc = "/".join(["master", "_doc", "notebooks"] + paths[pos + 2:])
    url = repository + "/" + loc
    url = url.replace("github.com", "raw.githubusercontent.com")
    return Image(url, width=width)

if __name__ == "__main__":
    ie_layout_html()
