"""
@file
@brief  Looks for paths, Miktek, Graphviz...
"""
import sys
import os


def find_in_PATH(prog):
    """
    look into every path mentioned in ``%PATH%`` a specific file,
    it raises an exception if not Found

    @param      prog        program to look for
    @return                 path

    .. versionadded:: 0.9
    """
    path = os.environ["PATH"]
    for p in path.split(";"):
        f = os.path.join(p, prog)
        if os.path.exists(f):
            return p
    return None


def find_graphviz_dot():
    """
    determines the path to graphviz (on Windows),
    the function tests the existence of versions 34 to 45
    assuming it was installed in a standard folder: ``C:\Program Files\MiKTeX 2.9\miktex\bin\x64``

    @return         path to dot

    :raises FileNotFoundError: if graphviz not found

    .. versionadded:: 0.9
    """
    if sys.platform.startswith("win"):
        version = range(34, 45)
        for v in version:
            graphviz_dot = r"C:\Program Files (x86)\Graphviz2.{0}\bin\dot.exe".format(
                v)
            if os.path.exists(graphviz_dot):
                return graphviz_dot
        p = find_in_PATH("dot.exe")
        if p is None:
            typstr = str  # unicode#
            raise FileNotFoundError(
                "unable to find graphviz, look into paths such as: " + typstr(graphviz_dot))
        else:
            return os.path.join(p, "dot.exe")
    else:
        # linux
        return "dot"


def find_latex_path():
    """
    @return ``C:\Program Files\MiKTeX 2.9\miktex\bin\x64``

    :raises FileNotFoundError: if latex not found

    .. versionadded:: 0.9
    """
    if sys.platform.startswith("win"):
        latex = latex0 = r"C:\Program Files\MiKTeX 2.9\miktex\bin\x64"
        if not os.path.exists(latex):
            latex = find_in_PATH("latex.exe")
            if latex is None or not os.path.exists(latex):
                typstr = str  # unicode#
                raise FileNotFoundError(
                    "unable to find latex (miktex), look into paths such as: " + typstr(latex0))
        return latex
    else:
        # linux
        return ""


def find_pandoc_path():
    """
    determines pandoc location

    @return         path to pandoc

    .. versionadded:: 0.9
    """
    if sys.platform.startswith("win"):
        path = os.environ["USERPROFILE"]
        pandoc = os.path.join(path, "AppData", "Local", "Pandoc")
        tries = [pandoc]
        if not os.path.exists(pandoc):
            # we try others users because pandoc goes into a user folder by
            # default
            root = os.path.normpath(os.path.join(path, ".."))
            users = os.listdir(root)
            for u in users:
                p = os.path.join(root, u)
                if os.path.isdir(p):
                    pandoc = os.path.join(p, "AppData", "Local", "Pandoc")
                    if os.path.exists(pandoc):
                        return pandoc
                    tries.append(pandoc)
            pandoc = find_in_PATH("pandoc.exe")
            if pandoc is None:
                raise FileNotFoundError(
                    "unable to find pandoc, look into paths such as:\n" + "\n".join(tries))
            else:
                return pandoc
        else:
            return pandoc
    else:
        # linux
        return ""


def get_graphviz_dot():
    """
    finds Graphviz executable dot, does something specific for Windows
    """
    if sys.platform.startswith("win"):
        # appveyor
        graphviz_dot = "C:\\ProgramData\\chocolatey\\lib\\graphviz.portable\\tools\\release\\bin\\dot.exe"
        if os.path.exists(graphviz_dot):
            return graphviz_dot

        version = range(34, 42)
        for v in version:
            graphviz_dot = r"C:\Program Files (x86)\Graphviz2.{0}\bin\dot.exe".format(
                v)
            if os.path.exists(graphviz_dot):
                break

    if sys.platform.startswith("win"):
        if not os.path.exists(graphviz_dot):
            raise FileNotFoundError(graphviz_dot)
    else:
        graphviz_dot = "dot"
    return graphviz_dot
