"""
@file
@brief Class to transfer files to a website using FTP, we only transfer updated files

.. versionadded:: 1.0
"""
from __future__ import print_function
import re
import os
import io
import warnings
import sys
import ftplib
from .files_status import FilesStatus
from ..loghelper.flog import noLOG

if sys.version_info[0] == 2:
    from codecs import open


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

        @code
        ftn  = FileTreeNode("c:/somefolder")
        ftp  = TransferFTP("ftp.website.fr", "login", "password", fLOG=print)
        fftp = FolderTransferFTP (ftn, ftp, "status_file.txt",
                root_web = "/www/htdocs/app/pyquickhelper/helpsphinx")

        fftp.start_transfering()

        ftp.close()
        @endcode

    The following example is more complete:

    @code
    import sys, os
    from pyquickhelper import TransferFTP, FileTreeNode, FolderTransferFTP
    from pyquickhelper import open_window_params

    login = "login"
    params = { "password":"" }
    newparams = open_window_params (params, title="password",
                        help_string = "password", key_save="my_password")
    password = newparams["password"]

    ftp = TransferFTP("ftp.website.fr",
                    login,
                    password,
                    fLOG=print)

    location = r"local_location\GitHub\%s\dist\html"
    this = os.path.abspath(os.path.dirname(__file__))
    rootw = "/www/htdocs/app/%s/helpsphinx"

    for module in [
            "pyquickhelper",
            "pyensae",
            ] :
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
    @endcode

    .. versionadded:: 1.0
    """

    def __init__(self, file_tree_node, ftp_transfer, file_status, root_local=None,
                 root_web=None, footer_html=None, content_filter=None,
                 is_binary=content_as_binary, text_transform=None, filter_out=None,
                 exc=False, fLOG=noLOG):
        """
        constructor

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
        @param      fLOG                logging function

        Function *text_transform(self, filename, content)* returns the modified content.

        If *filter_out* is a function, the signature is::

            def filter_out(full_file_name, filename):
                # ...
                return True # if the file is filtered out, False otherwise

        .. versionchanged:: 1.3
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
        if filter_out is not None and not isinstance(filter_out, str  # unicode#
                                                     ):
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
        iterates on eligible file for transfering (if they have been modified)

        @return         iterator on file name
        """
        for f in self._ftn:
            if f.isfile():
                if self._filter_out(f.fullname):
                    continue
                n, r = self._ft.has_been_modified_and_reason(f.fullname)
                if n:
                    yield f

    def update_status(self, file):
        """
        update the status of a file

        @param      file        filename
        @return                 @see cl FileInfo
        """
        r = self._ft.update_copied_file(file)
        self._ft.save_dates()
        return r

    def preprocess_before_transfering(self, path, force_binary=False):
        """
        Applies some preprocessing to the file to transfer.
        It adds the footer for example.
        It returns a stream which should be closed by using method @see me close_stream.

        @param      path            file name
        @param      force_binary    impose a binary transfer
        @return                     binary stream, size

        .. versionchanged:: 1.4
            Returns also size.
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
                        if ext in [".js"]:
                            # just a warning
                            warnings.warn(
                                "FTP transfer, encoding issue with: " + path)
                            return self.preprocess_before_transfering(path, True)
                        else:
                            raise FolderTransferFTPException(
                                'unable to transfer:\n  File "{0}", line 1'.format(path)) from e

                # footer
                if self._footer_html is not None and os.path.splitext(
                        path)[-1].lower() in (".htm", ".html"):
                    spl = content.split("</body>")
                    if len(spl) == 1:
                        raise FolderTransferFTPException(
                            'tag </body> was not found, it must be written in lower case,\n  File "{0}", line 1'.format(path))

                    if len(spl) != 2:
                        spl = ["</body>".join(spl[:-1]), spl[-1]]

                    content = spl[0] + self._footer_html + "</body>" + spl[-1]

                # filter
                try:
                    content = self._content_filter(content, path)
                except Exception as e:
                    raise FolderTransferFTPException(
                        "File {0} cannot be transferred (exception)".format(path)) from e
                if content is None:
                    raise FolderTransferFTPException(
                        "File {0} cannot be transferred due to its content".format(path))

                # transform
                if self._text_transform is not None:
                    content = self._text_transform(self, path, content)

                # to binary
                bcont = content.encode("utf8")
                return io.BytesIO(bcont), len(bcont)

    def close_stream(self, stream):
        """
        close a stream opened by @see me preprocess_before_transfering

        @param      stream      stream to close
        """
        if isinstance(stream, io.BytesIO):
            pass
        else:
            stream.close()

    def start_transfering(self):
        """
        starts transfering files to the remote website

        @return         list of transfered @see cl FileInfo
        @exception      the class raises an exception (@see cl FolderTransferFTPException)
                        if more than 5 issues happened
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
                raise ValueError("the local root is not accurate:\n{0}\nFILE:\n{1}\nRELPATH:\n{2}".format(
                    self, file.fullname, relp))
            path = self._root_web + "/" + os.path.split(relp)[0]
            path = path.replace("\\", "/")

            size = os.stat(file.fullname).st_size
            self.fLOG("[upload % 8d bytes name=%s -- fullname=%s -- to=%s]" % (
                size,
                os.path.split(file.fullname)[-1],
                file.fullname,
                path))

            if self._exc:
                data, size = self.preprocess_before_transfering(file.fullname)
            else:
                try:
                    data, size = self.preprocess_before_transfering(
                        file.fullname)
                except FolderTransferFTPException as ex:
                    warnings.warn(
                        "unable to transfer '{0}' due to {1}".format(file.fullname, ex))
                    continue

            if size > 2**19:
                blocksize = 2**18
                transfered = 0

                def callback_function(*l, private_p=[blocksize, transfered, size], **p):
                    private_p[1] += private_p[0]
                    self.fLOG("  transfered: %1.3f - %d/%d" %
                              (1.0 * private_p[1] / private_p[2], private_p[1], private_p[2]))
                cb = callback_function
            else:
                blocksize = 2**15
                cb = None

            if self._exc:
                r = self._ftp.transfer(
                    data, path, os.path.split(file.fullname)[-1], blocksize=blocksize, callback=cb)
            else:
                try:
                    r = self._ftp.transfer(
                        data, path, os.path.split(file.fullname)[-1], blocksize=blocksize, callback=cb)
                except FileNotFoundError as e:
                    r = False
                    issues.append((file.fullname, "not found", e))
                    self.fLOG("    issue", e)
                except ftplib.error_perm as ee:
                    r = False
                    issues.append((file.fullname, str(ee), ee))
                    self.fLOG("    issue", ee)
                except TimeoutError as eee:
                    r = False
                    issues.append((file.fullname, "TimeoutError", eee))
                    self.fLOG("    issue", eee)
                except EOFError as eeee:
                    r = False
                    issues.append((file.fullname, "EOFError", eeee))
                    self.fLOG("    issue", eeee)
                except ConnectionAbortedError as eeeee:
                    r = False
                    issues.append(
                        (file.fullname, "ConnectionAbortedError", eeeee))
                    self.fLOG("    issue", eeeee)

            self.close_stream(data)

            sum_bytes += size

            if r:
                fi = self.update_status(file.fullname)
                done.append(fi)

            if len(issues) >= 10:
                raise FolderTransferFTPException("too many issues:\n{0}".format(
                    "\n".join("{0} -- {1} --- {2}".format(a, b, type(c)) for a, b, c in issues)))

        return done
