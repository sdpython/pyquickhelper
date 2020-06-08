"""
@file
@brief Command line about transfering files.
"""
import os
import glob


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

    .. cmdref::
        :title: Upload one or several files to a FTP server
        :cmd: -m pyquickhelper ftp_upload --help

        Uploads a file, a list of files, files defined
        by a pattern to a FTP server using FTP or SFTP
        protocol.

    The user and the password can be prefix by
    `keyring,`. The module :epkg:`keyring` is then used
    to retrieve the values. Example:
    ``--user=keyring,user,site``.
    """
    from ..filehelper import TransferFTP

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

    if user.startswith("keyring,"):
        spl = user[len("keyring,"):].split(',')
        if len(spl) != 2:
            raise ValueError("Unable to get user '{}'.".format(user))
        import keyring
        user = keyring.get_password(spl[0], spl[1])
        if user is None:
            raise ValueError("No stored user for '{}'.".format(user))

    if pwd.startswith("keyring,"):
        spl = pwd[len("keyring,"):].split(',')
        if len(spl) != 2:
            raise ValueError("Unable to get user '{}'.".format(pwd))
        import keyring
        pwd = keyring.get_password(spl[0], spl[1])
        if pwd is None:
            raise ValueError("No stored user for '{}'.".format(pwd))

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
