"""
Various checking
"""
import os

def check():
    """
    checks difflibjs is present
    """
    path = os.path.abspath(os.path.dirname(__file__))
    fold = os.path.join(path, "temp_difflibjs")
    r = os.path.exists(fold)
    if not r : return r
    f = os.path.join(fold, "jsdifflib.zip")
    r = os.path.exists(f)
    if not r : return r
    size = os.stat(f).st_size
    return size > 0