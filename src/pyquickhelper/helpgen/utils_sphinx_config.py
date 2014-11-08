"""
@file
@brief Check various settings.

"""

import sys, os

def ie_layout_html():
    """
    The layout produced by sphinx does not always work with Internet Explorer.
    See `Issue with some Sphinx themes and Internet Explorer <http://www.xavierdupre.fr/blog/2014-10-27_nojs.html>`_.

    @return         boolean

    If False, raises an exception.
    """
    tofind = '<meta http-equiv="X-UA-Compatible" content="IE=edge" />'

    path = os.path.dirname(sys.executable)
    layout = os.path.join( path, "Lib","site-packages","sphinx","themes","basic","layout.html")
    if os.path.exists(layout):
        with open(layout, "r", encoding="utf-8") as f :
            content = f.read()
        if tofind not in content:
            all = [ "unable to find: " + tofind  + " in "]
            all.append ('  File "{0}", line 1'.format(layout))
            raise Exception("\n".join(all))
        return True
    else:
        raise FileNotFoundError("Sphinx is not properly installed, unable to find: " + layout)

if __name__ == "__main__":
    ie_layout_html()