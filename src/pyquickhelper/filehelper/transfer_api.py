"""
@file
@brief API to move files
"""
import json
import hashlib
from io import StringIO
from ..loghelper.flog import noLOG
from ..loghelper.convert_helper import str2datetime, datetime2str


class TransferAPI_FileInfo:
    """
    Keeps tracks of transferred files.
    """

    def __init__(self, name, pieces, last_update):
        """
        Information about a transferred file.

        @param      name            name of the file
        @param      pieces          list of pieces contributing to the file
        @param      last_update     last_update
        """
        self.name = name
        self.pieces = pieces
        self.last_update = last_update

    def __str__(self):
        """
        usual
        """
        mes = "[%s,#%d,%s]" % (self.name, len(self.pieces), self.last_update)
        return mes

    def add_piece(self, piece):
        """
        Adds a piece.

        @param      piece       add piece
        """
        self.pieces.append(piece)

    @staticmethod
    def read_json(s):
        """
        Retrieves information from a :epkg:`json` string.
        """
        st = StringIO(s)
        js = json.load(st)
        js[2] = str2datetime(js[2])
        return TransferAPI_FileInfo(*js)

    def to_json(self):
        """
        Serializes this class info JSON.
        """
        li = [self.name, self.pieces, datetime2str(self.last_update)]
        return json.dumps(li)


class TransferAPI:
    """
    Defines an API to transfer files over a remote location.
    """

    def __init__(self, fLOG=noLOG):
        """
        @param      fLOG        logging function
        """
        self.fLOG = fLOG if fLOG else noLOG

    def transfer(self, path, data):
        """
        It assumes a data holds in memory,
        tansfer data to path.

        @param      data        bytes
        @param      path        path to remove location
        @return                 boolean
        """
        raise NotImplementedError()

    def retrieve(self, path, exc=True):
        """
        Retrieves data from path.

        @param      path        remove location
        @param      exc         keep exception
        @return                 data
        """
        raise NotImplementedError()

    def retrieve_mapping(self, decrypt):
        """
        Returns the mapping.

        @param      decrypt     decrypt function
        @return                 list of key,value pair
        """
        m = self.retrieve("__mapping__", exc=False)
        if m is None:
            return {}
        else:
            return TransferAPI.bytes2mapping(m)

    def transfer_mapping(self, mapping, encrypt, filename=None):
        """
        Transfers the mapping.

        @param      mapping     mapping
        @param      encrypt     encryption function
        @param      filename    local filename
        @return                 boolean
        """
        b = TransferAPI.mapping2bytes(mapping)
        if filename is not None:
            with open(filename, "wb") as f:
                f.write(b)
        return self.transfer("__mapping__", b)

    @staticmethod
    def mapping2bytes(mapping):
        """
        Serializes a mapping.

        @param  mapping     dictionary  { str, @see cl TransferAPI_FileInfo }
        @return             bytes
        """
        rows = []
        for k, v in sorted(mapping.items()):
            r = "{0}\t{1}".format(k, v.to_json())
            rows.append(r)
        return "\n".join(rows).encode()

    @staticmethod
    def bytes2mapping(byt):
        """
        Deserializes a mapping.

        @param      byt     bytes
        @return             dictionary  { str, @see cl TransferAPI_FileInfo }
        """
        lines = byt.decode().split("\n")
        res = {}
        for line in lines:
            spl = line.split("\t")
            res[spl[0]] = TransferAPI_FileInfo.read_json("\n".join(spl[1:]))
        return res

    @staticmethod
    def checksum_md5(data):
        """
        Computes MD5 for a file.

        @param      data            some data
        @return                     string
        """
        zero = hashlib.md5()
        zero.update(data)
        return zero.hexdigest()

    def get_remote_path(self, data, name, piece=0):
        """
        Produces a remote path.

        @param      data        binary data to transfer (to be hashed)
        @param      name        local name
        @param      piece       pieces
        @return                 remote path

        *~ hash of everything*
        """
        m1 = TransferAPI.checksum_md5(name.encode() + str(piece).encode())
        m2 = TransferAPI.checksum_md5(data)
        return m1 + "_" + m2


class MockTransferAPI(TransferAPI):
    """
    Class used for unit test purposes, simple key, value storage.
    """

    def __init__(self, fLOG=noLOG):
        """
        @param      fLOG        logging function
        """
        TransferAPI.__init__(self, fLOG)
        self._storage = {}

    def transfer(self, path, data):
        """
        It assumes a data holds in memory,
        tansfer data to path.

        @param      data        bytes
        @param      path        path to remove location
        @return                 boolean
        """
        self._storage[path] = data
        return True

    def retrieve(self, path, exc=True):
        """
        Retrieves data from path.

        @param      path        remove location
        @param      exc         keep exception
        @return                 data
        """
        if exc:
            return self._storage[path]
        else:
            try:
                return self._storage[path]
            except KeyError:
                return None
