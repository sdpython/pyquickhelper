# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension which if all parameters are documented.

.. versionadded:: 1.5
"""
import inspect
from typing import Tuple
import warnings
import sys


class _Types:
    @property
    def prop(self):
        pass

    @staticmethod
    def stat(self):
        pass


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
    if kind not in ("method", "property", "staticmethod"):
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
    elif kind == "property":
        if not inspect.isclass(myfunc):
            raise TypeError("'{0}' is not a class".format(docname))
        myfunc = getattr(myfunc, spl[-1])
        if inspect.isfunction(myfunc) or inspect.ismethod(myfunc):
            raise TypeError(
                "'{0}' is not a property - {1}".format(docname, myfunc))
        if myfunc.__class__ is not _Types.prop.__class__:
            raise TypeError(
                "'{0}' is not a property(*) - {1}".format(docname, myfunc))
        if not isinstance(myfunc, property):
            raise TypeError(
                "'{0}' is not a static property(**) - {1}".format(docname, myfunc))
        name = spl[-1]
    elif kind == "method":
        if not inspect.isclass(myfunc):
            raise TypeError("'{0}' is not a class".format(docname))
        myfunc = getattr(myfunc, spl[-1])
        if not inspect.isfunction(myfunc) and not inspect.ismethod(myfunc):
            raise TypeError(
                "'{0}' is not a method - {1}".format(docname, myfunc))
        if isinstance(myfunc, staticmethod):
            raise TypeError(
                "'{0}' is not a method(*) - {1}".format(docname, myfunc))
        if sys.version_info >= (3, 4):
            if len(myfunc.__code__.co_varnames) == 0:
                raise TypeError(
                    "'{0}' is not a method(**) - {1}".format(docname, myfunc))
            elif myfunc.__code__.co_varnames[0] != 'self':
                raise TypeError(
                    "'{0}' is not a method(***) - {1}".format(docname, myfunc))
        name = spl[-1]
    elif kind == "staticmethod":
        if not inspect.isclass(myfunc):
            raise TypeError("'{0}' is not a class".format(docname))
        myfunc = getattr(myfunc, spl[-1])
        if not inspect.isfunction(myfunc) and not inspect.ismethod(myfunc):
            raise TypeError(
                "'{0}' is not a static method - {1}".format(docname, myfunc))
        if myfunc.__class__ is not _Types.stat.__class__:
            raise TypeError(
                "'{0}' is not a static method(*) - {1}".format(docname, myfunc))
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
    for kind in ("function", "method", "staticmethod", "property", "class"):
        try:
            myfunc, name = import_object(docname, kind, use_init=use_init)
            return myfunc, name, kind
        except Exception as e:
            # not this kind
            excs.append((kind, e))

    sec = "\n".join("{0}-{1}-{2}".format(k, type(e), e).replace("\n", " ")
                    for k, e in excs)
    raise ImportError(
        "Unable to import '{0}'. Exceptions met:\n----\n{1}\n----".format(docname, sec))
