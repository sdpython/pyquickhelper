# -*- coding: utf-8 -*-
"""
@file
@brief Magic parser to parse magic commands
"""
import argparse
import shlex

from ..loghelper.flog import noLOG


class MagicCommandParser(argparse.ArgumentParser):

    """
    Adds method ``parse_cmd`` to :epkg:`*py:argparse:ArgumentParser`.
    """

    def __init__(self, prog, *args, **kwargs):
        """
        custom constructor, see :epkg:`*py:argparse:ArgumentParser`.

        @param  prog        command name
        @param  args        positional arguments
        @param  kwargs      named arguments
        """
        argparse.ArgumentParser.__init__(self, prog=prog, *args, **kwargs)
        self._keep_args = {}

    @staticmethod
    def _private_get_name(*args):
        """
        guesses the name of a parameter knowning the argument
        given to @see me add_argument
        """
        if args == ('-h', '--help'):
            return "help"
        typstr = str
        for a in args:
            if isinstance(a, typstr):
                if a[0] != "-":
                    return a
                elif a.startswith("--"):
                    return a[2:].replace("-", "_")
        raise KeyError(  # pragma: no cover
            "Unable to find parameter name in: " + typstr(args))

    def add_argument(self, *args, **kwargs):
        """
        Overloads the method,
        see `ArgumentParser <https://docs.python.org/3/library/argparse.html>`_.
        Among the parameters:

        * *no_eval*: avoid considering the parameter
          value as a potential variable stored in the notebook workspace.
        * *eval_type*: *type* can be used for parsing and *eval_type*
          is the expected return type.

        The method adds parameter *no_eval* to avoid considering the parameter
        value as a potential variable stored in the notebook workspace.
        """
        name = MagicCommandParser._private_get_name(*args)
        if name in ["help", "-h", "--h"]:
            super(argparse.ArgumentParser, self).add_argument(*args, **kwargs)
        else:
            self._keep_args[name] = (args, kwargs.copy())
            if kwargs.get("no_eval", False):
                del kwargs["no_eval"]
            if kwargs.get("eval_type", None):
                del kwargs["eval_type"]

            super(argparse.ArgumentParser, self).add_argument(*args, **kwargs)

            if args != ('-h', '--help'):
                pass
            elif kwargs.get("action", "") != "help":
                raise ValueError(  # pragma: no cover
                    "Unable to add parameter -h, --help, already taken for help.")

    def has_choices(self, name):
        """
        tells if a parameter has choises

        @param      name        parameter name
        @return                 boolean
        """
        if name not in self._keep_args:
            raise KeyError(
                "Unable to find parameter name: {0} in {1}".format(
                    name, list(self._keep_args.keys())))
        return "choices" in self._keep_args[name][1]

    def has_eval(self, name):
        """
        Tells if a parameter value should be consider as a variable or some python code
        to evaluate.

        @param      name        parameter name
        @return                 boolean
        """
        if name not in self._keep_args:
            raise KeyError(
                "Unable to find parameter name: {0} in {1}".format(
                    name, list(self._keep_args.keys())))
        return "no_eval" not in self._keep_args[name][1]

    def expected_type(self, name):
        """
        Returns the expected type for the parameter.

        @param      name        parameter name
        @return                 type or None of unknown
        """
        if name in self._keep_args:
            return self._keep_args[name][1].get("type", None)
        return None

    def expected_eval_type(self, name):
        """
        return the expected evaluation type for the parameter
        (if the value is interpreter as a python expression)

        @param      name        parameter name
        @return                 type or None of unknown
        """
        if name in self._keep_args:
            return self._keep_args[name][1].get("eval_type", None)
        return None

    def parse_cmd(self, line, context=None, fLOG=noLOG):
        """
        Splits line using `shlex <https://docs.python.org/3/library/shlex.html>`_
        and call `parse_args <https://docs.python.org/3/library/
        argparse.html#argparse.ArgumentParser.parse_args>`_

        @param      line        string
        @param      context     if not None, tries to evaluate expression the command may contain
        @param      fLOG        logging function
        @return                 list of strings

        The function distinguishes between the type used to parse
        the command line (type) and the expected type after the evaluation
        *eval_type*.
        """
        args = shlex.split(line, posix=False)
        res = self.parse_args(args)

        if context is not None:
            up = {}
            for k, v in res.__dict__.items():
                if self.has_choices(k) or not self.has_eval(k):
                    up[k] = v
                else:
                    ev = self.eval(v, context=context, fLOG=fLOG)
                    v_exp = self.expected_eval_type(k)
                    if (ev is not None and (v_exp is None or v_exp == type(ev)) and  # pylint: disable=C0123
                            (type(v) != type(ev) or v != ev)):  # pylint: disable=C0123
                        up[k] = ev
                    elif v_exp is not None and type(v) != v_exp:  # pylint: disable=C0123
                        up[k] = v_exp(v)

            if len(up) > 0:
                for k, v in up.items():
                    res.__dict__[k] = v

        return res

    def eval(self, value, context, fLOG=noLOG):
        """
        Evaluate a string knowing the context,
        it returns *value* if it does not belong to the context
        or if it contains brackets or symbols (+, *),
        if the value cannot be evaluated (with function `eval <https://docs.python.org/3/library/functions.html#eval>`_),
        it returns the value value

        @param      value       string
        @param      context     something like ``self.shell.user_ns``
        @param      fLOG        logging function
        @return                 *value* or its evaluation

        The method interprets variable inside list, tuple or dictionaries (for *value*).
        """
        typstr = str
        if isinstance(value, typstr):
            if value in context:
                return context[value]
        elif isinstance(value, list):
            return [self.eval(v, context, fLOG=fLOG) for v in value]
        elif isinstance(value, tuple):
            return tuple(self.eval(v, context, fLOG=fLOG) for v in value)
        elif isinstance(value, dict):
            return {k: self.eval(v, context, fLOG=fLOG) for k, v in value.items()}

        if isinstance(value, typstr) and (
                "[" in value or "]" in value or "+" in value or "*" in value or
                value.split(".")[0] in context):
            try:
                res = eval(value, {}, context)
                return res
            except Exception as e:  # pragma: no cover
                fLOG(
                    "Unable to interpret {} due to {}.".format(typstr(value), e))
                return value
        return value
