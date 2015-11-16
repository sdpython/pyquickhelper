"""
@file
@brief API to move files using FTP

.. versionadded:: 1.3
"""
import os
import sys
from ..loghelper import noLOG
from .transfer_api import TransferAPI


class TransferAPIFile(TransferAPI):
    """
    defines an API to transfer files over another location
    """

    def __init__(self, location, fLOG=noLOG):
        """
        constructor

        @param      location    location
        @param      fLOG        logging function
        """
        TransferAPI.__init__(self, fLOG=fLOG)
        self._location = location

    def transfer(self, path, data):
        """
        we assume a data holds in memory,
        tansfer data to path

        @param      data        bytes
        @param      path        path to remove location
        @return                 boolean
        """
        src = os.path.join(self._location, path)
        fol = os.path.dirname(src)
        if not os.path.exists(fol):
            os.makedirs(fol)
        with open(src, "wb") as f:
            f.write(data)
        return True

    def retrieve(self, path, exc=True):
        """
        retrieve data from path

        @param      path        remove location
        @param      exc         keep exception
        @return                 data
        """
        src = os.path.join(self._location, path)
        if os.path.exists(src):
            with open(src, "rb") as f:
                return f.read()
        elif exc:
            if sys.version_info[0] == 2:
                FileNotFoundError = Exception
            raise FileNotFoundError(path)
        else:
            return None
