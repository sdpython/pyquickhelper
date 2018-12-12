"""
@file
@brief Automate the creation of a parser based on a function.
"""
from __future__ import print_function
import argparse
import inspect
import re
import sys
from docutils import nodes
from ..helpgen import docstring2html


def clean_documentation_for_cli(doc, cleandoc):
    """
    Cleans the documentation before integrating
    into a command line documentation.

    @param      doc         documentation
    @param      cleandoc    a string which tells how to clean,
                            or a function which takes a function and
                            returns a string

    The function removes everything after ``.. cmdref::`` and ``.. cmdreflist``
    as it creates an infinite loop of processus if this command
    is part of the documentation of the command line itself.
    """
    for st in ('.. versionchanged::', '.. versionadded::', '.. cmdref::', '.. cmdreflist::'):
        if st in doc:
            doc = doc.split(st)[0]
    if isinstance(cleandoc, (list, tuple)):
        for cl in cleandoc:
            doc = clean_documentation_for_cli(doc, cl)
        return doc
    else:
        if isinstance(cleandoc, str):
            if cleandoc == 'epkg':
                reg = re.compile('(:epkg:(`[0-9a-zA-Z_:.*]+`))')
                fall = reg.findall(doc)
                for c in fall:
                    doc = doc.replace(c[0], c[1].replace(':', '.'))
                return doc
            elif cleandoc == 'link':
                reg = re.compile('(`(.+?) <.+?>`_)')
                fall = reg.findall(doc)
                for c in fall:
                    doc = doc.replace(c[0], c[1].replace(':', '.'))
                return doc
            else:
                raise ValueError(
                    "cleandoc='{0}' is not implemented, only 'epkg'.".format(cleandoc))
        elif callable(cleandoc):
            return cleandoc(doc)
        else:
            raise ValueError(
                "cleandoc is not a string or a callable object but {0}".format(type(cleandoc)))


def create_cli_parser(f, prog=None, layout="sphinx", skip_parameters=('fLOG',),
                      cleandoc=("epkg", "link"), **options):
    """
    Automatically creates a parser based on a function,
    its signature with annotation and its documentation (assuming
    this documentation is written using :epkg:`Sphinx` syntax).

    @param      f               function
    @param      prog            to give the parser a different name than the function name
    @param      use_sphinx      simple documentation only requires :epkg:`docutils`,
                                richer requires :epkg:`sphinx`
    @param      skip_parameters do not expose these parameters
    @param      cleandoc        cleans the documentation before converting it into text,
                                @see fn clean_documentation_for_cli
    @param      options         additional :epkg:`Sphinx` options
    @return                     :epkg:`*py:argparse:ArgumentParser`

    If an annotation offers mutiple types,
    the first one will be used for the command line.
    """
    docf = clean_documentation_for_cli(f.__doc__, cleandoc)
    doctree = docstring2html(docf, writer="doctree",
                             layout=layout, ret_doctree=True, **options)

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
        "local function"
        for node_list in doctree.traverse(nodes.field_list):
            node_list.clear()

    # create the parser
    fulldoc = docstring2html(docf, writer="rst", layout='sphinx',
                             filter_nodes=clear_node_list, **options)
    fulldoc = fulldoc.replace("``", "`")

    # add arguments with the signature
    signature = inspect.signature(f)
    parameters = signature.parameters
    parser = argparse.ArgumentParser(prog=prog or f.__name__, description=fulldoc,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    if skip_parameters is None:
        skip_parameters = []
    names = {"h": "already taken"}
    for k, p in parameters.items():
        if k in skip_parameters:
            continue
        if k not in docparams:
            raise ValueError(
                "Parameter '{0}' is not documented in\n{1}.".format(k, docf))
        create_cli_argument(parser, p, docparams[k], names)

    # end
    return parser


def create_cli_argument(parser, param, doc, names):
    """
    Adds an argument for :epkg:`*py:argparse:ArgumentParser`.

    @param      parser      :epkg:`*py:argparse:ArgumentParser`
    @param      param       parameter (from the signature)
    @param      doc         documentation for this parameter
    @param      names       for shortnames

    If an annotation offers mutiple types,
    the first one will be used for the command line.
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

    pnames = ["--" + p.name]
    if shortname:
        pnames.insert(0, "-" + shortname)
        names[shortname] = p.name

    if isinstance(typ, list):
        # Multiple options for the same parameter
        typ = typ[0]

    if typ in (int, str, float, bool):
        default = None if p.default == inspect._empty else p.default
        if default is not None:
            parser.add_argument(*pnames, type=typ, help=doc, default=default)
        else:
            parser.add_argument(*pnames, type=typ, help=doc)
    elif typ is None or str(typ) == "<class 'NoneType'>":
        parser.add_argument(*pnames, type=str, help=doc, default="")
    elif str(typ) == "<class 'type'>":
        # Positional argument
        parser.add_argument(*pnames, help=doc)
    else:
        raise NotImplementedError(
            "typ='{0}' not supported (parameter '{1}'). \n"
            "None should be replaced by an empty string \n"
            "as empty value are received that way.".format(typ, p))


def call_cli_function(f, args=None, parser=None, fLOG=print, skip_parameters=('fLOG',),
                      cleandoc=("epkg", 'link'), **options):
    """
    Calls a function *f* given parsed arguments.

    @param      f               function to call
    @param      args            arguments to parse (if None, it considers sys.argv)
    @param      parser          parser (can be None, in that case, @see fn create_cli_parser is called)
    @param      fLOG            logging function
    @param      skip_parameters see @see fn create_cli_parser
    @param      cleandoc        cleans the documentation before converting it into text,
                                @see fn clean_documentation_for_cli
    @param      options         additional :epkg:`Sphinx` options

    This function is used in command line @see fn pyq_sync.
    Its code can can be used as an example.
    The command line can be tested as:

    ::

        class TextMyCommandLine(unittest.TestCase):

            def test_mycommand_line_help(self):
                fLOG(
                    __file__,
                    self._testMethodName,
                    OutputPrint=__name__ == "__main__")

                rows = []

                def flog(*l):
                    rows.append(l)

                mycommand_line(args=['-h'], fLOG=flog)

                r = rows[0][0]
                if not r.startswith("usage: mycommand_line ..."):
                    raise Exception(r)
    """
    if parser is None:
        parser = create_cli_parser(
            f, skip_parameters=skip_parameters, cleandoc=cleandoc, **options)
    if args is not None and (args == ['--help'] or args == ['-h']):  # pylint: disable=R1714
        fLOG(parser.format_help())
    else:
        try:
            args = parser.parse_args(args=args)
        except SystemExit:
            if fLOG:
                fLOG("Unable to parse argument:")
                fLOG("    ", " ".join(args))
                fLOG("")
                fLOG(parser.format_usage())
            args = None

        if args is not None:
            signature = inspect.signature(f)
            parameters = signature.parameters
            kwargs = {}
            has_flog = False
            for k in parameters:
                if k == "fLOG":
                    has_flog = True
                    continue
                if hasattr(args, k):
                    val = getattr(args, k)
                    if val == '':
                        val = None
                    kwargs[k] = val
            if has_flog:
                res = f(fLOG=fLOG, **kwargs)
            else:
                res = f(**kwargs)
            if res is not None and isinstance(res, str):
                fLOG(res)


def guess_module_name(fct):
    """
    Guesses the module name based on a function.

    @param      fct     function
    @return             module name
    """
    mod = fct.__module__
    spl = mod.split('.')
    name = spl[0]
    if name == 'src':
        return spl[1]
    else:
        return spl[0]


def cli_main_helper(dfct, args, fLOG=print):
    """
    Implements the main commmand line for a module.

    @param      dfct        dictionary ``{ key: fct }``
    @param      args        arguments
    @param      fLOG        logging function

    The function makes it quite simple to write a file
    ``__main__.py`` which implements the syntax
    ``python -m <module> <command> <arguments>``.
    Here is an example of implementation based on this
    function:

    ::

        import sys


        def main(args, fLOG=print):
            '''
            Implements ``python -m pyquickhelper <command> <args>``.

            @param      args        command line arguments
            @param      fLOG        logging function
            '''
            try:
                from .pandashelper import df2rst
                from .pycode import clean_files
                from .cli import cli_main_helper
            except ImportError:
                from pyquickhelper.pandashelper import df2rst
                from pyquickhelper.pycode import clean_files
                from pyquickhelper.cli import cli_main_helper

            fcts = dict(df2rst=df2rst, clean_files=clean_files)
            cli_main_helper(fcts, args=args, fLOG=fLOG)


        if __name__ == "__main__":
            main(sys.argv[1:])

    The function takes care of the parsing of the command line by
    leveraging the signature and the documentation of the function
    if its docstring is written in :epkg:`rst` format.
    For example, function @see fn clean_files is automatically wrapped
    with function @see fn call_cli_function. The command
    ``python -m pyquickhelper clean_files --help`` produces
    the following output:

    .. cmdref::
        :title: Clean files
        :cmd: -m pyquickhelper clean_files --help

        The command line cleans files in a folder.
    """
    if fLOG is None:
        raise ValueError("fLOG must be defined.")
    first = None
    for _, v in dfct.items():
        first = v
        break
    if not first:
        raise ValueError("dictionary must not be empty.")

    def print_available():
        maxlen = max(map(len, dfct)) + 3
        fLOG("Available commands:")
        fLOG("")
        for a, fct in sorted(dfct.items()):
            doc = fct.__doc__.strip("\r\n ").split("\n")[0]
            fLOG("    " + a + " " * (maxlen - len(a)) + doc)

    modname = guess_module_name(first)
    if len(args) < 1:
        fLOG("Usage:")
        fLOG("")
        fLOG("    python -m {0} <command>".format(modname))
        fLOG("")
        fLOG("To get help:")
        fLOG("")
        fLOG("    python -m {0} <command> --help".format(modname))
        fLOG("")
        print_available()
    else:
        cmd = args[0]
        if sys.platform.startswith("win"):
            cp = args.copy()
            del cp[0]
        if cmd in dfct:
            fct = dfct[cmd]
            sig = inspect.signature(fct)
            if 'args' not in sig.parameters or 'fLOG' not in sig.parameters:
                call_cli_function(fct, args=cp, fLOG=fLOG,
                                  skip_parameters=('fLOG', ))
            else:
                fct(args=cp, fLOG=fLOG)
        else:
            fLOG("Command not found: '{0}'.".format(cmd))
            fLOG("")
            print_available()
