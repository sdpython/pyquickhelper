"""
@file
@brief  Functions about checking, statistics on files used in the documentation.
"""
import os
import re
from ..filehelper import explore_folder, explore_folder_iterfile


def enumerate_notebooks_link(nb_folder, nb_rst):
    """
    Looks for all links to a notebook in the documentation.

    @param      nb_folder   notebook folder
    @param      nb_rst      documentation folder
    @return                 iterator on *(rst_file, nb_file, link type, pos_start, pos_end, string, title)*

    The function also outputs unreferenced notebooks.
    *rst_file* is None in that case.

    Example of outputs:

    ::

        ('...index_class.rst', '...having_a_form_in_a_notebook.ipynb', 'ref', 79880, 79912, ':ref:`havingaforminanotebookrst`')
        ('...index_module.rst', '...having_a_form_in_a_notebook.ipynb', 'ref', 277928, 277960, ':ref:`havingaforminanotebookrst`')

    """
    # We check that all readme.txt follow utf-8.
    for name in explore_folder_iterfile(nb_folder, "((readme)|(README))[.]txt$",
                                        ".*((checkpoints)|(MACOSX)).*", fullname=True):
        with open(name, "r", encoding="utf-8") as f:
            try:
                nbcontent = f.read()
            except UnicodeDecodeError as e:
                raise ValueError(
                    "Issue with file '{0}'".format(name)) from e
        reg_title = re.compile("\\\"([#] [^#]+?)\\n")

    rsts = explore_folder(nb_rst, ".*[.]rst$")[1]
    crsts = {}
    for rst in rsts:
        with open(rst, "r", encoding="utf-8") as f:
            try:
                crsts[rst] = f.read()
            except UnicodeDecodeError as e:
                raise ValueError(
                    "Issue with file '{0}'".format(rst)) from e

    nbcount = {}

    for name in explore_folder_iterfile(nb_folder, ".*[.]ipynb$", ".*checkpoints.*", fullname=True):
        with open(name, "r", encoding="utf-8") as f:
            try:
                nbcontent = f.read()
            except UnicodeDecodeError as e:
                raise ValueError(
                    "Issue with file '{0}'".format(name)) from e
        reg_title = re.compile("\\\"([#] [^#]+?)\\n")
        ftitle = reg_title.findall(nbcontent)
        if len(ftitle) > 0:
            title = ftitle[0].strip(" \n\r\t")
        else:
            title = None
        sh = os.path.splitext(os.path.split(name)[-1])[0]
        reg1 = re.compile("[/ ](" + sh + ")\\n")
        reg2 = re.compile("(:ref:`.*? <{0}rst>`)".format(sh.replace("_", "")))
        reg3 = re.compile("(:ref:`{0}rst`)".format(sh.replace("_", "")))
        reg4 = re.compile("(<.*?" + sh + ">)\\n")
        nbcount[name] = 0
        for rst, content in crsts.items():
            iter = reg1.finditer(content)
            for it in iter:
                nbcount[name] += 1
                yield (rst, name, "toctree", it.start(0), it.end(0), it.groups(0)[0], title)
            iter = reg4.finditer(content)
            for it in iter:
                nbcount[name] += 1
                yield (rst, name, "toctreen", it.start(0), it.end(0), it.groups(0)[0], title)
            iter = reg2.finditer(content)
            for it in iter:
                nbcount[name] += 1
                yield (rst, name, "refn", it.start(0), it.end(0), it.groups(0)[0], title)
            iter = reg3.finditer(content)
            for it in iter:
                nbcount[name] += 1
                yield (rst, name, "ref", it.start(0), it.end(0), it.groups(0)[0], title)
        if nbcount[name] == 0:
            yield (None, name, None, -1, -1, "", title)
