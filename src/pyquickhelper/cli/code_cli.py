"""
@file
@brief Command line about transfering files.
"""
import importlib


def code_stat(names, output=None, fLOG=print):
    """
    Returns statistics about the documentation of a module.

    :param names: module name comma separated value
    :param output: output file name
    :param fLOG: logging function
    :return: status

    .. cmdref::
        :title: Returns statistics about the documentation of a module
        :cmd: -m pyquickhelper code_stat --help

        The command line returns a table with the number of lines of code
        and documentatation.
    """
    from ..texthelper.code_helper import measure_documentation_module
    if not isinstance(names, list):
        names = names.split(',')
    mods = [importlib.import_module(name) for name in names]
    stat = measure_documentation_module(mods, ratio=True, as_df=True)

    if output is None:
        fLOG(stat)
        return None
    if output.endswith(".xlsx"):
        stat.to_excel(output, index=False)
    else:
        stat.to_csv(output, index=False)
    return stat
