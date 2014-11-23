#-*- coding: utf-8 -*-
"""
@file
@brief Magic command to handle files
"""
import argparse, shlex

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