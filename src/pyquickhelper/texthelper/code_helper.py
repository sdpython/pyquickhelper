# -*- coding: utf-8 -*-
"""
@file
@brief Some functions about diacritics
"""
import importlib
import inspect
import keyword
import os
import re
from textwrap import dedent
import warnings


def change_style(name):
    """
    Switches from *AaBb* into *aa_bb*.

    @param      name    name to convert
    @return             converted name

    Example:

    .. runpython::
        :showcode:

        from pyquickhelper.texthelper import change_style

        print("changeStyle --> {0}".format(change_style('change_style')))
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s2 if not keyword.iskeyword(s2) else s2 + "_"


def add_rst_links(text, values, tag="epkg", n=4):
    """
    Replaces words by something like ``:epkg:'word'``.

    @param      text        text to process
    @param      values      values
    @param      tag         tag to use
    @param      n           number of consecutive words to look at
    @return                 new text

    .. runpython::
        :showcode:

        from pyquickhelper.texthelper import add_rst_links
        text = "Maybe... Python is winning the competition for machine learning language."
        values = {'Python': 'https://www.python.org/',
                  'machine learning': 'https://en.wikipedia.org/wiki/Machine_learning'}
        print(add_rst_links(text, values))
    """
    def replace(words, i, n):
        mx = max(len(words), i + n)
        for last in range(mx, i, -1):
            w = ''.join(words[i:last])
            if w in values:
                return last, f":{tag}:`{w}`"
        return i + 1, words[i]

    reg = re.compile("(([\\\"_*`\\w']+)|([\\W]+)|([ \\n]+))")
    words = reg.findall(text)
    words = [_[0] for _ in words]
    res = []
    i = 0
    while i < len(words):
        i, w = replace(words, i, n)
        res.append(w)
    return ''.join(res)


def _measure_documentation_append(counts, kind, doc, code):
    if kind not in counts:
        counts[kind] = {
            ("raw_length", "doc"): 0,
            ("raw_length", "code"): 0,
            ("length", "doc"): 0,
            ("length", "code"): 0,
            ("line", "doc"): 0,
            ("line", "code"): 0,
        }
    c = counts[kind]
    doc = "" if doc is None else dedent(doc)
    code = "" if code is None else dedent(code)

    c["raw_length", "doc"] += len(doc)
    c["raw_length", "code"] += len(code)

    c["length", "doc"] += len(doc.replace(" ", "").replace("\n", ""))
    c["length", "code"] += len(code.replace(" ", "").replace("\n", ""))

    c["line", "doc"] += 0 if len(doc) == 0 else len(doc.split("\n"))
    c["line", "code"] += 0 if len(code) == 0 else len(code.split("\n"))


def _measure_documentation_update(counts, c):
    for key in c:
        if key not in counts:
            counts[key] = c[key]
        else:
            for k, v in c[key].items():
                counts[key][k] += v


def _measure_documentation_ratio(counts):
    for _, d in counts.items():
        up = {}
        for k in d:
            if k[1] == "code":
                up[k[0], "ratio"] = (
                    d[k[0], "doc"] / max(d[k] + d[k[0], "doc"], 1))
        d.update(up)


def _dictionary_to_dataframe(doc, cols=None):
    data = []
    for k, v in doc.items():
        if isinstance(k, str):
            ks = [k]
        else:
            ks = list(k)
        if isinstance(v, (float, int)):
            obs = (cols or []) + ks + [v]
            data.append(obs)
        else:
            lines = _dictionary_to_dataframe(v, (cols or []) + ks)
            data.extend(lines)
    if cols is None:
        import pandas
        df = pandas.DataFrame(data)
        if df.shape[1] == 4:
            df.columns = ['kind', 'stat', 'doc_code', 'value']
        return df
    return data


def measure_documentation(mod, ratio=False, include_hidden=False, f_kind=None, as_df=False):
    """
    Measures the fact a module is documented.

    :param mod: module
    :param ratio: compute ratios
    :param include_hidden: includes hidden function (starting with `"_"`)
    :param f_kind: function `f(obj: python_object) -> str` which returns
        the fist key the result must be indexed by, the function cannot
        returns `'function'` or `'class'`
    :param as_df: return the result as a dataframe
    :return: dictionary

    .. runpython::
        :showcode:

        import pprint
        from pyquickhelper.texthelper import code_helper
        from pyquickhelper.texthelper.code_helper import measure_documentation
        pprint.pprint(measure_documentation(code_helper))
    """
    counts = {}
    code_mod = None
    if inspect.ismodule(mod):
        code_mod = mod.__name__
    if inspect.isclass(mod):
        doc = mod.__doc__
        if hasattr(mod, "__init__"):
            try:
                code = inspect.getsource(mod.__init__)
            except TypeError:
                code = ""
        else:
            code = ""
        _measure_documentation_append(counts, "class", doc, code)
    if f_kind is not None:
        kind = f_kind(mod)
        doc = mod.__doc__
        if hasattr(mod, "__init__"):
            try:
                code = inspect.getsource(mod.__init__)
            except TypeError:
                code = ""
        else:
            code = ""
        _measure_documentation_append(counts, kind, doc, code)
    names = dir(mod)
    for name in names:
        if name[0] == "_" and not include_hidden:
            continue
        obj = getattr(mod, name)
        if inspect.ismethod(obj):
            doc = obj.__doc__
            code = inspect.getsource(obj)
            _measure_documentation_append(counts, "class", doc, code)
            if f_kind is not None:
                kind = f_kind(obj)
                _measure_documentation_append(counts, kind, doc, code)
        elif inspect.isfunction(obj):
            if obj.__module__ != code_mod:
                continue
            doc = obj.__doc__
            kind = "function"
            try:
                code = inspect.getsource(obj)
            except TypeError:
                kind = "function_c"
                code = ""
            _measure_documentation_append(counts, kind, doc, code)
            if f_kind is not None:
                kind = f_kind(obj)
                _measure_documentation_append(counts, kind, doc, code)
        elif inspect.isclass(obj):
            if obj.__module__ != code_mod:
                continue
            c = measure_documentation(obj, include_hidden=include_hidden)
            _measure_documentation_update(counts, c)
    if ratio:
        _measure_documentation_ratio(counts)
    if as_df:
        return _dictionary_to_dataframe(counts)
    return counts


def measure_documentation_module(mod, ratio=False, include_hidden=False, f_kind=None, silent=True, as_df=False):
    """
    Measures the fact a module is documented.

    :param mod: module or a list of modules, in case of a list
        of modules, a dictionary is returned per module
    :param ratio: compute ratios
    :param include_hidden: includes hidden function (starting with `"_"`)
    :param f_kind: function `f(obj: python_object) -> str` which returns
        the fist key the result must be indexed by, the function cannot
        returns `'function'` or `'class'`
    :param silent: continue even if the import of a module failed
    :param as_df: return the result as a dataframe
    :return: dictionary

    .. runpython::
        :showcode:

        import pprint
        import pyquickhelper
        from pyquickhelper.texthelper.code_helper import measure_documentation_module
        pprint.pprint(measure_documentation_module(pyquickhelper))
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if isinstance(mod, list):
            counts = {}
            for m in mod:
                c = measure_documentation_module(
                    m, ratio=ratio, include_hidden=include_hidden, f_kind=f_kind, silent=silent)
                counts[m.__name__] = c
            if as_df:
                df = _dictionary_to_dataframe(counts)
                df.columns = ['module', 'kind', 'stat', 'doc_code', 'value']
                return df
            return counts
        counts = measure_documentation(
            mod, include_hidden=include_hidden, f_kind=f_kind)
        path = os.path.dirname(mod.__file__)
        for sub in os.listdir(path):
            if sub in {'.'}:
                continue
            name, ext = os.path.splitext(sub)
            if ext:
                if hasattr(mod, sub):
                    c = measure_documentation(
                        getattr(mod, sub), include_hidden=include_hidden, f_kind=f_kind)
                    _measure_documentation_update(counts, c)
                else:
                    full_name = f"{mod.__name__}.{name}"
                    try:
                        sub_mod = importlib.import_module(full_name)
                    except ImportError as e:
                        if silent:
                            continue
                        raise ImportError(
                            f"Unable to import {full_name!r}.") from e
                    c = measure_documentation(
                        sub_mod, include_hidden=include_hidden, f_kind=f_kind)
                    _measure_documentation_update(counts, c)
                continue

            init = os.path.join(path, sub, "__init__.py")
            if not os.path.exists(init):
                continue
            if hasattr(mod, sub):
                c = measure_documentation(
                    getattr(mod, sub), include_hidden=include_hidden, f_kind=f_kind)
                _measure_documentation_update(counts, c)
            else:
                full_name = f"{mod.__name__}.{name}"
                try:
                    sub_mod = importlib.import_module(full_name)
                except ImportError as e:
                    if silent:
                        continue
                    raise ImportError(
                        f"Unable to import {full_name!r}.") from e
                c = measure_documentation(
                    sub_mod, include_hidden=include_hidden, f_kind=f_kind)
                _measure_documentation_update(counts, c)

        if ratio:
            _measure_documentation_ratio(counts)
        if as_df:
            df = _dictionary_to_dataframe(counts)
            return df
        return counts
