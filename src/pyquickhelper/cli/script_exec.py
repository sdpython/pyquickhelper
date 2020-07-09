"""
@file
@brief Repeat execution.
"""


def repeat_script(script, every_second=20, stop_after_second=-1,
                  outfile='out.log', errfile='err.log',
                  exc=True, verbose=1, fLOG=print):
    """
    Runs a python script on a regular basis. The function
    is not multithreaded, it returns when all execution
    are done.

    :param script: script to run
    :param every_second: every second
    :param stop_after_second: stop after a given time or never if -1
    :param outfile: file which receives the standard output
    :param errfile: file which receives the standard error
    :param exc: True to stop if an exception is raised, False to continue
    :param verbose: prints out every execution
    :param fLOG: logging function

    .. cmdref::
        :title: Repeat script execution every n seconds
        :cmd: -m pyquickhelper repeat_script --help

        The command line runs the execution a script
        on a regular basis.
    """
    from ..loghelper.time_helper import repeat_script_execution

    every_second = int(every_second)
    stop_after_second = int(stop_after_second)
    if stop_after_second == -1:
        stop_after_second = None
    exc = exc in ('1', 1, 'True', 'true', True)

    repeat_script_execution(script, every_second=every_second,
                            stop_after_second=stop_after_second,
                            outfile=outfile, errfile=errfile,
                            verbose=1, fLOG=fLOG, exc=exc)
