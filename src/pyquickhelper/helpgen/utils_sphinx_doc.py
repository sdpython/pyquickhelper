"""
@file
@brief various helpers to produce a Sphinx documentation

"""
import os
import re
import sys
import shutil
import importlib
from ..loghelper.flog import fLOG, noLOG
from ..filehelper.synchelper import remove_folder, synchronize_folder, explore_folder
from ._my_doxypy import process_string
from .utils_sphinx_doc_helpers import add_file_rst_template, process_var_tag, import_module
from .utils_sphinx_doc_helpers import get_module_objects, add_file_rst_template_cor, add_file_rst_template_title
from .utils_sphinx_doc_helpers import IndexInformation, RstFileHelp, HelpGenException, process_look_for_tag, make_label_index
from ..pandashelper.tblformat import df2rst


def validate_file_for_help(filename, fexclude=lambda f: False):
    """
    Accepts or rejects a file to be copied in the help folder.

    @param      filename        filename
    @param      fexclude        function to exclude some files
    @return                     boolean
    """
    if fexclude is not None and fexclude(filename):
        return False

    if filename.endswith(".pyd") or filename.endswith(".so"):
        return True

    if "rpy2" in filename:  # pragma: no cover
        with open(filename, "r") as ff:
            content = ff.read()
        if "from pandas.core." in content:
            return False

    return True


def replace_relative_import_fct(fullname, content=None):
    """
    Takes a :epkg:`python` file and replaces all relative
    imports it was able to find by an import which can be
    processed by :epkg:`Python` if the file were the main file.

    @param      fullname        name of the file
    @param      content         a preprocessed content of the file of
                                the content if it is None
    @return                     content of the file without relative imports

    .. versionchanged:: 1.8
        Does not change imports in comments.
    """
    if content is None:
        with open(fullname, "r", encoding="utf8") as f:
            content = f.read()

    fullpath = os.path.dirname(fullname)
    fullsplit = fullpath.replace('\\', '/').split('/')
    root = None
    for i in range(len(fullsplit), 1, -1):
        path = "/".join(fullsplit[:i])
        init = os.path.join(path, '__init__.py')
        src = os.path.join(path, 'src')
        cond = init or (not init and src)
        if not cond:
            root = i + 1
            break
        if i < len(fullsplit) and fullsplit[i] in ('src', 'site-packages'):
            root = i + 1
            break
    if root is None:
        raise FileNotFoundError(  # pragma: no cover
            "Unable to package root for '{}'.".format(fullname))

    lines = content.split("\n")
    name = "([a-zA-Z_][a-zA-Z_0-9]*)"
    namedot = "([a-zA-Z_][a-zA-Z_0-9.]*)"
    names = name + "(, " + name + ")*"
    end = "( .*)?$"
    regi = re.compile("{0}{1}{2}{3}{4}".format("^( *)from ([.]{1,3})",
                                               namedot, " import ", names, end))

    for i in range(0, len(lines)):
        line = lines[i]
        find = regi.search(line)

        if find:
            space, dot, rel, name0, names, _, end = find.groups()
            idot = len(dot)
            level = len(fullsplit) - root - idot + 1
            if level > 0:
                if end is None:
                    end = ""
                if names is None:
                    names = ""
                packname = ".".join(fullsplit[root:root + level])
                if rel:
                    packname += '.' + rel
                line = "{space}from {packname} import {name0}{names}{end}".format(
                    space=space, packname=packname, name0=name0, names=names, end=end)
                lines[i] = line
            else:
                raise ValueError(  # pragma: no cover
                    "Unable to replace relative import in '{0}', "
                    "root='{1}'\n{2}|{3}|{4}|{5}| level={6}".format(
                        line, fullsplit[root], dot, rel, name0, names, level))

    return "\n".join(lines)


def _private_process_one_file(
        fullname, to, silent, fmod, replace_relative_import, use_sys):
    """
    Copies one file from the source to the documentation folder.
    It processes some comments in doxygen format (@ param, @ return).
    It replaces relatives imports by a regular import.

    @param      fullname                    name of the file
    @param      to                          location (folder)
    @param      silent                      no logs if True
    @param      fmod                        modification functions
    @param      replace_relative_import     replace relative import
    @param      use_sys                     @see fn remove_undesired_part_for_documentation
    @return                                 extension, number of lines, number of lines in documentation
    """
    ext = os.path.splitext(fullname)[-1]

    if ext in {".jpeg", ".jpg", ".pyd", ".png", ".dat", ".dll", ".o",
               ".so", ".exe", ".enc", ".txt", ".gif", ".csv", '.pyx'}:
        if ext in (".pyd", ".so"):
            # If the file is being executed, the copy might keep the properties of
            # the original (only Windows).
            with open(fullname, "rb") as f:
                bin = f.read()
            with open(to, "wb") as f:
                f.write(bin)
        else:
            shutil.copy(fullname, to)
        return os.path.splitext(fullname)[-1], 0, 0
    else:
        try:
            with open(fullname, "r", encoding="utf8") as g:
                content = g.read()
        except UnicodeDecodeError:  # pragma: no cover
            try:
                with open(fullname, "r") as g:
                    content = g.read()
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end,
                                         "Unable to read '{0}' due to '{1}'".format(fullname, e.reason)) from e

        lines = [_.strip(" \t\n\r") for _ in content.split("\n")]
        lines = [_ for _ in lines if len(_) > 0]
        nblines = len(lines)

        keepc = content
        try:
            counts, content = migrating_doxygen_doc(content, fullname, silent)
        except SyntaxError as e:  # pragma: no cover
            if not silent:
                raise e
            content = keepc
            counts = dict(docrows=0)

        content = fmod(content, fullname)
        content = remove_undesired_part_for_documentation(
            content, fullname, use_sys)
        fold = os.path.split(to)[0]
        if not os.path.exists(fold):
            os.makedirs(fold)
        if replace_relative_import:
            content = replace_relative_import_fct(fullname, content)
        with open(to, "w", encoding="utf8") as g:
            g.write(content)

        return os.path.splitext(fullname)[-1], nblines, counts["docrows"]


def remove_undesired_part_for_documentation(content, filename, use_sys):
    """
    Some files contains blocs inserted between the two lines:

    * ``# -- HELP BEGIN EXCLUDE --``
    * ``# -- HELP END EXCLUDE --``

    Those lines will be commented out.

    @param      content     file content
    @param      filename    for error message
    @param      use_sys     string or None, enables, disables a section based on variables added to sys module
    @return                 modified file content

    If the parameter *use_sys* is false, the section of code
    will be commented out. If true, the section can be enabled.
    It relies on the following code::

        import sys
        if hasattr(sys, "<use_sys>") and sys.<use_sys>:

            # section to enable or disables

    The string ``<use_sys>`` will be replaced by the value of
    parameter *use_sys*.
    """
    marker_in = "# -- HELP BEGIN EXCLUDE --"
    marker_out = "# -- HELP END EXCLUDE --"

    lines = content.split("\n")
    res = []
    inside = False
    has_sys = False
    flask_trick = False
    for line in lines:
        if line.startswith("import sys"):
            has_sys = True
        if line.startswith(marker_in):
            if inside:
                raise HelpGenException(  # pragma: no cover
                    "issues with undesired blocs in file " + filename + " with: " + marker_in + "|" + marker_out)
            inside = True
            if use_sys:  # pragma: no cover
                if not has_sys:
                    res.append("import sys")
                res.append(
                    "if hasattr(sys, '{0}') and sys.{0}:".format(use_sys))
            res.append(line)
        elif line.startswith(marker_out):
            if use_sys and flask_trick:  # pragma: no cover
                res.append("    pass")
            if not inside:
                raise HelpGenException(  # pragma: no cover
                    "issues with undesired blocs in file " + filename + " with: " + marker_in + "|" + marker_out)
            inside = False
            flask_trick = False
            res.append(line)
        else:
            if inside:
                if use_sys:  # pragma: no cover
                    # specific trick for Flask
                    if line.startswith("@app."):
                        line = "# " + line
                        flask_trick = True
                    res.append("    " + line)
                else:
                    res.append("### " + line)
            else:
                res.append(line)
    return "\n".join(res)


def copy_source_files(input, output, fmod=lambda v, filename: v,
                      silent=False, filter=None, remove=True,
                      softfile=lambda f: False,
                      fexclude=lambda f: False,
                      addfilter=None, replace_relative_import=False,
                      copy_add_ext=None, use_sys=None, fLOG=fLOG):
    """
    Copies all sources files (input) into a folder (output),
    apply on each of them a modification.

    :param      input:                      input folder
    :param      output:                     output folder (it will be cleaned each time)
    :param      fmod:                       modifies the content of each file,
                                            this function takes a string and returns a string
    :param      silent:                     if True, do not stop when facing an issue with :epkg:`doxygen` documentation
    :param      filter:                     if None, process only file related to python code, otherwise,
                                            use this filter to select file (regular expression). If this parameter
                                            is None or is empty, the default value is something like:
                                            ``"(.+[.]py$)|(.+[.]pyd$)|(.+[.]cpp$)|(.+[.]h$)|(.+[.]dll$))"``.
    :param      remove:                     if True, remove every files in the output folder first
    :param      softfile:                   softfile is a function (f : filename --> True or False), when it is True,
                                            the documentation is lighter (no special members)
    :param      fexclude:                   function to exclude some files from the help
    :param      addfilter:                  additional filter, it should look like: ``"(.+[.]pyx$)|(.+[.]pyh$)"``
    :param      replace_relative_import:    replace relative import
    :param      copy_add_ext:               additional extension file to copy
    :param      use_sys:                    see :func:`remove_undesired_part_for_documentation
                                            <pyquickhelper.helpgen.utils_sphinx_doc.remove_undesired_part_for_documentation>`
    :param      fLOG:                       logging function
    :return:                                list of copied files
    """
    if not os.path.exists(output):
        os.makedirs(output)

    if remove:
        remove_folder(output, False, raise_exception=False)

    def_ext = ['py', 'pyd', 'cpp', 'h', 'dll', 'so', 'yml', 'o', 'def', 'gif',
               'exe', 'data', 'config', 'css', 'js', 'png', 'map', 'sass',
               'csv', 'tpl', 'jpg', 'jpeg']
    deffilter = "|".join("(.+[.]{0}$)".format(_) for _ in def_ext)
    if copy_add_ext is not None:
        res = ["(.+[.]%s$)" % e for e in copy_add_ext]
        deffilter += "|" + "|".join(res)

    fLOG("[copy_source_files] copy filter '{0}'".format(deffilter))

    if addfilter is not None and len(addfilter) > 0:
        if filter is None or len(filter) == 0:
            filter = "|".join([deffilter, addfilter])
        else:
            filter = "|".join([filter, addfilter])

    if filter is None:
        actions = synchronize_folder(input, output, filter=deffilter,
                                     avoid_copy=True, fLOG=fLOG)
    else:
        actions = synchronize_folder(input, output, filter=filter,
                                     avoid_copy=True, fLOG=fLOG)

    if len(actions) == 0:
        raise FileNotFoundError("empty folder: " + input)  # pragma: no cover

    ractions = []
    for a, file, dest in actions:
        if a != ">+":
            continue
        if not validate_file_for_help(file.fullname, fexclude):
            continue
        if file.name.endswith("setup.py"):
            continue
        if "setup.py" in file.name:
            raise FileNotFoundError(  # pragma: no cover
                "are you sure (setup.py)?, file: " + file.fullname)

        to = os.path.join(dest, file.name)
        dd = os.path.split(to)[0]
        if not os.path.exists(dd):
            fLOG("[copy_source_files] create ", dd,
                 "softfile={0} fexclude={1}".format(softfile, fexclude))
            os.makedirs(dd)
        fLOG("[copy_source_files] copy ", file.fullname, " to ", to)

        rext, rline, rdocline = _private_process_one_file(
            file.fullname, to, silent, fmod, replace_relative_import, use_sys)
        ractions.append((a, file, dest, rext, rline, rdocline))

    return ractions


def apply_modification_template(rootm, store_obj, template, fullname, rootrep,
                                softfile, indexes, additional_sys_path, fLOG=noLOG):
    """
    See @see fn add_file_rst.

    @param      rootm               root of the module
    @param      store_obj           keep track of all objects extracted from the module
    @param      template            rst template to produce
    @param      fullname            full name of the file
    @param      rootrep             file name in the documentation contains some folders which are not desired in the documentation
    @param      softfile            a function (f : filename --> True or False), when it is True,
                                    the documentation is lighter (no special members)
    @param      indexes             dictionary with the label and some information (IndexInformation)
    @param      additional_sys_path additional path to include to sys.path before importing a module
                                    (will be removed afterwards)
    @param      fLOG                logging function
    @return                         content of a .rst file

    .. faqref::
        :title: Why doesn't the documentation show compiled submodules?

        The instruction ``.. automodule:: <name>`` only shows objects *obj*
        which verify ``obj.__module__ == name``. This is always the case
        for modules written in Python but not necessarily for module
        compiled from C language. When the module is declared,
        the following structure contains the module name in second position.
        This name must not be the submodule shortname but the name
        the module has is the package. The C file
        *pyquickhelper/helpgen/compiled.c*
        implements submodule
        ``pyquickhelper.helpgen.compiled``, this value must replace
        ``<fullname>`` in the structure below, not simply *compiled*.

        ::

            static struct PyModuleDef moduledef = {
                    PyModuleDef_HEAD_INIT,
                    "<fullname>",
                    "Helper for parallelization with threads with C++.",
                    sizeof(struct module_state),
                    fonctions,
                    NULL,
                    threader_module_traverse,
                    threader_module_clear,
                    NULL
            };

    .. warning::
        This function still needs some improvments
        for C++ modules on MacOSX.
    """
    from pandas import DataFrame

    keepf = fullname
    filename = os.path.split(fullname)[-1]
    filenoext = os.path.splitext(filename)[0]
    fullname = fullname.strip(".").replace(
        "\\", "/").replace("/", ".").strip(".")
    if rootrep[0] in fullname:
        pos = fullname.index(rootrep[0])
        fullname = rootrep[1] + fullname[pos + len(rootrep[0]):]
    fullnamenoext = fullname[:-3] if fullname.endswith(".py") else fullname
    if fullnamenoext.endswith(".pyd"):
        fullnamenoext = '.'.join(fullnamenoext.split('.')[:-2])
    elif fullnamenoext.endswith('-linux-gnu.so'):
        fullnamenoext = '.'.join(fullnamenoext.split('.')[:-2])
    pythonname = None

    not_expected = os.environ.get(
        "USERNAME", os.environ.get("USER", "````````````"))
    if not_expected not in ('jenkins', 'vsts', 'runner') and not_expected in fullnamenoext:
        mes = ("The title is probably wrong (5): {0}\nnoext='{1}'\npython='{2}'\nrootm='{3}'\nrootrep='{4}'"
               "\nfullname='{5}'\nkeepf='{6}'\nnot_expected='{7}'")  # pragma: no cover
        raise HelpGenException(mes.format(  # pragma: no cover
            fullnamenoext, filenoext, pythonname, rootm, rootrep, fullname, keepf, not_expected))

    mo, prefix = import_module(
        rootm, keepf, fLOG, additional_sys_path=additional_sys_path)
    doc = ""
    shortdoc = ""

    additional = {}
    tspecials = {}

    if mo is not None:
        if isinstance(mo, str):  # pragma: no cover
            # it is an error
            spl = mo.split("\n")
            mo = "\n".join(["    " + _ for _ in spl])
            mo = "::\n\n" + mo + "\n\n"
            doc = mo
            shortdoc = "Error"
            pythonname = fullnamenoext
        else:
            pythonname = mo.__name__
            if mo.__doc__ is not None:
                doc = mo.__doc__
                doc = private_migrating_doxygen_doc(
                    doc.split("\n"), 0, fullname)
                doct = doc
                doc = []

                for d in doct:
                    if len(doc) != 0 or len(d) > 0:
                        doc.append(d)
                while len(doc) > 0 and len(doc[-1]) == 0:
                    doc.pop()

                shortdoc = doc[0] if len(doc) > 0 else ""
                if len(doc) > 1:
                    shortdoc += "..."

                doc = "\n".join(doc)
                doc = "module ``" + mo.__name__ + "``\n\n" + doc
                if ":githublink:" not in doc:
                    doc += "\n\n:githublink:`GitHub|py|*`"
            else:
                doc = ""
                shortdoc = "empty"

            # it produces the table for the function, classes, and
            objs = get_module_objects(mo)

            prefix = ".".join(fullnamenoext.split(".")[:-1])
            for ob in objs:

                if ob.type in ["method"] and ob.name.startswith("_"):
                    tspecials[ob.name] = ob

                ob.add_prefix(prefix)
                if ob.key in store_obj:
                    if isinstance(store_obj[ob.key], list):
                        store_obj[ob.key].append(ob)
                    else:
                        store_obj[ob.key] = [store_obj[ob.key], ob]
                else:
                    store_obj[ob.key] = ob

            for k, v in add_file_rst_template_cor.items():
                values = [[o.rst_link(None, class_in_bracket=False), o.truncdoc]
                          for o in objs if o.type == k]
                if len(values) > 0:
                    tbl = DataFrame(
                        columns=[k, "truncated documentation"], data=values)
                    for row in tbl.values:
                        if ":meth:`_" in row[0]:
                            row[0] = row[0].replace(":meth:`_", ":py:meth:`_")

                    if len(tbl) > 0:
                        maxi = max([len(_) for _ in tbl[k]])
                        s = 0 if tbl.iloc[0, 1] is None else len(
                            tbl.iloc[0, 1])
                        t = "" if tbl.iloc[0, 1] is None else tbl.iloc[0, 1]
                        tbl.iloc[0, 1] = t + (" " * (3 * maxi - s))
                        sph = df2rst(tbl)
                        titl = "\n\n" + add_file_rst_template_title[k] + "\n"
                        titl += "+" * len(add_file_rst_template_title[k])
                        titl += "\n\n"
                        additional[v] = titl + sph
                    else:
                        additional[v] = ""
                else:
                    additional[v] = ""

            del mo

    else:
        doc = "[sphinxerror]-C unable to import."

    if indexes is None:
        indexes = {}
    label = IndexInformation.get_label(indexes, "f-" + filenoext)
    indexes[label] = IndexInformation(
        "module", label, filenoext, doc, None, keepf)
    fLOG("[apply_modification_template] adding into index ", indexes[label])

    try:
        with open(keepf, "r") as ft:
            content = ft.read()
    except UnicodeDecodeError:
        try:
            with open(keepf, "r", encoding="latin-1") as ft:
                content = ft.read()
        except UnicodeDecodeError:  # pragma: no cover
            with open(keepf, "r", encoding="utf8") as ft:
                content = ft.read()

    plat = "Windows" if "This example only runs on Windows." in content else "any"

    # dealing with special members (does not work)
    # text_specials = "".join(["    :special-members: %s\n" % k for k in tspecials ])
    text_specials = ""

    if fullnamenoext.endswith(".__init__"):
        fullnamenoext = fullnamenoext[: -len(".__init__")]
    if filenoext.endswith(".__init__"):
        filenoext = filenoext[: -len(".__init__")]

    not_expected = os.environ.get(
        "USERNAME", os.environ.get("USER", "````````````"))
    if not_expected not in ('jenkins', 'vsts', 'runner') and not_expected in fullnamenoext:
        mes = ("The title is probably wrong (3): {0}\nnoext={1}\npython={2}\nrootm={3}\nrootrep={4}"
               "\nfullname={5}\nkeepf={6}\nnot_expected='{7}'")  # pragma: no cover
        raise HelpGenException(mes.format(  # pragma: no cover
            fullnamenoext, filenoext, pythonname, rootm, rootrep, fullname, keepf, not_expected))

    ttitle = "module ``{0}``".format(fullnamenoext)
    rep = {"__FULLNAME_UNDERLINED__": ttitle + "\n" + ("=" * len(ttitle)) + "\n",
           "__FILENAMENOEXT__": filenoext,
           "__FULLNAMENOEXT__": pythonname,
           "__DOCUMENTATION__": doc.split("\n.. ")[0],
           "__DOCUMENTATIONLINE__": shortdoc.split(".. todoext::")[0],
           "__PLATFORM__": plat,
           "__ADDEDMEMBERS__": text_specials,
           }

    for k, v in additional.items():
        rep[k] = v

    res = template
    for a, b in rep.items():
        res = res.replace(a, b)

    has_class = any(
        filter(lambda _: _.startswith("class "), content.split("\n")))
    if not has_class:
        spl = res.split("\n")
        spl = [_ for _ in spl if not _.startswith(".. inheritance-diagram::")]
        res = "\n".join(spl)

    if softfile(fullname):
        res = res.replace(":special-members:", "")

    return res


def add_file_rst(rootm, store_obj, actions, template=add_file_rst_template,
                 rootrep=("_doc.sphinxdoc.source.pyquickhelper.", ""),
                 fmod=lambda v, filename: v, softfile=lambda f: False,
                 mapped_function=None, indexes=None,
                 additional_sys_path=None, fLOG=noLOG):
    """
    Creates a :epkg:`rst` file for every source file.

    @param      rootm                   root of the module (for relative import)
    @param      store_obj               to keep table of all objects
    @param      actions                 output from @see fn copy_source_files
    @param      template                :epkg:`rst` template to produce
    @param      rootrep                 file name in the documentation contains some folders
                                        which are not desired in the documentation
    @param      fmod                    applies modification to the instanciated template
    @param      softfile                softfile is a function (f : filename --> True or False), when it is True,
                                        the documentation is lighter (no special members)
    @param      mapped_function         list of 2-tuple (pattern, function). Every file matching the pattern
                                        will be copied to the documentation folder, its content will be sent
                                        to the function and will produce a file <filename>.rst. Example:
                                        ``[ (".*[.]sql$", filecontent_to_rst) ]``
                                        The function takes two parameters: full_filename, content_filename. It returns
                                        a string (the rst file) or a tuple (rst file, short description).
                                        By default (if function is None), the function ``filecontent_to_rst`` will be called
                                        except for .rst file for which nothing is done.
    @param      indexes                 to index some information { dictionary label:IndexInformation (...) },
                                        the function populates it
    @param      additional_sys_path     additional path to include to sys.path before importing a module
                                        (will be removed afterwards)
    @param      fLOG                    logging function
    @return                             list of written files stored in RstFileHelp
    """
    if indexes is None:
        indexes = {}
    if mapped_function is None:
        mapped_function = []

    if additional_sys_path is None:
        additional_sys_path = []

    memo = {}
    app = []
    for action in actions:
        _, file, dest = action[:3]
        if not isinstance(file, str):
            file = file.name

        to = os.path.join(dest, file)
        rst = os.path.splitext(to)[0]
        rst += ".rst"
        ext = os.path.splitext(to)[-1]

        if sys.platform == "win32":
            cpxx = ".cp%d%d-" % sys.version_info[:2]
        elif sys.version_info[:2] <= (3, 7):
            cpxx = ".cpython-%d%dm-" % sys.version_info[:2]
        else:
            cpxx = ".cpython-%d%d-" % sys.version_info[:2]

        if file.endswith(".py") or (
                cpxx in file and (
                    file.endswith(".pyd") or file.endswith("linux-gnu.so")
                )):
            if os.stat(to).st_size > 0:
                content = apply_modification_template(
                    rootm, store_obj, template, to, rootrep, softfile, indexes,
                    additional_sys_path=additional_sys_path, fLOG=fLOG)
                content = fmod(content, file)

                # tweaks for example and studies
                zzz = to.replace("\\", "/")
                name = os.path.split(file)[-1]
                noex = os.path.splitext(name)[0]

                # todo: specific case: should be removed and added back in a
                # proper way
                if "examples/" in zzz or "studies/" in zzz:
                    content += "\n.. _%s_literal:\n\nCode\n----\n\n.. literalinclude:: %s\n\n" % (
                        noex, name)

                with open(rst, "w", encoding="utf8") as g:
                    g.write(content)
                app.append(RstFileHelp(to, rst, ""))

                for vv in indexes.values():
                    if vv.fullname == to:
                        vv.set_rst_file(rst)
                        break

        else:
            for pat, func in mapped_function:
                if func is None and ext == ".rst":
                    continue
                if pat not in memo:
                    memo[pat] = re.compile(pat)
                exp = memo[pat]
                if exp.search(file):
                    if isinstance(func, bool) and not func:
                        # we copy but we do nothing with it
                        pass
                    else:
                        with open(to, "r", encoding="utf8") as g:
                            content = g.read()
                        if func is None:
                            func = filecontent_to_rst
                        content = func(to, content)

                        if isinstance(content, tuple) and len(content) == 2:
                            content, doc = content
                        else:
                            doc = ""

                        with open(rst, "w", encoding="utf8") as g:
                            g.write(content)
                        app.append(RstFileHelp(to, rst, ""))

                        filenoext, ext = os.path.splitext(
                            os.path.split(to)[-1])
                        ext = ext.strip(".")
                        label = IndexInformation.get_label(
                            indexes, "ext-" + filenoext)
                        indexes[label] = IndexInformation(
                            "ext-" + ext, label, filenoext, doc, rst, to)
                        fLOG("[add_file_rst] add ext into index ", indexes[label])

    return app


def produces_indexes(store_obj, indexes, fexclude_index, titles=None,
                     correspondances=None, fLOG=fLOG):
    """
    Produces a file for each category of object found in the module.

    @param      store_obj           list of collected object, it is a dictionary
                                    key : ModuleMemberDoc or key : [ list of ModuleMemberDoc ]
    @param      indexes             list of things to index, dictionary { label : IndexInformation }
    @param      fexclude_index      to exclude files from the indices
    @param      titles              each type is mapped to a title to add to the :epkg:`rst` file
    @param      correspondances     each type is mapped to a label to add to the :epkg:`rst` file
    @param      fLOG                logging function
    @return                         dictionary: { type : rst content of the index }

    Default values if *titles* of *correspondances* is None:

    ::

        title = {"method": "Methods",
                 "staticmethod": "Static Methods",
                 "property": "Properties",
                 "function": "Functions",
                 "class": "Classes",
                 "module": "Modules"}

        correspondances = {"method": "l-methods",
                           "function": "l-functions",
                           "staticmethod": "l-staticmethods",
                           "property": "l-properties",
                           "class": "l-classes",
                           "module": "l-modules"}
    """
    from pandas import DataFrame

    if titles is None:
        titles = {"method": "Methods",
                  "staticmethod": "Static Methods",
                  "property": "Properties",
                  "function": "Functions",
                  "class": "Classes",
                  "module": "Modules"}

    if correspondances is None:
        correspondances = {"method": "l-methods",
                           "function": "l-functions",
                           "staticmethod": "l-staticmethods",
                           "property": "l-properties",
                           "class": "l-classes",
                           "module": "l-modules"}

    # we process store_obj
    types = {}
    for k, v in store_obj.items():
        if not isinstance(v, list):
            v = [v]
        for _ in v:
            if fexclude_index(_):
                continue
            types[_.type] = types.get(_.type, 0) + 1

    fLOG("[produces_indexes] store_obj: extraction of types: {}".format(types))
    res = {}
    for k in types:
        fLOG("[produces_indexes] type: [{}] - rst".format(k))
        values = []
        for t, so in store_obj.items():
            if not isinstance(so, list):
                so = [so]

            for o in so:
                if fexclude_index(o):
                    continue
                if o.type != k:
                    continue
                oclname = o.classname.__name__ if o.classname is not None else ""
                rlink = o.rst_link(class_in_bracket=False)
                fLOG("[produces_indexes]   + '{}': {}".format(o.name, rlink))
                values.append([o.name, rlink, oclname, o.truncdoc])

        values.sort()
        for row in values:
            if ":meth:`_" in row[1]:
                row[1] = row[1].replace(":meth:`_", ":py:meth:`_")

        # we filter private method or functions
        values = [
            row for row in values if ":meth:`__" in row or ":meth:`_" not in row]
        values = [
            row for row in values if ":func:`__" in row or ":func:`_" not in row]

        columns = ["_", k, "class parent", "truncated documentation"]
        tbl = DataFrame(columns=columns, data=values)
        if len(tbl.columns) >= 2:
            tbl = tbl.iloc[:, 1:].copy()

        if len(tbl) > 0:
            maxi = max([len(_) for _ in tbl[k]])
            s = 0 if tbl.iloc[0, 1] is None else len(tbl.iloc[0, 1])
            t = "" if tbl.iloc[0, 1] is None else tbl.iloc[0, 1]
            tbl.iloc[0, 1] = t + (" " * (3 * maxi - s))
            sph = df2rst(tbl)
            res[k] = sph
        fLOG("[produces_indexes] type: [{}] - shape: {}".format(k, tbl.shape))

    # we process indexes

    fLOG("[produces_indexes] indexes")
    types = {}
    for k, v in indexes.items():
        if fexclude_index(v):
            continue
        types[v.type] = types.get(v.type, 0) + 1

    fLOG("[produces_indexes] extraction of types: {}".format(types))

    for k in types:
        if k in res:
            raise HelpGenException(
                "you should not index anything related to classes, functions or method (conflict: %s)" % k)
        values = []
        for t, o in indexes.items():
            if fexclude_index(o):
                continue
            if o.type != k:
                continue
            values.append([o.name,
                           o.rst_link(),
                           o.truncdoc])
        values.sort()

        tbl = DataFrame(
            columns=["_", k, "truncated documentation"], data=values)
        if len(tbl.columns) >= 2:
            tbl = tbl[tbl.columns[1:]]

        if len(tbl) > 0:
            maxi = max([len(_) for _ in tbl[k]])
            tbl.iloc[0, 1] = tbl.iloc[0, 1] + \
                (" " * (3 * maxi - len(tbl.iloc[0, 1])))
            sph = df2rst(tbl)
            res[k] = sph

    # end

    for k in res:
        fLOG("[produces_indexes] index name '{}'".format(k))
        label = correspondances.get(k, k)
        title = titles.get(k, k)
        under = "=" * len(title)

        content = "\n".join([".. contents::", "    :local:",
                             "    :depth: 1", "", "", "Summary", "+++++++"])

        not_expected = os.environ.get(
            "USERNAME", os.environ.get("USER", "````````````"))
        if not_expected != "jenkins" and not_expected in title:
            raise HelpGenException(  # pragma: no cover
                "The title is probably wrong (2), found '{0}' in '{1}'".format(not_expected, title))

        res[k] = "\n.. _%s:\n\n%s\n%s\n\n%s\n\n%s" % (
            label, title, under, content, res[k])

    return res


def filecontent_to_rst(filename, content):
    """
    Produces a *.rst* file which contains the file.
    It adds a title and a label based on the
    filename (no folder included).

    @param      filename        filename
    @param      content         content
    @return                     new content
    """
    file = os.path.split(filename)[-1]
    full = file + "\n" + ("=" * len(file)) + "\n"

    not_expected = os.environ.get(
        "USERNAME", os.environ.get("USER", "````````````"))
    if not_expected != "jenkins" and not_expected in file:
        raise HelpGenException(  # pragma: no cover
            "The title is probably wrong (1): '{0}' found in '{1}'".format(not_expected, file))

    rows = ["", ".. _f-%s:" % file, "", "", full, "",
            # "fullpath: ``%s``" % filename,
            "", ""]
    if ".. RSTFORMAT." in content:
        rows.append(".. include:: %s " % file)
    else:
        rows.append(".. literalinclude:: %s " % file)
    rows.append("")

    nospl = content.replace("\n", "_!_!:!_")

    reg = re.compile("(.. beginshortsummary[.](.*?).. endshortsummary[.])")
    cont = reg.search(nospl)
    if cont:
        g = cont.groups()[1].replace("_!_!:!_", "\n")
        return "\n".join(rows), g.strip("\n\r ")

    if "@brief" in content:
        spl = content.split("\n")
        begin = None
        end = None
        for i, r in enumerate(spl):
            if "@brief" in r:
                begin = i
            if end is None and begin is not None and len(
                    r.strip(" \n\r\t")) == 0:
                end = i

        if begin is not None and end is not None:
            summary = "\n".join(spl[begin:end]).replace(
                "@brief", "").strip("\n\t\r ")
        else:
            summary = "no documentation"

        # looking for C++/java/C# comments
        spl = content.split("\n")
        begin = None
        end = None
        for i, r in enumerate(spl):
            if "/**" in spl[i]:
                begin = i
            if end is None and begin is not None and "*/" in spl[i]:
                end = i

        content = "\n".join(rows)
        if begin is not None and end is not None:
            filerows = private_migrating_doxygen_doc(
                spl[begin + 1:end - 1], 1, filename)
            rstr = "\n".join(filerows)
            rstr = re.sub(
                ":param +([a-zA-Z_][[a-zA-Z_0-9]*) *:", r"* **\1**:", rstr)
            content = content.replace(
                ".. literalinclude::", "\n%s\n\n.. literalinclude::" % rstr)

        return content, summary

    return "\n".join(rows), "no documentation"


def prepare_file_for_sphinx_help_generation(store_obj, input, output,
                                            subfolders, fmod_copy=lambda v, filename: v,
                                            template=add_file_rst_template,
                                            rootrep=(
                                                "_doc.sphinxdoc.source.project_name.", ""),
                                            fmod_res=lambda v, filename: v, silent=False,
                                            optional_dirs=None, softfile=lambda f: False,
                                            fexclude=lambda f: False, mapped_function=None,
                                            fexclude_index=lambda f: False, issues=None,
                                            additional_sys_path=None, replace_relative_import=False,
                                            module_name=None, copy_add_ext=None, use_sys=None,
                                            auto_rst_generation=True, fLOG=fLOG):
    """
    Prepares all files for :epkg:`Sphinx` generation.

    @param      store_obj       to keep track of all objects, it should be a dictionary
    @param      input           input folder
    @param      output          output folder (it will be cleaned each time)
    @param      subfolders      list of subfolders to copy from input to output, two cases:
                                    * a string input/<sub> --> output/<sub>
                                    * a tuple input/<sub[0]> --> output/<sub[1]>
    @param      fmod_copy       modifies the content of each file,
                                this function takes a string and the filename and returns a string
                                ``f(content, filename) --> string``
    @param      template        rst template to produce
    @param      rootrep         file name in the documentation contains some folders which are not desired in the documentation
    @param      fmod_res        applies modification to the instanciated template
    @param      silent          if True, do not stop when facing an issue with doxygen migration
    @param      optional_dirs   list of tuple with a list of folders (source, copy, filter) to
                                copy for the documentation, example:
                                ``( <folder_help>, "coverage", ".*" )``
    @param      softfile        softfile is a function (f : filename --> True or False), when it is True,
                                the documentation is lighter (no special members)
    @param      fexclude        function to exclude some files from the help
    @param      fexclude_index  function to exclude some files from the indices

    @param      mapped_function list of 2-tuple (pattern, function). Every file matching the pattern
                                will be copied to the documentation folder, its content will be sent
                                to the function and will produce a file <filename>.rst. Example:
                                ``[ (".*[.]sql$", filecontent_to_rst) ]``
                                The function takes two parameters: full_filename, content_filename. It returns
                                a string (the rst file) or a tuple (rst file, short description).
                                By default (if function is None), the function ``filecontent_to_rst`` will be called.

    @param      issues          if not None (a list), the function will store some issues here.

    @param      additional_sys_path     additional paths to includes to sys.path when import a module (will be removed afterwards)
    @param      replace_relative_import replace relative import
    @param      module_name             module name (cannot be None)
    @param      copy_add_ext            additional file extension to copy
    @param      use_sys                 @see fn remove_undesired_part_for_documentation
    @param      auto_rst_generation     add a file *.rst* for each source file
    @param      fLOG                    logging function

    @return                             list of written files stored in @see cl RstFileHelp

    Example:

    ::

        prepare_file_for_sphinx_help_generation (
                    {},
                    ".",
                    "_doc/sphinxdoc/source/",
                    subfolders      = [
                                        ("src/" + project_var_name,
                                         project_var_name),
                                         ],
                    silent          = True,
                    rootrep         = ("_doc.sphinxdoc.source.%s." %
                                       (project_var_name,), ""),
                    optional_dirs   = optional_dirs,
                    mapped_function = [ (".*[.]tohelp$", None) ] )

    It produces a file with the number of lines and files per extension.
    """
    if optional_dirs is None:
        optional_dirs = []

    if mapped_function is None:
        mapped_function = []

    if additional_sys_path is None:
        additional_sys_path = []

    if module_name is None:
        raise ValueError(  # pragma: no cover
            "module_name cannot be None")

    fLOG("[prepare_file_for_sphinx_help_generation] output='{}'".format(output))
    rootm = os.path.abspath(output)
    fLOG("[prepare_file_for_sphinx_help_generation] input='{}'".format(input))

    actions = []
    rsts = []
    indexes = {}

    for sub in subfolders:
        if isinstance(sub, str):
            src = (input + "/" + sub).replace("//", "/")
            dst = (output + "/" + sub).replace("//", "/")
        else:
            src = (input + "/" + sub[0]).replace("//", "/")
            dst = (output + "/" + sub[1]).replace("//", "/")

        if os.path.isfile(src):
            fLOG("  [p] ", src)
            _private_process_one_file(
                src, dst, silent, fmod_copy, replace_relative_import, use_sys)

            temp = os.path.split(dst)
            actions_t = [(">", temp[1], temp[0], 0, 0)]
            if auto_rst_generation:
                rstadd = add_file_rst(rootm, store_obj, actions_t,
                                      template, rootrep, fmod_res,
                                      softfile=softfile,
                                      mapped_function=mapped_function,
                                      indexes=indexes,
                                      additional_sys_path=additional_sys_path,
                                      fLOG=fLOG)
                rsts += rstadd
        else:
            fLOG("[prepare_file_for_sphinx_help_generation] processing '{}'".format(src))

            actions_t = copy_source_files(src, dst, fmod_copy, silent=silent,
                                          softfile=softfile, fexclude=fexclude,
                                          addfilter="|".join(
                                              ['(%s)' % _[0] for _ in mapped_function]),
                                          replace_relative_import=replace_relative_import,
                                          copy_add_ext=copy_add_ext,
                                          use_sys=use_sys, fLOG=fLOG)

            # without those two lines, importing the module might crash later
            importlib.invalidate_caches()
            importlib.util.find_spec(module_name)

            if auto_rst_generation:
                rsts += add_file_rst(rootm, store_obj, actions_t, template,
                                     rootrep, fmod_res, softfile=softfile,
                                     mapped_function=mapped_function,
                                     indexes=indexes,
                                     additional_sys_path=additional_sys_path,
                                     fLOG=fLOG)

        actions += actions_t

    # everything is cleaned from the build folder, so, it is no use
    for tu in optional_dirs:
        if len(tu) == 2:
            fold, dest, filt = tu + (".*", )
        else:
            fold, dest, filt = tu
        if filt is None:
            filt = ".*"
        if not os.path.exists(dest):
            fLOG("creating folder (sphinx) ", dest)
            os.makedirs(dest)

        copy_source_files(fold, dest, silent=silent, filter=filt,
                          softfile=softfile, fexclude=fexclude,
                          addfilter="|".join(['(%s)' % _[0]
                                              for _ in mapped_function]),
                          replace_relative_import=replace_relative_import,
                          copy_add_ext=copy_add_ext, fLOG=fLOG)

    # processing all store_obj to compute some indices
    fLOG("[prepare_file_for_sphinx_help_generation] processing all store_obj to compute some indices")
    fLOG("[prepare_file_for_sphinx_help_generation] extracted ",
         len(store_obj), " objects")
    res = produces_indexes(store_obj, indexes, fexclude_index, fLOG=fLOG)

    fLOG("[prepare_file_for_sphinx_help_generation] generating ",
         len(res), " indexes for ", ", ".join(list(res.keys())))
    allfiles = []
    for k, vv in res.items():
        out = os.path.join(output, "index_" + k + ".rst")
        allfiles.append("index_" + k)
        fLOG("  generates index", out)
        if k == "module":
            toc = ["\n\n.. toctree::"]
            toc.append("    :maxdepth: 1\n")
            for _ in rsts:
                if _.file is not None and len(_.file) > 0:
                    na = os.path.splitext(_.rst)[0].replace(
                        "\\", "/").split("/")
                    if "source" in na:
                        na = na[na.index("source") + 1:]
                    na = "/".join(na)
                    toc.append("    " + na)
            vv += "\n".join(toc)
        with open(out, "w", encoding="utf8") as fh:
            fh.write(vv)
        rsts.append(RstFileHelp(None, out, None))

    # generates a table with the number of lines per extension
    rows = []
    for act in actions:
        if "__init__.py" not in act[1].get_fullname() or act[-1] > 0:
            v = 1
            rows.append(act[-3:] + (v,))
            name = os.path.split(act[1].get_fullname())[-1]
            if name.startswith("auto_"):
                rows.append(("auto_*" + act[-3], act[-2], act[-1], v))
            elif "__init__.py" in name:
                rows.append(("__init__.py", act[-2], act[-1], v))
        elif "__init__.py" in act[1].get_fullname():
            v = 1
            rows.append(("empty __init__.py", act[-2], act[-1], v))

    # use DataFrame to produce a RST table
    from pandas import DataFrame
    df = DataFrame(
        data=rows, columns=["extension/kind", "nb lines", "nb doc lines", "nb files"])
    try:
        # for pandas >= 0.17
        df = df.groupby(
            "extension/kind", as_index=False).sum().sort_values("extension/kind")
    except AttributeError:  # pragma: no cover
        # for pandas < 0.17
        df = df.groupby(
            "extension/kind", as_index=False).sum().sort("extension/kind")

    # reports
    fLOG("[prepare_file_for_sphinx_help_generation] writing ", "all_report.rst")
    all_report = os.path.join(output, "all_report.rst")
    with open(all_report, "w") as falli:
        falli.write("\n:orphan:\n\n")
        falli.write(".. _l-statcode:\n")
        falli.write("\n")
        falli.write("Statistics on code\n")
        falli.write("==================\n")
        falli.write("\n\n")
        sph = df2rst(df, list_table=True)
        falli.write(sph)
        falli.write("\n")
    rsts.append(RstFileHelp(None, all_report, None))

    # all indexes
    fLOG("[prepare_file_for_sphinx_help_generation] writing ", "all_indexes.rst")
    all_index = os.path.join(output, "all_indexes.rst")
    with open(all_index, "w") as falli:
        falli.write("\n:orphan:\n\n")
        falli.write("\n")
        falli.write("All indexes\n")
        falli.write("===========\n")
        falli.write("\n\n")
        falli.write(".. toctree::\n")
        falli.write("    :maxdepth: 2\n")
        falli.write("\n")
        for k in sorted(allfiles):
            falli.write("    %s\n" % k)
        falli.write("\n")
    rsts.append(RstFileHelp(None, all_index, None))

    # last function to process images
    fLOG("looking for images", output)

    images = os.path.join(output, "images")
    fLOG("+looking for images into ", images, " for folder ", output)
    if os.path.exists(images):
        process_copy_images(output, images)

    # fixes indexed objects with incomplete names
    # :class:`name`  --> :class:`name <...>`
    fLOG("+looking for incomplete references", output)
    fix_incomplete_references(output, store_obj, issues=issues, fLOG=fLOG)
    # for t,so in store_obj.items() :

    # look for FAQ and example
    fLOG("[prepare_file_for_sphinx_help_generation] FAQ + examples")
    app = []
    for tag, title in [("FAQ", "FAQ"),
                       ("example", "Examples"),
                       ("NB", "Magic commands"), ]:
        onefiles = process_look_for_tag(tag, title, rsts)
        for page, onefile in onefiles:
            saveas = os.path.join(output, "all_%s%s.rst" %
                                  (tag,
                                   page.replace(":", "").replace("/", "").replace(" ", "")))
            with open(saveas, "w", encoding="utf8") as fh:
                fh.write(onefile)
            app.append(RstFileHelp(saveas, onefile, ""))
    rsts += app

    fLOG("[prepare_file_for_sphinx_help_generation] END", output)
    return actions, rsts


def process_copy_images(folder_source, folder_images):
    """
    Looks into every file .rst or .py for images (.. image:: imagename),
    if this image was found in directory folder_images, then the image is copied
    closes to the file.

    @param      folder_source       folder where to look for sources
    @param      folder_images       folder where to look for images
    @return                         list of copied images
    """
    _, files = explore_folder(folder_source, "[.]((rst)|(py))$")
    reg = re.compile(".. image::(.*)")
    cop = []
    for fn in files:
        try:
            with open(fn, "r", encoding="utf8") as f:
                content = f.read()
        except Exception as e:  # pragma: no cover
            try:
                with open(fn, "r") as f:
                    content = f.read()
            except Exception:
                raise Exception("Issue with file '{0}'".format(fn)) from e

        lines = content.split("\n")
        for line in lines:
            img = reg.search(line)
            if img:
                name = img.groups()[0].strip()
                fin = os.path.split(name)[-1]
                path = os.path.join(folder_images, fin)
                if os.path.exists(path):
                    dest = os.path.join(os.path.split(fn)[0], fin)
                    shutil.copy(path, dest)
                    fLOG("+copy img ", fin, " to ", dest)
                    cop.append(dest)
                else:
                    fLOG("-unable to find image ", name)
    return cop


def fix_incomplete_references(folder_source, store_obj, issues=None, fLOG=fLOG):
    """
    Looks into every file .rst or .py for incomplete reference. Example::

        :class:`name`  --> :class:`name <...>`.


    @param      folder_source       folder where to look for sources
    @param      store_obj           container for indexed objects
    @param      issues              if not None (a list), it will add issues (function, message)
    @param      fLOG                logging function
    @return                         list of fixed references
    """
    cor = {"func": ["function"],
           "meth": ["method", "property", "staticmethod"]
           }

    _, files = explore_folder(folder_source, "[.](py)$")
    reg = re.compile(
        "(:(py:)?((class)|(meth)|(func)):`([a-zA-Z_][a-zA-Z0-9_]*?)`)")
    cop = []
    for fn in files:
        try:
            with open(fn, "r", encoding="utf8") as f:
                content = f.read()
            encoding = "utf8"
        except Exception:  # pragma: no cover
            with open(fn, "r") as f:
                content = f.read()
            encoding = None

        mainname = os.path.splitext(os.path.split(fn)[-1])[0]

        modif = False
        lines = content.split("\n")
        rline = []
        for line in lines:
            ref = reg.search(line)
            if ref:
                all = ref.groups()[0]
                # pre = ref.groups()[1]
                typ = ref.groups()[2]
                nam = ref.groups()[-1]

                key = None
                obj = None
                for cand in cor.get(typ, [typ]):
                    k = "%s;%s" % (cand, nam)
                    if k in store_obj:
                        if isinstance(store_obj[k], list):
                            se = [
                                _s for _s in store_obj[k] if mainname in _s.rst_link()]
                            if len(se) == 1:
                                obj = se[0]
                                break
                        else:
                            key = k
                            obj = store_obj[k]
                            break

                if key in store_obj:
                    modif = True
                    lnk = obj.rst_link(class_in_bracket=False)
                    fLOG("  i,ref, found ", all, " --> ", lnk)
                    line = line.replace(all, lnk)
                else:
                    fLOG(
                        "  w,unable to replace key ", key, ": ", all, "in file", fn)
                    if issues is not None:
                        issues.append(("fix_incomplete_references",
                                       "unable to replace key %s, link %s in file %s" % (key, all, fn)))

            rline.append(line)

        if modif:
            if encoding == "utf8":
                with open(fn, "w", encoding="utf8") as f:
                    f.write("\n".join(rline))
            else:
                with open(fn, "w") as f:
                    f.write("\n".join(rline))
    return cop


def migrating_doxygen_doc(content, filename, silent=False, log=False, debug=False):
    """
    Migrates the doxygen documentation to rst format.

    @param      content     file content
    @param      filename    filename (to display useful error messages)
    @param      silent      if silent, do not raise an exception
    @param      log         if True, write some information in the logs (not only exceptions)
    @param      debug       display more information on the output if True
    @return                 statistics, new content file

    Function ``private_migrating_doxygen_doc`` enumerates the list of conversion
    which will be done.
    """
    if log:
        fLOG("migrating_doxygen_doc: ", filename)

    rows = []
    counts = {"docrows": 0}

    def print_in_rows(v, file=None):
        rows.append(v)

    def local_private_migrating_doxygen_doc(r, index_first_line, filename):
        counts["docrows"] += len(r)
        return _private_migrating_doxygen_doc(r, index_first_line,
                                              filename, debug=debug, silent=silent)

    process_string(content, print_in_rows, local_private_migrating_doxygen_doc,
                   filename, 0, debug=debug)
    return counts, "\n".join(rows)

# -- HELP BEGIN EXCLUDE --


def private_migrating_doxygen_doc(rows, index_first_line, filename,
                                  debug=False, silent=False):
    """
    Processes a block help (from doxygen to rst).

    @param      rows                list of text lines
    @param      index_first_line    index of the first line (to display useful message error)
    @param      filename            filename (to display useful message error)
    @param      silent              if True, do not display anything
    @param      debug               display more information if True
    @return                         another list of text lines

    @warning    This function uses regular expression to process the documentation,
                it does not import the module (as Sphinx does). It might misunderstand some code.

    @todo Try to import the module and if it possible, uses that information to help
    the parsing.

    The following line displays error message you can click on using SciTe

    ::

        raise SyntaxError("  File \"%s\", line %d, in ???\n    unable to process: %s " %(
            filename, index_first_line+i+1, row))

    __sphinx__skip__

    The previous string tells the function to stop processing the help.

    Doxygen conversions::

        @param      <param_name>  description
        :param      <param_name>: description

        @var        <param_name>  produces a table with the attributes

        @return             description
        :return:            description

        @rtype             description
        :rtype:            description

        @code
        code:: + indentation

        @endcode
        nothing

        @file
        nothing

        @brief
        nothing

        @ingroup  ...
        nothing

        @defgroup  ....
        nothing

        @image html ...

        @see,@ref  label forbidden
        should be <op> <fn> <label>, example: @ref cl label
        <op> must be in [fn, cl, at, me, te, md]

        :class:`label`
        :func:`label`
        :attr:`label`
        :meth:`label`
        :mod:`label`

        @warning description  (until next empty line)
        .. warning::
           description

        @todo
        .. todo:: a todo box

        ------------- not done yet

        @img      image name
        .. image:: test.png
            :width: 200pt

        .. raw:: html
            html indente

    """
    return _private_migrating_doxygen_doc(rows, index_first_line, filename,
                                          debug=debug, silent=silent)

# -- HELP END EXCLUDE --


def _private_migrating_doxygen_doc(rows, index_first_line, filename,
                                   debug=False, silent=False):
    if debug:  # pragma: no cover
        fLOG("------------------ P0")
        fLOG("\n".join(rows))
        fLOG("------------------ P")

    debugrows = rows
    rows = [_.replace("\t", "    ") for _ in rows]
    pars = re.compile("([@]param( +)([a-zA-Z0-9_]+)) ")
    refe = re.compile(
        "([@]((see)|(ref)) +((fn)|(cl)|(at)|(me)|(te)|(md)) +([a-zA-Z0-9_]+))($|[^a-zA-Z0-9_])")
    exce = re.compile("([@]exception( +)([a-zA-Z0-9_]+)) ")
    exem = re.compile("([@]example[(](.*?___)?(.*?)[)])")
    faq_ = re.compile("([@]FAQ[(](.*?___)?(.*?)[)])")
    nb_ = re.compile("([@]NB[(](.*?___)?(.*?)[)])")

    # min indent
    if len(rows) > 1:
        space_rows = [(r.lstrip(), r) for r in rows[1:] if len(r.strip()) > 0]
    else:
        space_rows = []
    if len(space_rows) > 0:
        min_indent = min(len(r[1]) - len(r[0]) for r in space_rows)
    else:
        min_indent = 0

    # We fix the first rows which might be different from the others.
    if len(rows) > 1:
        r = rows[0]
        r = (r.lstrip(), r)
        delta = len(r[1]) - len(r[0])
        if delta != min_indent:
            rows = rows.copy()
            rows[0] = " " * min_indent + rows[0].lstrip()

    # processing doxygen documentation
    indent = False
    openi = False
    beginends = {}

    typstr = str

    whole = "\n".join(rows)
    if "@var" in whole:
        whole = process_var_tag(whole, True)
        rows = whole.split("\n")

    for i in range(len(rows)):
        row = rows[i]

        if debug:
            fLOG("-- indent=%s openi=%s row=%s" % (indent, openi, row))

        if "__sphinx__skip__" in row:
            if not silent:
                fLOG("  File \"%s\", line %s, skipping" %
                     (filename, index_first_line + i + 1))
            break

        strow = row.strip(" ")

        if "@endFAQ" in strow or "@endexample" in strow or "@endNB" in strow:
            if "@endFAQ" in strow:
                beginends["FAQ"] = beginends.get("FAQ", 0) - 1
                sp = " " * row.index("@endFAQ")
                rows[i] = "\n" + sp + ".. endFAQ.\n"
            if "@endexample" in strow:
                beginends["example"] = beginends.get("example", 0) - 1
                sp = " " * row.index("@endexample")
                rows[i] = "\n" + sp + ".. endexample.\n"
            if "@endNB" in strow:  # pragma: no cover
                beginends["NB"] = beginends.get("NB", 0) - 1
                sp = " " * row.index("@endNB")
                rows[i] = "\n" + sp + ".. endNB.\n"
            continue

        if indent:
            if (not openi and len(strow) == 0) or "@endcode" in strow:
                indent = False
                rows[i] = ""
                openi = False
                if "@endcode" in strow:
                    beginends["code"] = beginends.get("code", 0) - 1
            else:
                rows[i] = "    " + rows[i]

        else:

            if strow.startswith("@warning"):
                pos = rows[i].find("@warning")
                sp = " " * pos
                rows[i] = rows[i].replace("@warning", "\n%s.. warning:: " % sp)
                indent = True

            elif strow.startswith("@todo"):
                pos = rows[i].find("@todo")
                sp = " " * pos
                rows[i] = rows[i].replace("@todo", "\n%s.. todo:: " % sp)
                indent = True

            elif strow.startswith("@ingroup"):
                rows[i] = ""

            elif strow.startswith("@defgroup"):
                rows[i] = ""

            elif strow.startswith("@image"):
                pos = rows[i].find("@image")
                sp = " " * pos
                spl = strow.split()
                img = spl[-1]
                if img.startswith("http://"):
                    rows[i] = "\n%s.. fancybox:: " % sp + img + "\n\n"
                else:

                    if img.startswith("images") or img.startswith("~"):
                        # we assume it is a relative path to the source
                        img = img.strip("~")
                        spl_path = filename.replace("\\", "/").split("/")
                        pos = spl_path.index("src")
                        dots = [".."] * (len(spl_path) - pos - 2)
                        ref = "/".join(dots) + "/"
                    else:
                        ref = ""

                    sp = " " * row.index("@image")
                    rows[i] = "\n%s.. image:: %s%s\n%s    :align: center\n" % (
                        sp, ref, img, sp)

            elif strow.startswith("@code"):
                pos = rows[i].find("@code")
                sp = " " * pos
                prev = i - 1
                while prev > 0 and len(rows[prev].strip(" \n\r\t")) == 0:
                    prev -= 1
                rows[i] = ""
                if rows[prev].strip("\n").endswith("."):
                    rows[prev] += "\n\n%s::\n" % sp
                else:
                    rows[prev] += (":" if rows[prev].endswith(":") else "::")
                indent = True
                openi = True
                beginends["code"] = beginends.get("code", 0) + 1

            # basic tags
            row = rows[i]

            # tag param
            look = pars.search(row)
            lexxce = exce.search(row)
            example = exem.search(row)
            faq = faq_.search(row)
            nbreg = nb_.search(row)

            if look:
                rep = look.groups()[0]
                sp = look.groups()[1]
                name = look.groups()[2]
                to = ":param%s%s:" % (sp, name)
                rows[i] = row.replace(rep, to)

                # it requires an empty line before if the previous line does
                # not start by :
                if i > 0 and not rows[
                        i - 1].strip().startswith(":") and len(rows[i - 1].strip()) > 0:
                    rows[i] = "\n" + rows[i]

            elif lexxce:
                rep = lexxce.groups()[0]
                sp = lexxce.groups()[1]
                name = lexxce.groups()[2]
                to = ":raises%s%s:" % (sp, name)
                rows[i] = row.replace(rep, to)

                # it requires an empty line before if the previous line does
                # not start by :
                if i > 0 and not rows[
                        i - 1].strip().startswith(":") and len(rows[i - 1].strip()) > 0:
                    rows[i] = "\n" + rows[i]

            elif example:
                sp = " " * row.index("@example")
                rep = example.groups()[0]
                exa = example.groups()[2].replace("[|", "(").replace("|]", ")")
                pag = example.groups()[1]
                if pag is None:
                    pag = ""
                fil = os.path.splitext(os.path.split(filename)[-1])[0]
                fil = re.sub(r'([^a-zA-Z0-9_])', "", fil)
                ref = fil + "-l%d" % (i + index_first_line)
                ref2 = make_label_index(exa, typstr(example.groups()))
                to = "\n\n%s.. _le-%s:\n\n%s.. _le-%s:\n\n%s**Example: %s**  \n\n%s.. example(%s%s;;le-%s).\n" % (
                    sp, ref, sp, ref2, sp, exa, sp, pag, exa, ref)
                rows[i] = row.replace(rep, to)

                # it requires an empty line before if the previous line does
                # not start by :
                if i > 0 and not rows[
                        i - 1].strip().startswith(":") and len(rows[i - 1].strip()) > 0:
                    rows[i] = "\n" + rows[i]
                beginends["example"] = beginends.get("example", 0) + 1

            elif faq:
                sp = " " * row.index("@FAQ")
                rep = faq.groups()[0]
                exa = faq.groups()[2].replace("[|", "(").replace("|]", ")")
                pag = faq.groups()[1]
                if pag is None:
                    pag = ""
                fil = os.path.splitext(os.path.split(filename)[-1])[0]
                fil = re.sub(r'([^a-zA-Z0-9_])', "", fil)
                ref = fil + "-l%d" % (i + index_first_line)
                ref2 = make_label_index(exa, typstr(faq.groups()))
                to = "\n\n%s.. _le-%s:\n\n%s.. _le-%s:\n\n%s**FAQ: %s**  \n\n%s.. FAQ(%s%s;;le-%s).\n" % (
                    sp, ref, sp, ref2, sp, exa, sp, pag, exa, ref)
                rows[i] = row.replace(rep, to)

                # it requires an empty line before if the previous line does
                # not start by :
                if i > 0 and not rows[
                        i - 1].strip().startswith(":") and len(rows[i - 1].strip()) > 0:
                    rows[i] = "\n" + rows[i]
                beginends["FAQ"] = beginends.get("FAQ", 0) + 1

            elif nbreg:  # pragma: no cover
                sp = " " * row.index("@NB")
                rep = nbreg.groups()[0]
                exa = nbreg.groups()[2].replace("[|", "(").replace("|]", ")")
                pag = nbreg.groups()[1]
                if pag is None:
                    pag = ""
                fil = os.path.splitext(os.path.split(filename)[-1])[0]
                fil = re.sub(r'([^a-zA-Z0-9_])', "", fil)
                ref = fil + "-l%d" % (i + index_first_line)
                ref2 = make_label_index(exa, typstr(nbreg.groups()))
                to = "\n\n%s.. _le-%s:\n\n%s.. _le-%s:\n\n%s**NB: %s**  \n\n%s.. NB(%s%s;;le-%s).\n" % (
                    sp, ref, sp, ref2, sp, exa, sp, pag, exa, ref)
                rows[i] = row.replace(rep, to)

                # it requires an empty line before if the previous line does
                # not start by :
                if i > 0 and not rows[
                        i - 1].strip().startswith(":") and len(rows[i - 1].strip()) > 0:
                    rows[i] = "\n" + rows[i]
                beginends["NB"] = beginends.get("NB", 0) + 1

            elif "@return" in row:
                rows[i] = row.replace("@return", ":return:")
                # it requires an empty line before if the previous line does
                # not start by :
                if i > 0 and not rows[
                        i - 1].strip().startswith(":") and len(rows[i - 1].strip()) > 0:
                    rows[i] = "\n" + rows[i]

            elif "@rtype" in row:
                rows[i] = row.replace("@rtype", ":rtype:")
                # it requires an empty line before if the previous line does
                # not start by :
                if i > 0 and not rows[
                        i - 1].strip().startswith(":") and len(rows[i - 1].strip()) > 0:
                    rows[i] = "\n" + rows[i]

            elif "@brief" in row:
                rows[i] = row.replace("@brief", "").strip()
            elif "@file" in row:
                rows[i] = row.replace("@file", "").strip()

            # loop on references
            refl = refe.search(rows[i])
            while refl:
                see = "see" in refl.groups()[1]
                see = ""  # " " if see else ""
                ty = refl.groups()[4]
                name = refl.groups()[-2]
                if len(name) == 0:
                    raise SyntaxError(
                        "name should be empty: " + typstr(refl.groups()))
                rep = refl.groups()[0]
                ty = {"cl": "class", "me": "meth", "at": "attr",
                      "fn": "func", "te": "term", "md": "mod"}[ty]
                to = "%s:%s:`%s`" % (see, ty, name)
                rows[i] = rows[i].replace(rep, to)
                refl = refe.search(rows[i])

    if not debug:
        for i, row in enumerate(rows):
            if "__sphinx__skip__" in row:
                break
            if "@param" in row or "@return" in row or "@see" in row or "@warning" in row \
                    or "@todo" in row or "@code" in row or "@endcode" in row or "@brief" in row or "@file" in row \
                    or "@rtype" in row or "@exception" in row \
                    or "@example" in row or "@NB" in row or "@endNB" in row or "@endexample" in row:
                if not silent:  # pragma: no cover
                    fLOG("#########################")
                    _private_migrating_doxygen_doc(
                        debugrows, index_first_line, filename, debug=True)
                    fLOG("#########################")
                    mes = "  File \"%s\", line %d, in ???\n    unable to process: %s \nwhole blocks:\n%s" % (
                        filename, index_first_line + i + 1, row, "\n".join(rows))
                    fLOG("[sphinxerror]-D ", mes)
                else:  # pragma: no cover
                    mes = "  File \"%s\", line %d, in ???\n    unable to process: %s \nwhole blocks:\n%s" % (
                        filename, index_first_line + i + 1, row, "\n".join(rows))
                raise SyntaxError(mes)  # pragma: no cover

    for k, v in beginends.items():
        if v != 0:  # pragma: no cover
            mes = "  File \"%s\", line %d, in ???\n    unbalanced tag %s: %s \nwhole blocks:\n%s" % (
                filename, index_first_line + i + 1, k, row, "\n".join(rows))
            fLOG("[sphinxerror]-E ", mes)
            raise SyntaxError(mes)

    # add githublink
    link = [_ for _ in rows if ":githublink:" in _]
    if len(link) == 0:
        rows.append("")
        rows.append("{1}:githublink:`%|py|{0}`".format(
            index_first_line, " " * min_indent))

    # clean rows
    clean_rows = []
    for row in rows:
        if row.strip():
            clean_rows.append(row)
        elif len(clean_rows) > 0:
            clean_rows.append('')
    return clean_rows


def doc_checking():
    """
    Example of a doc string.
    """
    pass


class useless_class_UnicodeStringIOThreadSafe (str):

    """avoid conversion problem between str and char,
    class protected again Thread issue"""

    def __init__(self):
        """
        creates a lock
        """
        str.__init__(self)
        import threading
        self.lock = threading.Lock()
