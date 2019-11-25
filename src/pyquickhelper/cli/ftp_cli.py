"""
@file
@brief Command line about transfering files.
"""
import os
import glob
from ..filehelper import TransferFTP


def ftp_upload(files, dest, host, user, pwd, ftps=False, fLOG=print):
    """
    Pushes a file to a server using :epkg:`FTP` or :epkg:`SFTP`.

    :param files: local files to move, comma separated or
        defined with a pattern if character ``*`` is used
    :param dest: destination folder
    :param host: server name or ip address
    :param user: user to log in
    :param pwd: password for the user
    :param ftps: use :epkg:`SFTP` or :epkg:`FTP`
    :param fLOG: logging function
    :return: status
    """
    if isinstance(files, str):
        files = [files]
    new_files = []
    for name in files:
        if ',' in name:
            new_files.extend(name.split(','))
        else:
            new_files.append(name)
    files = new_files
    new_files = []
    for name in files:
        if "*" in name:
            new_files.extend(glob.glob(name))
        else:
            new_files.append(name)
    files = new_files

    ftps = 'SFTP' if ftps in ('1', 'True', 'true', 1, True) else 'FTP'
    ftp = TransferFTP(host, user, pwd, ftps=ftps, fLOG=fLOG)

    for file in files:
        if not os.path.exists(file):
            raise FileNotFoundError("Unable to find '{}'.".format(file))
        if fLOG:
            fLOG("[ftp_upload] transfer '{}'".format(file))
        r = ftp.transfer(file, dest, file.split('/')[-1])
    try:
        ftp.close()
    except Exception as e:
        fLOG("[ftp_upload] closing failed due to {}.".format(e))
    return r
