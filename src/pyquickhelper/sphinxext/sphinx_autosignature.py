# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to describe a function,
inspired from `autofunction <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/autodoc/__init__.py#L1082>`_
and `AutoDirective <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/autodoc/__init__.py#L1480>`_.
"""
import inspect
import re
import sys
import sphinx
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util import logging
from .import_object_helper import import_any_object, import_path


class autosignature_node(nodes.Structural, nodes.Element):

    """
    Defines *autosignature* node.
    """
    pass


def enumerate_extract_signature(doc, max_args=20):
    """
    Looks for substring like the following and clean the signature
    to be able to use function *_signature_fromstr*.

    @param      doc         text to parse
    @param      max_args    maximum number of parameters
    @return                 iterator of found signatures

    ::

        __init__(self: cpyquickhelper.numbers.weighted_number.WeightedDouble,
                 value: float, weight: float=1.0) -> None

    It is limited to 20 parameters.
    """
    el = "((?P<p%d>[*a-zA-Z_][*a-zA-Z_0-9]*) *(?P<a%d>: *[a-zA-Z_][\\[\\]0-9a-zA-Z_.]+)? *(?P<d%d>= *[^ ]+?)?)"
    els = [el % (i, i, i) for i in range(0, max_args)]
    par = els[0] + "?" + "".join(["( *, *" + e + ")?" for e in els[1:]])
    exp = "(?P<name>[a-zA-Z_][0-9a-zA-Z_]*) *[(] *(?P<sig>{0}) *[)]".format(
        par)
    reg = re.compile(exp)
    for func in reg.finditer(doc.replace("\n", " ")):
        yield func


def enumerate_cleaned_signature(doc, max_args=20):
    """
    Removes annotation from a signature extracted with
    @see fn enumerate_extract_signature.

    @param      doc         text to parse
    @param      max_args    maximum number of parameters
    @return                 iterator of found signatures
    """
    for sig in enumerate_extract_signature(doc, max_args=max_args):
        dic = sig.groupdict()
        name = sig["name"]
        args = []
        for i in range(0, max_args):
            p = dic.get('p%d' % i, None)
            if p is None:
                break
            d = dic.get('d%d' % i, None)
            if d is None:
                args.append(p)
            else:
                args.append("%s%s" % (p, d))
        yield "{0}({1})".format(name, ", ".join(args))


class AutoSignatureDirective(Directive):
    """
    This directive displays a shorter signature than
    :epkg:`sphinx.ext.autodoc`. Available options:

    * *nosummary*: do not display a summary (shorten)
    * *annotation*: shows annotation
    * *nolink*: if False, add a link to a full documentation (produced by
      :epkg:`sphinx.ext.autodoc`)
    * *members*: shows members of a class
    * *path*: three options, *full* displays the full path including
      submodules, *name* displays the last name,
      *import* displays the shortest syntax to import it
      (default).
    * *debug*: diplays debug information
    * *syspath*: additional paths to add to ``sys.path`` before importing,
      ';' separated list

    The signature is not always available for builtin functions
    or :epkg:`C++` functions depending on the way to bind them to :epkg:`Python`.
    See `Set the __text_signature__ attribute of callables <https://github.com/pybind/pybind11/issues/945>`_.

    The signature may not be infered by module ``inspect``
    if the function is a compiled C function. In that case,
    the signature must be added to the documentation. It will
    parsed by *autosignature* with by function
    @see fn enumerate_extract_signature with regular expressions.
    """
    required_arguments = 0
    optional_arguments = 0

    final_argument_whitespace = True
    option_spec = {
        'nosummary': directives.unchanged,
        'annotation': directives.unchanged,
        'nolink': directives.unchanged,
        'members': directives.unchanged,
        'path': directives.unchanged,
        'debug': directives.unchanged,
        'syspath': directives.unchanged,
    }

    has_content = True
    autosignature_class = autosignature_node

    def run(self):
        self.filename_set = set()
        # a set of dependent filenames
        self.reporter = self.state.document.reporter
        self.env = self.state.document.settings.env

        opt_summary = 'nosummary' not in self.options
        opt_annotation = 'annotation' in self.options
        opt_link = 'nolink' not in self.options
        opt_members = self.options.get('members', None)
        opt_debug = 'debug' in self.options
        if opt_members in (None, '') and 'members' in self.options:
            opt_members = "all"
        opt_path = self.options.get('path', 'import')
        opt_syspath = self.options.get('syspath', None)

        if opt_debug:
            keep_logged = []

            def keep_logging(*els):
                keep_logged.append(" ".join(str(_) for _ in els))
            logging_function = keep_logging
        else:
            logging_function = None

        try:
            source, lineno = self.reporter.get_source_and_line(self.lineno)
        except AttributeError:  # pragma: no cover
            source = lineno = None

        # object name
        object_name = " ".join(_.strip("\n\r\t ") for _ in self.content)
        if opt_syspath:
            syslength = len(sys.path)
            sys.path.extend(opt_syspath.split(';'))
        try:
            obj, _, kind = import_any_object(
                object_name, use_init=False, fLOG=logging_function)
        except ImportError as e:
            mes = "[autosignature] unable to import '{0}' due to '{1}'".format(
                object_name, e)
            logger = logging.getLogger("autosignature")
            logger.warning(mes)
            if logging_function:
                logging_function(mes)  # pragma: no cover
            if lineno is not None:
                logger.warning(
                    '   File "{0}", line {1}'.format(source, lineno))
            obj = None
            kind = None
        if opt_syspath:
            del sys.path[syslength:]

        if opt_members is not None and kind != "class":  # pragma: no cover
            logger = logging.getLogger("autosignature")
            logger.warning(
                "[autosignature] option members is specified but '{0}' "
                "is not a class (kind='{1}').".format(object_name, kind))
            obj = None

        # build node
        node = self.__class__.autosignature_class(rawsource=object_name,
                                                  source=source, lineno=lineno,
                                                  objectname=object_name)

        if opt_path == 'import':
            if obj is None:
                logger = logging.getLogger("autosignature")
                logger.warning(
                    "[autosignature] object '{0}' cannot be imported.".format(object_name))
                anchor = object_name
            elif kind == "staticmethod":
                cl, fu = object_name.split(".")[-2:]
                pimp = import_path(obj, class_name=cl, fLOG=logging_function)
                anchor = '{0}.{1}.{2}'.format(pimp, cl, fu)
            else:
                pimp = import_path(
                    obj, err_msg="object name: '{0}'".format(object_name))
                anchor = '{0}.{1}'.format(pimp, object_name.split(".")[-1])
        elif opt_path == 'full':
            anchor = object_name
        elif opt_path == 'name':
            anchor = object_name.split(".")[-1]
        else:  # pragma: no cover
            logger = logging.getLogger("autosignature")
            logger.warning(
                "[autosignature] options path is '{0}', it should be in "
                "(import, name, full) for object '{1}'.".format(opt_path, object_name))
            anchor = object_name

        if obj is None:
            if opt_link:
                text = "\n:py:func:`{0} <{1}>`\n\n".format(anchor, object_name)
            else:
                text = "\n``{0}``\n\n".format(anchor)
        else:
            obj_sig = obj.__init__ if kind == "class" else obj
            try:
                signature = inspect.signature(obj_sig)
                parameters = signature.parameters
            except TypeError as e:  # pragma: no cover
                mes = "[autosignature](1) unable to get signature of '{0}' - {1}.".format(
                    object_name, str(e).replace("\n", "\\n"))
                logger = logging.getLogger("autosignature")
                logger.warning(mes)
                if logging_function:
                    logging_function(mes)
                signature = None
                parameters = None
            except ValueError as e:  # pragma: no cover
                # Backup plan, no __text_signature__, this happen
                # when a function was created with pybind11.
                doc = obj_sig.__doc__
                sigs = set(enumerate_cleaned_signature(doc))
                if len(sigs) == 0:
                    mes = "[autosignature](2) unable to get signature of '{0}' - {1}.".format(
                        object_name, str(e).replace("\n", "\\n"))
                    logger = logging.getLogger("autosignature")
                    logger.warning(mes)
                    if logging_function:
                        logging_function(mes)
                    signature = None
                    parameters = None
                elif len(sigs) > 1:
                    mes = "[autosignature](2) too many signatures for '{0}' - {1} - {2}.".format(
                        object_name, str(e).replace("\n", "\\n"), " *** ".join(sigs))
                    logger = logging.getLogger("autosignature")
                    logger.warning(mes)
                    if logging_function:
                        logging_function(mes)
                    signature = None
                    parameters = None
                else:
                    try:
                        signature = inspect._signature_fromstr(
                            inspect.Signature, obj_sig, list(sigs)[0])
                        parameters = signature.parameters
                    except TypeError as e:
                        mes = "[autosignature](3) unable to get signature of '{0}' - {1}.".format(
                            object_name, str(e).replace("\n", "\\n"))
                        logger = logging.getLogger("autosignature")
                        logger.warning(mes)
                        if logging_function:
                            logging_function(mes)
                        signature = None
                        parameters = None

            domkind = {'meth': 'func', 'function': 'func', 'method': 'meth',
                       'class': 'class', 'staticmethod': 'meth',
                       'property': 'meth'}[kind]
            if signature is None:
                if opt_link:
                    text = "\n:py:{2}:`{0} <{1}>`\n\n".format(
                        anchor, object_name, domkind)
                else:
                    text = "\n``{0} {1}``\n\n".format(kind, object_name)
            else:
                signature = self.build_parameters_list(
                    parameters, opt_annotation)
                text = "\n:py:{3}:`{0} <{1}>` ({2})\n\n".format(
                    anchor, object_name, signature, domkind)

        if obj is not None and opt_summary:
            # Documentation.
            doc = obj.__doc__  # if kind != "class" else obj.__class__.__doc__
            if doc is None:  # pragma: no cover
                mes = "[autosignature] docstring empty for '{0}'.".format(
                    object_name)
                logger = logging.getLogger("autosignature")
                logger.warning(mes)
                if logging_function:
                    logging_function(mes)
            else:
                if "type(object_or_name, bases, dict)" in doc:
                    raise TypeError(  # pragma: no cover
                        "issue with {0}\n{1}".format(obj, doc))
                docstring = self.build_summary(doc)
                text += docstring + "\n\n"

        if opt_members is not None and kind == "class":
            docstring = self.build_members(obj, opt_members, object_name,
                                           opt_annotation, opt_summary)
            docstring = "\n".join(
                map(lambda s: "    " + s, docstring.split("\n")))
            text += docstring + "\n\n"

        text_lines = text.split("\n")
        if logging_function:
            text_lines.extend(['    ::', '', '        [debug]', ''])
            text_lines.extend('        ' + li for li in keep_logged)
            text_lines.append('')
        st = StringList(text_lines)
        nested_parse_with_titles(self.state, st, node)
        return [node]

    def build_members(self, obj, members, object_name, annotation, summary):
        """
        Extracts methods of a class and document them.
        """
        if members != "all":
            members = {_.strip() for _ in members.split(",")}
        else:
            members = None
        rows = []
        cl = obj
        methods = inspect.getmembers(cl)
        for name, value in methods:
            if name[0] == "_" or (members is not None and name not in members):
                continue
            if name not in cl.__dict__:
                # Not a method of this class.
                continue  # pragma: no cover
            try:
                signature = inspect.signature(value)
            except TypeError as e:  # pragma: no cover
                logger = logging.getLogger("autosignature")
                logger.warning(
                    "[autosignature](2) unable to get signature of "
                    "'{0}.{1} - {2}'.".format(object_name, name, str(e).replace("\n", "\\n")))
                signature = None
            except ValueError:  # pragma: no cover
                signature = None

            if signature is not None:
                parameters = signature.parameters
            else:
                parameters = []  # pragma: no cover

            if signature is None:
                continue  # pragma: no cover

            signature = self.build_parameters_list(parameters, annotation)
            text = "\n:py:meth:`{0} <{1}.{0}>` ({2})\n\n".format(
                name, object_name, signature)

            if value is not None and summary:
                doc = value.__doc__
                if doc is None:  # pragma: no cover
                    logger = logging.getLogger("autosignature")
                    logger.warning(
                        "[autosignature] docstring empty for '{0}.{1}'.".format(object_name, name))
                else:
                    docstring = self.build_summary(doc)
                    lines = "\n".join(
                        map(lambda s: "    " + s, docstring.split("\n")))
                    text += "\n" + lines + "\n\n"

            rows.append(text)

        return "\n".join(rows)

    def build_summary(self, docstring):
        """
        Extracts the part of the docstring before the parameters.

        @param      docstring       document string
        @return                     string
        """
        lines = docstring.split("\n")
        keep = []
        for line in lines:
            sline = line.strip(" \r\t")
            if sline.startswith(":param") or sline.startswith("@param"):
                break
            if sline.startswith("Parameters"):
                break
            if sline.startswith(":returns:") or sline.startswith(":return:"):
                break  # pragma: no cover
            if sline.startswith(":rtype:") or sline.startswith(":raises:"):
                break  # pragma: no cover
            if sline.startswith(".. ") and "::" in sline:
                break
            if sline == "::":
                break  # pragma: no cover
            if sline.startswith(":githublink:"):
                break  # pragma: no cover
            if sline.startswith("@warning") or sline.startswith(".. warning::"):
                break  # pragma: no cover
            keep.append(line)
        res = "\n".join(keep).rstrip("\n\r\t ")
        if res.endswith(":"):
            res = res[:-1] + "..."  # pragma: no cover
        res = AutoSignatureDirective.reformat(res)
        return res

    def build_parameters_list(self, parameters, annotation):
        """
        Builds the list of parameters.

        @param      parameters      list of `Parameters <https://docs.python.org/3/library/inspect.html#inspect.Parameter>`_
        @param      annotation      add annotation
        @return                     string (RST format)
        """
        pieces = []
        for name, value in parameters.items():
            if len(pieces) > 0:
                pieces.append(", ")
            pieces.append("*{0}*".format(name))
            if annotation and value.annotation is not inspect._empty:
                pieces.append(":{0}".format(value.annotation))
            if value.default is not inspect._empty:
                pieces.append(" = ")
                if isinstance(value.default, str):
                    de = "'{0}'".format(value.default.replace("'", "\\'"))
                else:
                    de = str(value.default)
                pieces.append("`{0}`".format(de))
        return "".join(pieces)

    @staticmethod
    def reformat(text, indent=4):
        """
        Formats the number of spaces in front every line
        to be equal to a specific value.

        @param      text        text to analyse
        @param      indent      specify the expected indentation for the result
        @return                 number
        """
        mins = None
        spl = text.split("\n")
        for line in spl:
            wh = line.strip("\r\t ")
            if len(wh) > 0:
                wh = line.lstrip(" \t")
                m = len(line) - len(wh)
                mins = m if mins is None else min(mins, m)

        if mins is None:
            return text
        dec = indent - mins
        if dec > 0:
            res = []
            ins = " " * dec
            for line in spl:
                wh = line.strip("\r\t ")
                if len(wh) > 0:
                    res.append(ins + line)
                else:
                    res.append(wh)
            text = "\n".join(res)
        elif dec < 0:
            res = []
            dec = -dec
            for line in spl:
                wh = line.strip("\r\t ")
                if len(wh) > 0:
                    res.append(line[dec:])
                else:
                    res.append(wh)
            text = "\n".join(res)
        return text


def visit_autosignature_node(self, node):
    """
    What to do when visiting a node @see cl autosignature_node.
    """
    pass


def depart_autosignature_node(self, node):
    """
    What to do when leaving a node @see cl autosignature_node.
    """
    pass


def setup(app):
    """
    Create a new directive called *autosignature* which
    displays the signature of the function.
    """
    app.add_node(autosignature_node,
                 html=(visit_autosignature_node, depart_autosignature_node),
                 epub=(visit_autosignature_node, depart_autosignature_node),
                 latex=(visit_autosignature_node, depart_autosignature_node),
                 elatex=(visit_autosignature_node, depart_autosignature_node),
                 text=(visit_autosignature_node, depart_autosignature_node),
                 md=(visit_autosignature_node, depart_autosignature_node),
                 rst=(visit_autosignature_node, depart_autosignature_node))

    app.add_directive('autosignature', AutoSignatureDirective)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
