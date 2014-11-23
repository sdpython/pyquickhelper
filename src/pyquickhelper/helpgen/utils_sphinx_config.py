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

if __name__ == "__main__":
    ie_layout_html()