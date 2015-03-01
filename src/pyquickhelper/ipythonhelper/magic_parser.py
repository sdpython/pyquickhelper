#-*- coding: utf-8 -*-
"""
@file
@brief Magic command to handle files
"""
import argparse
import shlex

from ..loghelper.flog import noLOG


class MagicCommandParser (argparse.ArgumentParser):

    """
    add method ``parse_cmd`` to
    `argparse.ArgumentParser <https://docs.python.org/3.4/library/argparse.html#argumentparser-objects>`_

    .. versionadded:: 0.9
    """

    def __init__(self, *l, **p):
        """
        custom constructor, see `ArgumentParser <https://docs.python.org/3.4/library/argparse.html>`_
        """
        argparse.ArgumentParser.__init__(self, *l, **p)
        self._keep_args = {}

    @staticmethod
    def _private_get_name(*args):
        """
        guesses the name of a parameter knowning the argument
        given to @see me add_argument
        """
        for i, a in enumerate(args):
            if isinstance(a, str):
                if a[0] != "-":
                    return a
                elif a.startswith("--"):
                    return a[2:].replace("-", "_")
        raise KeyError("unable to find parameter name in: " + str(args))

    def add_argument(self, *args, **kwargs):
        """
        overloads the methods, see `ArgumentParser <https://docs.python.org/3.4/library/argparse.html>`_
        """
        super(argparse.ArgumentParser, self).add_argument(*args, **kwargs)
        if args != ('-h', '--help'):
            name = MagicCommandParser._private_get_name(*args)
            self._keep_args[name] = (args, kwargs)

    def has_choices(self, name):
        """
        tells if a parameter has choises

        @param      name        parameter name
        @return                 boolean
        """
        if name not in self._keep_args:
            raise KeyError("unable to find parameter name: {0} in {1}".format(
                name, list(self._keep_args.keys())))
        return "choices" in self._keep_args[name][1]

    def parse_cmd(self, line, context=None, fLOG=noLOG):
        """
        split line using `shlex <https://docs.python.org/3.4/library/shlex.html>`_
        and call `parse_args <https://docs.python.org/3.4/library/argparse.html#argparse.ArgumentParser.parse_args>`_

        @param      line        string
        @param      context     if not None, tries to evaluate expression the command may contain
        @param      fLOG        logging function
        @return                 list of strings
        """
        args = shlex.split(line, posix=False)
        res = self.parse_args(args)

        if context is not None:
            up = {}
            for k, v in res.__dict__.items():
                if self.has_choices(k):
                    up[k] = v
                else:
                    ev = self.eval(v, context=context, fLOG=fLOG)
                    if ev != v:
                        up[k] = ev

            if len(up) > 0:
                for k, v in up.items():
                    res.__dict__[k] = v

        return res

    def eval(self, value, context, fLOG=noLOG):
        """
        Evaluate a string knowing the context,
        it returns *value* if it does not belong to the context
        or if it contains brackets or symbols (+, *),
        if the value cannot be evaluated (with function `eval <https://docs.python.org/3.4/library/functions.html#eval>`_),
        it returns the value value

        @param      value       string
        @param      context     something like ``self.shell.user_ns``
        @return                 *value* or its evaluation
        """
        if value in context:
            return context[value]

        if isinstance(value, str) and (
                "[" in value or "]" in value or "+" in value or "*" in value or
                value.split(".")[0] in context):
            try:
                res = eval(value, {}, context)
                return res
            except Exception as e:
                fLOG(
                    "unable to interpret: " + str(value), " exception ", str(e))
                return value
        else:
            return value
