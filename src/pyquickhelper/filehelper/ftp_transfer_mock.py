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
        TransferFTP.__init__(self, site, fLOG=fLOG, login=None, password=None)

    def transfer(self, file, to, debug=False, blocksize=None, callback=None):
        """
        does nothing, returns True
        """
        return True

    def close(self):
        """
        does noting
        """
        pass
