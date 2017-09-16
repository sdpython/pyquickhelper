"""
===================
Syncing two folders
===================

This example is about syncing two folders
or creating a backup.

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
synchronize_folder(os.path.join(os.path.dirname(__file__), "..", "_doc", "_notebooks"),
                   dest, fLOG=print)
