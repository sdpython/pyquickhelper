
Sphinx Extensions
=================

I use this module to automate most of the process
which compiles and publishes the material for my teachings.
One part of that is a series of
:epkg:`sphinx` extensions. A couple assume
that the module they are documenting follows the same
design as this one, the others are design free.

.. contents::
    :local:

Design Free
-----------

epkg
++++

Same design as pyquickhelper
----------------------------

:mod:`f-fakefunctiontodocumentation`

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
