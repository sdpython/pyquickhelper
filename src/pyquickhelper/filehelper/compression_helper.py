"""
@file
@brief Functions about compressing files.
"""

import os
import zipfile
import datetime
import gzip
import sys
from io import BytesIO

from ..loghelper.flog import noLOG, run_cmd
from .fexceptions import FileException
from ..texthelper.diacritic_helper import remove_diacritics

if sys.version_info[0] == 2:
    from codecs import open


def zip_files(filename, file_set, root=None, fLOG=noLOG):
    """
    put all files from an iterator in a zip file

    @param      filename        final zip file (can be None)
    @param      file_set        iterator on file to add
    @param      root            if not None, all path are relative to this path
    @param      fLOG            logging function
    @return                     number of added files (or content if filename is None)

    .. versionchanged:: 1.3
        Parameter *root* was added.

    .. versionchanged:: 1.4
        *filename* can be None, the function compresses into bytes without saving the results.
        Rename parameter *fileSet* into *file_set*.
    """
    nb = 0
    a1980 = datetime.datetime(1980, 1, 1)
    if filename is None:
        filename = BytesIO()
    with zipfile.ZipFile(filename, 'w') as myzip:
        for file in file_set:
            if not os.path.exists(file):
                continue
            st = os.stat(file)
            atime = datetime.datetime.fromtimestamp(st.st_atime)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime)
            if atime < a1980 or mtime < a1980:
                new_mtime = st.st_mtime + (4 * 3600)  # new modification time
                while datetime.datetime.fromtimestamp(new_mtime) < a1980:
                    new_mtime += (4 * 3600)  # new modification time

                fLOG("zip_files: changing time timestamp for file ", file)
                os.utime(file, (st.st_atime, new_mtime))

            arcname = os.path.relpath(file, root) if root else None
            myzip.write(file, arcname=arcname)
            nb += 1
    return filename.getvalue() if isinstance(filename, BytesIO) else nb


def unzip_files(zipf, where_to=None, fLOG=noLOG, fvalid=None, remove_space=True):
    """
    unzip files from a zip archive

    @param      zipf            archive (or bytes or BytesIO)
    @param      where_to        destination folder (can be None, the result is a list of tuple)
    @param      fLOG            logging function
    @param      fvalid          function which takes two paths (zip name, local name) and return True if the file
                                must be unzipped, False otherwise, if None, the default answer is True
    @param      remove_space    remove spaces in created local path (+ ``',()``)
    @return                     list of unzipped files

    .. versionchanged:: 1.4
        Add parameter *fvalid*.
        Moved to *filehelper*.
    """
    if sys.version_info[0] == 2:
        if isinstance(zipf, bytearray):
            zipf = BytesIO(zipf)
    else:
        if isinstance(zipf, bytes):
            zipf = BytesIO(zipf)

    files = []
    with zipfile.ZipFile(zipf, "r") as file:
        for info in file.infolist():
            if where_to is None:
                files.append((info.filename, file.read(info.filename)))
            else:
                clean = remove_diacritics(info.filename)
                if remove_space:
                    clean = clean.replace(" ", "") \
                                 .replace("'", "") \
                                 .replace(",", "_") \
                                 .replace("(", "_") \
                                 .replace(")", "_")
                tos = os.path.join(where_to, clean)
                if not os.path.exists(tos):
                    if fvalid and not fvalid(info.filename, tos):
                        fLOG("    skipping", info.filename)
                        continue
                    data = file.read(info.filename)
                    # check encoding to avoid characters not allowed in paths
                    if not os.path.exists(tos):
                        if sys.platform.startswith("win"):
                            tos = tos.replace("/", "\\")
                        finalfolder = os.path.split(tos)[0]
                        if not os.path.exists(finalfolder):
                            fLOG("    creating folder (zip)",
                                 os.path.abspath(finalfolder))
                            try:
                                os.makedirs(finalfolder)
                            except FileNotFoundError as e:
                                mes = "Unexpected error\ninfo.filename={0}\ntos={1}\nfinalfolder={2}\nlen(nfinalfolder)={3}".format(
                                    info.filename, tos, finalfolder, len(finalfolder))
                                raise FileNotFoundError(mes) from e
                        if not info.filename.endswith("/"):
                            try:
                                with open(tos, "wb") as u:
                                    u.write(data)
                            except FileNotFoundError as e:
                                # probably an issue in the path name
                                # the next lines are just here to distinguish
                                # between the two cases
                                if not os.path.exists(finalfolder):
                                    raise e
                                else:
                                    newname = info.filename.replace(
                                        " ", "_").replace(",", "_")
                                    if sys.platform.startswith("win"):
                                        newname = newname.replace("/", "\\")
                                    tos = os.path.join(where_to, newname)
                                    finalfolder = os.path.split(tos)[0]
                                    if not os.path.exists(finalfolder):
                                        fLOG("    creating folder (zip)",
                                             os.path.abspath(finalfolder))
                                        os.makedirs(finalfolder)
                                    with open(tos, "wb") as u:
                                        u.write(data)
                            files.append(tos)
                            fLOG("    unzipped ", info.filename, " to ", tos)
                    elif not tos.endswith("/"):
                        files.append(tos)
                elif not info.filename.endswith("/"):
                    files.append(tos)
    return files


def gzip_files(filename, file_set, fLOG=noLOG):
    """
    put all files from an iterator in a zip file and then in a gzip file

    @param      filename        final gzip file (double compression, extension should something like .zip.gz)
    @param      file_set        iterator on file to add
    @param      fLOG            logging function
    @return                     bytes (if filename is None) or None

    .. versionchanged:: 1.4
        Remove parameter *filename_zip*, compress in memory.
        Rename parameter *filename_gz* into *filename*, *fileSet* into *file_set*.

    """
    content = zip_files(None, file_set, fLOG=fLOG)
    if filename is None:
        filename = BytesIO()
    f = gzip.open(filename, 'wb')
    f.write(content)
    f.close()
    return filename.getvalue() if isinstance(filename, BytesIO) else None


def ungzip_files(filename, where_to=None, fLOG=noLOG, fvalid=None, remove_space=True):
    """
    decompress files from a gzip file

    @param      filename        final gzip file (double compression, extension should something like .zip.gz)
    @param      where_to        destination folder (can be None, the result is a list of tuple)
    @param      fLOG            logging function
    @param      fvalid          function which takes two paths (zip name, local name) and return True if the file
                                must be unzipped, False otherwise, if None, the default answer is True
    @param      remove_space    remove spaces in created local path (+ ``',()``)
    @return                     number of added files

    .. versionadded:: 1.4
    """
    if sys.version_info[0] == 2:
        if isinstance(filename, bytearray):
            filename = BytesIO(filename)
    else:
        if isinstance(filename, bytes):
            filename = BytesIO(filename)
    f = gzip.open(filename, 'rb')
    content = f.read()
    f.close()
    return unzip_files(content, where_to=where_to, fLOG=fLOG)


def zip7_files(filename_7z, file_set, fLOG=noLOG, temp_folder="."):
    """
    If *7z* is installed, the function uses it
    to compress file into 7z format. The file *filename_7z* must not exist
    (`7z <http://www.7-zip.org/>`_).

    @param      filename_7z     final destination
    @param      fileSet         list of files to compress
    @param      fLOG            logging function
    @param      temp_folder     the function stores the list of files in a file in the
                                folder *temp_folder*, it will be removed afterwords
    @return                     number of added files

    """
    if sys.platform.startswith("win"):
        exe = r"C:\Program Files\7-Zip\7z.exe"
        if not os.path.exists(exe):
            raise FileNotFoundError("unable to find: {0}".format(exe))
    else:
        exe = "7z"

    if os.path.exists(filename_7z):
        raise FileException("{0} already exists".format(filename_7z))

    notxist = [fn for fn in file_set if not os.path.exists(fn)]
    if len(notxist) > 0:
        raise FileNotFoundError(
            "unable to compress unexisting files:\n{0}".format("\n".join(notxist)))

    flist = os.path.join(temp_folder, "listfiles7z.txt")
    with open(flist, "w", encoding="utf8") as f:
        f.write("\n".join(file_set))

    cmd = '"{0}" a "{1}" @"{2}"'.format(exe, filename_7z, flist)
    run_cmd(cmd, wait=True)
    return len(file_set)


def un7zip_files(zipf, where_to=None, fLOG=noLOG, fvalid=None, remove_space=True):
    """
    unzip files from a zip archive compress with 7z

    @param      zipf            archive (or bytes or BytesIO)
    @param      where_to        destination folder (can be None, the result is a list of tuple)
    @param      fLOG            logging function
    @param      fvalid          function which takes two paths (zip name, local name) and return True if the file
                                must be unzipped, False otherwise, if None, the default answer is True
    @param      remove_space    remove spaces in created local path (+ ``',()``)
    @return                     list of unzipped files

    The function requires module `pylzma <https://pypi.python.org/pypi/pylzma>`_.

    .. versionadded:: 1.4
    """
    from py7zlib import Archive7z
    if not isinstance(zipf, BytesIO):
        if sys.version_info[0] == 2:
            if isinstance(zipf, bytearray):
                zipf = BytesIO(zipf)
            else:
                zipf = open(zipf, "rb")
        else:
            if isinstance(zipf, bytes):
                zipf = BytesIO(zipf)
            else:
                zipf = open(zipf, "rb")

    files = []
    file = Archive7z(zipf)
    for info in file.files:
        if where_to is None:
            files.append((info.filename, info.read()))
        else:
            clean = remove_diacritics(info.filename)
            if remove_space:
                clean = clean.replace(" ", "") \
                             .replace("'", "") \
                             .replace(",", "_") \
                             .replace("(", "_") \
                             .replace(")", "_")
            tos = os.path.join(where_to, clean)
            if not os.path.exists(tos):
                if fvalid and not fvalid(info.filename, tos):
                    fLOG("    skipping", info.filename)
                    continue
                data = info.read()
                # check encoding to avoid characters not allowed in paths
                if not os.path.exists(tos):
                    if sys.platform.startswith("win"):
                        tos = tos.replace("/", "\\")
                    finalfolder = os.path.split(tos)[0]
                    if not os.path.exists(finalfolder):
                        fLOG("    creating folder (7z)",
                             os.path.abspath(finalfolder))
                        try:
                            os.makedirs(finalfolder)
                        except FileNotFoundError as e:
                            mes = "Unexpected error\ninfo.filename={0}\ntos={1}\nfinalfolder={2}\nlen(nfinalfolder)={3}".format(
                                info.filename, tos, finalfolder, len(finalfolder))
                            raise FileNotFoundError(mes) from e
                    if not info.filename.endswith("/"):
                        try:
                            with open(tos, "wb") as u:
                                u.write(data)
                        except FileNotFoundError as e:
                            # probably an issue in the path name
                            # the next lines are just here to distinguish
                            # between the two cases
                            if not os.path.exists(finalfolder):
                                raise e
                            else:
                                newname = info.filename.replace(
                                    " ", "_").replace(",", "_")
                                if sys.platform.startswith("win"):
                                    newname = newname.replace("/", "\\")
                                tos = os.path.join(where_to, newname)
                                finalfolder = os.path.split(tos)[0]
                                if not os.path.exists(finalfolder):
                                    fLOG("    creating folder (7z)",
                                         os.path.abspath(finalfolder))
                                    os.makedirs(finalfolder)
                                with open(tos, "wb") as u:
                                    u.write(data)
                        files.append(tos)
                        fLOG("    unzipped ", info.filename, " to ", tos)
                elif not tos.endswith("/"):
                    files.append(tos)
            elif not info.filename.endswith("/"):
                files.append(tos)
    return files
