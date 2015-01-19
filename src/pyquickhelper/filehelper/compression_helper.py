"""
@file
@brief Functions about compressing files.
"""

import os, re, zipfile, datetime, gzip, sys

from ..loghelper.flog import noLOG, run_cmd
from .fexceptions import FileException

def zip_files (filename, fileSet, fLOG = noLOG) :
    """
    put all files from an iterator in a zip file

    @param      filename        final zip file
    @param      fileSet         iterator on file to add
    @param      fLOG            logging function
    @return                     number of added files
    """
    nb = 0
    a1980 = datetime.datetime(1980,1,1)
    with zipfile.ZipFile(filename, 'w') as myzip:
        for file in fileSet :
            st    = os.stat(file)
            atime = datetime.datetime.fromtimestamp(st.st_atime)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime)
            if atime < a1980 or mtime < a1980 :
                new_mtime = st.st_mtime + (4*3600) #new modification time
                while datetime.datetime.fromtimestamp(new_mtime) < a1980 :
                    new_mtime += (4*3600) #new modification time

                fLOG("zip_files: changing time timestamp for file ", file)
                os.utime(file,(st.st_atime,new_mtime))

            myzip.write(file)
            nb += 1
    return nb

def gzip_files (filename_gz, fileSet, fLOG = noLOG, filename_zip = None) :
    """
    put all files from an iterator in a zip file and then in a gzip file

    @param      filename_gz     final gzip file (double compression, extension should something like .zip.gz)
    @param      filename_zip    temporary zip file (will be removed after the zipping unless it is different from None)
    @param      fileSet         iterator on file to add
    @param      fLOG            logging function
    @return                     number of added files
    """
    if filename_zip is None :
        zipf = filename_gz + ".temp.zip"
    else : zipf = filename_zip
    nb = zip_files (zipf, fileSet, fLOG = fLOG)

    f = gzip.open(filename_gz, 'wb')
    with open(zipf, "rb") as gr :
        bb = gr.read(1000000)
        while len(bb) > 0 :
            f.write(bb)
            bb = gr.read(1000000)
    f.close()

    if filename_zip is None :
        os.remove (zipf)

    return nb

def zip7_files(filename_7z, fileSet, fLOG = noLOG, temp_folder = "."):
    """

    If `7z <http://www.7-zip.org/>`_ is installed, the function uses it
    to compress file into 7z format. The file *filename_7z* must not exist.

    .. index:: 7zip, 7z

    @param      filename_7z     final destination
    @param      fileSet         list of files to compress
    @param      fLOG            logging function
    @param      temp_folder     the function stores the list of files in a file in the
                                folder *temp_folder*, it will be removed afterwords
    @return                     number of added files

    .. versionadded:: 0.9

    """
    if sys.platform.startswith("win"):
        exe = r"C:\Program Files\7-Zip\7z.exe"
        if not os.path.exists(exe):
            raise FileNotFoundError("unable to find: {0}".format(exe))
    else:
        exe = "7z"

    if os.path.exists(filename_7z):
        raise FileException("{0} already exists".format(filename_7z))

    notxist = [ fn for fn in fileSet if not os.path.exists(fn) ]
    if len(notxist) > 0:
        raise FileNotFoundError("unable to compress unexisting files:\n{0}".format("\n".join(notxist)))

    flist = os.path.join(temp_folder, "listfiles7z.txt")
    with open(flist,"w",encoding="utf8") as f:
        f.write("\n".join(fileSet))

    cmd = '"{0}" a "{1}" @"{2}"'.format(exe, filename_7z, flist)
    run_cmd(cmd, wait=True)

    #os.remove(flist)

    return len(fileSet)