"""
@file
@brief API to move files using FTP

.. versionadded:: 1.3
"""
import ftplib
import io
from ..loghelper import noLOG
from .transfer_api import TransferAPI
from .ftp_transfer import TransferFTP


class TransferAPIFtp(TransferAPI):
    """
    defines an API to transfer files over a remote location
    through FTP
    """

    def __init__(self, site, login, password, root="backup", fLOG=noLOG):
        """
        constructor

        @param      site        website
        @param      login       login
        @param      password    password
        @param      root        root on the website
        @param      fLOG        logging function
        """
        self.fLOG = fLOG if fLOG else noLOG
        self._ftp = TransferFTP(site, login, password, fLOG=fLOG)
        self._root = root

    def connect(self):
        """
        connect
        """
        pass
        # self._ftp.connect()

    def close(self):
        """
        close the connection
        """
        pass
        # self._ftp._close()

    def transfer(self, path, data):
        """
        we assume a data holds in memory,
        tansfer data to path

        @param      data        bytes
        @param      path        path to remove location
        @return                 boolean
        """
        spl = path.split("/")
        to = self._root + "/" + "/".join(spl[:-1])
        to = to.strip("/")
        byt = io.BytesIO(data)
        r = self._ftp.transfer(byt, to, spl[-1])
        return r

    def retrieve(self, path, exc=True):
        """
        retrieve data from path

        @param      path        remove location
        @param      exc         keep exception
        @return                 data
        """
        spl = path.split("/")
        src = self._root + "/" + "/".join(spl[:-1])
        src = src.strip("/")
        if exc:
            r = self._ftp.retrieve(src, spl[-1], None)
        else:
            try:
                r = self._ftp.retrieve(src, spl[-1], None)
            except ftplib.error_perm:
                r = None
        return r
