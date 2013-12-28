"""
@brief      test log(time=12s)
@author     Xavier Dupre
"""


from __future__ import print_function
import sys, os, unittest, re, io, datetime, shutil


try :
    import src
except ImportError :
    import os, sys
    path =  os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append(path)
    import src
    
from src.pyquickhelper.loghelper.flog           import fLOG, removedirs
from src.pyquickhelper.sync.synchelper          import explore_folder
import src.pyquickhelper.helpgen.utils_sphinx_doc as utils_sphinx_doc
from src.pyquickhelper.loghelper.pysvn_helper   import get_repo_version, get_repo_log
from src.pyquickhelper.sync.synchelper          import synchronize_folder


class TestSphinxDocFull (unittest.TestCase):
    
    def test_full_documentation (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        path    = os.path.split(__file__)[0]
        temp    = os.path.join(path, "temp_doc")
        if os.path.exists (temp) : removedirs(temp)
        assert not os.path.exists(temp)
        os.mkdir(temp)
            
        file    = os.path.join(path, "..", "..", "..", "..", "python", "project_template")
        fLOG(os.path.normpath(os.path.abspath(file)))
        assert os.path.exists(file)
        
        sysp = os.path.join(file, "_doc", "sphinxdoc","source")
        assert os.path.exists(sysp)
        sys.path.insert (0,sysp)
        import conf
        del sys.path [0]
        
        synchronize_folder (sysp, temp, 
                            filter = lambda c: "__pycache__" not in c and "project_template" not in c)
        shutil.copy(os.path.join(file, "README.rst"), temp)

        # copy the files 
        project_var_name = "project_name"
        issues           = [ ]
        store_obj        = { }
                    
        utils_sphinx_doc.prepare_file_for_sphinx_help_generation ( 
                    store_obj,
                    file, 
                    temp, 
                    subfolders      = [ ("src/" + project_var_name, project_var_name), ],
                    silent          = True,
                    rootrep         = ("_doc.sphinxdoc.source.%s." % (project_var_name,), ""),
                    optional_dirs   = [],
                    mapped_function = [ (".*[.]tohelp$", None) ],
                    issues          = issues)
                        
        fLOG("end of prepare_file_for_sphinx_help_generation")
        
        files = [   os.path.join(temp, "index_ext-tohelp.rst"),
                    os.path.join(temp, "index_function.rst"),
                    os.path.join(temp, "glossary.rst"),
                    os.path.join(temp, "index_class.rst"),
                    os.path.join(temp, "index_module.rst"),
                    os.path.join(temp, "index_method.rst"), 
                    os.path.join(temp, "filechanges.rst"),
                    ]
        for f in files :
            if not os.path.exists(f) :
                raise FileNotFoundError(f + "\nabspath: " + os.path.abspath(f))
            
        file = os.path.join(temp, "project_name","subproject2","myexample2.py")
        assert os.path.exists (file)
        with open(file, "r", encoding="utf8") as f : content = f.read()
        assert "del sys.path[0]" in content
        assert "class myclass2 (myclass) :" in content
        assert "from subproject.myexample import myclass" in content
        assert "# replace # from ..subproject.myexample import myclass" in content
        
        file = os.path.join(temp, "project_name","subproject2","myexample2.rst")
        assert os.path.exists (file)
        with open(file, "r", encoding="utf8") as f : content = f.read()
        if "temp_doc.project_name.subproject2.myexample2" not in content :
            raise Exception("unable to find a string in \n" + content)
            
        file = os.path.join(temp, "project_name","subproject","myexampleb.py")
        assert os.path.exists (file)
        with open(file, "r", encoding="utf8") as f : content = f.read()
        assert "# replace # from .myexample import myclass" in content
            
        fileth = os.path.join(temp, "project_name","subproject","myexample_nouse.tohelp")
        assert os.path.exists (fileth)
        filerst = os.path.join(temp, "project_name","subproject","myexample_nouse.rst")
        assert os.path.exists (filerst)
        
        with open(files[0],"r",encoding="utf8") as f : content = f.read()
        assert "nouse" in content
        
        for f in ["fix_incomplete_references"] :
            func = [ _ for _ in issues if _[0] == f ]
            if len(func) > 0 :
                mes = "\n".join ( [_[1] for _ in func ])
                stk = [ ]
                for k,v in store_obj.items () :
                    if isinstance(v,list) :
                        for o in v :
                            stk.append ( "storedl %s=%s " % (k,o.rst_link()) )
                    else :
                        stk.append ( "stored  %s=%s " % (k,v.rst_link()) )
                mes += "\nstored:\n" + "\n".join ( stk)
                raise Exception("issues detected for function " + f + "\n" + mes)
            
            
        
        
if __name__ == "__main__"  :
    unittest.main ()    
