"""
@file
@brief  Mock class @see cl TransferFTP

.. versionadded:: 1.0
    moved from pyensae to pyquickhelper
"""

from ..loghelper.flog import noLOG
from .ftp_transfer import TransferFTP
from ftplib import FTP


class MockTransferFTP (TransferFTP):

    """
    mock @see cl TransferFTP
    """

    def __init__(self, site, login, password, fLOG=noLOG):
        """
        same signature as @see cl TransferFTP
        """
        self._logins = []
        self._ftp = FTP(None)
        self.LOG = fLOG
        self._atts = dict(site=site, login=login, password=password)

    def transfer(self, file, to, name, debug=False, blocksize=None, callback=None):
        """
        does nothing, returns True
        """
        return True

    def close(self):
        """
        does noting
        """
        pass
