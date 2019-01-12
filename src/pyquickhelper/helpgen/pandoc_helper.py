"""
@file
@brief Helpers to call pandoc and convert documents
"""
import os
from .conf_path_tools import find_pandoc_path
from ..loghelper import noLOG, run_cmd


def call_pandoc(params, fLOG=noLOG):
    """
    Call :epkg:`pandoc`.

    @param      params  parameters
    @param      fLOG    logging function
    @return             out, err
    """
    pandoc = os.path.join(find_pandoc_path(), "pandoc")
    cmd = '"{0}" {1}'.format(pandoc, params)
    out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
    if err is not None and "Cannot decode byte" in err:
        raise Exception(
            "Issue with pandac:\n{0}\nOUT:\n{1}\nERR\n{2}".format(cmd, out, err))
    return out, err


def latex2rst(input, output, encoding="utf-8", fLOG=noLOG, temp_file=None):
    """
    convert a latex document into a rst document using pandoc

    @param      input       input file
    @param      output      output file
    @param      encoding    encoding
    @param      temp_file   temporary file
    @param      fLOG        logging function
    @return                 see @see fn call_pandoc

    If the encoding is not utf-8, the function uses *temp_file* to store
    the temporary conversion into utf-8.
    """
    if encoding not in ("utf-8", "utf8"):
        with open(input, "r", encoding=encoding) as f:
            content = f.read()
        if temp_file is None:
            raise ValueError("temp_file cannot be None, encoding is not utf-8 and a temporary " +
                             "file will be used to do the conversion.")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(content)
        input = temp_file
    else:
        temp_file = None
    cmd = '-s -t rst --toc "{0}" -o "{1}"'.format(input, output)
    out, err = call_pandoc(cmd, fLOG=fLOG)
    if temp_file is not None:
        os.remove(temp_file)
    return out, err
