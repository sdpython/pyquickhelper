
.. blogpost::
    :title: Missing signature for functions
    :keywords: signature, inspect
    :date: 2018-08-03
    :categories: python

    The signature of a function is not always available
    in :epkg:`Python`. The buildin functions
    do not follow the same pattern as functions
    written in :epkg:`Python` but they provide
    a backup plan with the attribute ``__text_signature__``:

    .. runpython::
        :showcode:

        print(open.__text_signature__)

    As a result, ``inspect.signature(open)`` returns a
    non empty result. However, for a function
    defined with `pybind11 <https://github.com/pybind/pybind11/>`_,
    this backup plan is not available:
    `Set the __text_signature__ attribute of callables <https://github.com/pybind/pybind11/issues/945>`_.
    That's why the class
    :class:`AutoSignatureDirective <pyquickhelper.sphinxext.sphinx_autosignature.AutoSignatureDirective>`
    may or may not work with regular expressions parsing the documentation
    computed by *pybind11* as a same function could have
    several :epkg:`C++` signature with different types.
