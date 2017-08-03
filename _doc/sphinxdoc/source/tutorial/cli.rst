
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
scenario will grow. This function is used
by function:

.. autosignature:: pyquickhelper.cli.cli_helper.call_cli_function

One command line is defined based on the previous function.
The code of the command line is reduced.

::

    def pyq_sync(fLOG=print, args=None):
        """
        Synchronizer folder ecrypt using function @see fn synchronize_folder.

        @param      fLOG        logging function
        @param      args        to overwrite ``sys.args``

        .. cmdref::
            :title: synchronize two folders
            :cmd: pyquickhelper.cli.pyq_sync_cli:pyq_sync

            Synchronize two folders from the command line.
        """
        try:
            from pyquickhelper.filehelper.synchelper import synchronize_folder
            from pyquickhelper.cli.cli_helper import call_cli_function
        except ImportError:
            folder = os.path.normpath(os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "..", ".."))
            sys.path.append(folder)
            from pyquickhelper.filehelper.synchelper import synchronize_folder
            from pyquickhelper.cli.cli_helper import call_cli_function

        call_cli_function(synchronize_folder, args=args, fLOG=fLOG,
                          skip_parameters=('fLOG', 'operations', 'log1'))
