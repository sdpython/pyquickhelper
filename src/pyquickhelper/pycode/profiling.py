"""
@file
@brief Profiling helpers
"""
import os
from io import StringIO
import cProfile
import pstats
import site


def _process_pstats(ps, clean_text):
    """
    Converts class `Stats <https://docs.python.org/3/library/
    profile.html#pstats.Stats>`_ into something
    readable for a dataframe.
    """
    def add_rows(rows, d):
        tt1, tt2 = 0, 0
        for k, v in d.items():
            stin = 0
            stall = 0
            row = {
                'file': "%s:%d" % (clean_text(k[0]), k[1]),
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


def profile(fct, sort='cumulative', rootrem=None, as_df=False,
            pyinst_format=None, **kwargs):
    """
    Profiles the execution of a function.

    @param      fct             function to profile
    @param      sort            see `sort_stats <https://docs.python.org/3/library/
                                profile.html#pstats.Stats.sort_stats>`_
    @param      rootrem         root to remove in filenames
    @param      as_df           return the results as a dataframe and not text
    @param      pyinst_format   format for :epkg:`pyinstrument`, if not empty,
                                the function uses this module or raises an exception if not
                                installed, the options are *text*, *textu* (text with colors),
                                *json*, *html*
    @param      kwargs          additional parameters used to create the profiler
    @return                     raw results, statistics text dump (or dataframe is *as_df* is True)

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
        fct()
        pr.disable()
        s = StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats(sort)
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
                            raise TypeError(
                                "rootrem must contains strings or tuple not {0}".format(rootrem))
            return res

        if as_df:

            def better_name(row):
                if len(row['fct']) > 15:
                    return "{}-{}".format(row['file'].split(':')[-1], row['fct'])
                name = row['file'].replace("\\", "/")
                return "{}-{}".format(name.split('/')[-1], row['fct'])

            rows = _process_pstats(ps, clean_text)
            import pandas
            df = pandas.DataFrame(rows)
            df = df[['fct', 'file', 'ncalls1', 'ncalls2', 'tin', 'cum_tin',
                     'tall', 'cum_tall']]
            df['namefct'] = df.apply(lambda row: better_name(row), axis=1)
            df = df.groupby(['namefct', 'file'], as_index=False).sum().sort_values(
                'cum_tall', ascending=False).reset_index(drop=True)
            return ps, df
        else:
            res = clean_text(res)
            return ps, res
    elif as_df:
        raise ValueError(  # pragma: no cover
            "as_df is not a compatible option with pyinst_format")
    else:
        try:
            from pyinstrument import Profiler
        except ImportError as e:  # pragma: no cover
            raise ImportError("pyinstrument is not installed.") from e

        profiler = Profiler(**kwargs)
        profiler.start()
        fct()
        profiler.stop()

        if pyinst_format == "text":
            return profiler, profiler.output_text(unicode=False, color=False)
        elif pyinst_format == "textu":
            return profiler, profiler.output_text(unicode=True, color=True)
        elif pyinst_format == "json":
            from pyinstrument.renderers import JSONRenderer
            return profiler, profiler.output(JSONRenderer())
        elif pyinst_format == "html":
            return profiler, profiler.output_html()
        else:
            raise ValueError("Unknown format '{}'.".format(pyinst_format))
