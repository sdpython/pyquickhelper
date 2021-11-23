"""
@file
@brief Check various settings.
"""
import sys
import os
import site
from io import BytesIO
import urllib.request as urllib_request


def getsitepackages():
    """
    Overwrites function :epkg:`getsitepackages`
    which does not work for a virtual environment.

    @return         site-package somewhere
    """
    try:
        return site.getsitepackages()
    except AttributeError:
        import sphinx
        return [os.path.normpath(os.path.join(os.path.dirname(sphinx.__file__), ".."))]


def locate_image_documentation(image_name):
    """
    Tries to local an image in the module for help generation in a folder ``_doc``.

    @param      image_name      path
    @return                     local file

    When a notebook is taken out from the sources, the image using NbImage
    cannot be displayed because the function cannot guess from which project
    it was taken. The function was entering an infinite loop.
    The function can deal with subfolder and not only the folder which contains the notebook.
    """
    image_name = os.path.abspath(image_name)
    if os.path.exists(image_name):
        return image_name
    folder, filename = os.path.split(image_name)
    while (len(folder) > 0 and
            (not os.path.exists(folder) or "_doc" not in os.listdir(folder))):
        fold = os.path.split(folder)[0]
        if fold == folder:
            break
        folder = fold
    doc = os.path.join(folder, "_doc")
    if not os.path.exists(doc):
        raise FileNotFoundError(
            "Unable to find a folder called _doc, "
            "the function cannot locate an image %r, doc=%r, folder=%r."
            "" % (image_name, doc, folder))
    for root, _, files in os.walk(doc):
        for name in files:
            t = os.path.join(root, name)
            fn = os.path.split(t)[-1]
            if filename == fn:
                return t
    raise FileNotFoundError(image_name)


def _NbImage_path(name, repository=None, force_github=False, branch='master'):
    if not isinstance(name, str):
        return name
    if os.path.exists(name):
        return os.path.abspath(name).replace("\\", "/")
    if not name.startswith('http://') and not name.startswith('https://'):
        # local file
        local = name
        local_split = name.split("/")
        if "notebooks" not in local_split:
            local = locate_image_documentation(local)
            return local
    else:
        return name

    # otherwise --> github
    paths = local.replace("\\", "/").split("/")
    try:
        pos = paths.index("notebooks") - 1
    except IndexError as e:
        # we are looking for the right path
        raise IndexError(
            "The image is not retrieved from a notebook from a folder "
            "`_docs/notebooks` or you changed the current folder:"
            "\n{0}".format(local)) from e
    except ValueError as ee:
        # we are looking for the right path
        raise IndexError(
            "The image is not retrieve from a notebook from a folder "
            "``_docs/notebooks`` or you changed the current folder:"
            "\n{0}".format(local)) from ee

    if repository is None:
        module = paths[pos - 1]
        if module not in sys.modules:
            if "ensae_teaching_cs" in local:
                # For some specific modules, we add the location.
                repository = "https://github.com/sdpython/ensae_teaching_cs/"
            else:
                raise ImportError(
                    "The module {0} was not imported, cannot guess "
                    "the location of the repository".format(module))
        else:
            modobj = sys.modules[module]
            if not hasattr(modobj, "__github__"):
                raise AttributeError(
                    "The module has no attribute '__github__'. "
                    "The repository cannot be guessed.")
            repository = modobj.__github__
        repository = repository.rstrip("/")

    loc = "/".join([branch, "_doc", "notebooks"] + paths[pos + 2:])
    url = repository + "/" + loc
    url = url.replace("github.com", "raw.githubusercontent.com")
    return url


def _NbImage(url, width=None):
    if isinstance(url, str):
        if url.startswith('http://') or url.startswith('https://'):
            with urllib_request.urlopen(url) as u:
                text = u.read()
            content = BytesIO(text)
            return NbImage(content)
    return NbImage(url, width=width)


def NbImage(*name, repository=None, force_github=False, width=None,
            branch='master', row_height=200):
    """
    Retrieves a name or a url of the image if it is not found in the local folder
    or a subfolder.

    :param name: image name (name.png) (or multiple names)
    :param force_github: force the system to retrieve the image from GitHub
    :param repository: repository, see below
    :param width: to modify the width
    :param branch: branch
    :param row_height: row height if there are multiple images
    :return: an `Image object
        <http://ipython.org/ipython-doc/2/api/generated/IPython.core.display.html
        #IPython.core.display.Image>`_

    We assume the image is retrieved from a notebook.
    This function will display an image even though the notebook is not run
    from the sources. IPython must be installed.

    if *repository* is None, then the function will use the variable
    ``module.__github__`` to guess the location of the image.
    The function is able to retrieve an image in a subfolder.
    Displays a better message if ``__github__`` was not found.

    See notebook :ref:`examplenbimagerst`.
    """
    from IPython.core.display import Image
    if len(name) == 1:
        url = _NbImage_path(
            name[0], repository=repository,
            force_github=force_github, branch=branch)
        return Image(url, width=width)

    if len(name) == 0:
        raise ValueError(  # pragma: no cover
            "No image to display.")

    from ..imghelper.img_helper import concat_images
    from PIL import Image as pil_image
    images = []
    for img in name:
        url = _NbImage_path(
            img, repository=repository,
            force_github=force_github, branch=branch)
        if url.startswith('http://') or url.startswith('https://'):
            with urllib_request.urlopen(url) as u:
                text = u.read()
            content = BytesIO(text)
            images.append(pil_image.open(content))
        else:
            images.append(pil_image.open(url))

    if width is None:
        width = max(img.size[0] for img in images) * 2
        width = max(200, width)

    new_image = concat_images(images, width=width, height=row_height)
    b = BytesIO()
    new_image.save(b, format='png')
    data = b.getvalue()
    return Image(data, width=width)
