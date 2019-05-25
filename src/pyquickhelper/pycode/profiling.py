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


def profile(fct, sort='cumulative', rootrem=None, as_df=False):
    """
    Profiles the execution of a function.

    @param      fct     function to profile
    @param      sort    see `sort_stats <https://docs.python.org/3/library/
                        profile.html#pstats.Stats.sort_stats>`_
    @param      rootrem root to remove in filenames
    @param      as_df   return the results as a dataframe and not text
    @return             raw results, statistics text dump (or dataframe is *as_df* is True)
    """
    pr = cProfile.Profile()
    pr.enable()
    fct()
    pr.disable()
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats(sort)
    ps.print_stats()
    res = s.getvalue()
    try:
        pack = site.getsitepackages()
    except AttributeError:
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
        rows = _process_pstats(ps, clean_text)
        import pandas
        df = pandas.DataFrame(rows)
        df = df[['fct', 'file', 'ncalls1', 'ncalls2', 'tin', 'cum_tin',
                 'tall', 'cum_tall']]
        df = df.groupby(['fct', 'file'], as_index=False).sum().sort_values(
            'cum_tall', ascending=False).reset_index(drop=True)
        return ps, df
    else:
        res = clean_text(res)
        return ps, res
