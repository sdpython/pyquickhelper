
.. _l-sphinxextc:

Sphinx Extensions
=================

I use this module to automate most of the process
which compiles and publishes the material for my teachings.
One part of that is a series of
:epkg:`sphinx` extensions. A couple assume
that the module they are documenting follows the same
design as this one, the others are design free. The whole list
is available at
:ref:`List of Sphinx commands added by pyquickhelper <f-sphinxext-pyq>`.

.. contents::
    :local:

Design Free
-----------

:epkg:`Sphinx` implements many
`markups <http://www.sphinx-doc.org/en/stable/markup/index.html#sphinxmarkup>`_.
This module adds a couple of them. Many cheat sheets
(see `cheat sheet 1 <https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html>`_,
`cheat sheet 2 <http://docs.sphinxdocs.com/en/latest/cheatsheet.html>`_,
`Sphinx Memo <http://rest-sphinx-memo.readthedocs.io/en/latest/ReST.html>`_)
can be found on internet.
Most if the time, this extension need a change in the
configuration file *conf.py* before using them to document.

.. _l-sphinx-epkg:

*epkg*: cache references
++++++++++++++++++++++++

Location: :func:`epkg_role <pyquickhelper.sphinxext.sphinxext_epkg_extension.epkg_role>`.

In *conf.py*:

::

    extensions = [ ...
        'pyquickhelper.sphinxext.sphinx_epkg_extension']

    epkg_dictionary = {
        'pandoc': 'http://johnmacfarlane.net/pandoc/',                                       # 1
        'pandas': ('http://pandas.pydata.org/pandas-docs/stable/',                           # 2
            ('http://pandas.pydata.org/pandas-docs/stable/generated/pandas.{0}.html', 1)),   # 3
        }

The variable ``epkg_dictionary`` stores the list of url to display. It can be a simple
string or a list of possibililies with multiple parameters. The three options above can
used like this. The last one allows one parameter separated by ``:``.

.. sidebar:: Code for examples

    ::

        * Option 1: :epkg:`pandoc`
        * Option 2: :epkg:`pandas`,
        * Option 3: :epkg:`pandas:DataFrame`

* Option 1: :epkg:`pandoc`
* Option 2: :epkg:`pandas`,
* Option 3: :epkg:`pandas:DataFrame`

Same design as pyquickhelper
----------------------------

:ref:`f-fakefunctiontodocumentation`

Parameters
++++++++++

Different styles:

:func:`f1 <pyquickhelper.helpgen._fake_function_to_documentation.f1>`:

::

    def f1(a, b):
       """
        Addition 1

        @param      a       parameter a
        @param      b       parameter b
        @return             ``a+b``
        """
        return a + b

:func:`f2 <pyquickhelper.helpgen._fake_function_to_documentation.f2>`:

::

    def f2(a, b):
        """Addition 2
        @param      a       parameter a
        @param      b       parameter b
        @return             ``a+b``"""
        return a + b

:func:`f3 <pyquickhelper.helpgen._fake_function_to_documentation.f3>`:

::

    def f3(a, b):
        """
        Addition 3

        :param a: parameter a
        :param b: parameter a
        :returns: ``a+b``
        """
        return a + b

:func:`f4 <pyquickhelper.helpgen._fake_function_to_documentation.f4>`:

::

    def f4(a, b):
        """Addition 4
        :param a: parameter a
        :param b: parameter a
        :returns: ``a+b``"""
        return a + b

:func:`f5 <pyquickhelper.helpgen._fake_function_to_documentation.f5>`:

::

    def f5(a, b):
        """
        Addition 5

        Parameters
        ----------

        a: parameter a

        b: parameter b

        Returns
        -------
        ``a+b``
        """
        return a + b

:func:`f6 <pyquickhelper.helpgen._fake_function_to_documentation.f6>`:

::

    def f6(a, b):
        """
        Addition 6

        Args:
            a: parameter a
            b: parameter b

        Returns:
            ``a+b``
        """
