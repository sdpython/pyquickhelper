"""
@brief      test log(time=1s)
@author     Xavier Dupre
"""


import sys, os, unittest, inspect


try :
    import src
except ImportError :
    path =  os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append(path)
    import src
    
from src.pyquickhelper.loghelper.flog           import fLOG
import src.pyquickhelper.helpgen.utils_sphinx_doc as utils_sphinx_doc

class TestSphinxDoc2 (unittest.TestCase):
        
    def test_apply_modification_template_obj (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        
        path    = os.path.split(__file__)[0]
        file    = os.path.normpath(os.path.join(path, "..", "..", "src", "pyquickhelper", "loghelper", "pqh_exception.py"))
        rootm   = os.path.normpath(os.path.join(path, "..", "..", "src"))
        
        store_obj = { }
        softfile = lambda f : False        
        rst = utils_sphinx_doc.apply_modification_template (rootm,
                    store_obj,
                    utils_sphinx_doc.add_file_rst_template,
                    file,
                    os.path.normpath(os.path.join(path, "..", "..", "src")),
                    softfile,
                    {},
                    additional_sys_path = [])
                    
        assert len(rst)>0
        assert len(store_obj) > 0
        for k,v in store_obj.items () :
            fLOG("test1",k,v)
            
    @staticmethod
    def private_static() :
        """ doc pr"""
        res = 0
        return res
        
    @property
    def prop(self) :
        """ doc prop"""
        return 1
        
    def __gt__(self, o) :
        """doc gt"""
        return True
            
    def test_inspect_object(self) :
        """ test 2"""
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        
        mod = sys.modules[__name__]
        fLOG(type(mod), mod.__file__, mod.__name__)
        objs = utils_sphinx_doc.get_module_objects (mod)
        fLOG("objs=",objs)
        ty = { }
        for _ in objs : 
            ty [_.type] = ty.get(_.type, 0) + 1
        fLOG(ty)
        if ty.get("method",0) > 5 or ty.get("staticmethod",0) == 0 :
            for _ in objs : 
                if _.type == "method" : continue
                if "private" in _.name : 
                    assert "doc pr" in _.doc
                fLOG(_.type, _.name, _.doc.replace ("\n","\\n"))
            for _ in objs : 
                if _.type != "method" : continue
                fLOG(_.type, _.module, _.name, _.doc.replace ("\n","\\n"))

        assert ty.get("property",0) == 1
        if ty.get("staticmethod",0) != 1:
            raise Exception("{0}".format(str(ty)))
        assert ty["method"] > 0
        
if __name__ == "__main__"  :
    unittest.main ()    
