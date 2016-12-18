"""
===================
Syncing two folders
===================

"""

###############################
from pyquickhelper.filehelper import synchronize_folder

###############################
dest = "temp_sync"
import os
if not os.path.exists(dest):
    print("creating", dest)
    os.makedirs(dest)
else:
    print("folder already created", dest)

###############################
synchronize_folder(os.path.abspath(os.path.dirname(__file__)),
                   dest, fLOG=print)
