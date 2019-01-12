"""
@file
@brief Keeps an encrypted of personal data
"""
import re
import os
import datetime
import zlib
from io import BytesIO as StreamIO
from .files_status import FilesStatus
from ..loghelper.flog import noLOG
from .transfer_api import TransferAPI_FileInfo
from .encryption import encrypt_stream, decrypt_stream


class EncryptedBackupError(Exception):
    """
    raised by @see cl EncryptedBackup
    """
    pass


class EncryptedBackup:

    """
    This class aims at keeping an encrypted and compressed backup of files.
    Every file is compressed and then encrypted before being uploaded to the
    remote location. Its name still contains the container but the
    file name is a hash. A

    .. exref::
        :title: Encrypted and compressed backup

        Here is an example which stores everything on hard drive.
        A second run only modifies files updated between the two processes.
        A modified file does not remove the previous version,
        it creates a new file.
        Example::

            from pyquickhelper.loghelper import fLOG
            from pyquickhelper.filehelper import FileTreeNode, EncryptedBackup
            from pyensae.remote import TransferAPIFile

            key_crypt = "crypt"

            local = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
            this = os.path.normpath(os.path.dirname(__file__))
            file_status=os.path.join(this, "backup_status.txt")
            file_map=os.path.join(this, "backup_mapping.txt")

            backup = True
            if backup:
                # code to backup
                root = os.path.normpath(os.path.join(os.path.dirname(__file__)))
                api = TransferAPIFile("f:\\\\mycryptedbackup")
                ft = FileTreeNode(root, repository=True)
                enc = EncryptedBackup(
                    key=key_crypt,
                    file_tree_node=ft,
                    transfer_api=api,
                    root_local=local,
                    file_status=file_status,
                    file_map=file_map,
                    fLOG=print)

                enc.start_transfering()

            restore = not backup
            if restore:
                # code to restore
                root = os.path.normpath(os.path.join(os.path.dirname(__file__)))
                api = TransferAPIFile("f:\\\\mycryptedbackup")
                enc = EncryptedBackup(
                    key=key_crypt,
                    file_tree_node=None,
                    transfer_api=api,
                    root_local=local,
                    file_status=file_status,
                    file_map=file_map,
                    fLOG=print)

                dest=os.path.join(this, "_temp")
                enc.retrieve_all(dest)
    """

    def __init__(self, key, file_tree_node, transfer_api,
                 file_status, file_map, root_local=None,
                 root_remote=None, filter_out=None,
                 threshold_size=2 ** 24, algo="AES",
                 compression="lzma", fLOG=noLOG):
        """
        constructor

        @param      key                 key for encryption
        @param      file_tree_node      @see cl FileTreeNode
        @param      transfer_api        @see cl TransferFTP
        @param      file_status         file keeping the status for each file (date, hash of the content for the last upload)
        @param      file_map            keep track of local filename and remote location
        @param      root_local          local root
        @param      root_remote         remote root
        @param      filter_out          regular expression to exclude some files, it can also be a function.
        @param      threshold_size      above that size, big files are split
        @param      algo                encrypting algorithm
        @param      compression         kind of compression ``'lzma'`` or ``'zip'``
        @param      fLOG                logging function
        """
        self._key = key
        self.fLOG = fLOG
        self._ftn = file_tree_node
        self._api = transfer_api
        self._map = file_map
        self._algo = algo
        self._mapping = None
        self._compress = compression
        self._threshold_size = threshold_size
        self._root_local = root_local if root_local is not None else (
            file_tree_node.root if file_tree_node else None)
        self._root_remote = root_remote if root_remote is not None else ""
        if filter_out is not None and not isinstance(filter_out, str):
            self._filter_out = filter_out
        else:
            self._filter_out_reg = None if filter_out is None else re.compile(
                filter_out)
            self._filter_out = (lambda f: False) if filter_out is None else (
                lambda f: self._filter_out_reg.search(f) is not None)

        self._ft = FilesStatus(file_status) if file_status else None

    def iter_eligible_files(self):
        """
        iterates on eligible file for transfering (if they have been modified)

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
        update the status of a file

        @param      file        filename
        @return                 @see cl FileInfo
        """
        r = self._ft.update_copied_file(file)
        self._ft.save_dates()
        return r

    def update_mapping(self, key, maps):
        """
        update the status of a file

        @param      key         key
        @param      maps        update the mapping
        """
        self.Mapping[key] = maps
        self.transfer_mapping()

    def load_mapping(self):
        """
        retrieves existing mapping

        @return         dictionary
        """
        self._mapping = self._api.retrieve_mapping(lambda data: decrypt_stream(
            self._key, data, chunksize=None, algo=self._algo))
        return self._mapping

    def transfer_mapping(self):
        """
        transfer the mapping
        """
        self._api.transfer_mapping(self.Mapping,
                                   lambda data: encrypt_stream(
                                       self._key, data, chunksize=None, algo=self._algo),
                                   self._map)

    @property
    def Mapping(self):
        """
        returns the mapping
        """
        return self._mapping

    def enumerate_read_encrypt(self, fullname):
        """
        enumerate pieces of files as bytes

        @param      fullname        fullname
        @return                     iterator on chunk of data
        """
        with open(fullname, "rb") as f:
            try:
                data = f.read(self._threshold_size)
                cont = True
            except PermissionError as e:
                yield e
                cont = False
            if cont:
                while data and cont:
                    data = self.compress(data)
                    enc = encrypt_stream(
                        self._key, data, chunksize=None, algo=self._algo)
                    yield enc
                    try:
                        data = f.read(self._threshold_size)
                    except PermissionError as e:
                        yield e
                        cont = False

    def compress(self, data):
        """
        compress data

        @param      data        binary data
        @return                 binary data
        """
        if self._compress == "zip":
            return zlib.compress(data)
        elif self._compress == "lzma":
            # delay import
            try:
                import lzma
            except ImportError:
                import pylzma as lzma
            return lzma.compress(data)
        elif self._compress is None:
            return data
        else:
            raise ValueError(
                "unexpected compression algorithm {0}".format(self._compress))

    def decompress(self, data):
        """
        decompress data

        @param      data        binary data
        @return                 binary data
        """
        if self._compress == "zip":
            return zlib.decompress(data)
        elif self._compress == "lzma":
            # delay import
            try:
                import lzma
            except ImportError:
                import pylzma as lzma
            return lzma.decompress(data)
        elif self._compress is None:
            return data
        else:
            raise ValueError(
                "unexpected compression algorithm {0}".format(self._compress))

    def start_transfering(self):
        """
        starts transfering files to the remote website

        :return: list of transferred @see cl FileInfo
        :raises FolderTransferFTPException: The class raises an
            exception (@see cl FolderTransferFTPException)
            if more than 5 issues happened.
        """
        self.load_mapping()

        issues = []
        total = list(self.iter_eligible_files())
        sum_bytes = 0
        done = []
        for i, file in enumerate(total):
            if i % 20 == 0:
                self.fLOG("#### transfering %d/%d (so far %d bytes)" %
                          (i, len(total), sum_bytes))
            relp = os.path.relpath(file.fullname, self._root_local)
            if ".." in relp:
                raise ValueError("the local root is not accurate:\n{0}\nFILE:\n{1}\nRELPATH:\n{2}".format(
                    self, file.fullname, relp))

            path = self._root_remote + "/" + os.path.split(relp)[0]
            path = path.replace("\\", "/")

            size = os.stat(file.fullname).st_size
            self.fLOG("[upload % 8d bytes name=%s -- fullname=%s -- to=%s]" % (
                size,
                os.path.split(file.fullname)[-1],
                file.fullname,
                path))

            maps = TransferAPI_FileInfo(relp, [], datetime.datetime.now())
            r = True
            for ii, data in enumerate(self.enumerate_read_encrypt(file.fullname)):
                if data is None or isinstance(data, Exception):
                    # it means something went wrong
                    r = False
                    err = data
                    break
                to = self._api.get_remote_path(data, relp, ii)
                to = path + "/" + to
                to = to.lstrip("/")
                r &= self.transfer(to, data)
                maps.add_piece(to)
                sum_bytes += len(data)
                if not r:
                    break

            if r:
                self.update_status(file.fullname)
                self.update_mapping(relp, maps)
                done.append(relp)
            else:
                self.fLOG("   issue", err)
                issues.append((relp, err))

            if len(issues) >= 5:
                raise EncryptedBackupError("too many issues:\n{0}".format(
                    "\n".join("{0} -- {1}".format(a, b) for a, b in issues)))

        self.transfer_mapping()
        return done, issues

    def transfer(self, to, data):
        """
        transfer data

        @param      to      remote path
        @param      data    binary data
        @return             boolean
        """
        return self._api.transfer(to, data)

    def retrieve(self, path, filename=None, root=None):
        """
        retrieve a backuped file

        @param      path        path of the file to retrieve
        @param      filename    if not None, store the file into this file
        @param      root        if not None, store the file into root + path
        @return                 filename or data
        """
        if self.Mapping is None:
            raise EncryptedBackupError(
                "load the mapping with method load_mapping")
        if path not in self.Mapping:
            raise EncryptedBackupError(
                "the mapping is not up to date or file {0} cannot be found".format(path))
        info = self.Mapping[path]
        if len(info.pieces) == 0:
            # the file is empty
            if root is not None:
                filename = os.path.join(root, path)
            if filename is not None:
                dirname = os.path.dirname(filename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                with open(filename, "w") as f:
                    pass
            return filename
        else:
            if root is not None:
                filename = os.path.join(root, path)
            if filename is not None:
                dirname = os.path.dirname(filename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                with open(filename, "wb") as f:
                    for p in info.pieces:
                        data = self._api.retrieve(p)
                        data = decrypt_stream(
                            self._key, data, chunksize=None, algo=self._algo)
                        data = self.decompress(data)
                        f.write(data)
                return filename
            else:
                if len(info.pieces) == 1:
                    return self._api.retrieve(info.pieces[0])
                else:
                    byt = StreamIO()
                    for p in info.pieces:
                        data = self._api.retrieve(p)
                        data = decrypt_stream(
                            self._key, data, chunksize=None, algo=self._algo)
                        data = self.decompress(data)
                        byt.write(data)
                    return byt.getvalue()

    def retrieve_all(self, dest, regex=None):
        """
        retrieve all backuped files

        @param      dest        destination
        @param      regex       retrieve a subset matching the regular expression
        @return                 list of restored files
        """
        rema = re.compile(regex) if regex else None

        def match(na):
            "local function"
            if rema:
                return rema.search(na)
            else:
                return True

        self.fLOG("load mapping")
        self.load_mapping()
        self.fLOG("number of files", len(self.Mapping))
        done = []
        for k in sorted(self.Mapping.keys()):
            name = self.retrieve(k, root=dest)
            if match(name):
                size = os.stat(name).st_size
                self.fLOG("[download % 8d bytes name=%s -- fullname=%s -- to=%s]" % (
                    size,
                    os.path.split(name)[-1],
                    dest,
                    os.path.dirname(name)))
                done.append(name)
        return done
