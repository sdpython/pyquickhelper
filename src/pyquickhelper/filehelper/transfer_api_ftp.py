"""
@file
@brief API to move files using FTP
"""
import ftplib
from io import BytesIO
from ..loghelper import noLOG
from .transfer_api import TransferAPI
from .ftp_transfer import TransferFTP
from .ftp_mock import MockTransferFTP


class TransferAPIFtp(TransferAPI):
    """
    Defines an API to transfer files over a remote location
    through :epkg:`FTP`.
    """

    def __init__(self, site, login, password, root="backup",
                 ftps='FTP', fLOG=noLOG):
        """
        @param      site        website
        @param      login       login
        @param      password    password
        @param      root        root on the website
        @param      ftps        protocol, see @see cl TransferFTP
        @param      fLOG        logging function
        """
        TransferAPI.__init__(self, fLOG=fLOG)
        self._ftp = (TransferFTP(site, login, password, fLOG=fLOG, ftps=ftps)
                     if site else MockTransferFTP(ftps=ftps, fLOG=fLOG))
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
        It assumes a data holds in memory,
        tansfer data to path.

        @param      data        bytes
        @param      path        path to remove location
        @return                 boolean
        """
        spl = path.rsplit("/")
        to = self._root + "/" + "/".join(spl[:-1])
        to = to.rstrip("/")
        byt = BytesIO(data)
        r = self._ftp.transfer(byt, to, spl[-1])
        return r

    def retrieve(self, path, exc=True):
        """
        retrieve data from path

        @param      path        remove location
        @param      exc         keep exception
        @return                 data
        """
        spl = path.rsplit("/")
        src = self._root + "/" + "/".join(spl[:-1])
        src = src.rstrip("/")
        if exc:
            r = self._ftp.retrieve(src, spl[-1], None)
        else:
            try:
                r = self._ftp.retrieve(src, spl[-1], None)
            except ftplib.error_perm:
                r = None
        return r
