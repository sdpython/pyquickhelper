"""
@file
@brief Helpers around time.
"""
import os
import time
from .run_cmd import run_script


def repeat_execution(fct, every_second=1, stop_after_second=5,
                     verbose=0, fLOG=None, exc=True):
    """
    Runs a function on a regular basis. The function
    is not multithreaded, it returns when all execution
    are done.

    @param      fct                 function to run
    @param      every_second        every second
    @param      stop_after_second   stop after a given time or never if None
    @param      verbose             prints out every execution
    @param      fLOG                logging function
    @param      exc                 if False, catch exception,
                                    else does not catch them
    @return                         results of the function if
                                    *stop_after_second* is not None
    """
    iter = 0
    start = time.monotonic()
    end = None if stop_after_second is None else start + stop_after_second
    current = start
    res = []
    while end is None or current < end:
        iter += 1
        if exc:
            r = fct()
            if verbose > 0 and fLOG is not None:
                fLOG("[repeat_execution] iter={} time={} end={}".format(
                    iter, current, end))
            if stop_after_second is not None:
                res.append(r)
        else:
            try:
                r = fct()
                if verbose > 0 and fLOG is not None:
                    fLOG("[repeat_execution] iter={} time={} end={}".format(
                        iter, current, end))
                if stop_after_second is not None:
                    res.append(r)
            except Exception as e:
                if verbose > 0 and fLOG is not None:
                    fLOG("[repeat_execution] iter={} time={} end={} error={}".format(
                        iter, current, end, str(e)))
        while current <= time.monotonic():
            current += every_second
        while time.monotonic() < current:
            time.sleep(every_second / 2)

    return res if res else None


def repeat_script_execution(script, every_second=1, stop_after_second=5,
                            outfile=None, errfile=None,
                            verbose=0, fLOG=None, exc=True):
    """
    Runs a python script on a regular basis. The function
    is not multithreaded, it returns when all execution
    are done.

    @param      script              script to run
    @param      every_second        every second
    @param      stop_after_second   stop after a given time or never if None
    @param      outfile             file which receives the standard output
    @param      errfile             file which receives the standard error
    @param      verbose             prints out every execution
    @param      fLOG                logging function
    @param      exc                 if False, catch exception,
                                    else does not catch them
    @return                         all outputs if
                                    *stop_after_second* is not None
    """
    if not os.path.exists(script):
        raise FileNotFoundError("Unable to find '{}'.".format(script))

    iter = [0]

    def fct_():
        out, err = run_script(script, wait=True)
        if out and outfile:
            with open(outfile, "a", encoding="utf-8") as f:
                f.write('[repeat_script_execution] iter={}\n'.format(iter[0]))
                f.write(out)
        if err and errfile:
            with open(errfile, "a", encoding="utf-8") as f:
                f.write('[repeat_script_execution] iter={}\n'.format(iter[0]))
                f.write(err)
        iter[0] += 1
        return out

    return repeat_execution(fct_, every_second=every_second,
                            stop_after_second=stop_after_second,
                            verbose=verbose, fLOG=fLOG, exc=exc)
