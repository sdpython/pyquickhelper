# -*- coding: utf-8 -*-
"""
@file
@brief      a node which contains a file or a folder
"""
import os
import re
import datetime
import time
import shutil
import hashlib
import warnings
from ..loghelper.pqh_exception import PQHException
from ..loghelper.flog import noLOG
from ..loghelper.pyrepo_helper import SourceRepository


class FileTreeNode:

    """
    Defines a node for a folder or a tree.
    Example:

    ::

        def example (p1, p2, hash_size = 1024**2*2, svn1 = True, svn2 = False) :
            extout = re.compile (FileTreeNode.build_expression ("dvi bbl blg ilg ind old out pyc pyd " \\
                                        "bak idx obj log aux pdb sbr ncb res idb suo dep " \\
                                        "ogm manifest dsp dsz user ilk bsc exp eps".split ()))
            extfou = re.compile ("(exeinterpreter[/\\\\].*[.]dll)|([/\\\\]upgradereport)|" \\
                                "(thumbs[.]db)|([.]svn)|(temp[_/\\\\].*)")

            def filter (root, path, f, d) :
                root = root.lower ()
                path = path.lower ()
                f    = f.lower ()
                if extout.search (f) :
                    if not d and not f.endswith(".pyc"):
                        print("rejected (o1)", path, f)
                    return False
                fu = os.path.join (path, f)
                if extfou.search (fu) :
                    if not d and not f.endswith(".pyc"):
                        print("rejected (o2)", path, f)
                    return False
                return True

            f1  = p1
            f2  = p2

            node1 = FileTreeNode(f1, filter = filter, repository = svn1)
            node2 = FileTreeNode(f2, filter = filter, repository = svn2)
            print(len(node1), node1.max_date())
            print(len(node2), node2.max_date())

            res = node1.difference(node2, hash_size=hash_size)
            return res

        print(__file__, "synchro", OutputPrint = __name__ == "__main__")
        res = example (p1, p2)
    """

    _default_not_ext = "bbl out pyc log lib ind pdb opt".split()
    _default_out = re.compile("([.]svn)|(hal.*[.]((exe)|(dll)|(so)|(sln)|(vcproj)))" +
                              "|".join(["(.*[.]%s$)" % e for e in _default_not_ext]))

    @staticmethod
    def build_expression(ext):
        """
        Builds a regular expression validating a list of extension.

        @param      ext     list of extension (with no points)
        @return             pattern (string)
        """
        return ".*[.]" + "|".join(["(%s$)" % e for e in ext])

    def __init__(self, root, file=None, filter=None, level=0, parent=None,
                 repository=False, log=False, log1=False, fLOG=noLOG):
        """
        Defines a file, relative to a root.
        @param      root            root (it must exist)
        @param      file            file, if None, fill _children
        @param      filter          function (root, path, f, dir) --> True or False
                                        if this is a string, it will be converted into a
                                        regular expression (using re), and it will
                                        look into subfolders
        @param      level           hierarchy level
        @param      parent          link to the parent
        @param      repository      use SVN or GIT if True
        @param      log             log every explored folder
        @param      log1            intermediate logs (first level)
        @param      fLOG            logging function to use
        """
        if root is None:
            raise ValueError("root cannot be None")
        self._root = root
        self._file = None if file is None else file
        self._children = []
        self._type = None
        self._date = None
        self._size = None
        self._level = level
        self._parent = parent
        self._log = log
        self._log1 = log1
        self.module = None
        self.fLOG = fLOG

        if not os.path.exists(root):
            raise PQHException("path '%s' does not exist" % root)
        if not os.path.isdir(root):
            raise PQHException("path '%s' is not a folder" % root)

        if self._file is not None:
            if not self.exists():
                raise PQHException(
                    "%s does not exist [%s,%s]" % (self.get_fullname(), root, file))

        self._fillstat()
        if self.isdir():
            if isinstance(filter, str):
                # it assumes it is a regular expression instead of a function
                exp = re.compile(filter)

                def fil(root, path, f, dir, e=exp):
                    "local function"
                    return dir or (e.search(f) is not None)

                self._fill(fil, repository=repository)
            else:
                self._fill(filter, repository=repository)

    @property
    def name(self):
        """
        Returns the file name from the root.
        """
        return self._file

    @property
    def root(self):
        """
        Returns the root directory, the one used as a root for a synchronization.
        """
        return self._root

    @property
    def size(self):
        """
        Returns the size.
        """
        return self._size

    @property
    def date(self):
        """
        Returns the modification date.
        """
        return self._date

    @property
    def type(self):
        """
        Returns the file type  (``file`` or ``folder``).
        """
        return self._type

    @property
    def fullname(self):
        """
        Returns the full name.
        """
        return self.get_fullname()

    def hash_md5_readfile(self):
        """
        Computes a hash of a file.

        @return     string
        """
        filename = self.get_fullname()
        f = open(filename, 'rb')
        m = hashlib.md5()
        readBytes = 1024 ** 2  # read 1024 bytes per time
        totalBytes = 0
        while readBytes:
            readString = f.read(readBytes)
            m.update(readString)
            readBytes = len(readString)
            totalBytes += readBytes
        f.close()
        return m.hexdigest()

    def get_content(self, encoding="utf8"):
        """
        Returns the content of a text file.

        @param      encoding        encoding
        @return                     content as a string
        """
        with open(self.fullname, "r", encoding=encoding) as f:
            return f.read()

    def get_fullname(self):
        """
        @return         the full name
        """
        if self._file is None:
            return self._root
        else:
            return os.path.join(self._root, self._file)

    def exists(self):
        """
        say if it does exist or not

        @return     boolean
        """
        return os.path.exists(self.get_fullname())

    def _fillstat(self):
        """
        private: fill _type, _size
        """
        full = self.get_fullname()
        if os.path.isfile(full):
            self._type = "file"
        else:
            self._type = "folder"

        stat = os.stat(self.get_fullname())
        self._size = stat.st_size
        temp = datetime.datetime.utcfromtimestamp(stat.st_mtime)
        self._date = temp

    def isdir(self):
        """
        is it a folder?

        @return     boolean
        """
        return os.path.isdir(self.get_fullname())

    def isfile(self):
        """
        is it a file?

        @return     boolean
        """
        return os.path.isfile(self.get_fullname())

    def __str__(self):
        """
        usual
        """
        line = [self._root] if self._level == 0 else []
        fi = "" if self._file is None else self._file
        fi = os.path.split(fi)[-1]
        if len(fi) > 0:
            line.append("    " * self._level + fi)
        for c in self._children:
            r = str(c)
            line.append(r)
        return "\n".join(line)

    def repo_ls(self, path):
        """
        call ls of an instance of @see cl SourceRepository
        """
        if "_repo_" not in self.__dict__:
            self._repo_ = SourceRepository(True)
        return self._repo_.ls(path)

    def _fill(self, filter, repository):
        """look for subfolders
        @param      filter      boolean function
        @param      repository  use svn or git
        """
        if not self.isdir():
            raise PQHException(
                "unable to look into a file %s full %s" % (self._file, self.get_fullname()))

        if repository:
            opt = "repo_ls"
            full = self.get_fullname()
            fi = "" if self._file is None else self._file
            entry = self.repo_ls(full)
            temp = [os.path.relpath(p.name, full) for p in entry]
            all = []
            for s in temp:
                all.append(s)
        else:
            opt = "listdir"
            full = self.get_fullname()
            fi = "" if self._file is None else self._file
            all = [a for a in os.listdir(full) if a not in [".", ".."]]

        all.sort()
        self._children = []
        for a in all:
            fu = os.path.join(full, a)
            isd = os.path.isdir(fu)
            if self._log and isd:
                self.fLOG("[FileTreeNode], entering", a)
            elif self._log1 and self._level <= 0:
                self.fLOG("[FileTreeNode], entering", a)
            if filter is None or filter(self._root, fi, a, isd):
                try:
                    n = FileTreeNode(self._root, os.path.join(fi, a), filter, level=self._level + 1,
                                     parent=self, repository=repository, log=self._log,
                                     log1=self._log1 or self._log, fLOG=self.fLOG)
                except PQHException as e:
                    if "does not exist" in str(e):
                        self.fLOG(
                            "a folder should exist, but is it is not, it continues [opt=%s]" % opt)
                        self.fLOG(e)
                        continue
                if n.isdir() and len(n._children) == 0:
                    continue
                self._children.append(n)

    def get(self):
        """
        return a dictionary with some values which describe the file

        @return     dict
        """
        res = {"name": "" if self._file is None else self._file,
               "root___": self._root,
               "time": str(self._date),
               "size": self._size,
               "type___": self._type}
        return res

    def __getitem__(self, i):
        """returns the element i
        @param      i       element
        @return             element
        """
        return self._children[i]

    def nb_children(self):
        """
        return the number of children

        @return         int
        """
        return len(self._children)

    def __iter__(self):
        """
        iterator on the element

        @return iterator on all contained files
        """
        yield self
        for c in self._children:
            for t in c:
                yield t

    def max_date(self):
        """return the more recent date
        """
        return max([node._date for node in self])

    def __len__(self):
        """
        Returns the number of elements in this folder and
        in the subfolders.
        """
        n = 0
        for _ in self:
            n += 1
        return n

    def get_dict(self, lower=False):
        """
        Returns a dictionary ``{ self._file : node }``.
        @param      lower       if True, every filename is converted into lower case
        """
        res = {}
        if lower:
            for node in self:
                if node._file is not None:
                    res[node._file.lower()] = node
        else:
            for node in self:
                if node._file is not None:
                    res[node._file] = node
        return res

    def sign(self, node, hash_size):
        """
        Returns ``==``, ``<`` or ``>`` according the dates
        if the size is not too big, if the sign is ``<`` or ``>``,
        applies the hash method.
        """
        if self._date == node._date:
            return "=="
        elif self._date < node._date:
            if self.isdir(
            ) or self._size != node._size or node._size > hash_size:
                return "<"
            else:
                h1 = self.hash_md5_readfile()
                h2 = node.hash_md5_readfile()
                if h1 != h2:
                    return "<"
                else:
                    return "=="
        else:
            if self.isdir(
            ) or self._size != node._size or node._size > hash_size:
                return ">"
            else:
                h1 = self.hash_md5_readfile()
                h2 = node.hash_md5_readfile()
                if h1 != h2:
                    return ">"
                else:
                    return "=="

    def difference(self, node, hash_size=1024 ** 2 * 2, lower=False):
        """
        Returns the differences with another folder.

        @param      node        other node
        @param      hash_size   above this size, it does not compute the hash key
        @param      lower       if True, every filename is converted into lower case
        @return                 list of [ (``?``, self._file, node (in self), node (in node)) ], see below for the choice of ``?``

        The question mark ``?`` means:
            - ``==`` no change
            - ``>``  more recent in self
            - ``<``  more recent in node
            - ``>+`` absent in node
            - ``<+`` absent in self

        """
        ti = time.perf_counter()
        d1 = self.get_dict(lower=lower)
        d2 = node.get_dict(lower=lower)
        res = []
        nb = 0
        for k, v in d1.items():
            ti2 = time.perf_counter()
            if ti2 - ti > 10:
                self.fLOG("FileTreeNode.difference: processed files", nb)
                ti = ti2
            if k not in d2:
                res.append((k, ">+", v, None))
            else:
                res.append((k, v.sign(d2[k], hash_size), v, d2[k]))
            nb += 1

        for k, v in d2.items():
            ti2 = time.perf_counter()
            if ti2 - ti > 10:
                self.fLOG("FileTreeNode.difference: processed files", nb)
                ti = ti2
            if k not in d1:
                res.append((k, "<+", None, v))
            nb += 1

        res.sort()
        zoo = [(v[1], v[0]) + v[2:] for v in res]

        return zoo

    def remove(self):
        """
        Removes the file.
        """
        full = self.get_fullname()
        self.fLOG("removing ", full)
        try:
            os.remove(full)
        except OSError as e:
            self.fLOG(
                "unable to remove ", full, " --- ", str(e).replace("\n", " "))
            self.fLOG("[pyqerror] ", e)

    def copy_to(self, path, exc=True):
        """
        Copies the file to *path*.

        @param      path        path
        @param      exc         catch exception when possible, warning otherwise

        If the new path doe nots exist, it will be created.

        @warning If a file already exists at the new location,
                 it checks the dates. The file is copied only if
                 the new file is older.
        """
        if not os.path.exists(path):
            raise PQHException("this path does not exist: '{0}'".format(path))
        if self.isdir():
            raise PQHException(
                "this node represents a folder " + self.get_fullname())
        full = self.get_fullname()
        temp = os.path.split(self._file)[0]
        dest = os.path.join(path, temp)
        fina = dest  # os.path.split (dest) [0]
        if not os.path.exists(fina):
            self.fLOG("creating directory: ", fina)
            os.makedirs(fina)
        try:
            # if 1 :
            self.fLOG("+ copy ", full, " to ", dest)
            shutil.copy(full, dest)
            cop = os.path.join(dest, os.path.split(full)[1])
            if not os.path.exists(cop):
                raise PQHException("Unable to copy '%s'." % cop)
            st1 = os.stat(full)
            st2 = os.stat(cop)
            t1 = datetime.datetime.utcfromtimestamp(st1.st_mtime)
            t2 = datetime.datetime.utcfromtimestamp(st2.st_mtime)
            if t1 >= t2:
                mes = "t1={0} for file '{1}' >= t2={2} for file '{3}'".format(
                    t1, full, t2, cop)
                if t1 > t2 and exc:
                    raise PQHException(mes)
                warnings.warn(mes, RuntimeWarning)
        except OSError as e:
            # else :
            self.fLOG("unable to copy file ", full, " to ", path)
            self.fLOG("[pyqerror]", e)
