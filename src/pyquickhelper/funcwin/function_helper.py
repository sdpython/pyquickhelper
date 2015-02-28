#-*- coding: utf-8 -*-
"""
@file
@brief  Various function needed when using the windows used to ask for parameters
"""
import sys
import re
import inspect
import datetime

from ..loghelper.flog import guess_machine_parameter


def get_function_list(module):
    """
    Extract all functions in a module

    @param      module      a object module
    @return                 the list of function included in a module, dictionary { name, object }
    """
    res = {}
    d = module.__dict__
    for k, v in d.items():
        if isinstance(v, get_function_list.__class__):
            res[k] = v
    return res


def has_unknown_parameters(func):
    """
    Returns True if the function contains a parameter like ``**params``.

    @param      func    function
    @return             True if the function contains something like ``**params``
    """
    de = func.__defaults__
    na = func.__code__.co_varnames
    all = inspect.getargspec(func)
    return len(all) > 2 and all[2] is not None


def extract_function_information(function):
    """
    Extract information about a function

    @warning We assume all parameters receive a default value.

    @param          function        function object
    @return                         dictionary { info : value }

    The returned dictionary will be composed as follows:
        - name:     name of the function
        - nbpar:    number of parameters
        - param:    list of parameters (dictionary) and their default value
        - types:    type of parameters (dictionary), if the default value does not exist,
                    the function will look in the help looking for the following:
                    @code
                      param    name  (type)
                    @endcode
        - help:     documentation of the function
        - helpparam: help associated to each parameters (dictionary),
                     assuming they are described in the documentation using
                     the same format as this docstring
        - module:   module which defines the function
    """
    if function.__doc__ is None:
        raise Exception("the function given to FrameFunction should be documented: help is displayed,"
                        " if you want parameter to be described, use javadoc format to do so: @<tag>  param_name  param_meaning with tag=param")

    res = dict()
    res["name"] = function.__name__
    nbp = function.__code__.co_argcount
    par = function.__code__.co_varnames[:nbp]
    res["nbpar"] = len(par)
    defd = function.__defaults__ if function.__defaults__ != None else []
    dec = len(par) - len(defd)

    typ = {}
    p = {}
    for pos, a in enumerate(par):
        p2 = pos - dec
        if p2 >= 0:
            b = defd[p2]
            typ[a] = b.__class__
        else:
            b = ""
            typ[a] = None
        if not a.startswith("_"):
            p[a] = b

    res["types"] = typ
    res["param"] = p
    res["help"] = function.__doc__

    mod = function.__module__
    mod = sys.modules.get(mod, None)
    res["module"] = mod

    regex = re.compile("@" + "param +([a-zA-Z0-9_]+) +(.+)")
    alls = regex.findall(res["help"])
    p = {}
    for a, b in alls:
        p[a.strip()] = b.strip()
    res["helpparam"] = p

    reg = re.compile(
        "@" + "param +([a-zA-Z_][a-zA-Z_0-9]*?) +[(]([a-zA-Z]+?)[)]")
    alls = reg.findall(res["help"])
    typ = {k: v for k, v in alls}
    for a in res["types"]:
        b = res["types"][a]
        if b is None or b == type(None):
            b = typ.get(a, None)
            if b is not None:
                if "|" in b:
                    e, ee = b.split("|")
                    e = eval(e)
                    ee = eval(ee)
                    res["types"][a] = lambda v, e=e, ee=ee: ee if (
                        len(v) == 0 or v == str(ee)) else e(v)
                elif b == "datetime":
                    res["types"][a] = datetime.datetime
                else:
                    res["types"][a] = eval(b)

    for a, b in res["types"].items():
        if b is None:
            file = res["module"].__file__ if res[
                "module"] is not None else "unknown"
            mes = "no defined type for function %s, parameter %s\n  File \"%s\", line 1" % (
                res["name"], a, file)
            raise TypeError(mes)

    return res


def private_adjust_parameters(param):
    """
    change the value of some parameters when they are NULL
        - user

    changes the parameters inplace.

    @param      param       list of parameters
    """
    res = guess_machine_parameter()
    for k in param:
        if param[k] is None and k.lower() in ["user", "username"]:
            res[k] = res["USERNAME"]


def private_get_function(function_name):
    """
    return the function object from its name, the name
    must contains a dot "." otherwise the function will assume
    it is defined in module @see md default_functions.

    @param      function_name   name of the function
    @return                     object
    """
    if "." in function_name:
        module = function_name.split(".")
        name = module[-1]
        fname = ".".join(module[:-1])

        if fname in sys.modules:
            mod = sys.modules[fname]
        else:
            mod = __import__(fname, globals(), locals(), [], 0)

        if name not in mod.__dict__:
            raise KeyError("module %s, function %s not in %s (path %s)" %
                           (module, name, str(mod.__dict__.keys()), mod.__file__))
        return mod.__dict__[name]
    else:
        from .default_functions import file_grep, file_list, file_split, file_head, test_regular_expression
        if function_name == "file_grep":
            return file_grep
        elif function_name == "file_list":
            return file_list
        elif function_name == "file_split":
            return file_split
        elif function_name == "file_head":
            return file_head
        elif function_name == "test_regular_expression":
            return test_regular_expression
        else:
            raise NameError("unknown exception " + function_name)