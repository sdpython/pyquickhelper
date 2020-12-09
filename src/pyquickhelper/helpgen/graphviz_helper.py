"""
@file
@brief Helper about graphviz.
"""
import os
from ..loghelper import run_cmd
from .conf_path_tools import find_graphviz_dot


def plot_graphviz(dot, ax=None, temp_dot=None, temp_img=None, dpi=300):
    """
    Plots a dot graph into a :epkg:`matplotlib` plot.

    @param  dot         dot language
    @param  ax          existing ax
    @param  temp_dot    temporary file, if None,
                        a file is created and removed
    @param  temp_img    temporary image, if None,
                        a file is created and removed
    @param  dpi         dpi
    @return             ax
    """
    if temp_dot is None:
        temp_dot = "temp_%d.dot" % id(dot)
        clean_dot = True
    else:
        clean_dot = False
    if temp_img is None:
        temp_img = "temp_%d.png" % id(dot)
        clean_img = True
    else:
        clean_img = False
    with open(temp_dot, "w", encoding="utf-8") as f:
        f.write(dot)
    dot_path = find_graphviz_dot()
    cmd = '"%s" -Gdpi=%d -Tpng -o "%s" "%s"' % (
        dot_path, dpi, temp_img, temp_dot)
    out, err = run_cmd(cmd, wait=True)
    if err is not None:
        err = err.strip("\r\n\t ")
    if len(err) > 0:
        if clean_dot:
            os.remove(temp_dot)
        if clean_img and os.path.exists(temp_img):
            os.remove(temp_img)
        raise RuntimeError(
            "Unable to run command line\n---OUT---\n{}\n---ERR---\n{}".format(
                out, err))
    if ax is None:
        import matplotlib.pyplot as plt
        ax = plt.gca()
        image = plt.imread(temp_img)
    else:
        import matplotlib.pyplot as plt
        image = plt.imread(temp_img)
    ax.imshow(image)
    if clean_dot:
        os.remove(temp_dot)
    if clean_img and os.path.exists(temp_img):
        os.remove(temp_img)
    return ax
