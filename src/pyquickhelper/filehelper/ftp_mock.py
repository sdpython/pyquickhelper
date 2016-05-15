"""
@file
@brief Mock classes

.. versionadded:: 1.4
"""

from ftplib import FTP
from ..loghelper.flog import noLOG
from .ftp_transfer import TransferFTP


class MockTransferFTP(TransferFTP):
    """
    mock @see cl TransferFTP
    """

    def __init__(self, fLOG=noLOG):
        """
        constructor

        @param      fLOG        logging function
        """
        TransferFTP.__init__(self, None, "login", "password")
        self._store = {}

    def run_command(self, command, *args):
        """
        Mock method :meth:`run_command <pyquickhelper.filehelper.ftp_transfer.TransferFTP.run_commnad>`
        """
        if command == FTP.mlsd and args == ('.',):
            return [('setup.py', {'name': 'setup.py'})]
        elif command == FTP.cwd and args == ('.',):
            return None
        elif command == FTP.cwd and args == ('..',):
            return None
        elif command == FTP.storbinary and args[0] == 'STOR test_transfer_ftp.py':
            self._store[args[0]] = args
            return None
        elif command == FTP.retrbinary and args[0] == 'RETR test_transfer_ftp.py':
            b = self._store[args[0].replace("RETR", "STOR")][1]
            return b'ee'
        elif command == FTP.cwd and args == ('backup',):
            self._store[args[0]] = args
            return None
        elif command == FTP.storbinary and args[0] == 'STOR setup.py':
            self._store[args[0]] = args
            return None
        elif command == FTP.retrbinary and args[0] == 'RETR setup.py':
            b = self._store[args[0].replace("RETR", "STOR")][1]
            s = b.getbuffer()
            args[1](s)
            return len(s)
        else:
            raise Exception("command='{0}'\nargs={1}".format(command, args))
