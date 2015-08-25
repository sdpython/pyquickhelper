"""
@file
@brief Helpers around network
"""

import time
from ..loghelper import run_cmd, fLOG, noLOG


def ping_machine(machine, fLOG=noLOG):
    """
    ping a machine returns the outout

    @param      machine         machine name
    @param      fLOG            logging function
    @return                     output
    """
    cmd = "ping " + machine
    out, err = run_cmd(cmd, wait=True, fLOG=noLOG)
    return out


def regular_ping_machine(machine, delay=1.0, nb_max=-1, fLOG=fLOG):
    """
    ping a machine on a regular basis

    @param      machine     machine to ping (or list of machines)
    @param      delay       delay between two pings (seconds)
    @param      nb_max      maximum number of ping of do, if -1, never stops
    @param      fLOG        logging function
    @return                 last results
    """
    if not isinstance(machine, list):
        machine = [machine]

    while nb_max == -1 or nb_max > 0:
        for m in machine:
            out = ping_machine(m)
            fLOG(out)
        time.sleep(delay)
        if nb_max > 0:
            nb_max -= 1
    return out
