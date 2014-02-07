"""
@brief      test log(time=0s)
@author     Xavier Dupre
"""


import sys, os, unittest

try :
    import src
except ImportError :
    path =  os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append(path)
    import src
    
from src.pyquickhelper.loghelper.flog           import fLOG
from src.pyquickhelper.helpgen.utils_sphinx_doc_helpers     import process_var_tag


class TestSphinxDoc2Issue (unittest.TestCase):
    
    @staticmethod
    def get_help():
        """ help to fetch"""
        return 1
    
    def test_issues1(self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        
        obj = TestSphinxDoc2Issue.get_help
        d1 = obj.__doc__

        obj = TestSphinxDoc2Issue.__dict__["get_help"]
        d2 =  obj.__func__.__doc__
        assert d1 == d2
        
    def test_var(self):
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        
        docstring = """
            This class opens a text file as if it were a binary file. It can deal with null characters which are missed by open function.

            @var    filename        file name
            @var    utf8            decode in utf8
            @var    errors          decoding in utf8 can raise some errors, @see cl str to understand the meaning of this parameter
            @var    fLOG            logging function (@see fn fLOG)
            @var    _buffer_size    read a text file _buffer_size bytes each time
            @var    _filter         function filter, None or return True or False whether a line should considered or not
            
            Example:
            @code
            f = TextFile (filename)
            f.open ()
            for line in f :
                print line
            f.close ()
            @endcode
            """    
        values = process_var_tag(docstring)
        assert len(values) == 6
        
        rst = process_var_tag(docstring, True)
        fLOG(rst)
        assert len(rst)  > 0
        
        
        

if __name__ == "__main__"  :
    unittest.main ()    
