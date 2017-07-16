"""
@file
@brief Automate the creation of a parser based on a function.

.. versionadded:: 1.5
"""
import argparse
import inspect
from docutils import nodes
from ..helpgen import docstring2html


def create_cli_parser(f, prog=None, layout="docutils"):
    """
    Automatically creates a parser based on a function,
    its signature with annotation and its documentation (assuming
    this documentation is written using Sphinx syntax).

    @param      f           function
    @param      prog        to give the parser a different name than the function name
    @param      use_sphinx  simple documentation only requires :epkg:`docutils`,
                            richer requires :epkg:`sphinx`
    @return                 :epkg:`*py:argparse:ArgumentParser`
    """
    docf = f.__doc__
    doctree = docstring2html(f, writer="doctree", layout=layout)

    # documentation
    docparams = {}
    for node_list in doctree.traverse(nodes.field_list):
        for node in node_list.traverse(nodes.field):
            text = list(filter(lambda c: c.astext().startswith(
                "param "), node.traverse(nodes.Text)))
            body = list(node.traverse(nodes.field_body))
            if len(text) == 1 and len(body) == 1:
                text = text[0]
                body = body[0]
                name = text.astext()
                name = name[5:].strip()
                doc = body.astext()
                if name in docparams:
                    raise ValueError(
                        "Parameter '{0}' is documented twice.\n{1}".format(name, docf))
                docparams[name] = doc

    def clear_node_list(doctree):
        for node_list in doctree.traverse(nodes.field_list):
            node_list.clear()

    # create the parser
    fulldoc = docstring2html(f, writer="rst", layout='sphinx',
                             filter_nodes=clear_node_list)

    # add arguments with the signature
    signature = inspect.signature(f)
    parameters = signature.parameters
    parser = argparse.ArgumentParser(prog=prog or f.__name__, description=fulldoc,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    names = {"h": "already taken"}
    for k, p in parameters.items():
        if k not in docparams:
            raise ValueError(
                "Parameter '{0}' is not documented in\n{1}.".format(k, docf))
        create_cli_argument(parser, p, docparams[k], names)

    # end
    return parser


def create_cli_argument(parser, param, doc, names):
    """
    Add an argument for :epkg:`*py:argparse:ArgumentParser`.

    @param      parser      :epkg:`*py:argparse:ArgumentParser`
    @param      param       parameter (from the signature)
    @param      doc         documentation for this parameter
    @param      names       for shortnames
    """
    p = param
    if p.annotation and p.annotation != inspect._empty:
        typ = p.annotation
    else:
        typ = type(p.default)
    if typ is None:
        raise ValueError(
            "Unable to infer type of '{0}' ({1})".format(p.name, p))

    if len(p.name) > 3:
        shortname = p.name[0]
        if shortname in names:
            shortname = p.name[0:2]
            if shortname in names:
                shortname = p.name[0:3]
                if shortname in names:
                    shortname = None
    else:
        shortname = None

    if p.name in names:
        raise ValueError(
            "You should change the name of parameter '{0}'".format(p.name))

    names = ["--" + p.name]
    if shortname:
        names.insert(0, "-" + shortname)

    if typ in (int, str, float, bool):
        default = None if p.default == inspect._empty else p.default
        if default is not None:
            parser.add_argument(*names, type=typ, help=doc, default=default)
        else:
            parser.add_argument(*names, type=typ, help=doc)
    else:
        raise NotImplementedError(
            "typ='{0}' not supported (parameter '{1}')".format(typ, p))
