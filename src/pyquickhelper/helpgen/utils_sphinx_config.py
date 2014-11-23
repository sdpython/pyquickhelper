"""
@file
@brief Check various settings.

"""

import sys, os, site

def ie_layout_html():
    """
    The layout produced by sphinx does not always work with Internet Explorer.
    See `Issue with some Sphinx themes and Internet Explorer <http://www.xavierdupre.fr/blog/2014-10-27_nojs.html>`_.

    @return         boolean

    If False, raises an exception.
    """
    tofind = '<meta http-equiv="X-UA-Compatible" content="IE=edge" />'

    sitep = [ _ for _ in site.getsitepackages() if "packages" in _ ]
    if len(sitep) == 1 :
        sitep = sitep[0]
    else:
        raise FileNotFoundError("unable to find site-packages\n{1}".format("\n".join(site.getsitepackages())) )
        
    if not os.path.exists(sitep):
        raise FileNotFoundError("unable to find site-packages, tried: {0}\nALL:\n{1}".format(sitep, 
                        "\n".join(site.getsitepackages())) )
                        
    path = os.path.dirname(sys.executable)
    layout = os.path.join( sitep,"sphinx","themes","basic","layout.html")
    if os.path.exists(layout):
        with open(layout, "r", encoding="utf-8") as f :
            content = f.read()
        if tofind not in content:
            alls = [ "unable to find: " + tofind  + " in ",
                     '  File "{0}", line 1'.format(layout) ,
                     'see http://www.xavierdupre.fr/blog/2014-10-30_nojs.html']
            raise Exception("\n".join(alls))
        return True
    else:
        raise FileNotFoundError("Sphinx is not properly installed, unable to find: " + layout)
        
def NbImage (name, repository = None, force_github = False, width = None):
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
    """
    from IPython.core.display import Image
    local = os.path.abspath(name)
    if not force_github and os.path.exists(local) : return Image(local)
    
    # otherwise --> github
    paths = local.replace("\\","/").split("/")
    try:
        pos = paths.index("notebooks")-1
    except IndexError as e :
        raise IndexError("the image is not retrieve from a notebook from a folder ``_docs/notebooks`` or you changed the current folder")
        
    if repository is None:
        module = paths[pos-1]
        if module not in sys.modules:
            raise ImportError("the module {0} was not imported, cannot guess the location of the repository".format(module))
        repository = sys.modules[module].__github__
        
    loc = "/".join( ["master", "_doc","notebooks" ] + paths[pos+2:] )
    url = repository + "/" + loc
    url = url.replace("github.com","raw.githubusercontent.com")
    return Image(url, width=width)
    
if __name__ == "__main__":
    ie_layout_html()