"""
@file
@brief various variables and classes used to produce a Sphinx documentation

"""

import inspect
import os
import copy
import re
import sys
import importlib
from ..pandashelper.tblformat import df2rst
from .helpgen_exceptions import HelpGenException, ImportErrorHelpGen


#: max length for short summaries
_length_truncated_doc = 120


#: template for a module, substring ``__...__`` ought to be replaced
add_file_rst_template = """
__FULLNAME_UNDERLINED__




.. inheritance-diagram:: __FULLNAMENOEXT__


Short summary
+++++++++++++

__DOCUMENTATION__


__CLASSES__

__FUNCTIONS__

__PROPERTIES__

__STATICMETHODS__

__METHODS__

Documentation
+++++++++++++

.. automodule:: __FULLNAMENOEXT__
    :members:
    :special-members: __init__
    :show-inheritance:

__ADDEDMEMBERS__

"""

#: fields to be replaced
add_file_rst_template_cor = {"class": "__CLASSES__",
                             "method": "__METHODS__",
                             "function": "__FUNCTIONS__",
                             "staticmethod": "__STATICMETHODS__",
                             "property": "__PROPERTIES__",
                             }

#: names for python objects
add_file_rst_template_title = {"class": "Classes",
                               "method": "Methods",
                               "function": "Functions",
                               "staticmethod": "Static Methods",
                               "property": "Properties",
                               }

#
# :platform: Unix, Windows
#   :synopsis: Analyze and reanimate dead parrots.
# .. moduleauthor:: xx <x@x>
# .. moduleauthor:: xx <x@x>
#  for autosummary
#   :toctree: __FILENAMENOEXT__/
#


def compute_truncated_documentation(doc, length=_length_truncated_doc,
                                    raise_exception=False):
    """
    Produces a truncated version of a docstring.

    @param      doc                 doc string
    @param      length              approximated length of the truncated docstring
    @param      raise_exception     raises an exception when the result is empty and the input is not
    @return                         truncated doc string
    """
    if len(doc) == 0:
        return doc
    else:
        doc_ = doc

        if "@brief " in doc:
            doc = doc.split("@brief ")
            doc = doc[-1]
        if ":githublink:" in doc:
            doc = doc.split(":githublink:")
            doc = doc[0]

        doc = doc.strip("\n\r\t ").replace("\t", "    ")

        # we stop at the first ...
        lines = [li.rstrip() for li in doc.split("\n")]
        pos = None
        for i, li in enumerate(lines):
            lll = li.lstrip()
            if lll.startswith(".. ") and li.endswith("::"):
                pos = i
                break
            if lll.startswith("* ") or lll.startswith("- "):
                pos = i
                break
        if pos is not None:
            lines = lines[:pos]

        # we filter out other stuff
        def filter_line(line):
            s = line.strip()
            if s.startswith(":title:"):
                return line.replace(":title:", "")
            elif s.startswith(":tag:") or s.startswith(":lid:"):
                return ""
            return line
        doc = "\n".join(filter_line(line) for line in lines)
        doc = doc.replace("\n", " ").replace("\r", "").strip("\n\r\t ")

        for subs in ["@" + "param", "@" + "return", ":param", ":return", ".. ", "::"]:
            if subs in doc:
                doc = doc[:doc.find(subs)].strip("\r\t ")

        if len(doc) >= _length_truncated_doc:
            spl = doc.split(" ")
            doc = ""
            cq, cq2 = 0, 0
            i = 0
            while i < len(spl) and (len(doc) < _length_truncated_doc or cq % 2 != 0 or cq2 % 2 != 0):
                cq += spl[i].count("`")
                cq2 += spl[i].count("``")
                doc += spl[i] + " "
                i += 1
            doc += "..."

        doc = re.sub(' +', ' ', doc)

        if raise_exception and len(doc) == 0:
            raise ValueError(  # pragma: no cover
                "bad format for docstring:\n{}".format(doc_))

        return doc


class ModuleMemberDoc:

    """
    Represents a member in a module.

    See :epkg:`*py:inspect`.

    Attributes:

    * *obj (object)*: object
    * *type (str)*: type
    * *cl (object)*: class it belongs to
    * *name (str)*: name
    * *module (str)*: module name
    * *doc (str)*: documentation
    * *truncdoc (str)*: truncated documentation
    * *owner (object)*: module
    """

    def __init__(self, obj, ty=None, cl=None, name=None, module=None):
        """
        @param      obj     any kind of object
        @param      ty      type (if you want to overwrite what the class will choose),
                            this type is a string (class, method, function)
        @param      cl      if is a method, class it belongs to
        @param      name    name of the object
        @param      module  module name if belongs to
        """
        if module is None:
            raise ValueError("module cannot be null")

        self.owner = module
        self.obj = obj
        self.cl = cl
        if ty is not None:
            self.type = ty
        self.name = name
        self.populate()

        typstr = str

        if self.cl is None and self.type in [
                "method", "staticmethod", "property"]:
            self.cl = self.obj.__class__
        if self.cl is None and self.type in [
                "method", "staticmethod", "property"]:
            raise TypeError(  # pragma: no cover
                "N/a method must have a class (not None): %s" % typstr(self.obj))

    def add_prefix(self, prefix):
        """
        Adds a prefix (for the documentation).
        @param      prefix      string
        """
        self.prefix = prefix

    @property
    def key(self):
        """
        Returns a key to identify it.
        """
        return "%s;%s" % (self.type, self.name)

    def populate(self):
        """
        Extracts some information about an object.
        """
        obj = self.obj
        ty = self.type if "type" in self.__dict__ else None
        typstr = str
        if ty is None:
            if inspect.isclass(obj):
                self.type = "class"
            elif inspect.ismethod(obj):
                self.type = "method"
            elif inspect.isfunction(obj) or "built-in function" in str(obj):
                self.type = "function"
            elif inspect.isgenerator(obj):
                self.type = "generator"
            else:
                raise TypeError(
                    "E/unable to deal with this type: " + typstr(type(obj)))

        if ty == "method":
            if isinstance(obj, staticmethod):
                self.type = "staticmethod"
            elif isinstance(obj, property):
                self.type = "property"
            elif sys.version_info >= (3, 4):
                # should be replaced by something more robust
                if len(obj.__code__.co_varnames) == 0:
                    self.type = "staticmethod"
                elif obj.__code__.co_varnames[0] != 'self':
                    self.type = "staticmethod"

        # module
        try:
            self.module = obj.__module__
            self.name = obj.__name__
        except Exception:
            if self.type in ["property", "staticmethod"]:
                self.module = self.cl.__module__
            else:
                self.module = None
            if self.name is None:
                raise IndexError("Unable to find a name for this object type={0}, self.type={1}, owner='{2}'".format(
                    type(obj), self.type, self.owner))

        # full path for the module
        if self.module is not None:
            self.fullpath = self.module
        else:
            self.fullpath = ""

        # documentation
        if self.type == "staticmethod":
            try:
                self.doc = obj.__func__.__doc__
            except Exception as ie:
                try:
                    self.doc = obj.__doc__
                except Exception as ie2:
                    self.doc = typstr(
                        ie) + " - " + typstr(ie2) + " \n----------\n " + typstr(dir(obj))
        else:
            try:
                self.doc = obj.__doc__
            except Exception as ie:
                self.doc = typstr(ie) + " \n----------\n " + typstr(dir(obj))

        try:
            self.file = self.module.__file__
        except Exception:
            self.file = ""

        # truncated documentation
        if self.doc is not None:
            self.truncdoc = compute_truncated_documentation(self.doc)
        else:
            self.doc = ""
            self.truncdoc = ""

        if self.name is None:
            raise TypeError(  # pragma: no cover
                "S/name is None for object: %s" % typstr(self.obj))

    def __str__(self):
        """
        usual
        """
        return "[key={0},clname={1},type={2},module_name={3},file={4}".format(
            self.key, self.classname, self.type, self.module, self.owner.__file__)

    def rst_link(self, prefix=None, class_in_bracket=True):
        """
        Returns a sphinx link on the object.

        @param      prefix              to correct the path with a prefix
        @param      class_in_bracket    if True, adds the class in bracket for methods and properties
        @return                         a string style, see below

        String style:

        ::

            :%s:`%s <%s>`               or
            :%s:`%s <%s>` (class)
        """
        cor = {"function": "func",
               "method": "meth",
               "staticmethod": "meth",
               "property": "meth"}

        if self.type in ["method", "staticmethod", "property"]:
            path = "%s.%s.%s" % (self.module, self.cl.__name__, self.name)
        else:
            path = "%s.%s" % (self.module, self.name)

        if prefix is not None:
            path = "%s.%s" % (prefix, path)

        if self.type in ["method", "staticmethod",
                         "property"] and class_in_bracket:
            link = ":%s:`%s <%s>` (%s)" % (
                cor.get(self.type, self.type), self.name, path, self.cl.__name__)
        else:
            link = ":%s:`%s <%s>`" % (
                cor.get(self.type, self.type), self.name, path)
        return link

    @property
    def classname(self):
        """
        Returns the class name if the object is a method.

        @return     class object
        """
        if self.type in ["method", "staticmethod", "property"]:
            return self.cl
        else:
            return None

    def __cmp__(self, oth):
        """
        Comparison operators, compares first the first,
        second the name (lower case).

        @param      oth         other object
        @return                 -1, 0 or 1
        """
        if self.type == oth.type:
            ln = self.fullpath + "@@@" + self.name.lower()
            lo = oth.fullpath + "@@@" + oth.name.lower()
            c = -1 if ln < lo else (1 if ln > lo else 0)
            if c == 0 and self.type == "method":
                ln = self.cl.__name__
                lo = self.cl.__name__
                c = -1 if ln < lo else (1 if ln > lo else 0)
            return c
        else:
            return - \
                1 if self.type < oth.type else (
                    1 if self.type > oth.type else 0)

    def __lt__(self, oth):
        """
        Operator ``<``.
        """
        return self.__cmp__(oth) == -1

    def __eq__(self, oth):
        """
        Operator ``==``.
        """
        return self.__cmp__(oth) == 0

    def __gt__(self, oth):
        """
        Operator ``>``.
        """
        return self.__cmp__(oth) == 1


class IndexInformation:

    """
    Keeps some information to index.
    """

    def __init__(self, type, label, name, text, rstfile, fullname):
        """
        @param      type        each type gets an index
        @param      label       label used to index
        @param      name        name to display
        @param      text        text to show as a short description
        @param      rstfile     tells which file the index refers to (rst file)
        @param      fullname    fullname of a file the rst file describes
        """
        self.type = type
        self.label = label
        self.name = name
        self.text = text
        self.fullname = fullname
        self.set_rst_file(rstfile)

    def __str__(self):
        """
        usual
        """
        return "%s -- %s" % (self.label, self.rst_link())

    def set_rst_file(self, rstfile):
        """
        Sets the rst file and checks the label is present in it.

        @param      rstfile        rst file
        """
        self.rstfile = rstfile
        if rstfile is not None:
            self.add_label_if_not_present()

    @property
    def truncdoc(self):
        """
        Returns ``self.text``.
        """
        return self.text.replace("\n", "  ").replace(
            "\t", "").replace("\r", "")

    def add_label_if_not_present(self):
        """
        The function checks the label is present in the original file.
        """
        if self.rstfile is not None:
            with open(self.rstfile, "r", encoding="utf8") as f:
                content = f.read()
            label = ".. _%s:" % self.label
            if label not in content:
                content = "\n%s\n%s" % (label, content)
                with open(self.rstfile, "w", encoding="utf8") as f:
                    f.write(content)

    @staticmethod
    def get_label(existing, suggestion):
        """
        Returns a new label given the existing ones.

        @param  existing    existing labels stored in a dictionary
        @param  suggestion  the suggestion will be chosen if it does not exists, ``suggestion + zzz`` otherwise
        @return             string
        """
        if existing is None:
            raise ValueError(  # pragma: no cover
                "existing must not be None")
        suggestion = suggestion.replace("_", "").replace(".", "")
        while suggestion in existing:
            suggestion += "z"
        return suggestion

    def rst_link(self):
        """
        return a link rst
        @return     rst link
        """
        if self.label.startswith("_"):
            return ":ref:`%s <%s>`" % (self.name, self.label[1:])
        else:
            return ":ref:`%s <%s>`" % (self.name, self.label)


class RstFileHelp:
    """
    Defines what a rst file and what it describes.
    """

    def __init__(self, file, rst, doc):
        """
        @param      file        original filename
        @param      rst         produced rst file
        @param      doc         documentation if any
        """
        self.file = file
        self.rst = rst
        self.doc = doc


def import_module(rootm, filename, log_function, additional_sys_path=None,
                  first_try=True):
    """
    Imports a module using its filename.

    @param      rootm                   root of the module (for relative import)
    @param      filename                file name of the module
    @param      log_function            logging function
    @param      additional_sys_path     additional path to include to ``sys.path`` before
                                        importing a module (will be removed afterwards)
    @param      first_try               first call to the function (to avoid infinite loop)
    @return                             module object, prefix

    The function can also import compiled modules.

    .. warning:: It adds the file path at the first
        position in ``sys.path`` and then deletes it.
    """
    if additional_sys_path is None:
        additional_sys_path = []
    memo = copy.deepcopy(sys.path)
    li = filename.replace("\\", "/")
    sdir = os.path.abspath(os.path.split(li)[0])
    relpath = os.path.relpath(li, rootm).replace("\\", "/")
    if "/" in relpath:
        spl = relpath.split("/")
        fmod = spl[0]  # this is the prefix
        relpath = "/".join(spl[1:])
    else:
        fmod = ""

    # has init
    init_ = os.path.join(sdir, "__init__.py")
    if init_ != filename and not os.path.exists(init_):
        # no init
        return "No __init__.py, unable to import %s" % (filename), fmod

    # we remove every path ending by "src" except if it is found in PYTHONPATH
    pythonpath = os.environ.get("PYTHONPATH", None)
    if pythonpath is not None:
        sep = ";" if sys.platform.startswith("win") else ":"
        pypaths = [os.path.normpath(_)
                   for _ in pythonpath.split(sep) if len(_) > 0]
    else:
        pypaths = []
    rem = []
    for i, p in enumerate(sys.path):
        if (p.endswith("src") and p not in pypaths) or ".zip" in p:
            rem.append(i)
    rem.reverse()
    for r in rem:
        del sys.path[r]

    # Extracts extended extension of the module.
    if li.endswith(".py"):
        cpxx = ".py"
        ext_rem = ".py"
    elif li.endswith(".pyd"):
        cpxx = ".cp%d%d-" % sys.version_info[:2]
        search = li.rfind(cpxx)
        ext_rem = li[search:]
    else:
        cpxx = ".cpython-%d%dm-" % sys.version_info[:2]
        search = li.rfind(cpxx)
        if search == -1:
            cpxx = ".cpython-%d%d-" % sys.version_info[:2]
            search = li.rfind(cpxx)
            if search == -1:
                raise ImportErrorHelpGen(
                    "Unable to guess extension from '{}'.".format(li))
        ext_rem = li[search:]
    if not ext_rem:
        raise ValueError("Unable to guess file extension '{0}'".format(li))
    if ext_rem != ".py":
        log_function("[import_module] found extension='{0}'".format(ext_rem))

    # remove fmod from sys.modules
    if fmod:
        addback = []
        rem = []
        for n, m in sys.modules.items():
            if n.startswith(fmod):
                rem.append(n)
                addback.append((n, m))
    else:
        addback = []
        relpath.replace(ext_rem, "")
        rem = []
        for n, m in sys.modules.items():
            if n.startswith(relpath):
                rem.append(n)
                addback.append((n, m))

    # we remove the modules
    # this line is important to remove all modules
    # from the sources in folder src and not the modified ones
    # in the documentation folder
    for r in rem:
        del sys.modules[r]

    # full path
    if rootm is not None:
        root = rootm
        tl = relpath
        fi = tl.replace(ext_rem, "").replace("/", ".")
        if fmod:
            fi = fmod + "." + fi
        context = None
        if fi.endswith(".__init__"):
            fi = fi[:-len(".__init__")]
    else:
        root = sdir
        tl = os.path.split(li)[1]
        fi = tl.replace(ext_rem, "")
        context = None

    if additional_sys_path is not None and len(additional_sys_path) > 0:
        # there is an issue here due to the confusion in the paths
        # the paths should be removed just after the import
        sys.path.extend(additional_sys_path)

    sys.path.insert(0, root)
    try:
        try:
            mo = importlib.import_module(fi, context)
        except ImportError:  # pragma: no cover
            log_function(
                "[import_module] unable to import module '{0}' fullname '{1}'".format(fi, filename))
            mo_spec = importlib.util.find_spec(fi, context)
            log_function("[import_module] imported spec", mo_spec)
            mo = mo_spec.loader.load_module()
            log_function("[import_module] successful try", mo_spec)

        if not mo.__file__.replace(  # pragma: no cover
                "\\", "/").endswith(filename.replace("\\", "/").strip("./")):
            namem = os.path.splitext(os.path.split(filename)[-1])[0]

            if "src" in sys.path:
                sys.path = [_ for _ in sys.path if _ != "src"]

            if namem in sys.modules:
                del sys.modules[namem]
                # add the context here for relative import
                # use importlib.import_module with the package argument filled
                # mo = __import__ (fi)
                try:
                    mo = importlib.import_module(fi, context)
                except ImportError:
                    mo = importlib.util.find_spec(fi, context)

                if not mo.__file__.replace(
                        "\\", "/").endswith(filename.replace("\\", "/").strip("./")):
                    raise ImportError("the wrong file was imported (2):\nEXP: {0}\nIMP: {1}\nPATHS:\n   - {2}"
                                      .format(filename, mo.__file__, "\n   - ".join(sys.path)))
            else:
                raise ImportError("the wrong file was imported (1):\nEXP: {0}\nIMP: {1}\nPATHS:\n   - {2}"
                                  .format(filename, mo.__file__, "\n   - ".join(sys.path)))

        sys.path = memo
        log_function("[import_module] import '{0}' successfully".format(
            filename), mo.__file__)
        for n, m in addback:
            if n not in sys.modules:
                sys.modules[n] = m
        return mo, fmod

    except ImportError as e:  # pragma: no cover
        exp = re.compile("No module named '(.*)'")
        find = exp.search(str(e))
        if find:
            module = find.groups()[0]
            log_function(
                "[warning] unable to import module " + module + " --- " + str(e).replace("\n", " "))

        log_function("  File \"%s\", line %d" % (__file__, 501))
        log_function("[warning] -- unable to import module (1) ", filename,
                     ",", fi, " in path ", sdir, " Error: ", str(e))
        log_function("    cwd ", os.getcwd())
        log_function("    path", sdir)
        import traceback
        stack = traceback.format_exc()
        log_function("      executable", sys.executable)
        log_function("      version", sys.version_info)
        log_function("      stack:\n", stack)

        message = ["-----", stack, "-----"]
        message.append("      executable: '{0}'".format(sys.executable))
        message.append("      version: '{0}'".format(sys.version_info))
        message.append("      platform: '{0}'".format(sys.platform))
        message.append("      ext_rem='{0}'".format(ext_rem))
        message.append("      fi='{0}'".format(fi))
        message.append("      li='{0}'".format(li))
        message.append("      cpxx='{0}'".format(cpxx))
        message.append("-----")
        for p in sys.path:
            message.append("      path: " + p)
        message.append("-----")
        for p in sorted(sys.modules):
            try:
                m = sys.modules[p].__path__
            except AttributeError:
                m = str(sys.modules[p])
            message.append("      module: {0}={1}".format(p, m))

        sys.path = memo
        for n, m in addback:
            if n not in sys.modules:
                sys.modules[n] = m

        if 'File "<frozen importlib._bootstrap>"' in stack:
            raise ImportErrorHelpGen(
                "frozen importlib._bootstrap is an issue:\n" + "\n".join(message)) from e

        return "Unable(1) to import %s\nError:\n%s" % (filename, str(e)), fmod

    except SystemError as e:  # pragma: no cover
        log_function("[warning] -- unable to import module (2) ", filename,
                     ",", fi, " in path ", sdir, " Error: ", str(e))
        import traceback
        stack = traceback.format_exc()
        log_function("      executable", sys.executable)
        log_function("      version", sys.version_info)
        log_function("      stack:\n", stack)
        sys.path = memo
        for n, m in addback:
            if n not in sys.modules:
                sys.modules[n] = m
        return "unable(2) to import %s\nError:\n%s" % (filename, str(e)), fmod

    except KeyError as e:  # pragma: no cover
        if first_try and "KeyError: 'pip._vendor.urllib3.contrib'" in str(e):
            # Issue with pip 9.0.2
            return import_module(rootm=rootm, filename=filename, log_function=log_function,
                                 additional_sys_path=additional_sys_path,
                                 first_try=False)
        else:
            log_function("[warning] -- unable to import module (4) ", filename,
                         ",", fi, " in path ", sdir, " Error: ", str(e))
            import traceback
            stack = traceback.format_exc()
            log_function("      executable", sys.executable)
            log_function("      version", sys.version_info)
            log_function("      stack:\n", stack)
            sys.path = memo
            for n, m in addback:
                if n not in sys.modules:
                    sys.modules[n] = m
            return "unable(4) to import %s\nError:\n%s" % (filename, str(e)), fmod

    except Exception as e:  # pragma: no cover
        log_function("[warning] -- unable to import module (3) ", filename,
                     ",", fi, " in path ", sdir, " Error: ", str(e))
        import traceback
        stack = traceback.format_exc()
        log_function("      executable", sys.executable)
        log_function("      version", sys.version_info)
        log_function("      stack:\n", stack)
        sys.path = memo
        for n, m in addback:
            if n not in sys.modules:
                sys.modules[n] = m
        return "unable(3) to import %s\nError:\n%s" % (filename, str(e)), fmod


def get_module_objects(mod):
    """
    Gets all the classes from a module.

    @param      mod     module objects
    @return             list of ModuleMemberDoc
    """

    # exp = { "__class__":"",
    #        "__dict__":"",
    #        "__doc__":"",
    #        "__format__":"",
    #        "__reduce__":"",
    #        "__reduce_ex__":"",
    #        "__subclasshook__":"",
    #        "__dict__":"",
    #        "__weakref__":""
    #         }

    cl = []
    for _, obj in inspect.getmembers(mod):
        try:
            stobj = str(obj)
        except RuntimeError:
            # One issue met in werkzeug
            # Working outside of request context.
            stobj = ""
        if inspect.isclass(obj) or \
           inspect.isfunction(obj) or \
           inspect.isgenerator(obj) or \
           inspect.ismethod(obj) or \
           ("built-in function" in stobj and not isinstance(obj, dict)):
            cl.append(ModuleMemberDoc(obj, module=mod))
            if inspect.isclass(obj):
                for n, o in inspect.getmembers(obj):
                    try:
                        ok = ModuleMemberDoc(
                            o, "method", cl=obj, name=n, module=mod)
                        if ok.module is not None:
                            cl.append(ok)
                    except Exception as e:
                        if str(e).startswith("S/"):
                            raise e

    res = []
    for _ in cl:
        try:
            # if _.module != None :
            if _.module == mod.__name__:
                res.append(_)
        except Exception:
            pass

    res.sort()
    return res


def process_var_tag(
        docstring, rst_replace=False, header=None):
    """
    Processes a docstring using tag ``@ var``, and return a list of 2-tuple::

        @ var    filename        file name
        @ var    utf8            decode in utf8?
        @ var    errors          decoding in utf8 can raise some errors

    @param      docstring       string
    @param      rst_replace     if True, replace the var bloc var a rst bloc
    @param      header          header for the table, if None, ``["attribute", "meaning"]``
    @return                     a matrix with two columns or a string if rst_replace is True

    """
    from pandas import DataFrame

    if header is None:
        header = ["attribute", "meaning"]

    reg = re.compile("[@]var +([_a-zA-Z][a-zA-Z0-9_]*?) +((?:(?!@var).)+)")

    indent = len(docstring)
    spl = docstring.split("\n")
    docstring = []
    bigrow = ""
    for line in spl:
        if len(line.strip("\r \t")) == 0:
            docstring.append(bigrow)
            bigrow = ""
        else:
            ind = len(line) - len(line.lstrip(" "))
            indent = min(ind, indent)
            bigrow += line + "\n"
    if len(bigrow) > 0:
        docstring.append(bigrow)

    values = []
    if rst_replace:
        for line in docstring:
            line2 = line.replace("\n", " ")
            if "@var" in line2:
                all = reg.findall(line2)
                val = []
                for a in all:
                    val.append(list(a))
                if len(val) > 0:
                    tbl = DataFrame(columns=header, data=val)
                    rst = df2rst(tbl, list_table=True)
                    if indent > 0:
                        rst = "\n".join((" " * indent) +
                                        _ for _ in rst.split("\n"))
                    values.append(rst)
            else:
                values.append(line)
        return "\n".join(values)
    else:
        for line in docstring:
            line = line.replace("\n", " ")
            if "@var" in line:
                alls = reg.findall(line)
                for a in alls:
                    values.append(a)
        return values


def make_label_index(title, comment):
    """
    Builds a :epkg:`sphinx` label from a string by
    removing any odd characters.

    @param      title       title
    @param      comment     add this string in the exception when it raises one
    @return                 label
    """
    def accept(c):
        if "a" <= c <= "z":
            return c
        if "A" <= c <= "Z":
            return c
        if "0" <= c <= "9":
            return c
        if c in "-_":
            return c
        return ""

    try:
        r = "".join(map(accept, title))
        if len(r) == 0:
            typstr = str
            raise HelpGenException("unable to interpret this title (empty?): {0} (type: {2})\nCOMMENT:\n{1}".format(
                typstr(title), comment, typstr(type(title))))
        return r
    except TypeError as e:  # pragma: no cover
        typstr = str
        raise HelpGenException("unable to interpret this title: {0} (type: {2})\nCOMMENT:\n{1}".format(
            typstr(title), comment, typstr(type(title)))) from e


def process_look_for_tag(tag, title, files):
    """
    Looks for specific information in all files, collect them
    into one single page.

    @param      tag     tag
    @param      title   title of the page
    @param      files   list of files to look for
    @return             a list of tuple (page, content of the page)

    The function is looking for regular expression::

        .. tag(...).
        ...
        .. endtag.

    They can be split into several pages::

        .. tag(page::...).
        ...
        .. endtag.

    If the extracted example contains an image (..image:: ../../), the path
    is fixed too.

    The function parses the files instead of loading the files as a module.
    The function needs to replace ``\\\\`` by ``\\``, it does not takes into
    acount doc string starting with ``r'''``.
    The function calls @see fn remove_some_indent
    with ``backslash=True`` to replace double backslashes
    by simple backslashes.
    """
    def noneempty(a):
        if "___" in a:
            page, b = a.split("___")
            return "_" + page, b.lower(), b
        else:
            return "", a.lower(), a
    repl = "__!LI!NE!__"
    exp = re.compile(
        "[.][.] %s[(](.*?);;(.*?)[)][.](.*?)[.][.] end%s[.]" % (tag, tag))
    exp2 = re.compile(
        "[.][.] %s[(](.*?)[)][.](.*?)[.][.] end%s[.]" % (tag, tag))
    coll = []
    for file in files:
        if file.file is None:
            continue
        if "utils_sphinx_doc.py" in file.file:
            continue
        if file.file.endswith(".py"):
            try:
                with open(file.file, "r", encoding="utf8") as f:
                    content = f.read()
            except Exception:
                with open(file.file, "r") as f:
                    content = f.read()
            content = content.replace("\n", repl)
        else:
            content = "Binary file."

        all = exp.findall(content)
        all2 = exp2.findall(content)
        if len(all2) > len(all):
            raise HelpGenException(
                "an issue was detected in file: " + file.file)

        coll += [noneempty(a) +
                 (fix_image_page_for_root(c.replace(repl, "\n"), file), b) for a, b, c in all]

    coll.sort()
    coll = [(_[0],) + _[2:] for _ in coll]

    pages = set(_[0] for _ in coll)

    pagerows = []

    for page in pages:
        if page == "":
            tit = title
            suf = ""
        else:
            tit = title + ": " + page.strip("_")
            suf = page.replace(" ", "").replace("_", "")
            suf = re.sub(r'([^a-zA-Z0-9_])', "", suf)
            page = re.sub(r'([^a-zA-Z0-9_])', "", page)

        rows = ["""
            .. _l-{0}{3}:

            {1}
            {2}

            .. contents::
                :local:

            """.replace("            ", "").format(tag, tit, "=" * len(tit), suf)]

        not_expected = os.environ.get(
            "USERNAME", os.environ.get("USER", "````````````"))
        if not_expected != "jenkins" and not_expected in rows[0]:
            raise HelpGenException(
                "The title is probably wrong (4): {0}\ntag={1}\ntit={2}\nnot_expected='{3}'".format(rows[0], tag, tit, not_expected))

        for pa, a, b, c in coll:
            pan = re.sub(r'([^a-zA-Z0-9_])', "", pa)
            if page != pan:
                continue
            lindex = make_label_index(a, pan)
            rows.append("")
            rows.append(".. _lm-{0}:".format(lindex))
            rows.append("")
            rows.append(a)
            rows.append("+" * len(a))
            rows.append("")
            rows.append(remove_some_indent(b, backslash=True))
            rows.append("")
            spl = c.split("-")
            d = "file {0}.py".format(spl[1])  # line, spl[2].lstrip("l"))
            rows.append("see :ref:`%s <%s>`" % (d, c))
            rows.append("")

        pagerows.append((page, "\n".join(rows)))
    return pagerows


def fix_image_page_for_root(content, file):
    """
    Looks for images and fix their path as
    if the extract were copied to the root.

    @param      content     extracted content
    @param      file        file where is comes from (unused)
    @return                 content
    """
    rows = content.split("\n")
    for i in range(len(rows)):
        row = rows[i]
        if ".. image::" in row:
            spl = row.split(".. image::")
            img = spl[-1]
            if "../images" in img:
                img = img.lstrip("./ ")
            if len(spl) == 1:
                row = ".. image:: " + img
            else:
                row = spl[0] + ".. image:: " + img
            rows[i] = row
    return "\n".join(rows)


def remove_some_indent(s, backslash=False):
    """
    Brings text to the left.

    @param      s               text
    @param      backslash       if True, replace double backslash by simple backslash
    @return                     text
    """
    rows = s.split("\n")
    mi = len(s)
    for lr in rows:
        ll = lr.lstrip()
        if len(ll) > 0:
            d = len(lr) - len(ll)
            mi = min(d, mi)

    if mi > 0:
        keep = []
        for _ in rows:
            keep.append(_[mi:] if len(_.strip()) > 0 and len(_) > mi else _)
        res = "\n".join(keep)
    else:
        res = s

    if backslash:
        res = res.replace("\\\\", "\\")
    return res


def example_function_latex():
    """
    This function only contains an example with
    latex to check it is working fine.

    .. exref::
        :title: How to display a formula

        We want to check this formula to successfully converted.

        :math:`\\left \\{ \\begin{array}{l} \\min_{x,y} \\left \\{ x^2 + y^2 - xy + y \\right \\}
        \\\\ \\text{sous contrainte} \\; x + 2y = 1 \\end{array}\\right .`

        Brackets and backslashes might be an issue.
    """
    pass
