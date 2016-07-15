"""
@file
@brief provides some functionalities to upload file to a website

.. versionadded:: 1.0
    moved from pyensae to pyquickhelper
"""
from ftplib import FTP, error_perm
import os
import io
import sys

from ..loghelper.flog import noLOG


class TransferFTP(FTP):

    """
    this class uploads files to a website,
    if the remote does not exists, it creates it first

    .. exref::
        :title: Transfer files to webste through FTP

        Simple sketch to transfer a list of ``files`` to
        a website through FTP

        @code
        ftp = TransferFTP('ftp.<website>', alias, password, fLOG=print)

        issues = [ ]
        done = [ ]
        notdone = [ ]
        for file in files :

            try :
                r = ftp.transfer (file, path)
                if r : done.append( (file, path) )
                else : notdone.append ( (file, path) )
            except Exception as e :
                issues.append( (file, e) )

        try :
            ftp.close()
        except Exception as e :
            print ("unable to close FTP connection using ftp.close")

        @endcode

    .. versionadded:: 1.0
        Moved prom pyensee to pyquickhelper.
    """

    errorNoDirectory = "Can't change directory"
    blockSize = 2 ** 20

    def __init__(self, site, login, password, fLOG=noLOG):
        """
        constructor

        @param      site        website
        @param      login       login
        @param      password    password
        @param      fLOG        logging function
        """
        if site is not None:
            FTP.__init__(self, site, login, password)
        else:
            # mocking
            pass
        self.LOG = fLOG
        self._atts = dict(site=site)

    @property
    def Site(self):
        """
        return the website
        """
        return self._atts["site"]

    def _private_login(self):
        """
        logs in
        """
        self.LOG("connecting to ", self.Site)
        FTP.login(self)

    def run_command(self, command, *args):
        """
        run a FTP command

        @param      command     command
        @param      args        list of argument
        @return                 output of the command or True for success, False for failure
        """
        try:
            t = command(self, *args)
            if command == FTP.pwd or command == FTP.dir or \
                    command == FTP.mlsd or command == FTP.nlst:
                return t
            elif command != FTP.cwd:
                pass
            return True
        except Exception as e:
            if TransferFTP.errorNoDirectory in str(e):
                raise e
            self.LOG(e)
            self.LOG("    ** run exc ", str(command), str(args))
            self._private_login()
            t = command(self, *args)
            self.LOG("    ** run ", str(command), str(args))
            return t

    def print_list(self):
        """
        return the list of files in the current directory
        the function sends eveything to the logging function

        @return         output of the command or True for success, False for failure
        """
        return self.run_command(FTP.retrlines, 'LIST')

    def mkd(self, path):
        """
        creates a directory

        @param        path      path to the directory
        @return                 True or False
        """
        self.LOG("[mkd]", path)
        return self.run_command(FTP.mkd, path)

    def cwd(self, path, create=False):
        """
        go to a directory, if it does not exist, create it
        (if create is True)

        @param      path        path to the directory
        @param      create      True to create it
        @return                 True or False
        """
        try:
            self.run_command(FTP.cwd, path)
        except EOFError as e:
            raise EOFError("unable to go to: {0}".format(path)) from e
        except Exception as e:
            if create and TransferFTP.errorNoDirectory in str(e):
                self.mkd(path)
                self.cwd(path, create)
            else:
                raise e

    def pwd(self):
        """
        Return the pathname of the current directory on the server.

        @return         pathname
        """
        return self.run_command(FTP.pwd)

    def dir(self, path='.'):
        """
        list the content of a path

        @param      path        path
        @return                 list of path

        see :meth:`enumerate_ls <pyquickhelper.filehelper.ftp_transfer.TransferFTP.enumerate_ls>`

        .. versionchanged:: 1.0
        """
        return list(self.enumerate_ls(path))

    def ls(self, path='.'):
        """
        list the content of a path

        @param      path        path
        @return                 list of path

        see :meth:`enumerate_ls <pyquickhelper.filehelper.ftp_transfer.TransferFTP.enumerate_ls>`

        .. exref::
            :title: List files from FTP site

            @code
            from pyquickhelper.filehelper import TransferFTP
            ftp = TransferFTP("ftp....", "login", "password")
            res = ftp.ls("path")
            for v in res:
                print(v["name"])
            ftp.close()
            @endcode

        .. versionchanged:: 1.0
        """
        return list(self.enumerate_ls(path))

    def enumerate_ls(self, path='.'):
        """
        enumerate the content of a path

        @param      path        path
        @return                 list of dictionaries

        One dictionary::

            {'name': 'www',
             'type': 'dir',
             'unique': 'aaaa',
             'unix.uid': '1111',
             'unix.mode': '111',
             'sizd': '5',
             'unix.gid': '000',
             'modify': '111111'}

        .. versionadded:: 1.0
        """
        if sys.version_info[0] == 2:
            for a in self.run_command(FTP.nlst, path):
                r = dict(name=a)
                yield r
        else:
            for a in self.run_command(FTP.mlsd, path):
                r = dict(name=a[0])
                r.update(a[1])
                yield r

    def transfer(self, file, to, name, debug=False):
        """
        transfers a file

        @param      file        file name or stream (binary, BytesIO)
        @param      to          destination (a folder)
        @param      name        name of the stream on the website
        @param      debug       if True, displays more information
        @return                 status

        .. versionchanged:: 1.0
            file can be a file name or a stream,
            parameter *name* was added
        """
        path = to.split("/")
        path = [_ for _ in path if len(_) > 0]

        for p in path:
            self.cwd(p, True)

        if isinstance(file, str  # unicode#
                      ):
            if not os.path.exists(file):
                raise FileNotFoundError(file)
            with open(file, "rb") as f:
                r = self.run_command(
                    FTP.storbinary, 'STOR ' + name, f, TransferFTP.blockSize)
        elif isinstance(file, io.BytesIO):
            r = self.run_command(FTP.storbinary, 'STOR ' +
                                 name, file, TransferFTP.blockSize)
        elif isinstance(file, bytes):
            st = io.BytesIO(file)
            r = self.run_command(FTP.storbinary, 'STOR ' +
                                 name, st, TransferFTP.blockSize)
        else:
            r = self.run_command(FTP.storbinary, 'STOR ' +
                                 name, file, TransferFTP.blockSize)

        for p in path:
            self.cwd("..")

        return r

    def retrieve(self, fold, name, file, debug=False):
        """
        downloads a file

        @param      file        file name or stream (binary, BytesIO)
        @param      fold        full remote path
        @param      name        name of the stream on the website
        @param      debug       if True, displays more information
        @return                 status

        .. versionadded:: 1.3
        """
        path = fold.split("/")
        path = [_ for _ in path if len(_) > 0]

        for p in path:
            self.cwd(p, True)

        raise_exc = None

        if isinstance(file, str  # unicode#
                      ):
            with open(file, "wb") as f:
                def callback(block):
                    f.write(block)
                try:
                    data = self.run_command(
                        FTP.retrbinary, 'RETR ' + name, callback, TransferFTP.blockSize)
                    f.write(data)
                    r = True
                except error_perm as e:
                    raise_exc = e
                    r = False
        elif isinstance(file, io.BytesIO):
            def callback(block):
                file.write(block)
            try:
                r = self.run_command(
                    FTP.retrbinary, 'RETR ' + name, callback, TransferFTP.blockSize)
            except error_perm as e:
                raise_exc = e
                r = False
        else:
            b = io.BytesIO()

            def callback(block):
                b.write(block)
            try:
                self.run_command(FTP.retrbinary, 'RETR ' + name,
                                 callback, TransferFTP.blockSize)
            except error_perm as e:
                raise_exc = e

            r = b.getvalue()

        for p in path:
            self.cwd("..")

        if raise_exc:
            raise raise_exc

        return r
