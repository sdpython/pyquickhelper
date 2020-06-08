"""
@file
@brief Automate the creation of a parser based on a function.
"""
from __future__ import print_function
import argparse
import inspect
import re
from fire.docstrings import parse


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
                raise ValueError(  # pragma: no cover
                    "cleandoc='{0}' is not implemented, only 'epkg'.".format(cleandoc))
        elif callable(cleandoc):
            return cleandoc(doc)
        else:
            raise ValueError(  # pragma: no cover
                "cleandoc is not a string or a callable object but {0}".format(type(cleandoc)))


def create_cli_parser(f, prog=None, layout="sphinx", skip_parameters=('fLOG',),
                      cleandoc=("epkg", "link"), positional=None, cls=None, **options):
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
    @param      positional      positional argument
    @param      cls             parser class, :epkg:`*py:argparse:ArgumentParser`
                                by default
    @return                     :epkg:`*py:argparse:ArgumentParser`

    If an annotation offers mutiple types,
    the first one will be used for the command line.

    .. versionchanged:: 1.9
        Parameters *cls*, *positional* were added.
    """
    # delayed import to speed up import.
    # from ..helpgen import docstring2html
    if "@param" in f.__doc__:
        raise RuntimeError(  # pragma: no cover
            "@param is not allowed in documentation for function '{}' in '{}'.".format(
                f, f.__module__))
    docf = clean_documentation_for_cli(f.__doc__, cleandoc)
    fulldocinfo = parse(docf)
    docparams = {}
    for arg in fulldocinfo.args:
        if arg.name in docparams:
            raise ValueError(  # pragma: no cover
                "Parameter '{0}' is documented twice.\n{1}".format(
                    arg.name, docf))
        docparams[arg.name] = arg.description

    # add arguments with the signature
    signature = inspect.signature(f)
    parameters = signature.parameters
    if cls is None:
        cls = argparse.ArgumentParser
    parser = cls(prog=prog or f.__name__, description=fulldocinfo.summary,
                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    if skip_parameters is None:
        skip_parameters = []
    names = {"h": "already taken"}
    for k, p in parameters.items():
        if k in skip_parameters:
            continue
        if k not in docparams:
            raise ValueError(  # pragma: no cover
                "Parameter '{0}' is not documented in\n{1}.".format(k, docf))
        create_cli_argument(parser, p, docparams[k], names, positional)

    # end
    return parser


def create_cli_argument(parser, param, doc, names, positional):
    """
    Adds an argument for :epkg:`*py:argparse:ArgumentParser`.

    @param      parser      :epkg:`*py:argparse:ArgumentParser`
    @param      param       parameter (from the signature)
    @param      doc         documentation for this parameter
    @param      names       for shortnames
    @param      positional  positional arguments

    If an annotation offers mutiple types,
    the first one will be used for the command line.

    .. versionchanged:: 1.9
        Parameter *positional* was added.
    """
    p = param
    if p.annotation and p.annotation != inspect._empty:
        typ = p.annotation
    else:
        typ = type(p.default)
    if typ is None:
        raise ValueError(  # pragma: no cover
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
        raise ValueError(  # pragma: no cover
            "You should change the name of parameter '{0}'".format(p.name))

    if positional is not None and p.name in positional:
        pnames = [p.name]
    else:
        pnames = ["--" + p.name]
        if shortname:
            pnames.insert(0, "-" + shortname)
            names[shortname] = p.name

    if isinstance(typ, list):
        # Multiple options for the same parameter
        typ = typ[0]

    if typ in (int, str, float, bool):
        default = None if p.default == inspect._empty else p.default
        if typ == bool:
            # see https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
            def typ_(s):
                return s.lower() in {'true', 't', 'yes', '1'}
            typ = typ_
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
        raise NotImplementedError(  # pragma: no cover
            "typ='{0}' not supported (parameter '{1}'). \n"
            "None should be replaced by an empty string \n"
            "as empty value are received that way.".format(typ, p))


def call_cli_function(f, args=None, parser=None, fLOG=print, skip_parameters=('fLOG',),
                      cleandoc=("epkg", 'link'), prog=None, **options):
    """
    Calls a function *f* given parsed arguments.

    @param      f               function to call
    @param      args            arguments to parse (if None, it considers sys.argv)
    @param      parser          parser (can be None, in that case, @see fn create_cli_parser
                                is called)
    @param      fLOG            logging function
    @param      skip_parameters see @see fn create_cli_parser
    @param      cleandoc        cleans the documentation before converting it into text,
                                @see fn clean_documentation_for_cli
    @param      prog            to give the parser a different name than the function name
    @param      options         additional :epkg:`Sphinx` options
    @return                     the output of the wrapped function

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
        parser = create_cli_parser(f, prog=prog, skip_parameters=skip_parameters,
                                   cleandoc=cleandoc, **options)
    if args is not None and (args == ['--help'] or args == ['-h']):  # pylint: disable=R1714
        fLOG(parser.format_help())
    else:
        try:
            args = parser.parse_args(args=args)
        except SystemExit as e:  # pragma: no cover
            if fLOG:
                fLOG("Unable to parse argument due to '{0}':".format(e))
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
            if res is not None:
                if isinstance(res, str):
                    fLOG(res)
                elif isinstance(res, list):
                    for el in res:
                        fLOG(el)
                elif isinstance(res, dict):
                    for k, v in sorted(res.items()):
                        fLOG("{0}: {1}".format(k, v))
            return res
    return None


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
    return spl[0]


def cli_main_helper(dfct, args, fLOG=print):
    """
    Implements the main commmand line for a module.

    @param      dfct        dictionary ``{ key: fct }``
    @param      args        arguments
    @param      fLOG        logging function
    @return                 the output of the wrapped function

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

    The command line can be replaced by a GUI triggered
    with the following command line. It relies on module
    :epkg`tkinterquickhelper`. See @see fn call_gui_function.

    ::

        python -u -m <module> --GUI
    """
    if fLOG is None:
        raise ValueError("fLOG must be defined.")  # pragma: no cover
    first = None
    for _, v in dfct.items():
        first = v
        break
    if not first:
        raise ValueError("dictionary must not be empty.")  # pragma: no cover

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
        return None
    else:
        cmd = args[0]
        cp = args.copy()
        del cp[0]
        if cmd in dfct:
            fct = dfct[cmd]
            sig = inspect.signature(fct)
            if 'args' not in sig.parameters or 'fLOG' not in sig.parameters:
                return call_cli_function(fct, prog=cmd, args=cp, fLOG=fLOG,
                                         skip_parameters=('fLOG', ))
            else:
                return fct(args=cp, fLOG=fLOG)
        elif cmd in ('--GUI', '-G', "--GUITEST"):
            return call_gui_function(dfct, fLOG=fLOG, utest=cmd == "--GUITEST")
        else:
            fLOG("Command not found: '{0}'.".format(cmd))
            fLOG("")
            print_available()
            return None


def call_gui_function(dfct, fLOG=print, utest=False):
    """
    Opens a GUI based on :epkg:`tkinter` which allows the
    user to run a command line through a windows.
    The function requires :epkg:`tkinterquickhelper`.

    @param      dfct        dictionary ``{ key: fct }``
    @param      args        arguments
    @param      utest       for unit test purposes,
                            does not start the main loop if True

    This GUI can be triggered with the following command line:

    ::

        python -m <module> --GUI

    If one of your function prints out some information or
    raises an exception, option ``-u`` should be added:

    ::

        python -u -m <module> --GUI
    """
    try:
        import tkinterquickhelper
    except ImportError:  # pragma: no cover
        print("Option --GUI requires module tkinterquickhelper to be installed.")
        tkinterquickhelper = None
    if tkinterquickhelper:
        memo = dfct
        dfct = {}
        for k, v in memo.items():
            sig = inspect.signature(v)
            pars = list(sorted(sig.parameters))
            if pars == ["args", "fLOG"]:
                continue
            dfct[k] = v
        from tkinterquickhelper.funcwin import main_loop_functions
        first = None
        for _, v in dfct.items():
            first = v
            break
        modname = guess_module_name(first)
        win = main_loop_functions(dfct, title="{0} command line".format(modname),
                                  mainloop=not utest)
        return win
    return None
