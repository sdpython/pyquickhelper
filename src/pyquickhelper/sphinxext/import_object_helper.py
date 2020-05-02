# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension which if all parameters are documented.
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
    def stat():
        pass


def import_object(docname, kind, use_init=True, fLOG=None) -> Tuple[object, str]:
    """
    Extracts an object defined by its name including the module name.

    @param      docname     full name of the object
                            (example: ``pyquickhelper.sphinxext.sphinx_docassert_extension.import_object``)
    @param      kind        ``'function'`` or ``'class'`` or ``'kind'``
    @param      use_init    return the constructor instead of the class
    @param      fLOG        logging function
    @return                 tuple(object, name)
    @raises                 :epkg:`*py:RuntimeError` if cannot be imported,
                            :epkg:`*py:TypeError` if it is a method or a property,
                            :epkg:`*py:ValueError` if *kind* is unknown.
    """
    spl = docname.split(".")
    name = spl[-1]
    if kind not in ("method", "property", "staticmethod"):
        modname = ".".join(spl[:-1])
        code = 'from {0} import {1}\nmyfunc = {1}'.format(modname, name)
        codeobj = compile(code, 'conf{0}.py'.format(kind), 'exec')
        if fLOG:
            fLOG("[import_object] modname='{0}' code='{1}'".format(
                modname, code))
    else:
        modname = ".".join(spl[:-2])
        classname = spl[-2]
        code = 'from {0} import {1}\nmyfunc = {1}'.format(modname, classname)
        codeobj = compile(code, 'conf{0}2.py'.format(kind), 'exec')
        if fLOG:
            fLOG("[import_object] modname='{0}' code='{1}' classname='{2}'".format(
                modname, code, classname))

    context = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            exec(codeobj, context, context)
        except Exception as e:
            mes = "Unable to compile and execute '{0}' due to \n{1}\ngiven:\n{2}".format(
                code.replace('\n', '\\n'), e, docname)
            if fLOG:
                fLOG("[import_object] failed due to {0}".format(e))
            raise RuntimeError(mes) from e

    myfunc = context["myfunc"]
    if fLOG:
        fLOG(
            "[import_object] imported '{0}' --> '{1}'".format(docname, str(myfunc)))
    if kind == "function":
        if not inspect.isfunction(myfunc) and 'built-in function' not in str(myfunc) and \
                'built-in method' not in str(myfunc):
            # inspect.isfunction fails for C functions.
            raise TypeError("'{0}' is not a function".format(docname))
        name = spl[-1]
    elif kind == "property":
        if not inspect.isclass(myfunc):
            raise TypeError("'{0}' is not a class".format(docname))
        myfunc = getattr(myfunc, spl[-1])
        if inspect.isfunction(myfunc) or inspect.ismethod(myfunc):
            raise TypeError(
                "'{0}' is not a property - {1}".format(docname, myfunc))
        if (hasattr(_Types.prop, '__class__') and
                myfunc.__class__ is not _Types.prop.__class__):  # pylint: disable=E1101
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
        if not inspect.isfunction(myfunc) and not inspect.ismethod(myfunc) and not name.endswith('__'):
            raise TypeError(
                "'{0}' is not a method - {1}".format(docname, myfunc))
        if isinstance(myfunc, staticmethod):
            raise TypeError(
                "'{0}' is not a method(*) - {1}".format(docname, myfunc))
        if hasattr(myfunc, "__code__") and sys.version_info >= (3, 4):
            if len(myfunc.__code__.co_varnames) == 0:
                raise TypeError(
                    "'{0}' is not a method(**) - {1}".format(docname, myfunc))
            if myfunc.__code__.co_varnames[0] != 'self':
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


def import_any_object(docname, use_init=True, fLOG=None) -> Tuple[object, str, str]:
    """
    Extracts an object defined by its name including the module name.

    :param docname: full name of the object
        (example: ``pyquickhelper.sphinxext.sphinx_docassert_extension.import_object``)
    :param use_init: return the constructor instead of the class
    :param fLOG: logging function
    :returns: tuple(object, name, kind)
    :raises: :epkg:`*py:ImportError` if unable to import

    Kind is among ``'function'`` or ``'class'`` or ``'kind'``.
    """
    myfunc = None
    name = None
    excs = []
    for kind in ("function", "method", "staticmethod", "property", "class"):
        try:
            myfunc, name = import_object(
                docname, kind, use_init=use_init, fLOG=fLOG)
            if fLOG:
                fLOG(
                    "[import_any_object] ok '{0}' for '{1}' - use_unit={2}".format(kind, docname, use_init))
                fLOG("[import_any_object] __doc__={0} __name__={1} __module__={2}".format(
                    hasattr(myfunc, '__doc__'), hasattr(myfunc, '__name__'),
                    hasattr(myfunc, '__module__')))
                fLOG("[import_any_object] name='{0}' - module='{1}'".format(
                    name, getattr(myfunc, '__module__', None)))
            return myfunc, name, kind
        except Exception as e:
            # not this kind
            excs.append((kind, e))
            if fLOG:
                fLOG(
                    "[import_any_object] not '{0}' for '{1}' (use_unit={2})".format(kind, docname, use_init))

    sec = " ### ".join("{0}-{1}-{2}".format(k, type(e), e).replace("\n", " ")
                       for k, e in excs)
    raise ImportError(
        "Unable to import '{0}'. Exceptions met: {1}".format(docname, sec))


def import_path(obj, class_name=None, err_msg=None, fLOG=None):
    """
    Determines the import path which is
    the shortest way to import the function. In case the
    following ``from module.submodule import function``
    works, the import path will be ``module.submodule``.

    :param obj: object
    :param class_name: :epkg:`Python` does not really distinguish between
        static method and functions. If not None, this parameter
        should contain the name of the class which holds the static
        method given in *obj*
    :param err_msg: an error message to display if anything happens
    :param fLOG: logging function
    :returns: import path
    :raises: :epkg:`*py:TypeError` if object is a property,
        :epkg:`*py:RuntimeError` if cannot be imported

    The function does not work for methods or properties.
    It raises an exception or returns irrelevant results.

    .. versionchanged:: 1.8
        Parameter *err_msg* was added.
    """
    try:
        _ = obj.__module__
    except AttributeError:
        # This is a method.
        raise TypeError("obj is a method or a property ({0})".format(obj))

    if class_name is None:
        name = obj.__name__
    else:
        name = class_name
    elements = obj.__module__.split('.')
    found = None
    for i in range(1, len(elements) + 1):
        path = '.'.join(elements[:i])
        code = 'from {0} import {1}'.format(path, name)
        codeobj = compile(code, 'import_path_{0}.py'.format(name), 'exec')
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            context = {}
            try:
                exec(codeobj, context, context)
                found = path
                if fLOG:
                    fLOG("[import_path] succeeds: '{0}'".format(code))
                break
            except Exception:
                if fLOG:
                    fLOG("[import_path] fails: '{0}'".format(code))
                continue

    if found is None:
        raise RuntimeError("Unable to import object '{0}' ({1}). Full path: '{2}'{3}".format(
            name, obj, '.'.join(elements), ("\n-----\n" + err_msg) if err_msg else ''))
    return found
