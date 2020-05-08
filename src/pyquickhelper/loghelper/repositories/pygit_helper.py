# -*- coding: utf-8 -*-
"""
@file
@brief  Uses git to get version number.
"""

import os
import sys
import datetime
import warnings
import xml.etree.ElementTree as ET
import re
from xml.sax.saxutils import escape

from ..flog import fLOG, run_cmd


class GitException(Exception):
    """
    Exception raised by this module.
    """
    pass


def my_date_conversion(sdate):
    """
    Converts a date into a datetime.

    @param      sdate       string
    @return                 date
    """
    first = sdate.split(" ")[0]
    trois = first.replace(".", "-").replace("/", "-").split("-")
    return datetime.datetime(int(trois[0]), int(trois[1]), int(trois[2]))


def IsRepo(location, commandline=True):
    """
    Says if it a repository :epkg:`GIT`.

    @param      location        (str) location
    @param      commandline     (bool) use commandline or not
    @return                     bool
    """
    if location is None:
        location = os.path.normpath(os.path.abspath(
            os.path.join(os.path.split(__file__)[0], "..", "..", "..", "..")))

    try:
        get_repo_version(location, commandline, log=False)
        return True
    except Exception:
        return False


class RepoFile:

    """
    Mimic a :epkg:`GIT` file.
    """

    def __init__(self, **args):
        """
        @param   args       list of members to add
        """
        for k, v in args.items():
            self.__dict__[k] = v

        if hasattr(self, "name"):
            if '"' in self.name:  # pylint: disable=E0203
                #defa = sys.stdout.encoding if sys.stdout != None else "utf8"
                self.name = self.name.replace('"', "")
                #self.name = self.name.encode(defa).decode("utf-8")
            if "\\303" in self.name or "\\302" in self.name or "\\342" in self.name:
                # don't know yet how to avoid that
                name0 = self.name
                # see http://www.utf8-chartable.de/unicode-utf8-table.pl?utf8=oct
                # far from perfect
                self.name = self.name.replace(r"\302\240", chr(160)) \
                                     .replace(r"\302\246", "¦") \
                                     .replace(r"\302\256", "®") \
                                     .replace(r"\302\251", "©") \
                                     .replace(r"\302\260", "°") \
                                     .replace(r"\302\267", "·") \
                                     .replace(r"\303\203", "Ã") \
                                     .replace(r"\303\207", "Ç") \
                                     .replace(r"\303\211", "e") \
                                     .replace(r"\303\232", "Ú") \
                                     .replace(r"\303\240", "à") \
                                     .replace(r"\303\242", "â") \
                                     .replace(r"\303\244", "ä") \
                                     .replace(r"\303\246", "æ") \
                                     .replace(r"\303\247", chr(231)) \
                                     .replace(r"\303\250", chr(232)) \
                                     .replace(r"\303\251", chr(233)) \
                                     .replace(r"\303\252", "ê") \
                                     .replace(r"\303\253", "ë") \
                                     .replace(r"\303\256", "î") \
                                     .replace(r"\303\257", "ï") \
                                     .replace(r"\303\264", "ô") \
                                     .replace(r"\303\266", "ö") \
                                     .replace(r"\303\273", "û") \
                                     .replace(r"\303\274", "ü") \
                                     .replace(r"a\314\200", "à") \
                                     .replace(r"e\314\201", "é") \
                                     .replace(r"\342\200\231", "’")
                if not os.path.exists(self.name):
                    try:
                        ex = os.path.exists(name0)
                    except ValueError as e:
                        ex = str(e)
                    warnings.warn(
                        "The modification did not work\n'{0}'\nINTO\n'{1}'\n[{2}\nexists: {3}]".format(
                            name0, self.name, [self.name], ex))

    def __str__(self):
        """
        usual
        """
        return self.name


def get_cmd_git():
    """
    Gets the command line used to run :epkg:`git`.

    @return     string
    """
    if sys.platform.startswith("win32"):  # pragma: no cover
        cmd = r'"C:\Program Files\Git\bin\git.exe"'
        if not os.path.exists(cmd):
            cmd = r'"C:\Program Files (x86)\Git\bin\git.exe"'
            if not os.path.exists(cmd):
                # hoping git path is included in environment variable PATH
                cmd = "git"
    else:
        cmd = 'git'
    return cmd


def repo_ls(full, commandline=True):
    """
    Runs ``ls`` on a path.

    @param      full            full path
    @param      commandline use command line instead of pysvn
    @return                     output of client.ls
    """

    if not commandline:  # pragma: no cover
        try:
            raise NotImplementedError()
        except Exception:
            return repo_ls(full, True)
    else:
        cmd = get_cmd_git()
        cmd += " ls-tree -r HEAD \"%s\"" % full
        out, err = run_cmd(cmd,
                           wait=True,
                           encerror="strict",
                           encoding=sys.stdout.encoding if sys.stdout is not None else "utf8",
                           change_path=os.path.split(
                               full)[0] if os.path.isfile(full) else full,
                           shell=sys.platform.startswith("win32"))
        if len(err) > 0:
            raise GitException(  # pragma: no cover
                "Issue with path '{0}'\n[OUT]\n{1}\n[ERR]\n{2}".format(full, out, err))

        res = [RepoFile(name=os.path.join(full, _.strip().split("\t")[-1]))
               for _ in out.split("\n") if len(_) > 0]
        return res


def __get_version_from_version_txt(path):
    """
    Private function, tries to find a file ``version.txt`` which should
    contains the version number (if :epkg:`svn` is not present).

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


_reg_insertion = re.compile("([1-9][0-9]*) insertion")
_reg_deletion = re.compile("([1-9][0-9]*) deletion")
_reg_bytes = re.compile("([1-9][0-9]*) bytes")


def get_file_details(name, path=None, commandline=True):
    """
    Returns information about a file.

    @param      name            name of the file
    @param      path            path to repo
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     list of tuples

    The result is a list of tuple:

    * commit
    * name
    * added
    * inserted
    * bytes
    """
    if not commandline:  # pragma: no cover
        try:
            raise NotImplementedError()
        except Exception:
            return get_file_details(name, path, True)
    else:
        cmd = get_cmd_git()
        if sys.platform.startswith("win"):
            cmd += ' log --stat "' + os.path.join(path, name) + '"'
        else:
            cmd = [cmd, 'log', "--stat", os.path.join(path, name)]

        enc = sys.stdout.encoding if sys.stdout is not None else "utf8"
        out, err = run_cmd(cmd,
                           wait=True,
                           encerror="strict",
                           encoding=enc,
                           change_path=os.path.split(
                               path)[0] if os.path.isfile(path) else path,
                           shell=sys.platform.startswith("win32"),
                           preprocess=False)

        if len(err) > 0:  # pragma: no cover
            mes = "Problem with file '{0}'".format(os.path.join(path, name))
            raise GitException(
                mes + "\n" +
                err + "\nCMD:\n" + cmd + "\nOUT:\n" + out + "\n[giterror]\n" +
                err + "\nCMD:\n" + cmd)

        master = get_master_location(path, commandline)
        if master.endswith(".git"):
            master = master[:-4]

        if enc != "utf8" and enc is not None:
            by = out.encode(enc)
            out = by.decode("utf8")

        # We split into commits.
        commits = []
        current = []
        for line in out.split("\n"):
            if line.startswith("commit"):
                if len(current) > 0:
                    commits.append("\n".join(current))
                current = [line]
            else:
                current.append(line)
        if len(current) > 0:
            commits.append("\n".join(current))

        # We analyze each commit.
        rows = []
        for commit in commits:
            se = _reg_insertion.findall(commit)
            if len(se) > 1:
                raise Exception(  # pragma: no cover
                    "A commit is wrong \n{0}".format(commit))
            inser = int(se[0]) if len(se) == 1 else 0
            de = _reg_deletion.findall(commit)
            if len(de) > 1:
                raise Exception(  # pragma: no cover
                    "A commit is wrong \n{0}".format(commit))
            delet = int(de[0]) if len(de) == 1 else 0
            bi = _reg_bytes.findall(commit)
            if len(bi) > 1:
                raise Exception(  # pragma: no cover
                    "A commit is wrong \n{0}".format(commit))
            bite = int(bi[0]) if len(bi) == 1 else 0
            com = commit.split("\n")[0].split()[1]
            rows.append((com, name.strip(), inser, delet, bite))
        return rows


_reg_stat_net = re.compile("(.+) *[|] +([1-9][0-9]*)")
_reg_stat_bytes = re.compile(
    "(.+) *[|] Bin ([0-9]+) [-][>] ([0-9]+) bytes")


def get_file_details_all(path=None, commandline=True):
    """
    Returns information about all files

    @param      path            path to repo
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     list of tuples

    The result is a list of tuple:

    * commit
    * name
    * net
    * bytes
    """
    if not commandline:  # pragma: no cover
        try:
            raise NotImplementedError()
        except Exception:
            return get_file_details_all(path, True)
    else:
        cmd = get_cmd_git()
        if sys.platform.startswith("win"):
            cmd += ' --no-pager log --stat'
        else:
            cmd = [cmd, '--no-pager', 'log', "--stat"]

        enc = sys.stdout.encoding if sys.stdout is not None else "utf8"
        out, err = run_cmd(cmd,
                           wait=True,
                           encerror="strict",
                           encoding=enc,
                           change_path=os.path.split(
                               path)[0] if os.path.isfile(path) else path,
                           shell=sys.platform.startswith("win32"),
                           preprocess=False)

        if len(err) > 0:  # pragma: no cover
            mes = "Problem with '{0}'".format(path)
            raise GitException(
                mes + "\n" +
                err + "\nCMD:\n" + cmd + "\nOUT:\n" + out + "\n[giterror]\n" +
                err + "\nCMD:\n" + cmd)

        master = get_master_location(path, commandline)
        if master.endswith(".git"):
            master = master[:-4]

        if enc != "utf8" and enc is not None:
            by = out.encode(enc)
            out = by.decode("utf8")

        # We split into commits.
        commits = []
        current = []
        for line in out.split("\n"):
            if line.startswith("commit"):
                if len(current) > 0:
                    commits.append("\n".join(current))
                current = [line]
            else:
                current.append(line)
        if len(current) > 0:
            commits.append("\n".join(current))

        # We analyze each commit.
        rows = []
        for commit in commits:
            com = commit.split("\n")[0].split()[1]
            lines = commit.split("\n")
            for line in lines:
                r1 = _reg_stat_net.search(line)
                if r1:
                    name = r1.groups()[0].strip()
                    net = int(r1.groups()[1])
                    delta = 0
                else:
                    net = 0
                    r2 = _reg_stat_bytes.search(line)
                    if r2:
                        name = r2.groups()[0].strip()
                        fr = int(r2.groups()[1])
                        to = int(r2.groups()[2])
                        delta = to - fr
                    else:
                        continue
                rows.append((com, name, net, delta))
        return rows


def get_repo_log(path=None, file_detail=False, commandline=True, subset=None):
    """
    Gets the latest changes operated on a file in a folder or a subfolder.

    @param      path            path to look
    @param      file_detail     if True, add impacted files
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @param      subset          only provide file details for a subset of files
    @return                     list of changes, each change is a list of tuple (see below)

    The return results is a list of tuple with the following fields:

    - author
    - commit hash [:6]
    - date (datetime)
    - comment$
    - full commit hash
    - link to commit (if the repository is http://...)

    The function use a command line if an error occurred.
    It uses the xml format:

    ::

        <logentry revision="161">
            <author>xavier dupre</author>
            <date>2013-03-23T15:02:50.311828Z</date>
            <msg>pyquickhelper: first version</msg>
            <hash>full commit hash</hash>
        </logentry>

    Add link:

    ::

        https://github.com/sdpython/pyquickhelper/commit/8d5351d1edd4a8997f358be39da80c72b06c2272

    More: `git pretty format <http://opensource.apple.com/source/Git/Git-19/src/git-htmldocs/pretty-formats.txt>`_
    See also `pretty format <https://www.kernel.org/pub/software/scm/git/docs/git-log.html#_pretty_formats>`_ (html).
    To get details about one file and all the commit.

    ::

        git log  --stat -- _unittests/ut_loghelper/data/sample_zip.zip

    For some reason, the call to @see fn str2datetime seemed to cause exception such as::

        File "<frozen importlib._bootstrap>", line 2212, in _find_and_load_unlocked
        File "<frozen importlib._bootstrap>", line 321, in _call_with_frames_removed
        File "<frozen importlib._bootstrap>", line 2254, in _gcd_import
        File "<frozen importlib._bootstrap>", line 2237, in _find_and_load
        File "<frozen importlib._bootstrap>", line 2224, in _find_and_load_unlocked

    when it was used to generate documentation for others modules than *pyquickhelper*.
    Not using this function helps. The cause still remains obscure.
    """
    if file_detail:
        if subset is None:
            res = get_file_details_all(path, commandline=commandline)
            details = {}
            for commit in res:
                com = commit[0]
                if com not in details:
                    details[com] = []
                details[com].append(commit[1:])
        else:
            files = subset
            details = {}
            for i, name in enumerate(files):
                res = get_file_details(name.name if isinstance(name, RepoFile) else name,
                                       path, commandline=commandline)
                for commit in res:
                    com = commit[0]
                    if com not in details:
                        details[com] = []
                    details[com].append(commit[1:])
        logs = get_repo_log(path=path, file_detail=False,
                            commandline=commandline)
        final = []
        for log in logs:
            com = log[4]
            if com not in details:
                continue
            det = details[com]
            for d in det:
                final.append(tuple(log) + d)
        return final

    if path is None:
        path = os.path.normpath(
            os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..", "..")))

    if not commandline:  # pragma: no cover
        try:
            raise NotImplementedError()
        except Exception:
            return get_repo_log(path, file_detail, True)
    else:
        cmd = get_cmd_git()
        if sys.platform.startswith("win"):  # pragma: no cover
            cmd += ' log --pretty=format:"<logentry revision=\\"%h\\">' + \
                   '<author>%an</author><date>%ci</date><hash>%H</hash><msg>%s</msg></logentry>" ' + \
                   path
        else:
            cmd_tmp = '--pretty=format:<logentry revision="%h"><author>%an</author><date>%ci' + \
                      '</date><hash>%H</hash><msg>%s</msg></logentry>'
            cmd = [cmd, 'log', cmd_tmp, path]

        enc = sys.stdout.encoding if sys.stdout is not None else "utf8"
        out, err = run_cmd(cmd, wait=True, encerror="strict", encoding=enc,
                           change_path=os.path.split(
                               path)[0] if os.path.isfile(path) else path,
                           shell=sys.platform.startswith("win32"), preprocess=False)

        if len(err) > 0:  # pragma: no cover
            mes = "Problem with file '{0}'".format(path)
            raise GitException(mes + "\n" +
                               err + "\nCMD:\n" + cmd + "\nOUT:\n" + out +
                               "\n[giterror]\n" + err + "\nCMD:\n" + cmd)

        master = get_master_location(path, commandline)
        if master.endswith(".git"):
            master = master[:-4]

        if enc != "utf8" and enc is not None:
            by = out.encode(enc)
            out = by.decode("utf8")

        out = out.replace("\n\n", "\n")
        out = "<xml>\n%s\n</xml>" % out
        try:
            root = ET.fromstring(out)
        except ET.ParseError:
            # it might be due to character such as << >>
            lines = out.split("\n")
            out = []
            suffix = "</msg></logentry>"
            for line in lines:
                if line.endswith(suffix):
                    pos = line.find("<msg>")
                    if pos == -1:
                        out.append(line)
                        continue
                    begin = line[:pos + 5]
                    body = line[pos + 5:-len(suffix)]
                    msg = escape(body)
                    line = begin + msg + suffix
                out.append(line)
            out = "\n".join(out)
            try:
                root = ET.fromstring(out)
            except ET.ParseError as eee:  # pragma: no cover
                raise GitException(
                    "Unable to parse:\n{0}".format(out)) from eee

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
            else:
                row.append("{0}//{1}".format(master, hash))
            res.append(row)
        return res


def get_repo_version(path=None, commandline=True, usedate=False, log=False):
    """
    Gets the latest check for a specific path or version number
    based on the date (if *usedate* is True).
    If *usedate* is False, it returns a mini hash (a string then).

    @param      path            path to look
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @param      usedate         if True, it uses the date to return a minor version number (1.1.thisone)
    @param      log             if True, returns the output instead of a boolean
    @return                     integer)
    """
    if not usedate:
        last = get_nb_commits(path, commandline)
        return last
    else:  # pragma: no cover
        if path is None:
            path = os.path.normpath(
                os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..", "..")))

        if not commandline:
            try:
                raise NotImplementedError()
            except Exception:
                return get_repo_version(path, True)
        else:
            cmd = get_cmd_git()
            cmd += ' git log --format="%h---%ci"'

            if path is not None:
                cmd += " \"%s\"" % path

            try:
                out, err = run_cmd(cmd, wait=True, encerror="strict",
                                   encoding=sys.stdout.encoding if sys.stdout is not None else "utf8",
                                   change_path=os.path.split(
                                       path)[0] if os.path.isfile(path) else path,
                                   log_error=False, shell=sys.platform.startswith("win32"))
            except Exception as e:
                raise GitException(
                    "Problem with subprocess. Path is '{0}'\n[OUT]\n{1}\n[ERR]\n{2}".format(path, out, err)) from e

            if len(err) > 0:
                if log:
                    fLOG("Problem with file ", path, err)
                if log:
                    return "OUT\n{0}\n[giterror]{1}\nCMD:\n{2}".format(out, err, cmd)
                else:
                    raise GitException(
                        "OUT\n{0}\n[giterror]{1}\nCMD:\n{2}".format(out, err, cmd))

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
                raise GitException(
                    "The command 'git help' should return something.")

            return res


def get_master_location(path=None, commandline=True):
    """
    Gets the remote master location.

    @param      path            path to look
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     integer (check in number)
    """
    if path is None:
        path = os.path.normpath(
            os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..", "..")))

    if not commandline:  # pragma: no cover
        try:
            raise NotImplementedError()
        except Exception:
            return get_master_location(path, True)
    else:
        cmd = get_cmd_git()
        cmd += " config --get remote.origin.url"

        try:
            out, err = run_cmd(cmd, wait=True, encerror="strict",
                               encoding=sys.stdout.encoding if sys.stdout is not None else "utf8",
                               change_path=os.path.split(
                                   path)[0] if os.path.isfile(path) else path,
                               log_error=False, shell=sys.platform.startswith("win32"))
        except Exception as e:  # pragma: no cover
            raise GitException(
                "Problem with subprocess. Path is '{0}'\n[OUT]\n{1}\n[ERR]\n{2}".format(path, out, err)) from e

        if len(err) > 0:
            raise GitException(  # pragma: no cover
                "Problem with path '{0}'\n[OUT]\n{1}\n[ERR]\n{2}".format(path, out, err))
        lines = out.split("\n")
        lines = [_ for _ in lines if len(_) > 0]
        res = lines[0]

        if len(res) == 0:
            raise GitException(  # pragma: no cover
                "The command 'git help' should return something.")

        return res


def get_nb_commits(path=None, commandline=True):
    """
    Returns the number of commit.

    @param      path            path to look
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     integer
    """
    if path is None:
        path = os.path.normpath(
            os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..", "..")))

    if not commandline:  # pragma: no cover
        try:
            raise NotImplementedError()
        except Exception:
            return get_nb_commits(path, True)
    else:
        cmd = get_cmd_git()
        cmd += ' rev-list HEAD --count'

        if path is not None:
            cmd += " \"%s\"" % path

        out, err = run_cmd(cmd,
                           wait=True,
                           encerror="strict",
                           encoding=sys.stdout.encoding if sys.stdout is not None else "utf8",
                           change_path=os.path.split(
                               path)[0] if os.path.isfile(path) else path,
                           log_error=False,
                           shell=sys.platform.startswith("win32"))

        if len(err) > 0:
            raise GitException(  # pragma: no cover
                "Unable to get commit number from path {0}\n[giterror]\n{1}\nCMD:\n{2}".format(path, err, cmd))

        lines = out.strip()
        try:
            nb = int(lines)
        except ValueError as e:
            raise ValueError(  # pragma: no cover
                "unable to parse: " + lines + "\nCMD:\n" + cmd) from e
        return nb


def get_file_last_modification(path, commandline=True):
    """
    Returns the last modification of a file.

    @param      path            path to look
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     integer
    """
    if path is None:
        path = os.path.normpath(
            os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..", "..")))

    if not commandline:  # pragma: no cover
        try:
            raise NotImplementedError()
        except Exception:
            return get_file_last_modification(path, True)
    else:
        cmd = get_cmd_git()
        cmd += ' log -1 --format="%ad" --'
        cmd += " \"%s\"" % path

        out, err = run_cmd(cmd,
                           wait=True,
                           encerror="strict",
                           encoding=sys.stdout.encoding if sys.stdout is not None else "utf8",
                           change_path=os.path.split(
                               path)[0] if os.path.isfile(path) else path,
                           log_error=False,
                           shell=sys.platform.startswith("win32"))

        if len(err) > 0:
            raise GitException(  # pragma: no cover
                "Unable to get commit number from path {0}\n[giterror]\n{1}\nCMD:\n{2}".format(path, err, cmd))

        lines = out.strip("\n\r ")
        return lines


def clone(location, srv, group, project, username=None, password=None, fLOG=None):
    """
    Clones a :epkg:`git` repository.

    @param      location    location of the clone
    @param      srv         git server
    @param      group       group
    @param      project     project name
    @param      username    username
    @param      password    password
    @param      fLOG        logging function
    @return                 output, error

    See `How to provide username and password when run "git clone git@remote.git"?
    <http://stackoverflow.com/questions/10054318/how-to-provide-username-and-password-when-run-git-clone-gitremote-git>`_

    .. exref::
        :title: Clone a git repository

        ::

            clone("local_folder", "github.com", "sdpython", "pyquickhelper")
    """
    if username is not None:
        address = "https://{0}:{1}@{2}/{3}/{4}.git".format(username,
                                                           password, srv, group, project)
    else:
        address = "https://{0}/{1}/{2}.git".format(srv, group, project)

    cmd = get_cmd_git()
    cmd += " clone " + address + " " + location
    out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
    if len(err) > 0 and "Cloning into" not in err and "Clonage dans" not in err:
        raise GitException(  # pragma: no cover
            "Unable to clone {0}\n[giterror]\n{1}\nCMD:\n{2}".format(address, err, cmd))
    return out, err


def rebase(location, srv, group, project, username=None, password=None, fLOG=None):
    """
    Runs ``git pull -rebase``  on a repository.

    @param      location    location of the clone
    @param      srv         git server
    @param      group       group
    @param      project     project name
    @param      username    username
    @param      password    password
    @param      fLOG        logging function
    @return                 output, error
    """
    if username is not None:
        address = "https://{0}:{1}@{2}/{3}/{4}.git".format(username,
                                                           password, srv, group, project)
    else:
        address = "https://{0}/{1}/{2}.git".format(srv, group, project)

    cwd = os.getcwd()
    os.chdir(location)
    cmd = get_cmd_git()
    cmd += " pull --rebase " + address
    out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
    os.chdir(cwd)
    if len(err) > 0 and "-> FETCH_HEAD" not in err:
        raise GitException(  # pragma: no cover
            "Unable to rebase {0}\n[giterror]\n{1}\nCMD:\n{2}".format(address, err, cmd))
    return out, err
