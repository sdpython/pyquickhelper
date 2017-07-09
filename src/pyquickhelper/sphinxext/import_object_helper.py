# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension which if all parameters are documented.

.. versionadded:: 1.5
"""
import inspect
from typing import Tuple
import warnings


def import_object(docname, kind, use_init=True) -> Tuple[object, str]:
    """
    Extract an object defined by its name including the module name.

    @param      docname     full name of the object
                            (example: ``pyquickhelper.sphinxext.sphinx_docassert_extension.import_object``)
    @param      kind        ``'function'`` or ``'class'`` or ``'kind'``
    @param      use_init    return the constructor instead of the class
    @return                 tuple(object, name)
    """
    spl = docname.split(".")
    name = spl[-1]
    context = {}
    if kind != "method":
        modname = ".".join(spl[:-1])
        code = 'from {0} import {1}\nmyfunc = {1}'.format(modname, name)
        codeobj = compile(code, 'conf{0}.py'.format(kind), 'exec')
    else:
        modname = ".".join(spl[:-2])
        classname = spl[-2]
        code = 'from {0} import {1}\nmyfunc = {1}'.format(modname, classname)
        codeobj = compile(code, 'conf{0}2.py'.format(kind), 'exec')

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            exec(codeobj, context, context)
        except Exception as e:
            raise Exception(
                "Unable to compile and execute '{0}' due to \n{1}\ngiven:\n{2}".format(code.replace('\n', '\\n'), e, docname)) from e

    myfunc = context["myfunc"]
    if kind == "function":
        if not inspect.isfunction(myfunc):
            raise TypeError("'{0}' is not a function".format(docname))
        name = spl[-1]
    elif kind == "method":
        if not inspect.isclass(myfunc):
            raise TypeError("'{0}' is not a class".format(docname))
        myfunc = getattr(myfunc, spl[-1])
        if not inspect.isfunction(myfunc) and not inspect.ismethod(myfunc):
            raise TypeError(
                "'{0}' is not a method - {1}".format(docname, myfunc))
        name = spl[-1]
    elif kind == "class":
        if not inspect.isclass(myfunc):
            raise TypeError("'{0}' is not a class".format(docname))
        name = spl[-1]
        myfunc = myfunc.__init__ if use_init else myfunc
    else:
        raise ValueError("Unknwon value for 'kind'")

    return myfunc, name


def import_any_object(docname, use_init=True) -> Tuple[object, str, str]:
    """
    Extract an object defined by its name including the module name.

    :param docname: full name of the object
        (example: ``pyquickhelper.sphinxext.sphinx_docassert_extension.import_object``)
    :param use_init: return the constructor instead of the class
    :returns: tuple(object, name, kind)
    :raises: ImportError if unable to import

    Kind is among ``'function'`` or ``'class'`` or ``'kind'``.
    """
    myfunc = None
    name = None
    excs = []
    for kind in ("function", "method", "class"):
        try:
            myfunc, name = import_object(docname, kind, use_init=use_init)
            return myfunc, name, kind
        except Exception as e:
            # not this kind
            excs.append(e)

    sec = "\n".join("{0}-{1}".format(type(e), e).replace("\n", " ")
                    for e in excs)
    raise ImportError(
        "Unable to import '{0}'. Exceptions met:\n----\n{1}\n----".format(docname, sec))
