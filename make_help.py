"""
generates the documentation using Sphinx
"""

import os,sys, subprocess, glob, shutil, re, datetime
from pandas import DataFrame

try:
    import pyquickhelper
except ImportError:
    sys.path.append ( os.path.normpath (os.path.abspath("src")))
    import pyquickhelper
    
from pyquickhelper.loghelper.flog           import run_cmd, fLOG
from pyquickhelper.loghelper.pysvn_helper   import get_repo_version
from pyquickhelper.pandashelper.tblformat   import df_to_rst
from pyquickhelper.helpgen.utils_sphinx_doc import prepare_file_for_sphinx_help_generation

project_var_name  = "pyquickhelper"
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
    res  = [ os.path.split(sys.executable)[0] ]
    res += [ os.path.join(res[-1], "Scripts") ]
    if sys.platform == "win32" :
        ver = "c:\\Python%d%d" % (sys.version_info.major, sys.version_info.minor)
        res += [ver ]
        res += [ os.path.join(res[-1], "Scripts") ]
    return res
    
def generate_changes(chan) :
    """
    @param  chan        filename
    """
    # builds the changes files
    try :
        logs = get_repo_log(path = os.path.abspath(os.path.join(os.path.split(__file__)[0], "src")))
    except :
        logs = [ ("none", 0, datetime.datetime.now(), "-") ]
        
    logs.sort(reverse=True)
    with open(chan, "w") as f :
        f.write("""\n.. _l-changes:\n\n\nChanges\n=======\n\nList of recent changes:\n""")
        first = True
        values = []
        for code, nbch, date, comment in logs :
            ds = "%04d-%02d-%02d" % (date.year, date.month, date.day)
            if first : 
                fLOG ("last changes: % 4d - %s - %s" % (nbch, ds, comment))
            if comment.startswith('*') :
                if first : 
                    fLOG ("last changes % 4d - %s - %s" % (nbch, ds, comment.strip("*")))
                    first = False
                values.append ( ["%04d" % nbch, "%s" % ds, comment.strip("*") ] )
        
        if len(values) > 0 :
            tbl = DataFrame ( columns=["change number", "date", "comment"], data=values)
            f.write ("\n\n" + df_to_rst(tbl) + "\n\n")

def generate_help_sphinx () :
    """
    
    """
    sys.path.append (os.path.abspath(os.path.join("_doc", "sphinxdoc","source")))
    import conf
    
    version = get_repo_version()
    if version != None :
        with open("version.txt", "w") as f : f.write(str(version) + "\n")
    
    # modifies the version number in conf.py
    svver = conf.release
    shutil.copy("README.rst", "_doc/sphinxdoc/source")
    shutil.copy("LICENSE.txt", "_doc/sphinxdoc/source")

    #changes
    chan = os.path.join (os.path.split (__file__) [0], "_doc", "sphinxdoc", "source", "filechanges.rst")
    generate_changes(chan)
    
    # copy the files 
    optional_dirs = [ ]
            
    prepare_file_for_sphinx_help_generation ( 
                {},
                ".", 
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

    thispath = os.path.normpath(os.path.abspath(os.path.split(__file__)[0]))
    docpath  = os.path.normpath(os.path.join(thispath, "_doc","sphinxdoc"))

    fLOG("checking encoding utf8...")
    for root, dirs, files in os.walk(docpath):
        for name in files:
            thn = os.path.join(root, name)
            if name.endswith(".rst") :
                try :
                    with open(thn, "r", encoding="utf8") as f : c=f.read()
                except Exception as e :
                    fLOG ("issue with file ", thn)
                    raise e
                
    fLOG("running sphinx... from", docpath)
    if not os.path.exists (docpath) :
        raise FileNotFoundError(docpath)
        
    if sys.platform == "win32" :
        make = os.path.join(docpath, "make.bat")
        if not os.path.exists(make) : raise FileNotFoundError(make)
            
    os.chdir (docpath)
    cmd = "make.bat clean".split ()
    run_cmd (cmd, wait = True)
        
    cmd = "make.bat html".split ()
    #run_cmd (cmd, wait = True, secure="make_help.log", stop_waiting_if = lambda v : "build succeeded" in v)
    #subprocess.call("make html", shell=True)
    os.system("make html")
    os.chdir (pa)

if __name__ == "__main__" :
    fLOG (OutputPrint = True)
    generate_help_sphinx()
    
