# -*- coding: utf-8 -*-
"""
@file
@brief      keep the status of a folder, assuming this folder is not moved
"""
import os
import datetime
from ..loghelper.flog import noLOG
from .file_info import convert_st_date_to_datetime, checksum_md5, FileInfo


class FilesStatus:
    """
    This class maintains a list of files
    and does some verifications in order to check if a file
    was modified or not (if yes, then it will be updated to the website).
    """

    def __init__(self, file, fLOG=noLOG):
        """
        file which will contains the status
        @param      file            file, if None, fill _children
        @param      fLOG            logging function
        """
        self._file = file
        self.copyFiles = {}
        self.fileKeep = file
        self.LOG = fLOG

        if os.path.exists(self.fileKeep):
            with open(self.fileKeep, "r", encoding="utf8") as f:
                for ni, _ in enumerate(f.readlines()):
                    if ni == 0 and _.startswith("\ufeff"):
                        _ = _[len("\ufeff"):]  # pragma: no cover
                    spl = _.strip("\r\n ").split("\t")
                    try:
                        if len(spl) >= 2:
                            a, b = spl[:2]
                            obj = FileInfo(a, int(b), None, None, None)
                            if len(spl) > 2 and len(spl[2]) > 0:
                                obj.set_date(
                                    convert_st_date_to_datetime(spl[2]))
                            if len(spl) > 3 and len(spl[3]) > 0:
                                obj.set_mdate(
                                    convert_st_date_to_datetime(spl[3]))
                            if len(spl) > 4 and len(spl[4]) > 0:
                                obj.set_md5(spl[4])
                            self.copyFiles[a] = obj
                        else:
                            raise ValueError(  # pragma: no cover
                                "expecting a filename and a date on this line: " + _)
                    except Exception as e:
                        raise Exception(  # pragma: no cover
                            "issue with line:\n  {0} -- {1}".format(_, spl)) from e

        # contains all file to update
        self.modifiedFile = {}

    def __iter__(self):
        """
        Iterates on all files stored in the current file,
        yield a couple *(filename, FileInfo)*.
        """
        for a, b in self.copyFiles.items():
            yield a, b

    def iter_modified(self):
        """
        Iterates on all modified files yield a
        couple *(filename, reason)*.
        """
        for a, b in self.modifiedFile:
            yield a, b

    def save_dates(self, checkfile=None):
        """
        Saves the status of the copy.

        @param      checkfile       check the status for file checkfile
        """
        typstr = str
        if checkfile is None:
            checkfile = []
        rows = []
        for k in sorted(self.copyFiles):
            obj = self.copyFiles[k]
            da = "" if obj.date is None else str(obj.date)
            mda = "" if obj.mdate is None else str(obj.mdate)
            sum5 = "" if obj.checksum is None else str(obj.checksum)

            if k in checkfile and len(da) == 0:
                raise ValueError(  # pragma: no cover
                    "There should be a date for file " + k + "\n" + str(obj))
            if k in checkfile and len(mda) == 0:
                raise ValueError(  # pragma: no cover
                    "There should be a mdate for file " + k + "\n" + str(obj))
            if k in checkfile and len(sum5) <= 10:
                raise ValueError(  # pragma: no cover
                    "There should be a checksum( for file " + k + "\n" + str(obj))

            values = [k, typstr(obj.size), da, mda, sum5]
            sval = "%s\n" % "\t".join(values)
            if "\tNone" in sval:
                raise AssertionError(  # pragma: no cover
                    "This case should happen " + sval + "\n" + str(obj))

            rows.append(sval)

        with open(self.fileKeep, "w", encoding="utf8") as f:
            for r in rows:
                f.write(r)

    def has_been_modified_and_reason(self, file):
        """
        Returns *(True, reason)* if a file was modified or *(False, None)* if not.
        @param      file            filename
        @return                     *(True, reason)* or *(False, None)*
        """
        res = True
        reason = None
        typstr = str

        if file not in self.copyFiles:
            reason = "new"
            res = True
        else:
            obj = self.copyFiles[file]
            st = os.stat(file)
            if st.st_size != obj.size:
                reason = "size %s != old size %s" % (
                    str(st.st_size), typstr(obj.size))
                res = True
            else:
                ld = obj.mdate
                _m = st.st_mtime
                d = convert_st_date_to_datetime(_m)
                if d != ld:
                    # dates are different but files might be the same
                    if obj.checksum is not None:
                        ch = checksum_md5(file)
                        if ch != obj.checksum:
                            reason = "date/md5 %s != old date %s  md5 %s != %s" % (
                                typstr(ld), typstr(d), obj.checksum, ch)
                            res = True
                        else:
                            res = False
                    else:
                        # it cannot know, it does nothing
                        res = False
                else:
                    # mda.... no expected modification (dates did not change)
                    res = False

        return res, reason

    def add_modified_file(self, file, reason):
        """
        Adds a file the modified list of files.

        @param      file        file to add
        @param      reason      reason for modification
        """
        if file in self.modifiedFile:
            raise KeyError("file {0} is already present".format(file))
        self.modifiedFile[file] = reason

    def add_if_modified(self, file):
        """
        Adds a file to self.modifiedList if it was modified.
        @param      file    filename
        @return             True or False
        """
        res, reason = self.has_been_modified_and_reason(file)
        if res:
            self.add_modified_file(res, reason)
        return res

    def difference(self, files, u4=False, nlog=None):
        """
        Goes through the list of files and tells which one has changed.

        @param      files           @see cl FileTreeNode
        @param      u4              @see cl FileTreeNode (changes the output)
        @param      nlog            if not None, print something every ``nlog`` processed files
        @return                     iterator on files which changed
        """
        memo = {}
        if u4:
            nb = 0
            for file in files:
                memo[file.fullname] = True
                if file._file is None:
                    continue
                nb += 1
                if nlog is not None and nb % nlog == 0:
                    self.LOG(  # pragma: no cover
                        "[FileTreeStatus], processed", nb, "files")

                full = file.fullname
                r, reason = self.has_been_modified_and_reason(full)
                if r:
                    if reason == "new":
                        r = (">+", file._file, file, None)
                        yield r
                    else:
                        r = (">", file._file, file, None)
                        yield r
                else:
                    r = ("==", file._file, file, None)
                    yield r
        else:
            nb = 0
            for file in files:
                memo[file.fullpath] = True
                nb += 1
                if nlog is not None and nb % nlog == 0:
                    self.LOG("[FileTreeStatus], processed", nb, "files")
                full = file.fullname
                if self.has_been_modified_and_reason(full):
                    yield file

        for file in self.copyFiles.values():
            if file.filename not in memo:
                yield ("<+", file.filename, None, None)

    def update_copied_file(self, file, delete=False):
        """
        Updates the file in copyFiles (before saving), update all fields.
        @param      file        filename
        @param      delete      to remove this file
        @return                 file object
        """
        if delete:
            if file not in self.copyFiles:
                raise FileNotFoundError(  # pragma: no cover
                    "Unable to find a file in the list of monitored files: '{0}'.".format(file))
            del self.copyFiles[file]
            return None
        st = os.stat(file)
        size = st.st_size
        mdate = convert_st_date_to_datetime(st.st_mtime)
        date = datetime.datetime.now()
        md = checksum_md5(file)
        obj = FileInfo(file, size, date, mdate, md)
        self.copyFiles[file] = obj
        return obj
