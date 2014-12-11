#-*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.

"""
import os,sys, shutil, datetime, re, importlib

from ..loghelper.flog           import run_cmd, fLOG
from ..loghelper.pyrepo_helper  import SourceRepository
from ..pandashelper.tblformat   import df_to_rst
from .utils_sphinx_doc          import prepare_file_for_sphinx_help_generation
from .utils_sphinx_doc_helpers  import HelpGenException, find_latex_path, find_graphviz_dot, find_pandoc_path
from ..sync.synchelper          import explore_folder, has_been_updated
from .utils_sphinx_config       import ie_layout_html

template_examples = """

List of programs
++++++++++++++++

.. toctree::
   :maxdepth: 2

.. autosummary:: __init__.py
   :toctree: %s/
   :template: modules.rst

Another list
++++++++++++

"""

def generate_help_sphinx (  project_var_name,
                            clean           = True,
                            root            = ".",
                            filter_commit   = lambda c : c.strip() != "documentation",
                            extra_ext       = [],
                            nbformats       = ["ipynb", "html", "python", "rst", "pdf"],
                            layout          = [("html", "build", {})]) :
    """
    runs the help generation
        - copies every file in another folder
        - replaces comments in doxygen format into rst format
        - replaces local import by global import (tweaking sys.path too)
        - calls sphinx to generate the documentation.

    @param      project_var_name    project name
    @param      clean               if True, cleans the previous documentation first, does not work on linux yet
    @param      root                see below
    @param      filter_commit       function which accepts a commit to show on the documentation (based on the comment)
    @param      extra_ext           list of file extensions
    @param      nbformats           requested formats for the notebooks conversion
    @param      layout              list of formats sphinx should generate such as html, latex, pdf, docx,
                                    it is a list of tuple (layout, build directory, parameters to override)

    The result is stored in path: ``root/_doc/sphinxdoc/source``.
    We assume the file ``root/_doc/sphinxdoc/source/conf.py`` exists
    as well as ``root/_doc/sphinxdoc/source/index.rst``.

    If you generate latex/pdf files, you should add variables ``latex_path`` and ``pandoc_path``
    in your file ``conf.py`` which defines the help.

    You can exclud some part while generating the documentation by adding:

        * ``# -- HELP BEGIN EXCLUDE --``
        * ``# -- HELP END EXCLUDE --``

    @code
    latex_path  = r"C:/Program Files/MiKTeX 2.9/miktex/bin/x64"
    pandoc_path = r"%USERPROFILE%/AppData/Local/Pandoc"
    @endcode

    @example(run help generation)
    @code
    # from the main folder which contains folder src
    generate_help_sphinx("pyquickhelper")
    @endcode
    @endexample

    By default, the function only consider files end by ``.py`` and ``.rst`` but you could
    add other files sharing the same extensions by adding this one
    in the ``extra_ext`` list.

    @example(other page of examples___run help generation)
    This example is exactly the same as the previous one but will be generated on another page of examples.
    @code
    # from the main folder which contains folder src
    generate_help_sphinx("pyquickhelper")
    @endcode
    @endexample

    @example(page with an accent -é- in the title___run help generation)
    Same page with an accent.
    @code
    # from the main folder which contains folder src
    generate_help_sphinx("pyquickhelper")
    @endcode
    @endexample

    The function requires:
        - pandoc
        - latex

    @warning Some themes such as `Bootstrap Sphinx Theme <http://ryan-roemer.github.io/sphinx-bootstrap-theme/>`_ do not work on Internet Explorer. In that case, the
             file ``<python_path>/Lib/site-packages/sphinx/themes/basic/layout.html``
             must be modified to add the following line (just below ``Content-Type``).

             @code
             <meta http-equiv="X-UA-Compatible" content="IE=edge" />
             @endcode
    """
    ie_layout_html()

    root = os.path.abspath(root)
    froot = root
    sys.path.append (os.path.join(root, "_doc", "sphinxdoc","source"))

    src = SourceRepository(commandline=True)
    version = src.version(root)
    if version is not None :
        with open("version.txt", "w") as f : f.write(str(version) + "\n")

    # modifies the version number in conf.py
    shutil.copy("README.rst", "_doc/sphinxdoc/source")
    shutil.copy("LICENSE.txt", "_doc/sphinxdoc/source")

    # import conf.py
    theconf = importlib.import_module('conf')
    if theconf is None:
        raise ImportError("unable to import conf.py which defines the help generation")

    latex_path      = theconf.__dict__.get("latex_path",find_latex_path())
    graphviz_dot    = theconf.__dict__.get("graphviz_dot", find_graphviz_dot())
    pandoc_path     = theconf.__dict__.get("pandoc_path",find_pandoc_path())

    #changes
    chan = os.path.join (root, "_doc", "sphinxdoc", "source", "filechanges.rst")
    generate_changes_repo(chan, root, filter_commit = filter_commit)

    # copy the files
    optional_dirs = [ ]

    mapped_function = [ (".*[.]%s$" % ext.strip(".") , None) for ext in extra_ext ]

    prepare_file_for_sphinx_help_generation (
                {},
                root,
                "_doc/sphinxdoc/source/",
                subfolders      = [
                                    ("src/" + project_var_name, project_var_name),
                                     ],
                silent          = True,
                rootrep         = ("_doc.sphinxdoc.source.%s." % (project_var_name,), ""),
                optional_dirs   = optional_dirs,
                mapped_function = mapped_function,
                replace_relative_import = False)

    fLOG("**** end of prepare_file_for_sphinx_help_generation")

    # notebooks
    notebook_dir = os.path.abspath(os.path.join("_doc", "notebooks"))
    notebook_doc = os.path.abspath(os.path.join("_doc/sphinxdoc/source", "notebooks"))
    if os.path.exists(notebook_dir):
        notebooks = explore_folder(notebook_dir, pattern=".*[.]ipynb", fullname=True)[1]
        notebooks = [ _ for _ in notebooks if "checkpoint" not in _ ]
        if len(notebooks) > 0:
            fLOG("**** notebooks", nbformats)
            build = os.path.abspath("build/notebooks")
            if not os.path.exists(build): os.makedirs(build)
            if not os.path.exists(notebook_doc): os.mkdir(notebook_doc)
            nbs = process_notebooks(notebooks,
                                    build=build,
                                    outfold=notebook_doc,
                                    formats=nbformats,
                                    latex_path=latex_path,
                                    pandoc_path=pandoc_path)
            nbs = list(set(nbs))
            add_notebook_page(nbs, os.path.join(notebook_doc,"..","all_notebooks.rst"))

        imgs = [ os.path.join(notebook_dir,_) for _ in os.listdir(notebook_dir) if ".png" in _  ]
        if len(imgs) > 0 :
            for img in imgs :
                shutil.copy (img, notebook_doc)


    #  run the documentation generation
    temp = os.environ ["PATH"]
    pyts = get_executables_path()
    sepj = ";" if sys.platform.startswith("win") else ":"
    script = sepj.join(pyts)
    fLOG ("adding " + script)
    temp = script + sepj + temp
    os.environ["PATH"] = temp
    fLOG("changing PATH", temp)
    pa = os.getcwd ()

    thispath = os.path.normpath(root)
    docpath  = os.path.normpath(os.path.join(thispath, "_doc","sphinxdoc"))

    fLOG("checking encoding utf8...")
    for root, dirs, files in os.walk(docpath):
        for name in files:
            thn = os.path.join(root, name)
            if name.endswith(".rst") :
                try :
                    with open(thn, "r", encoding="utf8") as f : f.read()
                except UnicodeDecodeError as e :
                    raise HelpGenException ("issue with encoding for file ", thn) from e
                except Exception as e :
                    raise HelpGenException ("issue with file ", thn) from e

    fLOG("running sphinx... from", docpath)
    if not os.path.exists (docpath) :
        raise FileNotFoundError(docpath)

    os.chdir (docpath)

    cmds=[]
    lays = []
    for t3 in layout :
        if isinstance(t3,str) : lay,build,override,newconf = t3,"build",{},None
        elif len(t3) == 1 :     lay,build,override,newconf = t3[0],"build",{},None
        elif len(t3) == 2 :     lay,build,override,newconf = t3[0],t3[1],{}, None
        elif len(t3) == 3 :     lay,build,override,newconf = t3[0],t3[1],t3[2],None
        else :                  lay,build,override,newconf = t3

        if lay == "pdf":
            lay = "latex"

        if clean and sys.platform.startswith("win"):
            if os.path.exists(build):
                for fold in os.listdir(build):
                    cmd = "rmdir /q /s {0}\\{1}".format(build,fold)
                    run_cmd(cmd, wait=True)
            cmd = r"del /q /s {0}\*".format(build)
            run_cmd (cmd, wait = True)

        over = [ " -D {0}={1}".format(k,v) for k,v in override.items() ]
        over = "".join(over)

        sconf = "" if newconf is None else " -c {0}".format(newconf)

        cmd = "sphinx-build -b {1} -d {0}/doctrees{2}{3} source {0}/{1}".format(build, lay, over, sconf)
        cmds.append(cmd)
        fLOG("run:", cmd)
        lays.append(lay)

    #cmd = "make {0}".format(lay)

    # This instruction should work but it does not. Sphinx seems to be stuck.
    #run_cmd (cmd, wait = True, secure="make_help.log", stop_waiting_if = lambda v : "build succeeded" in v)
    # The following one works but opens a extra windows.
    for cmd in cmds :
        os.system(cmd)

    # we copy the coverage files if it is missing
    covfold = os.path.join(docpath, "source", "coverage")
    if os.path.exists(covfold):
        fLOG("## coverage folder:", covfold)
        allfiles = os.listdir(covfold)
        allf = [ _ for _ in allfiles if _.endswith(".rst") ]
        if len(allf) == 0:
            # no rst file --> we copy
            allfiles = [ os.path.join(covfold, _) for _ in allfiles ]
            for lay in lays:
                covbuild = os.path.join(docpath, build, lay, "coverage")
                fLOG("covbuild", covbuild)
                if not os.path.exists(covbuild):
                    os.mkdir(covbuild)
                for f in allfiles:
                    fLOG("copy ", f, " to ", covbuild)
                    shutil.copy(f, covbuild)
    else:
        fLOG("## no coverage files", covfold)

    if "latex" in lays:
        post_process_latex_output(froot, False)

    if "pdf" in layout:
        compile_latex_output_final(froot, latex_path, False)

    # end
    os.chdir (pa)

def get_executables_path() :
    """
    returns the paths to Python, Python Scripts

    @return     a list of paths
    """
    res  = [ os.path.split(sys.executable)[0] ]
    if sys.platform.startswith("win") :
        res += [ os.path.join(res[-1], "Scripts") ]
        ver = "c:\\Python%d%d" % (sys.version_info.major, sys.version_info.minor)
        res += [ver ]
        res += [ os.path.join(res[-1], "Scripts") ]

    return res

def generate_changes_repo(  chan,
                            source,
                            exception_if_empty = True,
                            filter_commit = lambda c : c.strip() != "documentation") :
    """
    Generates a rst tables containing the changes stored by a svn or git repository,
    the outcome is stored in a file.
    The log comment must start with ``*`` to be taken into account.

    @param          chan                filename to write (or None if you don't need to)
    @param          source              source folder to get changes for
    @param          exception_if_empty  raises an exception if empty
    @param          filter_commit       function which accepts a commit to show on the documentation (based on the comment)
    @return                             string (rst tables with the changes)
    """
    # builds the changes files
    try :
        src = SourceRepository(commandline=True)
        logs = src.log(path = source)
    except Exception as e :
        if exception_if_empty :
            fLOG("error, unable to retrieve log from " + source)
            raise HelpGenException("unable to retrieve log from " + source) from e
        else :
            logs = [ ("none", 0, datetime.datetime.now(), "-") ]
            fLOG("error,",e)

    if len(logs) == 0 :
        fLOG("error, unable to retrieve log from " + source)
        if exception_if_empty:
            raise HelpGenException("retrieved logs are empty from " + source)
    else :
        fLOG("info, retrieved ", len(logs), " commits")

    rows = [ ]
    rows.append("""\n.. _l-changes:\n\n\nChanges\n=======\n\nList of recent changes:\n""")

    values = []
    for row in logs :
        code, nbch, date, comment = row[:4]
        last = row[-1]
        if last.startswith("http") :
            nbch = "`%s <%s>`_"% (str(nbch), last)

        ds = "%04d-%02d-%02d" % (date.year, date.month, date.day)
        if filter_commit(comment):
            if isinstance(nbch,int) :
                values.append ( ["%04d" % nbch, "%s" % ds, comment.strip("*") ] )
            else :
                values.append ( ["%s" % nbch, "%s" % ds, comment.strip("*") ] )

    if len(values) == 0 and exception_if_empty:
        raise HelpGenException("Logs were not empty but there was no comment starting with '*' from " + source + "\n" + "\n".join( [ str(_) for _ in logs ] ))

    if len(values) > 0 :
        from pandas import DataFrame
        tbl = DataFrame ( columns=["change number", "date", "comment"], data=values)
        rows.append("\n\n" + df_to_rst(tbl, align=["1x","1x","3x"]) + "\n\n")

    final = "\n".join(rows)
    if chan != None :
        with open(chan, "w", encoding="utf8") as f :
            f.write(final)
    return final

def process_notebooks(  notebooks,
                        outfold,
                        build,
                        latex_path = None,
                        pandoc_path = None,
                        formats = ["ipynb", "html", "python", "rst", "pdf"]
                        ):
    """
    Converts notebooks into html, rst, latex, pdf, python, docx using
    `nbconvert <http://ipython.org/ipython-doc/rel-1.0.0/interactive/nbconvert.html>`_.

    @param      notebooks   list of notebooks
    @param      outfold     folder which will contains the outputs
    @param      build       temporary folder which contains all produced files
    @param      pandoc_path path to pandoc
    @param      formats     list of formats to convert into (pdf format means latex then compilation)
    @param      latex_path  path to the latex compiler
    @return                 created files

    This function relies on `pandoc <http://johnmacfarlane.net/pandoc/index.html>`_.
    It also needs modules `pywin32 <http://sourceforge.net/projects/pywin32/>`_,
    `pygments <http://pygments.org/>`_.

    `pywin32 <http://sourceforge.net/projects/pywin32/>`_ might have some issues
    to find its DLL, look @see fn import_pywin32.

    The latex compilation uses `MiKTeX <http://miktex.org/>`_.
    The conversion into Word document directly uses pandoc.
    It still has an issue with table.

    @warning Some latex templates (for nbconvert) uses ``[commandchars=\\\\\\{\\}]{\\|}`` which allows commands ``\\\\`` and it does not compile.
                The one used here is ``report``.

    If *pandoc_path* is None, uses @see fn find_pandoc_path to guess it.
    If *latex_path* is None, uses @see fn find_latex_path to guess it.

    .. versionchanged:: 0.9
        For HTML conversion, read the following blog about mathjax: `nbconvert: Math is not displayed in the html output <https://github.com/ipython/ipython/issues/6440>`_.
        Add defaults values for *pandoc_path*, *latex_path*.

    """
    if pandoc_path is None:
        pandoc_path = find_pandoc_path()

    if latex_path is None:
        latex_path = find_latex_path()

    #graphviz_dot    = theconf.__dict__.get("graphviz_dot", find_graphviz_dot())

    if isinstance(notebooks,str):
        notebooks = [ notebooks ]

    if "PANDOCPY" in os.environ and sys.platform.startswith("win"):
        exe = os.environ["PANDOCPY"]
        exe = exe.rstrip("\\/")
        if exe.endswith("\\Scripts"):
            exe = exe[:len(exe)-len("Scripts")-1]
        if not os.path.exists(exe):
            raise FileNotFoundError(exe)
        fLOG("** using PANDOCPY", exe)
    else :
        if sys.platform.startswith("win"):
            from .utils_pywin32 import import_pywin32
            import_pywin32()
        exe = os.path.split(sys.executable)[0]

    extensions = {  "ipynb":    ".ipynb",
                    "latex":    ".tex",
                    "pdf":      ".pdf",
                    "html":     ".html",
                    "rst":      ".rst",
                    "python":   ".py",
                    "docx":     ".docx",
                    "word":     ".docx",
                }

    if sys.platform.startswith("win"):
        user = os.environ["USERPROFILE"]
        path = pandoc_path.replace("%USERPROFILE%", user)
        p = os.environ["PATH"]
        if path not in p :
            p += ";%WINPYDIR%\DLLs;" + path
            os.environ["WINPYDIR"]=exe
            os.environ["PATH"] = p

        ipy = os.path.join(exe, "Scripts", "ipython3.exe")
    else :
        ipy = os.path.join(exe, "ipython")

    cmd = '{0} nbconvert --to {1} "{2}"{5} --output="{3}/{4}"'
    files = [ ]

    for notebook in notebooks:
        nbout = os.path.split(notebook)[-1]
        if " " in nbout: raise HelpGenException("spaces are not allowed in notebooks file names: {0}".format(notebook))
        nbout = os.path.splitext(nbout)[0]
        for format in formats :

            options = ""
            if format == "pdf":
                title = os.path.splitext(os.path.split(notebook)[-1])[0].replace("_", " ")
                format = "latex"
                options = ' --post PDF --SphinxTransformer.author="" --SphinxTransformer.overridetitle="{0}"'.format(title)
                compilation = True
                pandoco = None
            elif format in ["word", "docx"] :
                format = "html"
                pandoco = "docx"
                compilation = False
            else :
                compilation = False
                pandoco = None

            # output
            outputfile = os.path.join(build, nbout + extensions[format])
            fLOG("--- produce ", outputfile)

            # we chech it was not done before
            if os.path.exists(outputfile) :
                dto = os.stat(outputfile).st_mtime
                dtnb = os.stat(notebook).st_mtime
                if dtnb < dto :
                    fLOG("-- skipping notebook", format, notebook, "(", outputfile, ")")
                    files.append ( outputfile )
                    if pandoco is None :
                        continue
                    else:
                        out2 = os.path.splitext(outputfile)[0] + "." + pandoco
                        if os.path.exists(out2):
                            continue

            templ = "full" if format != "latex" else "article"
            fLOG("### convert into ", format, " NB: ", notebook, " ### ", os.path.exists(outputfile), ":", outputfile)

            if format == "html":
                fmttpl = " --template {0}".format(templ)
            else :
                fmttpl = ""

            c = cmd.format(ipy, format, notebook, build, nbout, fmttpl)

            c += options
            fLOG(c)

            #
            if format not in ["ipynb"]:
                # for latex file
                if format == "latex":
                    cwd = os.getcwd()
                    os.chdir(build)

                if not sys.platform.startswith("win"): c = c.replace('"','')
                out,err = run_cmd(c,wait=True, do_not_log = False, log_error=False, shell = sys.platform.startswith("win"))

                if format == "latex":
                    os.chdir(cwd)

                if "raise ImportError" in err:
                    raise ImportError(err)
                if len(err)>0 :
                    if format == "latex":
                        # there might be some errors because the latex script needs to be post-processed
                        # sometimes (wrong characters such as " or formulas not captured as formulas)
                        pass
                    else:
                        err = err.lower()
                        if "error" in err or "critical" in err or "bad config" in err:
                            raise HelpGenException(err)

                # we should compile a second time
                # compilation = True  # already done above

            format = extensions[format].strip(".")

            # we add the file to the list of generated files
            files.append ( outputfile )

            if "--post PDF" in c :
                files.append ( os.path.join( build, nbout + ".pdf") )

            fLOG("******",format, compilation, outputfile)

            if compilation:
                # compilation latex
                if os.path.exists(latex_path):
                    if sys.platform.startswith("win"):
                        lat = os.path.join(latex_path, "pdflatex.exe")
                    else:
                        lat= "pdflatex"

                    tex = files[-1].replace(".pdf", ".tex")
                    post_process_latex_output_any(tex)
                    c = '"{0}" "{1}" -output-directory="{2}"'.format(lat, tex, os.path.split(tex)[0]) #  -interaction=batchmode
                    fLOG("   ** LATEX compilation (b)", c)
                    if not sys.platform.startswith("win"): c = c.replace('"','')
                    out,err = run_cmd(c,wait=True, do_not_log = False, log_error=False, shell = sys.platform.startswith("win"))
                    if len(err) > 0 :
                        raise HelpGenException(err)
                    f = os.path.join( build, nbout + ".pdf")
                    if not os.path.exists(f):
                        raise HelpGenException("missing file: {0}\nERR:\n{1}".format(f,err))
                    files.append(f)
                else:
                    fLOG("unable to find latex in", latex_path)

            elif pandoco is not None :
                # compilation pandoc
                fLOG("   ** pandoc compilation (b)", pandoco)
                outfilep = os.path.splitext(outputfile)[0] + "." + pandoco

                if sys.platform.startswith("win"):
                    c = r'"{0}\pandoc.exe" -f html -t {1} "{2}" -o "{3}"'.format(pandoc_path, pandoco, outputfile, outfilep)
                else:
                    c = r'pandoc -f html -t {1} "{2}" -o "{3}"'.format(pandoc_path, pandoco, outputfile, outfilep)

                if not sys.platform.startswith("win"): c = c.replace('"','')
                out,err = run_cmd(c,wait=True, do_not_log = False, log_error=False, shell = sys.platform.startswith("win"))
                if len(err) > 0 :
                    raise HelpGenException("issue with cmd: %s\nERR:\n%s" % (c, err))

            if format == "html":
                # we add a link to the notebook
                if not os.path.exists(outputfile):
                    raise FileNotFoundError(outputfile + "\nCONTENT in " + os.path.dirname (outputfile) + ":\n" + "\n".join( os.listdir ( os.path.dirname (outputfile) )) + "\nERR:\n" + err + "\nOUT:\n" + out + "\nCMD:\n" + c)
                files += add_link_to_notebook(outputfile, notebook, "pdf" in formats, False, "python" in formats)

            elif format == "ipynb":
                # we just copy the notebook
                files += add_link_to_notebook(outputfile, notebook, "ipynb" in formats, False, "python" in formats)

            elif format == "rst":
                # we add a link to the notebook
                files += add_link_to_notebook(outputfile, notebook, "pdf" in formats, "html" in formats, "python" in formats)

            elif format in ("tex", "latex", "pdf"):
                files += add_link_to_notebook(outputfile, notebook, False, False, False)

            elif format == "py":
                pass

            elif format in ["docx","word"]:
                pass

            else :
                raise HelpGenException("unexpected format " + format)

    copy = [ ]
    for f in files:
        dest = os.path.join(outfold, os.path.split(f)[-1])
        if not f.endswith(".tex"):

            if sys.version_info >= (3,4):
                try:
                    shutil.copy(f, outfold)
                    fLOG("copy ",f, " to ", outfold, "[",dest,"]")
                except shutil.SameFileError:
                    fLOG("w,file ", dest, "already exists")
                    pass
            else :
                try:
                    shutil.copy(f, outfold)
                    fLOG("copy ",f, " to ", outfold, "[",dest,"]")
                except shutil.Error as e :
                    if "are the same file" in str(e) :
                        fLOG("w,file ", dest, "already exists")
                    else :
                        raise e

            if not os.path.exists(dest):
                raise FileNotFoundError(dest)
        copy.append ( dest )

    # image
    for image in os.listdir(build):
        if image.endswith(".png") or image.endswith(".html") or image.endswith(".pdf"):
            image = os.path.join(build,image)
            dest = os.path.join(outfold, os.path.split(image)[-1])

            if sys.version_info >= (3,4):
                try:
                    shutil.copy(image, outfold)
                    fLOG("copy ",image, " to ", outfold, "[",dest,"]")
                except shutil.SameFileError:
                    fLOG("w,file ", dest, "already exists")
                    pass
            else :
                try:
                    shutil.copy(image, outfold)
                    fLOG("copy ",image, " to ", outfold, "[",dest,"]")
                except shutil.Error as e:
                    if "are the same file" in str(e) :
                        fLOG("w,file ", dest, "already exists")
                    else :
                        raise e

            if not os.path.exists(dest):
                raise FileNotFoundError(dest)
            copy.append ( dest )

    return copy

def add_link_to_notebook(file, nb, pdf, html, python):
    """
    add a link to the notebook in HTML format and does a little bit of cleaning
    for various format

    @param      file        notebook.html
    @param      nb          notebook (.ipynb)
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    @param      html        if True, add a link to the HTML conversion
    @param      python      if True, add a link to the Python conversion
    @return                 list of generated files

    The function does some cleaning too in the files.
    """
    ext = os.path.splitext(file)[-1]
    fLOG("    add_link_to_notebook", ext, " file ", file)

    fold,name = os.path.split(file)
    res = [ os.path.join(fold, os.path.split(nb)[-1]) ]
    newr,reason = has_been_updated(nb, res[-1])
    if newr:
        shutil.copy(nb, fold)

    if ext == ".ipynb":
        return res
    elif ext == ".html" :
        post_process_html_output(file, pdf, python)
        return res
    elif ext == ".tex" :
        post_process_latex_output(file, True)
        return res
    elif ext == ".rst"  :
        post_process_rst_output(file, html, pdf, python)
        return res
    else :
        raise HelpGenException("unable to add a link to this extension: " + ext)

def add_notebook_page(nbs, fileout):
    """
    creates a rst page with links to all notebooks

    @param      nbs             list of notebooks to consider
    @param      fileout         file to create
    @return                     created file name
    """
    rst = [ _ for _ in nbs if _.endswith(".rst") ]

    rows = ["", ".. _l-notebooks:","","","Notebooks","=========",""]

    exp = re.compile("[.][.] _([-a-zA-Z0-9_]+):")
    rst = sorted(rst)

    rows.append("")
    rows.append(".. toctree::")
    rows.append("")
    for file in rst:
        rows.append("    notebooks/{0}".format(os.path.splitext(os.path.split(file)[-1])[0]))

    rows.append("")
    with open(fileout, "w", encoding="utf8") as f :
        f.write("\n".join(rows))
    return fileout

def post_process_latex_output(root, doall):
    """
    post process the latex file produced by sphinx

    @param      root        root path or latex file to process
    @param      doall       do all transformations
    """
    if os.path.isfile(root):
        file = root
        with open(file, "r", encoding="utf8") as f : content = f.read()
        content = post_process_latex(content, doall)
        with open(file, "w", encoding="utf8") as f : f.write(content)
    else :
        build = os.path.join(root, "_doc", "sphinxdoc","build","latex")
        for tex in os.listdir(build):
            if tex.endswith(".tex"):
                file = os.path.join(build,tex)
                fLOG("modify file", file)
                with open(file, "r", encoding="utf8") as f : content = f.read()
                content = post_process_latex(content, doall)
                with open(file, "w", encoding="utf8") as f : f.write(content)

def post_process_latex_output_any(file):
    """
    post process the latex file produced by sphinx

    @param      file        latex filename
    """
    fLOG("   ** post_process_latex_output_any ", file)
    with open(file, "r", encoding="utf8") as f : content = f.read()
    content = post_process_latex(content, True, info = file)
    with open(file, "w", encoding="utf8") as f : f.write(content)

def post_process_rst_output(file, html, pdf, python):
    """
    process a RST file generated from the conversion of a notebook

    @param      file        filename
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    @param      html        if True, add a link to the HTML conversion
    @param      python      if True, add a link to the Python conversion
    """
    fLOG("    post_process_rst_output",file)

    fold,name = os.path.split(file)
    noext = os.path.splitext(name)[0]
    with open(file, "r", encoding="utf8") as f :
        lines = f.readlines()

    # remove empty lines in inserted code, also add line number
    def startss(line):
        for b in ["::",".. parsed-literal::", ".. code:: python",
                  ".. code-block:: python"]:
            if line.startswith(b): return b
        return None

    codeb = [".. code:: python", ".. code-block:: python"]
    inbloc = False
    for pos,line in enumerate(lines):
        if not inbloc :
            b = startss(line)
            if b is None:
                pass
            else :
                if b in codeb:
                    if "notebook" not in file :  # we remove line number for the notebooks
                        lines[pos] = "{0}\n    :linenos:\n\n".format(codeb[-1])
                    else:
                        lines[pos] = "{0}\n\n".format(codeb[-1])
                inbloc = True
                memopos = pos
        else:
            if len(line.strip(" \r\n")) == 0 and pos < len(lines)-1 and \
                lines[pos+1].startswith(" ") and len(lines[pos+1].strip(" \r\n")) > 0 :
                lines[pos] = ""

            elif not line.startswith(" ") and line != "\n" :
                inbloc = False

                if lines[memopos].startswith("::"):
                    code = "".join((_[4:] if _.startswith("    ") else _) for _ in lines[memopos+1:pos])
                    if len(code) == 0 :
                        fLOG ("EMPTY-SECTION in ", file)
                    else :
                        try:
                            cmp = compile(code, "", "exec")
                            if cmp is not None:
                                lines[memopos] = "{0}\n    :linenos:\n".format(".. code-block:: python")
                        except Exception as e :
                            pass

                memopos = None

    # code and images
    imgreg = re.compile("[.][.] image:: (.*)")
    for pos in range(0,len(lines)):
        #lines[pos] = lines[pos].replace(".. code:: python","::")
        if lines[pos].strip().startswith(".. image::"):
            # we assume every image should be placed in the same folder as the notebook itself
            img = imgreg.findall(lines[pos])
            if len(img) == 0 : raise HelpGenException("unable to extract image name in " + lines[pos])
            nameimg = img[0]
            short = nameimg.replace("%5C","/")
            short = os.path.split(short)[-1]
            lines[pos] = lines[pos].replace(nameimg, short)

    # title
    pos = 0
    for pos,line in enumerate(lines):
        line = line.strip("\n\r")
        if len(line) > 0 and line == "=" * len(line):
            lines[pos] = lines[pos].replace("=","*")
            pos2 = pos-1
            l = len(lines[pos])
            while len(lines[pos2])!=l: pos2-=1
            sep = "" if lines[pos2].endswith("\n") else "\n"
            lines[pos2] = "{0}{2}{1}".format(lines[pos],lines[pos2], sep)
            for p in range(pos2+1,pos):
                if lines[p] == "\n": lines[p] = ""
            break

    pos += 1
    if pos >= len(lines):
        raise HelpGenException("unable to find a title")

    # label
    labelname = name.replace(" ","").replace("_","").replace(":","").replace(".","").replace(",","")
    label = "\n.. _{0}:\n\n".format (labelname)
    lines.insert(0,label)

    # links
    links = [ '**Links:** :download:`notebook <{0}.ipynb>`'.format(noext) ]
    if html:
        links.append(':download:`html <{0}.html>`'.format(noext))
    if pdf:
        links.append(':download:`PDF <{0}.pdf>`'.format(noext))
    if python:
        links.append(':download:`python <{0}.py>`'.format(noext))
    lines[pos] = "{0}\n\n{1}\n\n".format(lines[pos],", ".join(links))

    # we remove the
    # <div
    # style="position:absolute;
    # ....
    # </div>
    reg = re.compile("([.]{2} raw[:]{2} html[\\n ]+<div[\\n ]+style=.?position:absolute;(.|\\n)*?[.]{2} raw[:]{2} html[\\n ]+</div>)")
    merged = "".join(lines)
    r = reg.findall(merged)
    if len(r) > 0 :
        fLOG("    *** remove div absolute in ",file)
        for spa in r :
            rep = spa[0]
            nbl = len(rep.split("\n"))
            merged = merged.replace(rep, "\n" * nbl)
        lines = [ (_ +"\n") for _ in merged.split("\n")]

    # bullets
    for pos,line in enumerate(lines):
        if pos == 0 : continue
        if len(line) > 0 and (line.startswith("- ") or line.startswith("* ")) \
            and pos < len(lines) :
            next = lines[pos+1]
            prev = lines[pos-1]
            if (next.startswith("- ") or next.startswith("* ")) \
               and not (prev.startswith("- ") or prev.startswith("* ")) \
               and not prev.startswith("  "):
                lines[pos-1] += "\n"
            elif line.startswith("-  ") and next.startswith("   ") \
                 and not prev.startswith("   ") and not prev.startswith("-  "):
                lines[pos-1] += "\n"
            elif line.startswith("- "):
                pass

    # remove last ::
    i = len(lines)
    for i in range(len(lines)-1,0,-1) :
        s = lines[i-1].strip(" \n\r")
        if len(s) != 0 and s != "::"  : break

    if i < len(lines):
        del lines[i:]

    with open(file, "w", encoding="utf8") as f :
        f.write("".join(lines))

def post_process_html_output(file, pdf, python):
    """
    process a HTML file generated from the conversion of a notebook

    @param      file        filename
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    @param      python      if True, add a link to the Python conversion

    .. versionchanged:: 0.9
        For HTML conversion, read the following blog about mathjax: `nbconvert: Math is not displayed in the html output <https://github.com/ipython/ipython/issues/6440>`_.

    """
    fold,name = os.path.split(file)
    noext = os.path.splitext(name)[0]
    if not os.path.exists(file): raise FileNotFoundError(file)
    with open(file, "r", encoding="utf8") as f :
        text = f.read()

    link = '''
            <div style="position:fixed;text-align:center;align:right;width:15%;bottom:50px;right:20px;background:#DDDDDD;">
            <p>
            {0}
            </p>
            </div>
            '''

    links = [ '<b>links</b><br /><a href="{0}.ipynb">notebook</a>'.format(noext) ]
    if pdf:
        links.append( '<a href="{0}.pdf">PDF</a>'.format(noext))
    if python:
        links.append( '<a href="{0}.py">python</a>'.format(noext))
    link = link.format( "\n<br />".join(links) )

    text = text.replace("</body>", link + "\n</body>")
    text = text.replace("<title>[]</title>", "<title>%s</title>" % name)
    if "<h1>" not in text and "<h1 id" not in text :
        text = text.replace("<body>", "<body><h1>%s</h1>" % name)

    # mathjax
    text = text.replace("https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS_HTML",
                        "https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML")

    with open(file, "w", encoding="utf8") as f :
        f.write(text)

def post_process_latex(st, doall, info = None):
    """
    modifies a latex file after its generation by sphinx

    @param      st      string
    @param      doall   do all transformations
    @param      info    for more understandable error messages
    @return             string

    ..versionchanged:: 0.9
        add parameter *info*, add tableofcontent in the document

    @todo Check latex is properly converted in HTML files
    """
    fLOG("   ** enter post_process_latex", doall, "%post_process_latex" in st)

    # we count the number of times we have \$ (which is unexpected unless the currency is used.
    dollar = st.split("\\$")
    if len(dollar) > 0 and (info is None or os.path.splitext(info)[-1] != ".html") :
        # probably an issue, for the time being, we are strict, no dollar as a currency in latex
        # we do not check HTML files, for the time being, the formulas appears in pseudo latex
        exp = re.compile(r"(.{3}[\\]\$)")
        found = 0
        for m in exp.finditer(st):
            found += 1
            t = m.groups()
            p1,p2 = m.start(), m.end()
            sub = st[p1:p2].strip(" \r\n")
            sub2 = st[max(p1-10,0):min(len(st),p2+10)]
            # very quick and dirty
            if sub not in [ ".*)\\$", "r`\\$}", "ar`\\$", "tt{\\$" ] :
                raise HelpGenException("unexpected \\$ in a latex file:\n{0}\nat position: {1},{2}\nsubstring: {3}\naround: {4}".format(info, p1,p2, sub, sub2))
        if found == 0 :
            raise NotImplementedError("unexpected issue with \\$ in file: {0}".format(info))

    st = st.replace("<br />","\\\\")
    st = st.replace("»",'"')

    if not doall :
        st = st.replace("\\maketitle","\\maketitle\n\n\\newchapter{Introduction}")

    st = st.replace("%5C","/").replace("%3A",":").replace("\\includegraphics{notebooks\\","\\includegraphics{")
    st = st.replace(r"\begin{document}",r"\setlength{\parindent}{0cm}%s\begin {document}" % "\n")
    st = st.replace(r"DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\{\}}",
                    r"DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\{\},fontsize=\small}")

    # hyperref
    if doall and "%post_process_latex" not in st :
        st = "%post_process_latex\n" + st
        reg = re.compile("hyperref[[]([a-zA-Z0-9]+)[]][{](.*?)[}]")
        allhyp = reg.findall(st)
        sections = [ ]
        for id,section in allhyp:
            sec = r"\subsection{%s} \label{%s}" % (section, id)
            sections.append ( (id,section, sec) )
    elif not doall:
        sections = [ ]
        # first section
        lines = st.split("\n")
        for i,line in enumerate(lines):
            if "\\section" in line :
                lines[i] = "\\newchapter{Documentation}\n" + lines[i]
                break
        st = "\n".join(lines)
    else:
        sections = []

    if len(sections) > 0 :
        lines = st.split("\n")
        for i,line in enumerate(lines):
            for _,section,sec in sections :
                if line.strip("\r\n ") == section :
                    fLOG("   **", section, " --> ", sec)
                    lines[i] = sec
        st = "\n".join(lines)

    st = st.replace("\\chapter", "\\section")
    st = st.replace("\\newchapter", "\\chapter")
    if r"\usepackage{multirow}" in st :
        st = st.replace(r"\usepackage{multirow}", r"\usepackage{multirow}\usepackage{amssymb}\usepackage{latexsym}\usepackage{amsfonts}\usepackage{ulem}")
    elif r"\usepackage{hyperref}" in st :
        st = st.replace(r"\usepackage{hyperref}", r"\usepackage{hyperref}\usepackage{amssymb}\usepackage{latexsym}\usepackage{amsfonts}\usepackage{ulem}")
    else :
        raise HelpGenException("unable to add new instructions usepackage in file {0}".format(info))

    # add tableofcontents
    lines = st.split("\n")
    for i,line in enumerate(lines):
        if "\\section" in line and "{" in line and "}" in line:
            # shoud be cleaner with regular expressions
            line = line + "\n\n\\tableofcontents\n\n\\noindent\\rule{4cm}{0.4pt}\n\n"
            lines[i] = line
    st = "\n".join(lines)

    return st

def compile_latex_output_final(root, latex_path, doall, afile = None):
    """
    compiles the latex documents

    @param      root        root
    @param      latex_path  path to the compiler
    @param      doall       do more transformation of the latex file before compiling it
    @param      afile       process a specific file
    """
    if sys.platform.startswith("win"):
        lat = os.path.join(latex_path, "pdflatex.exe")
    else:
        lat = "pdflatex"

    build = os.path.join(root, "_doc", "sphinxdoc","build","latex")
    for tex in os.listdir(build):
        if tex.endswith(".tex") and (afile is None or afile in tex):
            file = os.path.join(build, tex)
            if doall :
                c = '"{0}" "{1}" -output-directory="{2}"'.format(lat, file, build) #  -interaction=batchmode
            else :
                c = '"{0}" "{1}" -interaction=batchmode -output-directory="{2}"'.format(lat, file, build)
            fLOG("   ** LATEX compilation (c)", c)
            post_process_latex_output(file, doall)
            out,err = run_cmd(c,wait=True, do_not_log = False, log_error=False)
            if len(err) > 0 :
                raise HelpGenException(err)
            # second compilation
            fLOG("   ** LATEX compilation (d)", c)
            out,err = run_cmd(c,wait=True, do_not_log = False, log_error=False)
            if len(err) > 0 :
                raise HelpGenException(err)