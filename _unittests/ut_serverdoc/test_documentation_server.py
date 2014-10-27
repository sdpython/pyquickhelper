"""
@brief      test log(time=4s)

"""


import sys, os, unittest
from http.server import HTTPServer

try :
    import src
    import pyquickhelper
    import pyensae
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..", "..", "pyquickhelper", "src")))
    if path not in sys.path : sys.path.append (path)
    import src
    import pyquickhelper

from pyquickhelper                      import fLOG, run_doc_server, get_url_content


class TestDocumentationServer(unittest.TestCase):
    
    def test_server_start_run (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        data = os.path.join(path,"data")
        
        
        server = ('localhost', 8094)
        thread = run_doc_server(server, {"pyquickhelper":data}, True)
        
        url = "http://localhost:8094/pyquickhelper/"
        cont = get_url_content(url)
        assert len(cont)> 0
        assert "GitHub/pyquickhelper</a>" in cont
        
        thread.shutdown()    
        assert not thread.is_alive()
        
        
if __name__ == "__main__"  :
    unittest.main ()    

    