"""
@file
@brief API to move files using FTP
"""
import os
from ..loghelper import noLOG
from .transfer_api import TransferAPI


class TransferAPIFile(TransferAPI):
    """
    Defines an API to transfer files over another location.
    """

    def __init__(self, location, fLOG=noLOG):
        """
        @param      location    location
        @param      fLOG        logging function
        """
        TransferAPI.__init__(self, fLOG=fLOG)
        self._location = location

    def transfer(self, path, data):
        """
        It assumes a data holds in memory,
        tansfer data to path.

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
        Retrieves data from path.

        @param      path        remove location
        @param      exc         keep exception
        @return                 data
        """
        src = os.path.join(self._location, path)
        if os.path.exists(src):
            with open(src, "rb") as f:
                return f.read()
        elif exc:
            raise FileNotFoundError(path)
        else:
            return None
