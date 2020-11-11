"""
@file
@brief Class to transfer files to a website using FTP, it only transfers updated files
"""
from __future__ import print_function
import re
import os
import warnings
import sys
import ftplib
from io import BytesIO
from time import sleep
from random import random
from .files_status import FilesStatus
from ..loghelper.flog import noLOG
from .ftp_transfer import CannotCompleteWithoutNewLoginException


class FolderTransferFTPException(Exception):

    """
    custom exception for @see cl FolderTransferFTP
    """
    pass


_text_extensions = {".ipynb", ".html", ".py", ".cpp", ".h", ".hpp", ".c",
                    ".cs", ".txt", ".csv", ".xml", ".css", ".js", ".r", ".doc",
                    ".ind", ".buildinfo", ".rst", ".aux", ".out", ".log",
                    }


def content_as_binary(filename):
    """
    determines if filename is binary or None before transfering it

    @param      filename        filename
    @return                     boolean
    """
    global _text_extensions
    ext = os.path.splitext(filename)[-1].lower()
    if ext in _text_extensions:
        return False
    else:
        return True


class FolderTransferFTP:

    """
    This class aims at transfering a folder to a FTP website,
    it checks that a file was updated before transfering,
    @see cl TransferFTP .

    .. exref::
        :title: Transfer updated files to a website

        The following code shows how to transfer the content of a folder to
        website through FTP protocol.

        ::

            ftn  = FileTreeNode("c:/somefolder")
            ftp  = TransferFTP("ftp.website.fr", "login", "password", fLOG=print)
            fftp = FolderTransferFTP (ftn, ftp, "status_file.txt",
                    root_web = "/www/htdocs/app/pyquickhelper/helpsphinx")

            fftp.start_transfering()
            ftp.close()

    The following example is more complete:

    ::

        import sys, os
        from pyquickhelper.filehelper import TransferFTP, FileTreeNode, FolderTransferFTP
        import keyring

        user = keyring.get_password("webtransfer", "user")
        pwd = keyring.get_password("webtransfer", "pwd")

        ftp = TransferFTP("ftp.website.fr", user, pwd, fLOG=print)

        location = r"local_location/GitHub/%s/dist/html"
        this = os.path.abspath(os.path.dirname(__file__))
        rootw = "/root/subfolder/%s/helpsphinx"

        for module in ["pyquickhelper", "pyensae"] :
            root = location % module

            # documentation
            sfile = os.path.join(this, "status_%s.txt" % module)
            ftn  = FileTreeNode(root)
            fftp = FolderTransferFTP (ftn, ftp, sfile,
                                root_web = rootw % module,
                                fLOG=print)

            fftp.start_transfering()

            # setup, wheels
            ftn  = FileTreeNode(os.path.join(root,".."), filter = lambda root, path, f, dir: not dir)
            fftp = FolderTransferFTP (ftn, ftp, sfile,
                                root_web = (rootw % module).replace("helpsphinx",""),
                                fLOG=print)

            fftp.start_transfering()

        ftp.close()
    """

    def __init__(self, file_tree_node, ftp_transfer, file_status, root_local=None,
                 root_web=None, footer_html=None, content_filter=None,
                 is_binary=content_as_binary, text_transform=None, filter_out=None,
                 exc=False, force_allow=None, fLOG=noLOG):
        """
        @param      file_tree_node      @see cl FileTreeNode
        @param      ftp_transfer        @see cl TransferFTP
        @param      file_status         file keeping the status for each file (date, hash of the content for the last upload)
        @param      root_local          local root
        @param      root_web            remote root on the website
        @param      footer_html         append  this HTML code to any uploaded page (such a javascript code to count the audience)
                                        at the end of the file (before tag ``</body>``)
        @param      content_filter      function which transform the content if a specific string is found
                                        in the file, if the result is None, it raises an exception
                                        indicating  the file cannot be transfered (applies only on text files)
        @param      is_binary           function which determines if content of a files is binary or not
        @param      text_transform      function to transform the content of a text file before uploading it
        @param      filter_out          regular expression to exclude some files, it can also be a function.
        @param      exc                 raise exception if not able to transfer
        @param      force_allow         the class does not transfer a file containing a set of specific strings
                                        except if they are in the list
        @param      fLOG                logging function

        Function *text_transform(self, filename, content)* returns the modified content.

        If *filter_out* is a function, the signature is::

            def filter_out(full_file_name, filename):
                # ...
                return True # if the file is filtered out, False otherwise

        Function *filter_out* receives another parameter (filename)
        to give more information when raising an exception.
        """
        self._ftn = file_tree_node
        self._ftp = ftp_transfer
        self._status = file_status
        self._root_local = root_local if root_local is not None else file_tree_node.root
        self._root_web = root_web if root_web is not None else ""
        self.fLOG = fLOG
        self._footer_html = footer_html
        self._content_filter = content_filter
        self._is_binary = is_binary
        self._exc = exc
        self._force_allow = force_allow
        if filter_out is not None and not isinstance(filter_out, str):
            self._filter_out = filter_out
        else:
            self._filter_out_reg = None if filter_out is None else re.compile(
                filter_out)
            self._filter_out = (lambda f: False) if filter_out is None else (
                lambda f: self._filter_out_reg.search(f) is not None)

        self._ft = FilesStatus(file_status)
        self._text_transform = text_transform

    def __str__(self):
        """
        usual
        """
        mes = ["FolderTransferFTP"]
        mes += ["    local root: {0}".format(self._root_local)]
        mes += ["    remote root: {0}".format(self._root_web)]
        return "\n".join(mes)

    def iter_eligible_files(self):
        """
        Iterates on eligible file for transfering
        (if they have been modified).

        @return         iterator on file name
        """
        for f in self._ftn:
            if f.isfile():
                if self._filter_out(f.fullname):
                    continue
                n = self._ft.has_been_modified_and_reason(f.fullname)[0]
                if n:
                    yield f

    def update_status(self, file):
        """
        Updates the status of a file.

        @param      file        filename
        @return                 @see cl FileInfo
        """
        r = self._ft.update_copied_file(file)
        self._ft.save_dates()
        return r

    def preprocess_before_transfering(self, path, force_binary=False, force_allow=None):
        """
        Applies some preprocessing to the file to transfer.
        It adds the footer for example.
        It returns a stream which should be closed by
        using method @see me close_stream.

        @param      path            file name
        @param      force_binary    impose a binary transfer
        @param      force_allow     allow these strings even if they seem to be credentials
        @return                     binary stream, size

        Bypass utf-8 encoding checking when the extension is ``.rst.txt``.
        """
        if force_binary or self._is_binary(path):
            size = os.stat(path).st_size
            return open(path, "rb"), size
        else:
            if self._footer_html is None and self._content_filter is None:
                size = os.stat(path).st_size
                return open(path, "rb"), size
            else:
                size = os.stat(path).st_size
                with open(path, "r", encoding="utf8") as f:
                    try:
                        content = f.read()
                    except UnicodeDecodeError as e:
                        ext = os.path.splitext(path)[-1]
                        if ext in {".js"} or path.endswith(".rst.txt"):
                            # just a warning
                            warnings.warn(
                                "FTP transfer, encoding issue with '{0}'".format(path), UserWarning)
                            return self.preprocess_before_transfering(path, True)
                        else:
                            stex = str(e).split("\n")
                            stex = "\n    ".join(stex)
                            raise FolderTransferFTPException(
                                'Unable to transfer:\n  File "{0}", line 1\nEXC:\n{1}'.format(path, stex)) from e

                # footer
                if self._footer_html is not None and os.path.splitext(
                        path)[-1].lower() in (".htm", ".html"):
                    spl = content.split("</body>")
                    if len(spl) > 1:
                        if len(spl) != 2:
                            spl = ["</body>".join(spl[:-1]), spl[-1]]

                        content = spl[0] + self._footer_html + \
                            "</body>" + spl[-1]

                # filter
                try:
                    content = self._content_filter(
                        content, path, force_allow=force_allow)
                except Exception as e:  # pragma: no cover
                    import traceback
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    trace = traceback.format_exception(
                        exc_type, exc_value, exc_traceback)
                    if isinstance(trace, list):
                        trace = "\n".join(trace)
                    raise FolderTransferFTPException(
                        "File '{0}' cannot be transferred (filtering exception)\nfunction:\n{1}\nEXC\n{2}\nStackTrace:\n{3}".format(
                            path, self._content_filter, e, trace)) from e
                if content is None:
                    raise FolderTransferFTPException(
                        "File '{0}' cannot be transferred due to its content.".format(path))

                # transform
                if self._text_transform is not None:
                    content = self._text_transform(self, path, content)

                # to binary
                bcont = content.encode("utf8")
                return BytesIO(bcont), len(bcont)

    def close_stream(self, stream):
        """
        Closes a stream opened by @see me preprocess_before_transfering.

        @param      stream      stream to close
        """
        if isinstance(stream, BytesIO):
            pass
        else:
            stream.close()

    def start_transfering(self, max_errors=20, delay=None):
        """
        Starts transfering files to a remote :epkg:`FTP` website.

        :param max_errors: stops after this number of errors
        :param delay: delay between two files
        :return: list of transferred @see cl FileInfo
        :raises FolderTransferFTPException: the class raises
            an exception (@see cl FolderTransferFTPException)
            more than *max_errors* issues happened

        .. versionchanged:: 1.8
            Parameter *delay* was added.
        """
        issues = []
        done = []
        total = list(self.iter_eligible_files())
        sum_bytes = 0
        for i, file in enumerate(total):
            if i % 20 == 0:
                self.fLOG("#### transfering %d/%d (so far %d bytes)" %
                          (i, len(total), sum_bytes))
            relp = os.path.relpath(file.fullname, self._root_local)
            if ".." in relp:
                raise ValueError(  # pragma: no cover
                    "The local root is not accurate:\n{0}\nFILE:\n{1}"
                    "\nRELPATH:\n{2}".format(self, file.fullname, relp))
            path = self._root_web + "/" + os.path.split(relp)[0]
            path = path.replace("\\", "/")

            size = os.stat(file.fullname).st_size
            self.fLOG("[upload % 8d bytes name=%s -- fullname=%s -- to=%s]" % (
                size, os.path.split(file.fullname)[-1], file.fullname, path))

            if self._exc:
                data, size = self.preprocess_before_transfering(
                    file.fullname, force_allow=self._force_allow)
            else:
                try:
                    data, size = self.preprocess_before_transfering(
                        file.fullname, force_allow=self._force_allow)
                except FolderTransferFTPException as ex:  # pragma: no cover
                    stex = str(ex).split("\n")
                    stex = "\n    ".join(stex)
                    warnings.warn(
                        "Unable to transfer '{0}' due to [{1}].".format(file.fullname, stex), ResourceWarning)
                    issues.append(
                        (file.fullname, "FolderTransferFTPException", ex))
                    continue

            if size > 2**20:
                blocksize = 2**20
                transfered = 0

                def callback_function_(*args, **kwargs):
                    "local function"
                    private_p = kwargs.get('private_p', None)
                    if private_p is None:
                        raise ValueError("private_p cannot be None")
                    private_p[1] += private_p[0]
                    private_p[1] = min(private_p[1], size)
                    self.fLOG("  transferred: %1.3f - %d/%d" %
                              (1.0 * private_p[1] / private_p[2], private_p[1], private_p[2]))

                tp_ = [blocksize, transfered, size]
                cb = lambda *args2, **kwargs2: callback_function_(
                    *args2, private_p=tp_, **kwargs2)
            else:
                blocksize = None
                cb = None

            if self._exc:
                r = self._ftp.transfer(
                    data, path, os.path.split(file.fullname)[-1], blocksize=blocksize, callback=cb)
            else:
                try:
                    r = self._ftp.transfer(
                        data, path, os.path.split(file.fullname)[-1], blocksize=blocksize, callback=cb)
                except FileNotFoundError as e:  # pragma: no cover
                    r = False
                    issues.append((file.fullname, "not found", e))
                    self.fLOG("[FolderTransferFTP] - issue", e)
                except ftplib.error_perm as ee:  # pragma: no cover
                    r = False
                    issues.append((file.fullname, str(ee), ee))
                    self.fLOG("[FolderTransferFTP] - issue", ee)
                except TimeoutError as eee:  # pragma: no cover
                    r = False
                    issues.append((file.fullname, "TimeoutError", eee))
                    self.fLOG("[FolderTransferFTP] - issue", eee)
                except EOFError as eeee:  # pragma: no cover
                    r = False
                    issues.append((file.fullname, "EOFError", eeee))
                    self.fLOG("[FolderTransferFTP] - issue", eeee)
                except ConnectionAbortedError as eeeee:  # pragma: no cover
                    r = False
                    issues.append(
                        (file.fullname, "ConnectionAbortedError", eeeee))
                    self.fLOG("    issue", eeeee)
                except ConnectionResetError as eeeeee:  # pragma: no cover
                    r = False
                    issues.append(
                        (file.fullname, "ConnectionResetError", eeeeee))
                    self.fLOG("[FolderTransferFTP] - issue", eeeeee)
                except CannotCompleteWithoutNewLoginException as e8:  # pragma: no cover
                    r = False
                    issues.append(
                        (file.fullname, "CannotCompleteWithoutNewLoginException", e8))
                    self.fLOG("[FolderTransferFTP] - issue", e8)
                except Exception as e7:  # pragma: no cover
                    try:
                        import paramiko
                    except ImportError:
                        raise e7
                    if isinstance(e7, paramiko.sftp.SFTPError):
                        r = False
                        issues.append(
                            (file.fullname, "ConnectionResetError", e7))
                        self.fLOG("[FolderTransferFTP] - issue", e7)
                    else:
                        raise e7

            self.close_stream(data)

            sum_bytes += size

            if r:
                fi = self.update_status(file.fullname)
                done.append(fi)

            if len(issues) >= max_errors:
                raise FolderTransferFTPException(  # pragma: no cover
                    "Too many issues:\n{0}".format(
                        "\n".join("{0} -- {1} --- {2}".format(
                            a, b, str(c).replace('\n', ' ')) for a, b, c in issues)))

            if delay is not None and delay > 0:
                h = random()
                delta = (h - 0.5) * delay * 0.1
                delay_rnd = delay + delta
                sleep(delay_rnd)

        return done
