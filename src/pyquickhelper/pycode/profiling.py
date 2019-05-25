"""
@file
@brief Profiling helpers
"""
import os
from io import StringIO
import cProfile
import pstats
import site


def profile(fct, sort='cumulative', rootrem=None):
    """
    Profiles the execution of a function.

    @param      fct     function to profile
    @param      sort    see `sort_stats <https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats>`_
    @param      rootrem root to remove in filenames
    @return             statistics text dump
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
    res = res.replace(pack[-1], "site-packages")
    pack_ = os.path.normpath(os.path.join(pack[-1], '..'))
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
    return ps, res
