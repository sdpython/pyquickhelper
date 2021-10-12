"""
@file
@brief Command line about transfering files.
"""
import os
import io
from pstats import Stats, SortKey


def profile_stat(file_stat, output=None, calls=True, verbose=False,
                 clean_prefixes="", sort_key='line',
                 fct_width=50, fLOG=print):
    """
    Analyses the output of a profiling measured by module
    :mod:`cProfile`.

    :param file_stat: filename, profiling statistics
    :param output: output file, the extension determines the format,
        `.txt` for a text output, `.csv` for a comma separated value,
        `.xlsx` for excel output
    :param calls: flat output (False) or hierchical output (True),
        the hierarchical output shows the call stack
    :param clean_prefixes: prefixes to clean from the output,
        separated by `;`
    :param sort_key: `line` or `cumulative` or `time` (if calls is True)
    :param fct_width: number of character dedicatedd to the function name
         (if calls is True)
    :param verbose: more verbosity
    :param fLOG: logging function
    :return: status

    .. cmdref::
        :title: Analyses profiling results produced by module cProfile
        :cmd: -m pyquickhelper profile_stat --help

        The command line produces a flat output like method `print_stats`
        or a hierchical output showing function calls.
    """
    from ..pycode.profiling import profile2graph, profile2df
    prefixes = '' if clean_prefixes is None else clean_prefixes.split(';')
    verbose = verbose in (True, 'True', '1', 1)
    calls = calls in (True, 'True', '1', 1)
    if sort_key == 'line':
        sort_key = SortKey.LINE
    elif sort_key == 'cumulative':
        sort_key = SortKey.CUMULATIVE
    elif sort_key == 'line':
        sort_key = SortKey.TIME
    else:
        raise ValueError(
            "Unexpected value for sort_key=%r." % sort_key)

    def clean_text(text):
        for pref in prefixes:
            text = text.replace(pref, '')
        return text

    if calls:
        stats = Stats(file_stat)
        fct_width = int(fct_width)
        gr = profile2graph(stats, clean_text=clean_text,
                           verbose=verbose)
        if output is None:
            fLOG(gr[0].to_text(fct_width=fct_width, sort_key=sort_key))
            res = None
        else:
            ext = os.path.splitext(output)[-1]
            text = gr[0].to_text(fct_width=fct_width, sort_key=sort_key)
            if ext == '.txt':
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(text)
                res = text
            elif ext in {'.csv', '.xlsx'}:
                import pandas
                dicts = gr[0].as_dict(sort_key=sort_key)
                df = pandas.DataFrame(dicts)
                if ext == '.csv':
                    df.to_csv(output, index=False)
                else:
                    df.to_excel(output, index=False)
                res = text
            else:
                raise ValueError(
                    "Unexpected file extension %r." % output)
    else:
        st = io.StringIO()
        stats = Stats(file_stat, stream=st)
        stats.strip_dirs().sort_stats(sort_key).print_stats()
        text = st.getvalue()
        if output is None:
            fLOG(text)
            res = None
        else:
            df = profile2df(stats, clean_text=clean_text, verbose=verbose,
                            fLOG=print)
            ext = os.path.splitext(output)[-1]
            if ext == '.txt':
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(text)
                res = text
            elif ext in {'.csv', '.xlsx'}:
                df = profile2df(stats, clean_text=clean_text, as_df=True)
                if ext == '.csv':
                    df.to_csv(output, index=False)
                else:
                    df.to_excel(output, index=False)
                res = text
            else:
                raise ValueError(
                    "Unexpected file extension %r." % output)
    return res
