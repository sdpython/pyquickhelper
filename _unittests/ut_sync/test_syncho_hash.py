"""
@brief      test tree node (time=5s)
"""


import sys, os, unittest, re

try :
    import src
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    import src

from src.pyquickhelper.loghelper.flog        import fLOG
from src.pyquickhelper.sync.file_tree_node   import FileTreeNode
from src.pyquickhelper.sync.synchelper       import synchronize_folder, remove_folder

class TestSynchoHash (unittest.TestCase):
    
    def test_synchro_hash (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        fold = os.path.abspath(os.path.split(__file__)[0])
        data = os.path.join(fold, "data")
        seco = os.path.join(fold, "data", "temp_seco2")
        troi = os.path.join(fold, "temp_troi2")
        sec2 = os.path.join(troi, "temp_seco2")
        
        temp = os.path.join(fold, "temp_date")
        if not os.path.exists(temp):os.mkdir(temp)
        
        stay = os.path.join(sec2,"notfile.txt")
        nocp = os.path.join(seco,"file.txt")

        def filter_copy(file):
            return "temp_seco" not in file
        fLOG(filter_copy(stay),stay)
        assert not filter_copy(stay)
        
        if os.path.exists(troi):
            remove_folder(troi)
        
        if not os.path.exists(seco) : os.mkdir(seco)
        if not os.path.exists(troi) : os.mkdir(troi)
        if not os.path.exists(sec2) : os.mkdir(sec2)
        
        with open(nocp, "w") as f : f.write("should not be here")
        with open(stay, "w") as f : f.write("should stay")
        
        file_date = os.path.join(temp, "file_date.txt")
        if os.path.exists(file_date): os.remove(file_date)
        
        a = synchronize_folder(  data,
                        troi,
                        hash_size = 0,
                        repo1 = True,
                        filter_copy = filter_copy,
                        file_date = file_date)
                        
        assert os.path.exists(file_date)
        assert os.path.exists(os.path.join(troi,"sub","filetwo.txt"))
        assert os.path.exists(stay)
        assert not os.path.exists(stay.replace("notfile.txt", "file.txt"))
        
        b = synchronize_folder(  data,
                        troi,
                        hash_size = 0,
                        repo1 = True,
                        filter_copy = filter_copy,
                        file_date = file_date)
        
        assert len(a)==2
        assert a[0][0]==">+"==a[1][0]
        assert len(b) == 0
            

if __name__ == "__main__"  :
    unittest.main ()    
