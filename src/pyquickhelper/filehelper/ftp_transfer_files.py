"""
@file
@brief Class to transfer files to a website using FTP, we only transfer updated files

.. versionadded:: 1.0
"""
import os
from .files_status      import FilesStatus
from ..loghelper.flog   import noLOG

class FolderTransferFTPException(Exception):
    """
    custom exxception for @see cl FolderTransferFTP
    """
    pass

class FolderTransferFTP:
    """
    This class aims at transfering a folder to a FTP website,
    it checks that a file was updated before transfering,
    @see cl TransferFTP .

    @example(Transfer updated files to a website)

    The following code shows how to transfer the content of a folder to
    website through FTP protocol.

    @code
    ftn  = FileTreeNode("c:/somefolder")
    ftp  = TransferFTP("ftp.website.fr", "login", "password", fLOG=print)
    fftp = FolderTransferFTP (ftn, ftp, "status_file.txt",
            root_website = "/www/htdocs/app/pyquickhelper/helpsphinx")

    fftp.start_transfering()

    ftp.close()
    @endcode
    @endexample

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
                            root_website = rootw % module,
                            fLOG=print)

        fftp.start_transfering()

        # setup, wheels

        ftn  = FileTreeNode(os.path.join(root,".."), filter = lambda root, path, f, dir: not dir)
        fftp = FolderTransferFTP (ftn, ftp, sfile,
                            root_website = (rootw % module).replace("helpsphinx",""),
                            fLOG=print)

        fftp.start_transfering()


    ftp.close()
    @endcode

    .. versionadded:: 1.0
    """

    def __init__(self,
                    file_tree_node,
                    ftp_transfer,
                    file_status,
                    root_local = None,
                    root_website = None,
                    fLOG = noLOG):
        """
        constructor

        @param      file_tree_node      @see cl FileTreeNode
        @param      ftp_transfer        @see cl TransferFTP
        @param      file_status         file keeping the status file
        @param      root_local          local root
        @param      root_website        remote root on the website
        @param      fLOG                logging function
        """
        self._ftn = file_tree_node
        self._ftp = ftp_transfer
        self._status = file_status
        self._root_local = root_local if root_local is not None else file_tree_node.root
        self._root_website = root_website if root_website is not None else ""
        self.fLOG = fLOG

        self._ft = FilesStatus(file_status)

    def __str__(self):
        """
        usual
        """
        mes  = [ "FolderTransferFTP" ]
        mes += [ "    local root: {0}".format(self._root_local) ]
        mes += [ "    remote root: {0}".format(self._root_website) ]
        return "\n".join(mes)

    def iter_eligible_files(self):
        """
        iterates on eligible file for transfering (if they have been modified)

        @return         iterator on file name
        """
        for f in self._ftn:
            if f.isfile() :
                n,r = self._ft.has_been_modified_and_reason(f.fullname)
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

    def start_transfering(self):
        """
        starts transfering files to the remote website

        @return         list of transfered @see cl FileInfo
        @exception      the class raises an exception (@see cl FolderTransferFTPException)
                        if more than 5 issues happened
        """
        issues = [ ]
        done = [ ]
        total = list ( self.iter_eligible_files() )
        for i, file in enumerate(total):
            if i % 20 == 0:
                self.fLOG("#### transfering",i,len(total))
            relp = os.path.relpath(file.fullname, self._root_local)
            if ".." in relp:
                raise ValueError("the local root is not accurate:\n{0}\nFILE:\n{1}\nRELPATH:\n{2}".format(self, file.fullname, relp))
            path = self._root_website + "/" + os.path.split(relp)[0]
            path = path.replace("\\","/")
            try :
                r = self._ftp.transfer (file.fullname, path)
            except Exception as e :
                r = False
                issues.append( (file.fullname, e) )

            if r :
                fi = self.update_status(file.fullname)
                done.append(fi)

            if len(issues) >= 5 :
                raise FolderTransferFTPException("too many issues:\n{0}".format( "\n".join( "{0} -- {1}".format(a,b) for a,b in issues ) ) )

        return done