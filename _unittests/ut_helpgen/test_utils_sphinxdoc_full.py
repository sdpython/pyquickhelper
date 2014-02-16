"""
@brief      test log(time=12s)
@author     Xavier Dupre
"""
import os, sys, unittest, shutil


try :
    import src
except ImportError :
    path =  os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append(path)
    import src
    
from src.pyquickhelper.loghelper.flog           import fLOG, removedirs
import src.pyquickhelper.helpgen.utils_sphinx_doc as utils_sphinx_doc
from src.pyquickhelper.sync.synchelper          import synchronize_folder


class TestSphinxDocFull (unittest.TestCase):
    
    def test_full_documentation (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        path    = os.path.split(__file__)[0]
        temp    = os.path.join(path, "temp_doc")
        if os.path.exists (temp) : removedirs(temp)
        assert not os.path.exists(temp)
        os.mkdir(temp)
            
        file    = os.path.join(path, "..", "..", "..", "pyquickhelper")
        fLOG(os.path.normpath(os.path.abspath(file)))
        assert os.path.exists(file)
        
        sysp = os.path.join(file, "_doc", "sphinxdoc","source")
        assert os.path.exists(sysp)
        sys.path.insert (0,sysp)
        del sys.path [0]
        
        synchronize_folder (sysp, temp, 
                            filter = lambda c: "__pycache__" not in c and "pyquickhelper" not in c)
        shutil.copy(os.path.join(file, "README.rst"), temp)

        # copy the files 
        project_var_name = "pyquickhelper"
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
        
        files = [   
                    #os.path.join(temp, "index_ext-tohelp.rst"),
                    os.path.join(temp, "index_function.rst"),
                    os.path.join(temp, "glossary.rst"),
                    os.path.join(temp, "index_class.rst"),
                    os.path.join(temp, "index_module.rst"),
                    os.path.join(temp, "index_property.rst"),
                    os.path.join(temp, "index_method.rst"), 
                    os.path.join(temp, "all_example.rst"), 
                    os.path.join(temp, "all_FAQ.rst"), 
                    ]
        for f in files :
            if not os.path.exists(f) :
                raise FileNotFoundError(f + "\nabspath: " + os.path.abspath(f))
                    
        with open(files[0],"r",encoding="utf8") as f : f.read()
        
        for f in ["fix_incomplete_references"] :
            func = [ _ for _ in issues if _[0] == f and "utils_sphinx_doc.py" not in _[1]]
            if len(func) > 0 :
                fLOG(func)
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
