"""
@file
@brief Fix a bug: see https://bugs.python.org/issue6839.
"""
import sys
import struct
from zipfile import ZipFile, ZipInfo, ZipExtFile, _ZipDecrypter, BadZipFile
from zipfile import _FH_EXTRA_FIELD_LENGTH, _FH_FILENAME_LENGTH, _FH_SIGNATURE
from zipfile import stringFileHeader, structFileHeader, sizeFileHeader, _SharedFile


class WinZipFile(ZipFile):
    """
    Overwrite method :epkg:`*py:zipfile:ZipFile:open`.

    Issue `6839 <https://bugs.python.org/issue6839>`_ happens when
    a zip file is created on Windows. The created zip may contain
    full path with ``\\`` when the file list only contains ``/``.
    This raises exception ``BadZipFile`` with the following message:
    *File name in directory ... and header ... differ* due to a mismatch
    between backslashes. This owerwrite method :epkg:`*py:zipfile:ZipFile:open`
    to fix the line which checks that names are consistent in the file list
    and in the compressed content.
    """

    def open(self, name, mode="r", pwd=None, *, force_zip64=False):
        """
        Returns file-like object for 'name'.

        @param      name    is a string for the file name within the ZIP file, or a ZipInfo
                            object.
        @param      mode    should be 'r' to read a file already in the ZIP file, or 'w' to
                            write to a file newly added to the archive.
        @param      pwd     is the password to decrypt files (only used for reading).

        When writing, if the file size is not known in advance but may exceed
        2 GiB, pass force_zip64 to use the ZIP64 format, which can handle large
        files.  If the size is known in advance, it is best to pass a ZipInfo
        instance for name, with zinfo.file_size set.
        """
        if mode not in {"r", "w"}:
            raise ValueError('open() requires mode "r" or "w"')
        if pwd and not isinstance(pwd, bytes):
            raise TypeError("pwd: expected bytes, got %s" % type(pwd).__name__)
        if pwd and (mode == "w"):
            raise ValueError("pwd is only supported for reading files")
        if not self.fp:
            raise ValueError(
                "Attempt to use ZIP archive that was already closed")

        # Make sure we have an info object
        if isinstance(name, ZipInfo):
            # 'name' is already an info object
            zinfo = name
        elif mode == 'w':
            zinfo = ZipInfo(name)
            zinfo.compress_type = self.compression
        else:
            # Get info object for name
            zinfo = self.getinfo(name)

        if mode == 'w':
            return self._open_to_write(zinfo, force_zip64=force_zip64)

        if hasattr(self, "_writing") and self._writing:
            raise ValueError("Can't read from the ZIP file while there "
                             "is an open writing handle on it. "
                             "Close the writing handle before trying to read.")

        # Open for reading:
        self._fileRefCnt += 1
        if sys.version_info[:2] <= (3, 5):
            zef_file = _SharedFile(  # pylint: disable=E1120
                self.fp, zinfo.header_offset, self._fpclose, self._lock)
        zef_file = _SharedFile(self.fp, zinfo.header_offset,
                               self._fpclose, self._lock, lambda: hasattr(self, "_writing") and self._writing)
        try:
            # Skip the file header:
            fheader = zef_file.read(sizeFileHeader)
            if len(fheader) != sizeFileHeader:
                raise BadZipFile("Truncated file header")
            fheader = struct.unpack(structFileHeader, fheader)
            if fheader[_FH_SIGNATURE] != stringFileHeader:
                raise BadZipFile("Bad magic number for file header")

            fname = zef_file.read(fheader[_FH_FILENAME_LENGTH])
            if fheader[_FH_EXTRA_FIELD_LENGTH]:
                zef_file.read(fheader[_FH_EXTRA_FIELD_LENGTH])

            if zinfo.flag_bits & 0x20:
                # Zip 2.7: compressed patched data
                raise NotImplementedError(
                    "compressed patched data (flag bit 5)")

            if zinfo.flag_bits & 0x40:
                # strong encryption
                raise NotImplementedError("strong encryption (flag bit 6)")

            if zinfo.flag_bits & 0x800:
                # UTF-8 filename
                fname_str = fname.decode("utf-8")
            else:
                fname_str = fname.decode("cp437")

            if sys.platform.startswith("win"):
                if fname_str.replace("\\", "/") != zinfo.orig_filename.replace("\\", "/"):
                    raise BadZipFile(
                        'File name in directory %r and header %r differ.'
                        % (zinfo.orig_filename, fname))
            else:
                if fname_str != zinfo.orig_filename:
                    raise BadZipFile(
                        'File name in directory %r and header %r differ.'
                        % (zinfo.orig_filename, fname))

            # check for encrypted flag & handle password
            is_encrypted = zinfo.flag_bits & 0x1
            zd = None
            if is_encrypted:
                if not pwd:
                    pwd = self.pwd
                if not pwd:
                    raise RuntimeError("File %r is encrypted, password "
                                       "required for extraction" % name)

                zd = _ZipDecrypter(pwd)
                # The first 12 bytes in the cypher stream is an encryption header
                #  used to strengthen the algorithm. The first 11 bytes are
                #  completely random, while the 12th contains the MSB of the CRC,
                #  or the MSB of the file time depending on the header type
                #  and is used to check the correctness of the password.
                header = zef_file.read(12)
                h = list(map(zd, header[0:12]))
                if zinfo.flag_bits & 0x8:
                    # compare against the file type from extended local headers
                    check_byte = (zinfo._raw_time >> 8) & 0xff
                else:
                    # compare against the CRC otherwise
                    check_byte = (zinfo.CRC >> 24) & 0xff
                if h[11] != check_byte:
                    raise RuntimeError("Bad password for file %r" % name)

            return ZipExtFile(zef_file, mode, zinfo, zd, True)
        except Exception:
            zef_file.close()
            raise
