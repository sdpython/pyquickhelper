
.. _l-clihelpert:

Command lines
=============

.. contents::
    :local:

Automating parser creation
++++++++++++++++++++++++++

Write parsers for a command line is quite annoying
and it is often just wrapping a function. Why not
using the signature and the docstring to create it?

.. autosignature:: pyquickhelper.cli.cli_helper.create_cli_parser

The function is parsing the doctring to extract the documentation
for each parameter. It raises an exception whenever the documentation
list does not correspond to the signature.

.. runpython::
    :showcode:

    from pyquickhelper.cli import create_cli_parser

    def fpars(anint: int, bstring="r", creal: float=None):
        """
        Builds a unique string with the received information.

        :param anint: one integer
        :param bstring: one string
        :param creal: one real
        :return: concatenation
        """
        return "'{0}' - '{1}' - '{2}'".format(anint, bstring, creal)

    pars = create_cli_parser(fpars)
    doc = pars.format_help()
    print(doc)

The function does not handle all the types but the list of supported
scenario will grow.
