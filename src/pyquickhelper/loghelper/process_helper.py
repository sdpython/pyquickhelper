# -*- coding: utf-8 -*-
"""
@file
@brief Helpers about processes.
"""
from .flog import fLOG


def reap_children(timeout=3, subset=None, fLOG=fLOG):
    """
    Terminates children processes.
    Copied from `psutil <http://psutil.readthedocs.io/en/latest/index.html?highlight=terminate#terminate-my-children>`_.
    Tries hard to terminate and ultimately
    kill all the children of this process.

    @param      timeout     time out (seconds)
    @param      subset      subset of processes to be removed
    @param      fLOG        logging function
    @return                 killed processes
    """
    import psutil
    killed = set()

    def on_terminate(proc):
        fLOG("process {} terminated with exit code {}".format(proc, proc.returncode))
        killed.add(proc.pid)

    procs = psutil.Process().children()
    if subset is not None:
        procs = [p for p in procs if p.pid in subset]
    if len(procs) == 0:
        return None

    # send SIGTERM
    for p in procs:
        p.terminate()
    _, alive = psutil.wait_procs(
        procs, timeout=timeout, callback=on_terminate)
    if alive:
        # send SIGKILL
        for p in alive:
            fLOG("process {} survived SIGTERM; trying SIGKILL" % p)
            p.kill()
        _, alive = psutil.wait_procs(
            alive, timeout=timeout, callback=on_terminate)
        if alive:
            # give up
            for p in alive:
                fLOG("process {} survived SIGKILL; giving up" % p)
    return killed
