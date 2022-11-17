"""
@file
@brief Profiling helpers
"""
from collections import deque, OrderedDict
from io import StringIO
import json
import math
import os
import site
import cProfile
from pstats import Stats

try:
    from pstarts import SortKey
except ImportError:  # pragma: no cover
    # Python < 3.7

    class SortKey:
        LINE = 'line'
        CUMULATIVE = 'cumulative'
        TIME = 'time'


class ProfileNode:
    """
    Graph structure to represent a profiling.

    :param filename: filename
    :param line: line number
    :param func_name: function name
    :param nc1: number of calls 1
    :param nc2: number of calls 2
    :param tin: time spent in the function
    :param tout: time spent in the function and in the sub functions
    """

    def __init__(self, filename, line, func_name, nc1, nc2, tin, tall):
        if "method 'disable' of '_lsprof.Profiler'" in func_name:
            raise RuntimeError(  # pragma: no cover
                f"Function not allowed in the profiling: {func_name!r}.")
        self.filename = filename
        self.line = line
        self.func_name = func_name
        self.nc1 = nc1
        self.nc2 = nc2
        self.tin = tin
        self.tall = tall
        self.called_by = []
        self.calls_to = []
        self.calls_to_elements = []

    def add_called_by(self, pnode):
        "This function is called by these lines."
        self.called_by.append(pnode)

    def add_calls_to(self, pnode, time_elements):
        "This function calls this node."
        self.calls_to.append(pnode)
        self.calls_to_elements.append(time_elements)

    @staticmethod
    def _key(filename, line, fct):
        key = "%s:%d:%s" % (filename, line, fct)
        return key

    @property
    def key(self):
        "Returns `file:line`."
        return ProfileNode._key(self.filename, self.line,
                                self.func_name)

    def get_root(self):
        "Returns the root of the graph."
        done = set()

        def _get_root(node, stor=None):
            if stor is not None:
                stor.append(node)
            if len(node.called_by) == 0:
                return node
            if len(node.called_by) == 1:
                return _get_root(node.called_by[0], stor=stor)
            res = None
            for ct in node.called_by:
                k = id(node), id(ct)
                if k in done:
                    continue
                res = ct
                break
            if res is None:
                # All paths have been explored and no entry point was found.
                # Choosing the most consuming function.
                return None
            done.add((id(node), id(res)))
            return _get_root(res, stor=stor)

        root = _get_root(self)
        if root is None:
            candidates = []
            _get_root(self, stor=candidates)
            tall = [(n.tall, n) for n in candidates]
            tall.sort()
            root = tall[-1][-1]
        return root

    def __repr__(self):
        "usual"
        return "%s(%r, %r, %r, %r, %r, %r, %r)  # %d-%d" % (
            self.__class__.__name__,
            self.filename, self.line, self.func_name,
            self.nc1, self.nc2, self.tin, self.tall,
            len(self.called_by), len(self.calls_to))

    def __iter__(self):
        "Returns all nodes in the graph."
        done = set()
        stack = deque()
        stack.append(self)
        while len(stack) > 0:
            node = stack.popleft()
            if node.key in done:
                continue
            yield node
            done.add(node.key)
            stack.extend(node.calls_to)

    _modules_ = {
        '~', 'subprocess.py', 'posixpath.py', 'os.py',
        '<frozen importlib._bootstrap>', 'inspect.py',
        'version.py', 'typing.py', 'warnings.py', 'errors.py',
        'numbers.py', 'ast.py', 'threading.py', '_collections_abc.py',
        'datetime.py', 'abc.py', 'argparse.py', '__future__.py',
        'functools.py', 'six.py', 'sre_parse.py', 'contextlib.py',
        ' _globals.py', '_ios.py', 'types.py'}

    @staticmethod
    def filter_node_(node, info=None):
        """
        Filters out node to be displayed by default.

        :param node: node
        :param info: if the node is called by a function,
            this dictionary can be used to overwrite the attributes
            held by the node
        :return: boolean (True to keep, False to forget)
        """
        if node.filename in ProfileNode._modules_:
            if info is None:
                if (node.nc1 <= 10 and node.nc2 <= 10 and
                        node.tall <= 1e-4):
                    return False
            else:
                if (info['nc1'] <= 10 and info['nc2'] <= 10 and
                        info['tall'] <= 1e-4):
                    return False

        return True

    def as_dict(self, filter_node=None, sort_key=SortKey.LINE):
        """
        Renders the results of a profiling interpreted with
        function @fn profile2graph. It can then be loaded with
        a dataframe.

        :param filter_node: display only the nodes for which
            this function returns True, if None, the default function
            removes built-in function with small impact
        :param sort_key: sort sub nodes by...
        :return: rows
        """
        def sort_key_line(dr):
            if isinstance(dr, tuple):
                return (dr[0].filename, dr[0].line)
            return (dr.filename, dr.line)

        def sort_key_tin(dr):
            if isinstance(dr, tuple):
                return -dr[1][2]
            return -dr.tin

        def sort_key_tall(dr):
            if isinstance(dr, tuple):
                return -dr[1][3]
            return -dr.tall

        if sort_key == SortKey.LINE:
            sortk = sort_key_line
        elif sort_key == SortKey.CUMULATIVE:
            sortk = sort_key_tall
        elif sort_key == SortKey.TIME:
            sortk = sort_key_tin
        else:
            raise NotImplementedError(
                f"Unable to sort subcalls with this key {sort_key!r}.")

        def depth_first(node, roots_keys, indent=0):
            text = {'fct': node.func_name, 'where': node.key,
                    'nc1': node.nc1, 'nc2': node.nc2, 'tin': node.tin,
                    'tall': node.tall, 'indent': indent,
                    'ncalls': len(node.calls_to), 'debug': 'A'}
            yield text
            for n, nel in sorted(zip(node.calls_to,
                                     node.calls_to_elements),
                                 key=sortk):
                if n.key in roots_keys:
                    text = {'fct': n.func_name, 'where': n.key,
                            'nc1': nel[0], 'nc2': nel[1], 'tin': nel[2],
                            'tall': nel[3], 'indent': indent + 1,
                            'ncalls': len(n.calls_to), 'more': '+',
                            'debug': 'B'}
                    if (filter_node is not None and
                            not filter_node(n, info=text)):
                        continue
                    yield text
                else:
                    if filter_node is not None and not filter_node(n):
                        continue
                    for t in depth_first(n, roots_keys, indent + 1):
                        yield t

        if filter_node is None:
            filter_node = ProfileNode.filter_node_
        nodes = list(self)
        roots = [node for node in nodes if len(node.called_by) != 1]
        roots_key = {r.key: r for r in roots}
        rows = []
        for root in sorted(roots, key=sortk):
            if filter_node is not None and not filter_node(root):
                continue
            rows.extend(depth_first(root, roots_key))
        return rows

    def to_text(self, filter_node=None, sort_key=SortKey.LINE,
                fct_width=60):
        """
        Prints the profiling to text.

        :param filter_node: display only the nodes for which
            this function returns True, if None, the default function
            removes built-in function with small impact
        :param sort_key: sort sub nodes by...
        :return: rows
        """
        def align_text(text, size):
            if size <= 0:
                return text
            if len(text) <= size:
                return text + " " * (size - len(text))
            h = size // 2 - 1
            return text[:h] + "..." + text[-h + 1:]

        dicts = self.as_dict(filter_node=filter_node, sort_key=sort_key)
        max_nc = max(max(_['nc1'] for _ in dicts),
                     max(_['nc2'] for _ in dicts))
        dg = int(math.log(max_nc) / math.log(10) + 1.5)
        line_format = ("{indent}{fct} -- {nc1: %dd} {nc2: %dd} -- {tin:1.5f} {tall:1.5f}"
                       " -- {name} ({fct2})" % (dg, dg))
        text = []
        for row in dicts:
            line = line_format.format(
                indent=" " * (row['indent'] * 4),
                fct=align_text(row['fct'], fct_width - row['indent'] * 4),
                nc1=row['nc1'], nc2=row['nc2'], tin=row['tin'],
                tall=row['tall'], name=row['where'],
                fct2=row['fct'])
            if row.get('more', '') == '+':
                line += " +++"
            text.append(line)
        return "\n".join(text)

    def to_json(self, filter_node=None, sort_key=SortKey.LINE, as_str=True,
                **kwargs):
        """
        Renders the results of a profiling interpreted with
        function @fn profile2graph as :epkg:`JSON`.

        :param filter_node: display only the nodes for which
            this function returns True, if None, the default function
            removes built-in function with small impact
        :param sort_key: sort sub nodes by...
        :param as_str: converts the json into a string
        :param kwargs: see :func:`json.dumps`
        :return: rows

        See notebook :ref:`profilingrst` to see how to use
        the json output.
        """
        def sort_key_line(dr):
            if isinstance(dr, tuple):
                return (dr[0].filename, dr[0].line)
            return (dr.filename, dr.line)

        def sort_key_tin(dr):
            if isinstance(dr, tuple):
                return -dr[1][2]
            return -dr.tin

        def sort_key_tall(dr):
            if isinstance(dr, tuple):
                return -dr[1][3]
            return -dr.tall

        if sort_key == SortKey.LINE:
            sortk = sort_key_line
        elif sort_key == SortKey.CUMULATIVE:
            sortk = sort_key_tall
        elif sort_key == SortKey.TIME:
            sortk = sort_key_tin
        else:
            raise NotImplementedError(
                f"Unable to sort subcalls with this key {sort_key!r}.")

        def walk(node, roots_keys, indent=0):
            item = {'details': {
                'fct': node.func_name, 'where': node.key,
                'nc1': node.nc1, 'nc2': node.nc2, 'tin': node.tin,
                'tall': node.tall, 'indent': indent,
                'ncalls': len(node.calls_to)}}

            child = OrderedDict()
            for n, nel in sorted(zip(node.calls_to,
                                     node.calls_to_elements),
                                 key=sortk):
                key = (nel[0], f"{nel[3]:1.5f}:{n.func_name}")
                if n.key in roots_keys:
                    details = {'fct': n.func_name, 'where': n.key,
                               'nc1': nel[0], 'nc2': nel[1], 'tin': nel[2],
                               'tall': nel[3], 'indent': indent,
                               'ncalls': len(node.calls_to)}
                    if (filter_node is not None and
                            not filter_node(n, info=details)):
                        continue
                    child[key] = {'details': details}
                else:
                    if filter_node is not None and not filter_node(n):
                        continue
                    child[key] = walk(n, roots_key, indent + 1)

            if len(child) > 0:
                mx = max(_[0] for _ in child)
                dg = int(math.log(mx) / math.log(10) + 1.5)
                form = f"%-{dg}d-%s"
                child = OrderedDict((form % k, v) for k, v in child.items())
                item['calls'] = child
            return item

        if filter_node is None:
            filter_node = ProfileNode.filter_node_
        nodes = list(self)
        roots = [node for node in nodes if len(node.called_by) != 1]
        roots_key = {r.key: r for r in roots}
        rows = OrderedDict()
        for root in sorted(roots, key=sortk):
            if filter_node is not None and not filter_node(root):
                continue
            key = (root.nc1, f"{root.tall:1.5f}:::{root.func_name}")
            rows[key] = walk(root, roots_key)
        mx = max(_[0] for _ in rows)
        dg = int(math.log(mx) / math.log(10) + 1.5)
        form = f"%-{dg}d-%s"
        rows = OrderedDict((form % k, v) for k, v in rows.items())
        if as_str:
            return json.dumps({'profile': rows}, **kwargs)
        return {'profile': rows}


def _process_pstats(ps, clean_text=None, verbose=False, fLOG=None):
    """
    Converts class `Stats <https://docs.python.org/3/library/
    profile.html#pstats.Stats>`_ into something
    readable for a dataframe.

    :param ps: instance of type :func:`pstats.Stats`
    :param clean_text: function to clean function names
    :param verbose: change verbosity
    :param fLOG: logging function
    :return: list of rows
    """
    if clean_text is None:
        clean_text = lambda x: x

    def add_rows(rows, d):
        tt1, tt2 = 0, 0
        for k, v in d.items():
            stin = 0
            stall = 0
            if verbose and fLOG is not None:
                fLOG("[pstats] %s=%r" % (
                    (clean_text(k[0].replace("\\", "/")), ) + k[1:],
                    v))
            if len(v) < 5:
                continue
            row = {
                'file': "%s:%d" % (clean_text(k[0].replace("\\", "/")), k[1]),
                'fct': k[2],
                'ncalls1': v[0],
                'ncalls2': v[1],
                'tin': v[2],
                'tall': v[3]
            }
            stin += v[2]
            stall += v[3]
            if len(v) == 5:
                t1, t2 = add_rows(rows, v[-1])
                stin += t1
                stall += t2
            row['cum_tin'] = stin
            row['cum_tall'] = stall
            rows.append(row)
            tt1 += stin
            tt2 += stall
        return tt1, tt2

    rows = []
    add_rows(rows, ps.stats)
    return rows


def profile2df(ps, as_df=True, clean_text=None, verbose=False, fLOG=None):
    """
    Converts profiling statistics into a Dataframe.

    :param ps: an instance of `pstats
        <https://docs.python.org/3/library/profile.html#pstats.Stats>`_
    :param as_df: returns the results as a dataframe (True)
        or a list of dictionaries (False)
    :param clean_text: function to clean function names
    :param verbose: verbosity
    :param fLOG: logging function
    :return: a DataFrame

    ::

        import pstats
        from pyquickhelper.pycode.profiling import profile2df

        ps = pstats.Stats('bench_ortmodule_nn_gpu6.prof')
        df = profile2df(pd)
        print(df)
    """
    rows = _process_pstats(ps, clean_text, verbose=verbose, fLOG=fLOG)
    if not as_df:
        return rows

    import pandas
    df = pandas.DataFrame(rows)
    df = df[['fct', 'file', 'ncalls1', 'ncalls2', 'tin', 'cum_tin',
             'tall', 'cum_tall']]
    df = df.groupby(['fct', 'file'], as_index=False).sum().sort_values(
        'cum_tall', ascending=False).reset_index(drop=True)
    return df.copy()


def profile(fct, sort='cumulative', rootrem=None, as_df=False,
            pyinst_format=None, return_results=False, **kwargs):
    """
    Profiles the execution of a function.

    :param fct: function to profile
    :param sort: see `sort_stats <https://docs.python.org/3/library/
        profile.html#pstats.Stats.sort_stats>`_
    :param rootrem: root to remove in filenames
    :param as_df: return the results as a dataframe and not text
    :param pyinst_format: format for :epkg:`pyinstrument`, if not empty,
        the function uses this module or raises an exception if not
        installed, the options are *text*, *textu* (text with colors),
        *json*, *html*
    :param return_results: if True, return results as well
        (in the first position)
    :param kwargs: additional parameters used to create the profiler
    :return: raw results, statistics text dump (or dataframe is *as_df* is True)

    .. plot::

        import matplotlib.pyplot as plt
        from pyquickhelper.pycode.profiling import profile
        from pyquickhelper.texthelper import compare_module_version

        def fctm():
            return compare_module_version('0.20.4', '0.22.dev0')

        pr, df = profile(lambda: [fctm() for i in range(0, 1000)], as_df=True)
        ax = df[['namefct', 'cum_tall']].head(n=15).set_index(
            'namefct').plot(kind='bar', figsize=(8, 3), rot=30)
        ax.set_title("example of a graph")
        for la in ax.get_xticklabels():
            la.set_horizontalalignment('right');
        plt.show()
    """
    if pyinst_format is None:
        pr = cProfile.Profile(**kwargs)
        pr.enable()
        fct_res = fct()
        pr.disable()
        s = StringIO()
        ps = Stats(pr, stream=s).sort_stats(sort)
        ps.print_stats()
        res = s.getvalue()
        try:
            pack = site.getsitepackages()
        except AttributeError:  # pragma: no cover
            import numpy
            pack = os.path.normpath(os.path.abspath(
                os.path.join(os.path.dirname(numpy.__file__), "..")))
            pack = [pack]
        pack_ = os.path.normpath(os.path.join(pack[-1], '..'))

        def clean_text(res):
            res = res.replace(pack[-1], "site-packages")
            res = res.replace(pack_, "lib")
            if rootrem is not None:
                if isinstance(rootrem, str):
                    res = res.replace(rootrem, '')
                else:
                    for sub in rootrem:
                        if isinstance(sub, str):
                            res = res.replace(sub, '')
                        elif isinstance(sub, tuple) and len(sub) == 2:
                            res = res.replace(sub[0], sub[1])
                        else:
                            raise TypeError(  # pragma: no cover
                                "rootrem must contains strings or tuple not {0}"
                                ".".format(rootrem))
            return res

        if as_df:

            def better_name(row):
                if len(row['fct']) > 15:
                    return f"{row['file'].split(':')[-1]}-{row['fct']}"
                name = row['file'].replace("\\", "/")
                return f"{name.split('/')[-1]}-{row['fct']}"

            rows = _process_pstats(ps, clean_text)
            import pandas
            df = pandas.DataFrame(rows)
            df = df[['fct', 'file', 'ncalls1', 'ncalls2', 'tin', 'cum_tin',
                     'tall', 'cum_tall']]
            df['namefct'] = df.apply(lambda row: better_name(row), axis=1)
            df = df.groupby(['namefct', 'file'], as_index=False).sum().sort_values(
                'cum_tall', ascending=False).reset_index(drop=True)
            if return_results:
                return fct_res, ps, df
            return ps, df
        else:
            res = clean_text(res)
            if return_results:
                return fct_res, ps, res
            return ps, res
    if as_df:
        raise ValueError(  # pragma: no cover
            "as_df is not a compatible option with pyinst_format.")

    try:
        from pyinstrument import Profiler
    except ImportError as e:  # pragma: no cover
        raise ImportError("pyinstrument is not installed.") from e

    profiler = Profiler(**kwargs)
    profiler.start()
    fct_res = fct()
    profiler.stop()

    if pyinst_format == "text":
        if return_results:
            return fct_res, profiler, profiler.output_text(
                unicode=False, color=False)
        return profiler, profiler.output_text(unicode=False, color=False)
    if pyinst_format == "textu":
        if return_results:
            return fct_res, profiler, profiler.output_text(
                unicode=True, color=True)
        return profiler, profiler.output_text(unicode=True, color=True)
    if pyinst_format == "json":
        from pyinstrument.renderers import JSONRenderer
        if return_results:
            return fct_res, profiler, profiler.output(
                JSONRenderer())
        return profiler, profiler.output(JSONRenderer())
    if pyinst_format == "html":
        if return_results:
            return fct_res, profiler, profiler.output_html()
        return profiler, profiler.output_html()
    raise ValueError(f"Unknown format '{pyinst_format}'.")


def profile2graph(ps, clean_text=None, verbose=False, fLOG=None):
    """
    Converts profiling statistics into a graphs.

    :param ps: an instance of `pstats
        <https://docs.python.org/3/library/profile.html#pstats.Stats>`_
    :param clean_text: function to clean function names
    :param verbose: verbosity
    :param fLOG: logging function
    :return: an instance of class @see cl ProfileNode

    .. exref::
        :title: Hierarchical display for a profiling

        :epkg:`pyinstrument` has a nice display to show
        time spent and call stack at the same time. This function
        tries to replicate that display based on the results produced
        by module :mod:`cProfile`. Here is an example.

        .. runpython::
            :showcode:

            import time
            from pyquickhelper.pycode.profiling import profile, profile2graph


            def fct0(t):
                time.sleep(t)


            def fct1(t):
                time.sleep(t)


            def fct2():
                fct1(0.1)
                fct1(0.01)


            def fct3():
                fct0(0.2)
                fct1(0.5)


            def fct4():
                fct2()
                fct3()


            ps = profile(fct4)[0]
            root, nodes = profile2graph(ps, clean_text=lambda x: x.split('/')[-1])
            text = root.to_text()
            print(text)
    """
    if clean_text is None:
        clean_text = lambda x: x

    nodes = {}
    for k, v in ps.stats.items():
        if verbose and fLOG is not None:
            fLOG(f"[pstats] {k}={v!r}")
        if len(v) < 5:
            continue
        if k[0] == '~' and len(v) == 0:
            # raw function never called by another
            continue
        if "method 'disable' of '_lsprof.Profiler'" in k[2]:
            continue
        node = ProfileNode(
            filename=clean_text(k[0].replace("\\", "/")),
            line=k[1], func_name=k[2],
            nc1=v[0], nc2=v[1], tin=v[2], tall=v[3])
        if node.key in nodes:
            raise RuntimeError(  # pragma: no cover
                f"Key {node.key!r} is already present, node={node!r}.")
        nodes[node.key] = node

    for k, v in ps.stats.items():
        if "method 'disable' of '_lsprof.Profiler'" in k[2]:
            continue
        filename = clean_text(k[0].replace("\\", "/"))
        ks = ProfileNode._key(filename, k[1], k[2])
        node = nodes[ks]
        sublist = v[4]
        for f, vv in sublist.items():
            if "method 'disable' of '_lsprof.Profiler'" in f[2]:
                continue
            name = clean_text(f[0].replace("\\", "/"))
            key = ProfileNode._key(name, f[1], f[2])
            if key not in nodes:
                raise RuntimeError(  # pragma: no cover
                    "Unable to find key %r into\n%s" % (
                        key, "\n".join(sorted(nodes))))
            if k[0] == '~' and len(v) == 0:
                continue
            child = nodes[key]
            node.add_called_by(child)
            child.add_calls_to(node, vv)

    for k, v in nodes.items():
        root = v.get_root()
        break

    return root, nodes
