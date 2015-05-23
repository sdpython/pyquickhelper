#-*- coding: utf-8 -*-
"""
@file
@brief  Uses git to get version number.
"""

import os
import sys
import datetime
import xml.etree.ElementTree as ET

from ..flog import fLOG, run_cmd

if sys.version_info[0] == 2:
    from codecs import open


def my_date_conversion(sdate):
    """
    converts a date into a datetime

    @param      sdate       string
    @return                 date

    .. versionadded:: 1.0

    """
    first = sdate.split(" ")[0]
    trois = first.replace(".", "-").replace("/", "-").split("-")
    return datetime.datetime(int(trois[0]), int(trois[1]), int(trois[2]))


def IsRepo(location, commandline=True, log=False):
    """
    says if it a repository GIT

    @param      location        (str) location
    @param      commandline     (bool) use commandline or not
    @param      log             if True, return the log not a boolean
    @return                     bool
    """
    if location is None:
        location = os.path.normpath(os.path.abspath(
            os.path.join(os.path.split(__file__)[0], "..", "..", "..", "..")))

    try:
        get_repo_version(location, commandline, log=log)
        return True
    except Exception:
        if log:
            return get_repo_version(location, commandline, log=log)
        else:
            return False


class RepoFile:

    """
    mimic a GIT file
    """

    def __init__(self, **args):
        """
        constructor
        @param   args       list of members to add
        """
        for k, v in args.items():
            self.__dict__[k] = v

        if "name" in self.__dict__:
            if '"' in self.name:
                #defa = sys.stdout.encoding if sys.stdout != None else "utf8"
                self.name = self.name.replace('"', "")
                #self.name = self.name.encode(defa).decode("utf-8")
            if "\\303" in self.name:
                # don't know yet how to avoid that
                self.name = self.name.replace(r"\303\251", chr(233)) \
                                     .replace(r"\303\250", chr(232))

    def __str__(self):
        """
        usual
        """
        return self.name


def repo_ls(full, commandline=True):
    """
    run ``ls`` on a path
    @param      full            full path
    @param      commandline use command line instead of pysvn
    @return                     output of client.ls
    """

    if not commandline:
        try:
            raise NotImplementedError()
        except Exception:
            return repo_ls(full, True)
    else:
        if sys.platform.startswith("win32"):
            cmd = r'"C:\Program Files (x86)\Git\bin\git"'
        else:
            cmd = 'git'

        cmd += " ls-tree -r HEAD \"%s\"" % full
        out, err = run_cmd(cmd,
                           wait=True,
                           do_not_log=True,
                           encerror="strict",
                           encoding=sys.stdout.encoding if sys.version_info[
                               0] != 2 and sys.stdout is not None else "utf8",
                           change_path=os.path.split(
                               full)[0] if os.path.isfile(full) else full,
                           shell=sys.platform.startswith("win32"))
        if len(err) > 0:
            fLOG("problem with file ", full, err)
            raise Exception(err)

        res = [RepoFile(name=os.path.join(full, _.strip().split("\t")[-1]))
               for _ in out.split("\n") if len(_) > 0]
        return res


def __get_version_from_version_txt(path):
    """
    private function, tries to find a file ``version.txt`` which should
    contains the version number (if svn is not present)
    @param      path        folder to look, it will look to the the path of this file,
                            some parents directories and finally this path
    @return                 the version number

    @warning If ``version.txt`` was not found, it throws an exception.
    """
    file = os.path.split(__file__)[0]
    paths = [file,
             os.path.join(file, ".."),
             os.path.join(file, "..", ".."),
             os.path.join(file, "..", "..", ".."),
             path]
    for p in paths:
        fp = os.path.join(p, "version.txt")
        if os.path.exists(fp):
            with open(fp, "r") as f:
                return int(f.read().strip(" \n\r\t"))
    raise FileNotFoundError(
        "unable to find version.txt in\n" + "\n".join(paths))


def get_repo_log(path=None, file_detail=False, commandline=True):
    """
    get the latest changes operated on a file in a folder or a subfolder
    @param      path            path to look
    @param      file_detail     if True, add impacted files
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     list of changes, each change is a list of 4-uple:
                                    - author
                                    - commit hash [:6]
                                    - date (datetime)
                                    - comment$
                                    - full commit hash
                                    - link to commit (if the repository is http://...)

    The function use a command line if an error occurred. It uses the xml format:
    @code
    <logentry revision="161">
        <author>xavier dupre</author>
        <date>2013-03-23T15:02:50.311828Z</date>
        <msg>pyquickhelper: first version</msg>
        <hash>full commit hash</hash>
    </logentry>
    @endcode

    Add link:
    @code
    https://github.com/sdpython/pyquickhelper/commit/8d5351d1edd4a8997f358be39da80c72b06c2272
    @endcode

    More: `git pretty format <http://opensource.apple.com/source/Git/Git-19/src/git-htmldocs/pretty-formats.txt>`_

    .. versionchanged:: 1.0
        For some searon, the call to @see fn str_to_datetime seemed to cause exception such as::

            File "<frozen importlib._bootstrap>", line 2212, in _find_and_load_unlocked
            File "<frozen importlib._bootstrap>", line 321, in _call_with_frames_removed
            File "<frozen importlib._bootstrap>", line 2254, in _gcd_import
            File "<frozen importlib._bootstrap>", line 2237, in _find_and_load
            File "<frozen importlib._bootstrap>", line 2224, in _find_and_load_unlocked

        when it was used to generate documentation for others modules than pyquickhelper.
        Not using this function helps. The cause still remains obscure.

    """
    if file_detail:
        raise NotImplementedError()

    if path is None:
        path = os.path.normpath(
            os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..", "..")))

    if not commandline:
        try:
            raise NotImplementedError()
        except Exception:
            return get_repo_log(path, file_detail, True)
    else:
        if sys.platform.startswith("win32"):
            cmd = r'"C:\Program Files (x86)\Git\bin\git"'
            cmd += ' log --pretty=format:"<logentry revision=\\"%h\\"><author>%an</author><date>%ci</date><msg>%s</msg><hash>%H</hash></logentry>" ' + \
                path
        else:
            cmd = ['git']
            cmd += ['log',
                    '--pretty=format:<logentry revision="%h"><author>%an</author><date>%ci</date><msg>%s</msg><hash>%H</hash></logentry>', path]

        enc = sys.stdout.encoding if sys.version_info[
            0] != 2 and sys.stdout is not None else "utf8"
        out, err = run_cmd(cmd,
                           wait=True,
                           do_not_log=True,
                           encerror="strict",
                           encoding=enc,
                           change_path=os.path.split(
                               path)[0] if os.path.isfile(path) else path,
                           shell=sys.platform.startswith("win32"),
                           preprocess=False)

        if len(err) > 0:
            fLOG("problem with file ", path, err)
            raise Exception(
                err + "\nCMD:\n" + cmd + "\nOUT:\n" + out + "\nERR:\n" + err + "\nCMD:\n" + cmd)

        master = get_master_location(path, commandline)
        if master.endswith(".git"):
            master = master[:-4]

        if enc != "utf8" and enc is not None:
            by = out.encode(enc)
            out = by.decode("utf8")

        out = out.replace("\n\n", "\n")
        out = "<xml>%s</xml>" % out
        try:
            root = ET.fromstring(out)
        except ET.ParseError as ee:
            raise Exception("unable to parse:\n" + out) from ee

        res = []
        for i in root.iter('logentry'):
            revision = i.attrib['revision'].strip()
            author = i.find("author").text.strip()
            t = i.find("msg").text
            hash = i.find("hash").text
            msg = t.strip() if t is not None else "-"
            sdate = i.find("date").text.strip()
            dt = my_date_conversion(sdate.replace("T", " ").strip("Z "))
            row = [author, revision, dt, msg, hash]
            if master.startswith("http"):
                row.append(master + "/commit/" + hash)
            res.append(row)
        return res


def get_repo_version(path=None, commandline=True, usedate=False, log=False):
    """
    Get the latest check for a specific path or version number based on the date (is usedate is True)
    If usedate is False, it returns a mini hash (a string then)

    @param      path            path to look
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @param      usedate         if True, it uses the date to return a minor version number (1.1.thisone)
    @param      log             if True, returns the output instead of a boolean
    @return                     integer)
    """
    if not usedate:
        last = get_nb_commits(path, commandline)
        return last
    else:
        if path is None:
            path = os.path.normpath(
                os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..", "..")))

        if not commandline:
            try:
                raise NotImplementedError()
            except Exception:
                return get_repo_version(path, True)
        else:
            if sys.platform.startswith("win32"):
                # %H for full commit hash
                cmd = r'"C:\Program Files (x86)\Git\bin\git" log --format="%h---%ci"'
            else:
                cmd = 'git log --format="%h---%ci"'

            if path is not None:
                cmd += " \"%s\"" % path

            out, err = run_cmd(cmd,
                               wait=True,
                               do_not_log=True,
                               encerror="strict",
                               encoding=sys.stdout.encoding if sys.version_info[
                                   0] != 2 and sys.stdout is not None else "utf8",
                               change_path=os.path.split(
                                   path)[0] if os.path.isfile(path) else path,
                               log_error=False,
                               shell=sys.platform.startswith("win32"))

            if len(err) > 0:
                if log:
                    fLOG("problem with file ", path, err)
                if log:
                    return "OUT\n{0}\nERR:{1}\nCMD:\n{2}".format(out, err, cmd)
                else:
                    raise Exception(err)

            lines = out.split("\n")
            lines = [_.split("---") for _ in lines if len(_) > 0]
            temp = lines[0]
            if usedate:
                dt = my_date_conversion(temp[1].replace("T", " ").strip("Z "))
                dt0 = datetime.datetime(dt.year, 1, 1, 0, 0, 0)
                res = "%d" % (dt - dt0).days
            else:
                res = temp[0]

            if len(res) == 0:
                raise Exception(
                    "the command 'git help' should return something")

            return res


def get_master_location(path=None, commandline=True):
    """
    get the master location

    @param      path            path to look
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     integer (check in number)
    """
    if path is None:
        path = os.path.normpath(
            os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..", "..")))

    if not commandline:
        try:
            raise NotImplementedError()
        except Exception:
            return get_repo_version(path, True)
    else:
        if sys.platform.startswith("win32"):
            cmd = r'"C:\Program Files (x86)\Git\bin\git"'
        else:
            cmd = 'git'

        cmd += " config --get remote.origin.url"

        out, err = run_cmd(cmd,
                           wait=True,
                           do_not_log=True,
                           encerror="strict",
                           encoding=sys.stdout.encoding if sys.version_info[
                               0] != 2 and sys.stdout is not None else "utf8",
                           change_path=os.path.split(
                               path)[0] if os.path.isfile(path) else path,
                           log_error=False,
                           shell=sys.platform.startswith("win32"))

        if len(err) > 0:
            fLOG("problem with file ", path, err)
            raise Exception(err)
        lines = out.split("\n")
        lines = [_ for _ in lines if len(_) > 0]
        res = lines[0]

        if len(res) == 0:
            raise Exception("the command 'git help' should return something")

        return res


def get_nb_commits(path=None, commandline=True):
    """
    returns the number of commit

    @param      path            path to look
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     integer
    """
    if path is None:
        path = os.path.normpath(
            os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..", "..")))

    if not commandline:
        try:
            raise NotImplementedError()
        except Exception as e:
            return get_repo_version(path, True)
    else:
        if sys.platform.startswith("win32"):
            # %H for full commit hash
            cmd = r'"C:\Program Files (x86)\Git\bin\git" rev-list HEAD --count'
        else:
            cmd = 'git rev-list HEAD --count'

        if path is not None:
            cmd += " \"%s\"" % path

        out, err = run_cmd(cmd,
                           wait=True,
                           do_not_log=True,
                           encerror="strict",
                           encoding=sys.stdout.encoding if sys.version_info[
                               0] != 2 and sys.stdout is not None else "utf8",
                           change_path=os.path.split(
                               path)[0] if os.path.isfile(path) else path,
                           log_error=False,
                           shell=sys.platform.startswith("win32"))

        if len(err) > 0:
            raise Exception(
                "unable to get commit number from path {0}\nERR:\n{1}\nCMD:\n{2}".format(path, err, cmd))

        lines = out.strip()
        try:
            nb = int(lines)
        except ValueError as e:
            raise ValueError(
                "unable to parse: " + lines + "\nCMD:\n" + cmd) from e
        return nb


def clone(location,
          srv,
          group,
          project,
          username=None,
          password=None):
    """
    clone a repository

    @param      location    location of the clone
    @param      srv         git server
    @param      group       group
    @param      project     project name
    @param      username    username
    @param      password    password
    @return                 output, error

    see `How to provide username and password when run "git clone git@remote.git"? <http://stackoverflow.com/questions/10054318/how-to-provide-username-and-password-when-run-git-clone-gitremote-git>`_

    @example(Clone a git repository)

    @code
    clone(r"local_folder", "github.com", "sdpython", "pyquickhelper")
    @endcode

    @endexample

    .. versionadded:: 0.9
    """
    if username is not None:
        address = "https://{0}:{1}@{2}/{3}/{4}.git".format(username,
                                                           password, srv, group, project)
    else:
        address = "https://{2}/{3}/{4}.git".format(username,
                                                   password, srv, group, project)

    cmd = "git clone " + address + " " + location
    out, err = run_cmd(cmd, wait=True)
    if len(err) > 0 and "Cloning into" not in err:
        raise Exception(
            "unable to clone {0}\nERR:\n{1}\nCMD:\n{2}".format(address, err, cmd))
    return out, err


def rebase(location,
           srv,
           group,
           project,
           username=None,
           password=None):
    """
    run ``git pull -rebase``  on a repository

    @param      location    location of the clone
    @param      srv         git server
    @param      group       group
    @param      project     project name
    @param      username    username
    @param      password    password
    @return                 output, error

    .. versionadded:: 0.9
    """
    if username is not None:
        address = "https://{0}:{1}@{2}/{3}/{4}.git".format(username,
                                                           password, srv, group, project)
    else:
        address = "https://{2}/{3}/{4}.git".format(username,
                                                   password, srv, group, project)

    cwd = os.getcwd()
    os.chdir(location)
    cmd = "git pull --rebase " + address
    out, err = run_cmd(cmd, wait=True)
    os.chdir(cwd)
    if len(err) > 0 and "-> FETCH_HEAD" not in err:
        raise Exception(
            "unable to rebase {0}\nERR:\n{1}\nCMD:\n{2}".format(address, err, cmd))
    return out, err
