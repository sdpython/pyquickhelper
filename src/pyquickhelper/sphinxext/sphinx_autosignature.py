# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to describe a function,
inspired from `autofunction <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/autodoc/__init__.py#L1082>`_
and `AutoDirective <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/autodoc/__init__.py#L1480>`_.

.. versionadded:: 1.5
"""
import inspect
import sphinx
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util import logging
from .import_object_helper import import_any_object


class autosignature_node(nodes.Structural, nodes.Element):

    """
    defines *autosignature* node
    """
    pass


class AutoSignatureDirective(Directive):
    """
    This directive displays a shorter signature than
    `sphinx.ext.autodoc <http://www.sphinx-doc.org/en/stable/ext/autodoc.html#module-sphinx.ext.autodoc>`_.
    Available options:

    * *nosummary*: do not display a summary (shorten)
    * *annotation*: shows annotation
    * *nolink*: add a link to a full documentation (produced by
      `sphinx.ext.autodoc <http://www.sphinx-doc.org/en/stable/ext/autodoc.html#module-sphinx.ext.autodoc>`_)
    * *members*: shows members of a class
    """
    required_arguments = 0
    optional_arguments = 0

    final_argument_whitespace = True
    option_spec = {
        'nosummary': directives.unchanged,
        'annotation': directives.unchanged,
        'nolink': directives.unchanged,
        'members': directives.unchanged,
    }

    has_content = True
    autosignature_class = autosignature_node

    def run(self):
        # type: () -> List[nodes.Node]
        self.filename_set = set()   # type: Set[unicode]
        # a set of dependent filenames
        self.reporter = self.state.document.reporter
        self.env = self.state.document.settings.env

        opt_summary = 'nosummary' not in self.options
        opt_annotation = 'annotation' in self.options
        opt_link = 'nolink' not in self.options
        opt_members = self.options.get('members', None)
        if opt_members in (None, '') and 'members' in self.options:
            opt_members = "all"

        try:
            source, lineno = self.reporter.get_source_and_line(self.lineno)
        except AttributeError:
            source = lineno = None

        # object name
        object_name = " ".join(_.strip("\n\r\t ") for _ in self.content)
        try:
            obj, name, kind = import_any_object(object_name, use_init=False)
        except ImportError as e:
            logger = logging.getLogger("AutoSignature")
            logger.warning(
                "[AutoSignature] unable to import '{0}'".format(object_name))
            if lineno is not None:
                logger.warning(
                    '   File "{0}", line {1}'.format(source, lineno))
            obj = None
            kind = None

        if opt_members is not None and kind != "class":
            logger = logging.getLogger("autosignature")
            logger.warning(
                "[autosignature] option members is specific but '{0}' is not a class.".format(object_name))
            obj = None

        # build node
        node = self.__class__.autosignature_class(rawsource=object_name,
                                                  source=source, lineno=lineno,
                                                  objectname=object_name)

        if obj is None:
            if opt_link:
                text = "\n:py:func:`{0} <{0}>`\n\n".format(object_name)
            else:
                text = "\n``{0}``\n\n".format(object_name)
        else:
            obj_sig = obj.__init__ if kind == "class" else obj
            try:
                signature = inspect.signature(obj_sig)
                parameters = signature.parameters
            except TypeError as e:
                logger = logging.getLogger("autosignature")
                logger.warning(
                    "[autosignature](1) unable to get signature of '{0}' - {2}.".format(object_name, str(e).replace("\n", "\\n")))
                signature = None
                parameters = None

            if signature is None:
                if opt_link:
                    text = "\n:py:func:`{0} <{0}>`\n\n".format(object_name)
                else:
                    text = "\n``{0}``\n\n".format(object_name)
            else:
                signature = self.build_parameters_list(
                    parameters, opt_annotation)
                text = "\n:py:func:`{0} <{0}>` ({1})\n\n".format(
                    object_name, signature)

        if obj is not None and opt_summary:
            # Documentation.
            doc = obj.__doc__  # if kind != "class" else obj.__class__.__doc__
            if "type(object_or_name, bases, dict)" in doc:
                raise Exception("issue with {0}\n{1}".format(obj, doc))
            if doc is None:
                logger = logging.getLogger("autosignature")
                logger.warning(
                    "[autosignature] docstring empty for '{0}'.".format(object_name))
            else:
                docstring = self.build_summary(doc)
                text += docstring + "\n\n"

        if opt_members is not None and kind == "class":
            docstring = self.build_members(obj, opt_members, object_name,
                                           opt_annotation, opt_summary)
            docstring = "\n".join(
                map(lambda s: "    " + s, docstring.split("\n")))
            text += docstring + "\n\n"

        st = StringList(text.split("\n"))
        nested_parse_with_titles(self.state, st, node)
        return [node]

    def build_members(self, obj, members, object_name, annotation, summary):
        """
        Extract methods of a class and document them.
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
                continue
            try:
                signature = inspect.signature(value)
            except TypeError as e:
                logger = logging.getLogger("autosignature")
                logger.warning(
                    "[autosignature](2) unable to get signature of '{0}.{1} - {2}'.".format(object_name, name, str(e).replace("\n", "\\n")))
                signature = None
            except ValueError:
                signature = None

            if signature is not None:
                parameters = signature.parameters
            else:
                parameters = []

            if signature is None:
                continue

            signature = self.build_parameters_list(parameters, annotation)
            text = "\n:py:meth:`{0} <{1}.{0}>` ({2})\n\n".format(
                name, object_name, signature)

            if value is not None and summary:
                doc = value.__doc__
                if doc is None:
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
        Extract the part of the docstring before the parameters.

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
                break
            if sline.startswith(":rtype:") or sline.startswith(":raises:"):
                break
            if sline.startswith(".. ") and "::" in sline:
                break
            if sline == "::":
                break
            if sline.startswith(":githublink:"):
                break
            if sline.startswith("@warning") or sline.startswith(".. warning::"):
                break
            keep.append(line)
        res = "\n".join(keep).rstrip("\n\r\t ")
        if res.endswith(":"):
            res = res[:-1] + "..."
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
        Format the number of spaces in front every line
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
                 latex=(visit_autosignature_node, depart_autosignature_node),
                 text=(visit_autosignature_node, depart_autosignature_node),
                 rst=(visit_autosignature_node, depart_autosignature_node))

    app.add_directive('autosignature', AutoSignatureDirective)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
