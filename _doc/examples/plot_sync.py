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
try:
    copy = os.path.join(os.path.dirname(__file__), "..", "_doc", "notebooks")
except NameError:
    # __file__ does not exist when run with sphinx-gallery
    copy = os.path.join("..", "_doc", "notebooks")
synchronize_folder(copy, dest, fLOG=print)
