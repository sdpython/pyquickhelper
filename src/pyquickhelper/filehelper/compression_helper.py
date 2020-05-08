"""
@file
@brief Functions about compressing files.
"""

import os
import zipfile
import datetime
import gzip
import sys
import warnings
import tarfile
from io import BytesIO

from ..loghelper.flog import noLOG, run_cmd
from .fexceptions import FileException
from ..texthelper.diacritic_helper import remove_diacritics
from .synchelper import explore_folder


def zip_files(filename, file_set, root=None, fLOG=noLOG):
    """
    Zips all files from an iterator.

    @param      filename        final zip file (can be None)
    @param      file_set        iterator on file to add
    @param      root            if not None, all path are relative to this path
    @param      fLOG            logging function
    @return                     number of added files (or content if filename is None)

    *filename* can be None, the function compresses
    into bytes without saving the results.
    """
    nb = 0
    a1980 = datetime.datetime(1980, 1, 1)
    if filename is None:
        filename = BytesIO()
    with zipfile.ZipFile(filename, 'w') as myzip:
        for file in file_set:
            if not os.path.exists(file):
                continue
            if fLOG:
                fLOG("[zip_files] '{0}'".format(file))
            st = os.stat(file)
            atime = datetime.datetime.fromtimestamp(st.st_atime)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime)
            if atime < a1980 or mtime < a1980:  # pragma: no cover
                new_mtime = st.st_mtime + (4 * 3600)  # new modification time
                while datetime.datetime.fromtimestamp(new_mtime) < a1980:
                    new_mtime += (4 * 3600)  # new modification time

                fLOG(
                    "[zip_files] changing time timestamp for file '{0}'".format(file))
                os.utime(file, (st.st_atime, new_mtime))

            arcname = os.path.relpath(file, root) if root else None
            myzip.write(file, arcname=arcname)
            nb += 1
    return filename.getvalue() if isinstance(filename, BytesIO) else nb


def unzip_files(zipf, where_to=None, fLOG=noLOG, fvalid=None, remove_space=True,
                fail_if_error=True):
    """
    Unzips files from a zip archive.

    @param      zipf            archive (or bytes or BytesIO)
    @param      where_to        destination folder (can be None, the result is a list of tuple)
    @param      fLOG            logging function
    @param      fvalid          function which takes two paths (zip name, local name) and return True if the file
                                must be unzipped, False otherwise, if None, the default answer is True
    @param      remove_space    remove spaces in created local path (+ ``',()``)
    @param      fail_if_error   fails if an error is encountered
                                (typically a weird character in a filename),
                                otherwise a warning is thrown.
    @return                     list of unzipped files
    """
    if isinstance(zipf, bytes):
        zipf = BytesIO(zipf)

    try:
        with zipfile.ZipFile(zipf, "r"):
            pass
    except zipfile.BadZipFile as e:  # pragma: no cover
        if isinstance(zipf, BytesIO):
            raise e
        raise IOError("Unable to read file '{0}'".format(zipf)) from e

    files = []
    with zipfile.ZipFile(zipf, "r") as file:
        for info in file.infolist():
            if fLOG:
                fLOG("[unzip_files] unzip '{0}'".format(info.filename))
            if where_to is None:
                try:
                    content = file.read(info.filename)
                except zipfile.BadZipFile as e:  # pragma: no cover
                    if fail_if_error:
                        raise zipfile.BadZipFile(
                            "Unable to extract '{0}' due to {1}".format(info.filename, e)) from e
                    warnings.warn(
                        "Unable to extract '{0}' due to {1}".format(info.filename, e), UserWarning)
                    continue
                files.append((info.filename, content))
            else:
                clean = remove_diacritics(info.filename)
                if remove_space:
                    clean = clean.replace(" ", "").replace("'", "").replace(",", "_") \
                                 .replace("(", "_").replace(")", "_")
                tos = os.path.join(where_to, clean)
                if not os.path.exists(tos):
                    if fvalid and not fvalid(info.filename, tos):
                        fLOG("[unzip_files]    skipping", info.filename)
                        continue
                    try:
                        data = file.read(info.filename)
                    except zipfile.BadZipFile as e:  # pragma: no cover
                        if fail_if_error:
                            raise zipfile.BadZipFile(
                                "Unable to extract '{0}' due to {1}".format(info.filename, e)) from e
                        warnings.warn(
                            "Unable to extract '{0}' due to {1}".format(info.filename, e), UserWarning)
                        continue
                    # check encoding to avoid characters not allowed in paths
                    if not os.path.exists(tos):
                        if sys.platform.startswith("win"):
                            tos = tos.replace("/", "\\")
                        finalfolder = os.path.split(tos)[0]
                        if not os.path.exists(finalfolder):
                            fLOG("[unzip_files]    creating folder (zip)",
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
                            except FileNotFoundError as e:  # pragma: no cover
                                # probably an issue in the path name
                                # the next lines are just here to distinguish
                                # between the two cases
                                if not os.path.exists(finalfolder):
                                    raise e
                                newname = info.filename.replace(
                                    " ", "_").replace(",", "_")
                                if sys.platform.startswith("win"):
                                    newname = newname.replace("/", "\\")
                                tos = os.path.join(where_to, newname)
                                finalfolder = os.path.split(tos)[0]
                                if not os.path.exists(finalfolder):
                                    fLOG("[unzip_files]    creating folder (zip)",
                                         os.path.abspath(finalfolder))
                                    os.makedirs(finalfolder)
                                with open(tos, "wb") as u:
                                    u.write(data)
                            files.append(tos)
                            fLOG("[unzip_files]    unzipped ",
                                 info.filename, " to ", tos)
                    elif not tos.endswith("/"):
                        files.append(tos)
                elif not info.filename.endswith("/"):
                    files.append(tos)
    return files


def gzip_files(filename, file_set, encoding=None, fLOG=noLOG):
    """
    Compresses all files from an iterator in a zip file
    and then in a gzip file.

    @param      filename        final gzip file (double compression, extension should something like .zip.gz)
    @param      file_set        iterator on file to add
    @param      encoding        encoding of input files (no double compression then)
    @param      fLOG            logging function
    @return                     bytes (if filename is None) or None
    """
    if filename is None:
        filename = BytesIO()
    if encoding is None:
        content = zip_files(None, file_set, fLOG=fLOG)
        f = gzip.open(filename, 'wb')
        f.write(content)
        f.close()
        return filename.getvalue() if isinstance(filename, BytesIO) else None
    f = gzip.open(filename, 'wt', encoding="utf-8")
    for name in file_set:
        with open(name, "r", encoding="utf-8") as ft:
            content = ft.read()
        f.write(content)
    f.close()
    return filename.getvalue() if isinstance(filename, BytesIO) else None


def ungzip_files(filename, where_to=None, fLOG=noLOG, fvalid=None, remove_space=True,
                 unzip=True, encoding=None):
    """
    Uncompresses files from a gzip file.

    @param      filename        final gzip file (double compression, extension should something like .zip.gz)
    @param      where_to        destination folder (can be None, the result is a list of tuple)
    @param      fLOG            logging function
    @param      fvalid          function which takes two paths (zip name, local name) and return True if the file
                                must be unzipped, False otherwise, if None, the default answer is True
    @param      remove_space    remove spaces in created local path (+ ``',()``)
    @param      unzip           unzip file after gzip
    @param      encoding        encoding
    @return                     list of unzipped files
    """
    if isinstance(filename, bytes):
        is_file = False
        filename = BytesIO(filename)
    else:
        is_file = True

    if encoding is None:
        f = gzip.open(filename, 'rb')
        content = f.read()
        f.close()
        if unzip:
            try:
                return unzip_files(content, where_to=where_to, fLOG=fLOG)
            except Exception as e:  # pragma: no cover
                raise IOError(
                    "Unable to unzip file '{0}'".format(filename)) from e
        elif where_to is not None:
            filename = os.path.split(filename)[-1].replace(".gz", "")
            filename = os.path.join(where_to, filename)
            with open(filename, "wb") as f:
                f.write(content)
            return filename
        return content
    else:
        f = gzip.open(filename, 'rt', encoding="utf-8")
        content = f.read()
        f.close()
        if is_file:
            filename = filename.replace(".gz", "")
            with open(filename, "wb") as f:
                f.write(content)
            return filename
        return content


def zip7_files(filename_7z, file_set, fLOG=noLOG, temp_folder="."):
    """
    If :epkg:`7z` is installed, the function uses it
    to compress file into 7z format. The file *filename_7z* must not exist.

    @param      filename_7z     final destination
    @param      file_set        list of files to compress
    @param      fLOG            logging function
    @param      temp_folder     the function stores the list of files in a file in the
                                folder *temp_folder*, it will be removed afterwords
    @return                     number of added files

    .. faqref::
        :title: Why module pylzma does not work?
        :lid: faq-pylzma-ref

        The module :epkg:`pylzma`
        failed to decompress the file produced by the latest version
        of :epkg:`7z` (2016-09-23). The compression
        was changed by tweaking the command line. LZMA is used instead LZMA2.
        The current version does not include this
        `commit <https://github.com/fancycode/pylzma/commit/b5c3c2bd4ab7abfb65de772861ecc600fe37394b>`_.
        Or you can clone the package
        `sdpython.pylzma <https://github.com/sdpython/pylzma>`_
        and build it yourself with ``python setup.py bdist_wheel``.
    """
    if sys.platform.startswith("win"):  # pragma: no cover
        exe = r"C:\Program Files\7-Zip\7z.exe"
        if not os.path.exists(exe):
            raise FileNotFoundError("unable to find: {0}".format(exe))
    elif sys.platform.startswith("darwin"):
        exe = "7za"
    else:
        exe = "7z"

    if os.path.exists(filename_7z):
        raise FileException(  # pragma: no cover
            "'{0}' already exists".format(filename_7z))

    notxist = [fn for fn in file_set if not os.path.exists(fn)]
    if len(notxist) > 0:
        raise FileNotFoundError(  # pragma: no cover
            "unable to compress unexisting files:\n{0}".format("\n".join(notxist)))

    flist = os.path.join(temp_folder, "listfiles7z.txt")
    with open(flist, "w", encoding="utf8") as f:
        f.write("\n".join(file_set))

    cmd = '"{0}" -m0=lzma -mfb=64 a "{1}" "@{2}"'.format(
        exe, filename_7z, flist)
    out, err = run_cmd(cmd, wait=True)
    if "Error:" in out or not os.path.exists(filename_7z):
        raise FileException(  # pragma: no cover
            "An error occurred with cmd: '{0}'\nOUT:\n{1}\nERR\n{2}\n----".format(cmd, out, err))
    return len(file_set)


def un7zip_files(zipf, where_to=None, fLOG=noLOG, fvalid=None,
                 remove_space=True, cmd_line=False):
    """
    Unzips files from a zip archive compress with :epkg:`7z`.

    @param      zipf            archive (or bytes or BytesIO)
    @param      where_to        destination folder (can be None, the result is a list of tuple)
    @param      fLOG            logging function
    @param      fvalid          function which takes two paths (zip name, local name) and return True if the file
                                must be unzipped, False otherwise, if None, the default answer is True
    @param      remove_space    remove spaces in created local path (+ ``',()``)
    @param      cmd_line        use command line instead of module :epkg:`pylzma`
    @return                     list of unzipped files

    The function requires module :epkg:`pylzma`.
    See :ref:`Why module pylzma does not work? <faq-pylzma-ref>`.
    """
    if cmd_line:
        if not isinstance(zipf, str  # unicode
                          ):
            raise TypeError("Cannot use command line unless zipf is a file.")
        if remove_space:
            warnings.warn(
                '[un7zip_files] remove_space and cmd_line are incompatible options.', UserWarning)
        if fvalid:
            warnings.warn(
                'fvalid and cmd_line are incompatible options.', UserWarning)
        if sys.platform.startswith("win"):  # pragma: no cover
            exe = r"C:\Program Files\7-Zip\7z.exe"
            if not os.path.exists(exe):
                raise FileNotFoundError("unable to find: {0}".format(exe))

            if where_to is None:
                where_to = os.path.abspath(".")
        elif sys.platform.startswith("darwin"):
            exe = "7za"
        else:
            exe = "7z"

        cmd = '"{0}" x "{1}" -o{2}'.format(exe, zipf, where_to)
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
        if len(err) > 0 or "Error:" in out:
            raise FileException(  # pragma: no cover
                "Unable to un-7zip file '{0}'\n--CMD--\n{3}\n--OUT--\n{1}\n--ERR--\n{2}".format(zipf, out, err, cmd))

        return explore_folder(where_to)[1]
    else:
        from py7zlib import Archive7z, FormatError
        file_zipf = None
        if not isinstance(zipf, BytesIO):
            file_zipf = zipf
            if isinstance(zipf, bytes):
                zipf = BytesIO(zipf)
            else:
                zipf = open(zipf, "rb")

        files = []
        try:
            file = Archive7z(zipf)
        except FormatError as e:
            raise FileException(  # pragma: no cover
                "You should use a modified version available at https://github.com/sdpython/pylzma") from e
        for info in file.files:
            if where_to is None:
                files.append((info.filename, info.read()))
            else:
                clean = remove_diacritics(info.filename)
                if remove_space:
                    clean = clean.replace(" ", "").replace("'", "") \
                                 .replace(",", "_").replace("(", "_") \
                                 .replace(")", "_")
                tos = os.path.join(where_to, clean)
                if not os.path.exists(tos):
                    if fvalid and not fvalid(info.filename, tos):
                        fLOG("[un7zip_files]    skipping", info.filename)
                        continue
                    try:
                        data = info.read()
                    except NotImplementedError as e:  # pragma: no cover
                        # You should use command line.
                        if file_zipf is None:
                            raise TypeError(
                                "Cannot switch to command line unless zipf is a file.")
                        warnings.warn(
                            "[un7zip_files] '{0}' --> Unavailable format. Use command line.".format(zipf), UserWarning)
                        return un7zip_files(file_zipf, where_to=where_to, fLOG=fLOG, fvalid=fvalid,
                                            remove_space=remove_space, cmd_line=True)
                    except Exception as e:  # pragma: no cover
                        raise FileException("Unable to unzip file '{0}' from '{1}'".format(
                            info.filename, zipf)) from e
                    # check encoding to avoid characters not allowed in paths
                    if not os.path.exists(tos):
                        if sys.platform.startswith("win"):
                            tos = tos.replace("/", "\\")
                        finalfolder = os.path.split(tos)[0]
                        if not os.path.exists(finalfolder):
                            fLOG("[un7zip_files]    creating folder (7z)",
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
                                newname = info.filename.replace(
                                    " ", "_").replace(",", "_")
                                if sys.platform.startswith("win"):
                                    newname = newname.replace("/", "\\")
                                tos = os.path.join(where_to, newname)
                                finalfolder = os.path.split(tos)[0]
                                if not os.path.exists(finalfolder):
                                    fLOG("[un7zip_files]    creating folder (7z)",
                                         os.path.abspath(finalfolder))
                                    os.makedirs(finalfolder)
                                with open(tos, "wb") as u:
                                    u.write(data)
                            files.append(tos)
                            fLOG("[un7zip_files]    unzipped ",
                                 info.filename, " to ", tos)
                    elif not tos.endswith("/"):
                        files.append(tos)
                elif not info.filename.endswith("/"):
                    files.append(tos)
        return files


def unrar_files(zipf, where_to=None, fLOG=noLOG, fvalid=None, remove_space=True):
    """
    Uncompresses files from a rar archive compress with :epkg:`7z`
    on Window or *unrar* on linux.

    @param      zipf            archive (or bytes or BytesIO)
    @param      where_to        destination folder (can be None, the result is a list of tuple)
    @param      fLOG            logging function
    @param      fvalid          function which takes two paths (zip name, local name) and return True if the file
                                must be unzipped, False otherwise, if None, the default answer is True
    @param      remove_space    remove spaces in created local path (+ ``',()``)
    @return                     list of unzipped files
    """
    if sys.platform.startswith("win"):  # pragma: no cover
        exe = r"C:\Program Files\7-Zip\7z.exe"
        if not os.path.exists(exe):
            raise FileNotFoundError("unable to find: {0}".format(exe))

        if where_to is None:
            where_to = os.path.abspath(".")
        cmd = '"{0}" x "{1}" "-o{2}"'.format(exe, zipf, where_to)
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
        if len(err) > 0 or "Error:" in out:
            raise FileException(
                "Unable to unrar file '{0}'\nOUT\n{1}\nERR\n{2}".format(zipf, out, err))

        return explore_folder(where_to)[1]
    else:
        exe = "unrar"

        if where_to is None:
            where_to = os.path.abspath(".")
        cmd = '"{0}" x "{1}"'.format(exe, zipf)
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG, change_path=where_to)
        if len(err) > 0:
            raise FileException(
                "Unable to unrar file '{0}'\n--CMD--\n{3}\n--OUT--\n{1}\n--ERR--\n{2}".format(zipf, out, err, cmd))

        return explore_folder(where_to)[1]


def untar_files(filename, where_to=None, fLOG=noLOG, encoding=None):
    """
    Uncompresses files from a tar file.

    @param      filename        final tar file (double compression, extension should something like .zip.gz)
    @param      where_to        destination folder (can be None, the result is a list of tuple)
    @param      fLOG            logging function
    @param      encoding        encoding
    @return                     list of unzipped files
    """
    if isinstance(filename, bytes):
        fileobj = filename
        name = None
        targz = True
    else:
        name = filename
        fileobj = None
        targz = name.endswith(".tar.gz")

    if targz:
        tar = tarfile.open(name=name, fileobj=fileobj,
                           mode="r:gz", encoding=encoding)
        names = tar.getnames()
        tar.extractall(where_to)
        tar.close()
    else:
        tar = tarfile.open(name=name, fileobj=fileobj,
                           mode="r:", encoding=encoding)
        names = tar.getnames()
        tar.extractall(where_to)
        tar.close()
    if where_to is not None:
        return [os.path.join(where_to, name) for name in names]
    return names
