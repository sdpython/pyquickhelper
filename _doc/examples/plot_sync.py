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
    copy = os.path.dirname(__file__)
except NameError:
    # __file__ does not exist when run with sphinx-gallery
    copy = "."

paths_to_try = [os.path.join("..", "notebooks"),
                os.path.join("_doc", "notebooks")]

for path in paths_to_try:
    src = os.path.abspath(path)
    if os.path.exists(src):
        break

src = os.path.abspath(src)
synchronize_folder(src, dest, fLOG=print)
