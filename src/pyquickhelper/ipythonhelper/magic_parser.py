#-*- coding: utf-8 -*-
"""
@file
@brief Magic command to handle files
"""
import argparse, shlex

from ..loghelper.flog import noLOG

class MagicCommandParser (argparse.ArgumentParser):
    """
    add method ``parse_cmd`` to
    `argparse.ArgumentParser <https://docs.python.org/3.4/library/argparse.html#argumentparser-objects>`_

    .. versionadded:: 0.9
    """

    def parse_cmd(self, line):
        """
        split line using `shlex <https://docs.python.org/3.4/library/shlex.html>`_
        and call `parse_args <https://docs.python.org/3.4/library/argparse.html#argparse.ArgumentParser.parse_args>`_

        @param      line        string
        @return                 list of strings
        """
        args = shlex.split(line, posix=False)
        return self.parse_args(args)

    def eval(self, value, context, fLOG = noLOG):
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

        if "[" in value or "]" in value or "+" in value or "*" in value:
            try:
                res = eval ( value, {}, context)
                return res
            except Exception as e :
                fLOG("unable to interpret: " + str(value), " exception ", str(e))
                return value
        else:
            return value