"""
@file
@brief Main functions to produce the documentation for a module

"""
import os,sys, shutil, datetime
from pandas import DataFrame

from ..loghelper.flog           import run_cmd, fLOG
from ..loghelper.pyrepo_helper  import SourceRepository
from ..pandashelper.tblformat   import df_to_rst
from .utils_sphinx_doc          import prepare_file_for_sphinx_help_generation
from .utils_sphinx_doc_helpers  import HelpGenException

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

def get_executables_path() :
    """
    returns the paths to Python, Python Scripts
    
    @return     a list of paths
    """
    res  = [ os.path.split(sys.executable)[0] ]
    res += [ os.path.join(res[-1], "Scripts") ]
    if sys.platform == "win32" :
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
        tbl = DataFrame ( columns=["change number", "date", "comment"], data=values)
        rows.append("\n\n" + df_to_rst(tbl, align=["1x","1x","3x"]) + "\n\n")

    final = "\n".join(rows)
    if chan != None :
        with open(chan, "w") as f :
            f.write(final)
    return final

def generate_help_sphinx (  project_var_name, 
                            clean = True, 
                            root = ".",
                            filter_commit = lambda c : c.strip() != "documentation") :
    """
    runs the help generation
        - copies every file in another folder
        - replaces comments in doxygen format into rst format
        - replaces local import by global import (tweaking sys.path too)
        - calls sphinx to generate the documentation.
        
    @param      project_var_name    project name
    @param      clean               if True, cleans the previous documentation first
    @param      root                see below
    @param      filter_commit       function which accepts a commit to show on the documentation (based on the comment)
    
    The result is stored in path: ``root/_doc/sphinxdoc/source``.
    
    @example(run help generation)
    @code
    # from the main folder which contains folder src
    generate_help_sphinx("pyquickhelper")
    @endcode
    @endexample
    """
    sys.path.append (os.path.abspath(os.path.join("_doc", "sphinxdoc","source")))
    root = os.path.abspath(root)
    
    src = SourceRepository(commandline=True)
    version = src.version(os.path.abspath(root))
    if version != None :
        with open("version.txt", "w") as f : f.write(str(version) + "\n")
    
    # modifies the version number in conf.py
    shutil.copy("README.rst", "_doc/sphinxdoc/source")
    shutil.copy("LICENSE.txt", "_doc/sphinxdoc/source")

    #changes
    chan = os.path.join (root, "_doc", "sphinxdoc", "source", "filechanges.rst")
    generate_changes_repo(chan, root, filter_commit = filter_commit)
    
    # copy the files 
    optional_dirs = [ ]
            
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
                mapped_function = [ (".*[.]tohelp$", None) ] )
                
    fLOG("end of prepare_file_for_sphinx_help_generation")
                
    #  run the documentation generation
    if sys.platform == "win32" :
        temp = os.environ ["PATH"]
        pyts = get_executables_path()
        script = ";".join(pyts)
        fLOG ("adding " + script)
        temp = script + ";" + temp
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
                except Exception as e :
                    raise HelpGenException ("issue with file ", thn) from e
                
    fLOG("running sphinx... from", docpath)
    if not os.path.exists (docpath) :
        raise FileNotFoundError(docpath)
        
    if sys.platform == "win32" :
        make = os.path.join(docpath, "make.bat")
        if not os.path.exists(make) : raise FileNotFoundError(make)
            
    os.chdir (docpath)
    if clean :
        cmd = "make.bat clean".split ()
        run_cmd (cmd, wait = True)
        
    cmd = "make.bat html".split ()
    
    # This instruction should work but it does not. Sphinx seems to be stuck.
    #run_cmd (cmd, wait = True, secure="make_help.log", stop_waiting_if = lambda v : "build succeeded" in v)
    # The following one works but opens a extra windows.
    os.system("make html")
    
    # end
    os.chdir (pa)
    