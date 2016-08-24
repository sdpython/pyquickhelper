# -*- coding: utf-8 -*-
"""
@file
@brief Implements function @see fn run_cmd.
"""
import sys
import os
import time
import subprocess
from .flog_fake_classes import PQHException


class RunCmdException(Exception):
    """
    raised by function @see fn run_cmd
    """
    pass


def get_interpreter_path():
    """
    return the interpreter path
    """
    if sys.platform.startswith("win"):
        return sys.executable.replace("pythonw.exe", "python.exe")
    else:
        return sys.executable


def split_cmp_command(cmd, remove_quotes=True):
    """
    splits a command line
    @param      cmd             command line
    @param      remove_quotes   True by default
    @return                     list
    """
    if isinstance(cmd, str  # unicode#
                  ):
        spl = cmd.split()
        res = []
        for s in spl:
            if len(res) == 0:
                res.append(s)
            elif res[-1].startswith('"') and not res[-1].endswith('"'):
                res[-1] += " " + s
            else:
                res.append(s)
        if remove_quotes:
            nres = []
            for _ in res:
                if _.startswith('"') and _.endswith('"'):
                    nres.append(_.strip('"'))
                else:
                    nres.append(_)
            return nres
        else:
            return res
    else:
        return cmd


def decode_outerr(outerr, encoding, encerror, msg):
    """
    decode the output or the error after running a command line instructions

    @param      outerr      output or error
    @param      encoding    encoding (if None, it is replaced by ascii)
    @param      encerror    how to handle errors
    @param      msg         to add to the exception message
    @return                 converted string

    .. versionchanged:: 1.4
        If *encoding* is None, it is replaced by ``'ascii'``.
    """
    if encoding is None:
        encoding = "ascii"
    typstr = str  # unicode#
    if not isinstance(outerr, bytes):
        raise TypeError(
            "only able to decode bytes, not " + typstr(type(outerr)))
    try:
        out = outerr.decode(encoding, errors=encerror)
        return out
    except UnicodeDecodeError as exu:
        try:
            out = outerr.decode(
                "utf8" if encoding != "utf8" else "latin-1", errors=encerror)
            return out
        except Exception as e:
            out = outerr.decode(encoding, errors='ignore')
            raise Exception("issue with cmd (" + encoding + "):" +
                            typstr(msg) + "\n" + typstr(exu) + "\n-----\n" + out) from e
    raise Exception("complete issue with cmd:" + typstr(msg))


def skip_run_cmd(cmd,
                 sin="",
                 shell=True,
                 wait=False,
                 log_error=True,
                 secure=None,
                 stop_waiting_if=None,
                 do_not_log=False,
                 encerror="ignore",
                 encoding="utf8",
                 change_path=None,
                 communicate=True,
                 preprocess=True,
                 timeout=None,
                 catch_exit=False,
                 fLOG=None):
    """
    has the same signature as @see fn run_cmd but does nothing

    .. versionadded:: 1.0
    """
    return "", ""


def run_cmd(cmd, sin="", shell=True, wait=False, log_error=True, secure=None,
            stop_waiting_if=None, do_not_log=False, encerror="ignore", encoding="utf8",
            change_path=None, communicate=True, preprocess=True, timeout=None, catch_exit=False,
            fLOG=None):
    """
    run a command line and wait for the result
    @param      cmd                 command line
    @param      sin                 sin: what must be written on the standard input
    @param      shell               if True, cmd is a shell command (and no command window is opened)
    @param      wait                call ``proc.wait``
    @param      log_error           if log_error, call fLOG (error)
    @param      secure              if secure is a string (a valid filename), the function stores the output in a file
                                    and reads it continuously
    @param      stop_waiting_if     the function stops waiting if some condition is fulfilled.
                                    The function received the last line from the logs.
    @param      do_not_log          do not log the output
    @param      encerror            encoding errors (ignore by default) while converting the output into a string
    @param      encoding            encoding of the output
    @param      change_path         change the current path if  not None (put it back after the execution)
    @param      communicate         use method `communicate <https://docs.python.org/3.4/library/subprocess.html#subprocess.Popen.communicate>`_ which is supposed to be safer,
                                    parameter ``wait`` must be True
    @param      preprocess          preprocess the command line if necessary (not available on Windows) (False to disable that option)
    @param      timeout             when data is sent to stdin (``sin``), a timeout is needed to avoid waiting for ever (*timeout* is in seconds)
    @param      catch_exit          catch *SystemExit* exception
    @param      fLOG                logging function (if not None, bypass others parameters)
    @return                         content of stdout, stdres  (only if wait is True)
    @rtype      tuple

    .. exref::
        :title: Run a program using the command line)

        @code
        from pyquickhelper.loghelper import run_cmd
        out,err = run_cmd( "python setup.py install", wait=True)
        @endcode

    If you are using this function to run git function, parameter ``shell`` must be True.

    .. versionchanged:: 0.9
        parameters *timeout*, *fLOG* were added,
        the function now works with stdin

    .. versionchanged:: 1.3
        Catches *SystemExit* exception. Add parameter *catch_exit*.

    .. versionchanged:: 1.4
        Changed *fLOG* default value to None.
    """
    if secure is not None:
        with open(secure, "w") as f:
            f.write("")
        add = ">%s" % secure
        if isinstance(cmd, str  # unicode#
                      ):
            cmd += " " + add
        else:
            cmd.append(add)

    if fLOG is not None:
        fLOG("execute", cmd)

    if change_path is not None:
        current = os.getcwd()
        os.chdir(change_path)

    if sys.platform.startswith("win"):

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        if catch_exit:
            try:
                pproc = subprocess.Popen(cmd,
                                         shell=shell,
                                         stdin=subprocess.PIPE if sin is not None and len(
                                             sin) > 0 else None,
                                         stdout=subprocess.PIPE if wait else None,
                                         stderr=subprocess.PIPE if wait else None,
                                         startupinfo=startupinfo)
            except SystemExit as e:
                raise RunCmdException("SystemExit raised (1)") from e

        else:
            pproc = subprocess.Popen(cmd,
                                     shell=shell,
                                     stdin=subprocess.PIPE if sin is not None and len(
                                         sin) > 0 else None,
                                     stdout=subprocess.PIPE if wait else None,
                                     stderr=subprocess.PIPE if wait else None,
                                     startupinfo=startupinfo)

    else:
        cmdl = split_cmp_command(cmd) if preprocess else cmd
        if fLOG is not None:
            fLOG("--linux", cmdl)

        if catch_exit:
            try:
                pproc = subprocess.Popen(cmdl,
                                         shell=shell,
                                         stdin=subprocess.PIPE if sin is not None and len(
                                             sin) > 0 else None,
                                         stdout=subprocess.PIPE if wait else None,
                                         stderr=subprocess.PIPE if wait else None)
            except SystemExit as e:
                raise RunCmdException("SystemExit raised (2)") from e
        else:
            pproc = subprocess.Popen(cmdl,
                                     shell=shell,
                                     stdin=subprocess.PIPE if sin is not None and len(
                                         sin) > 0 else None,
                                     stdout=subprocess.PIPE if wait else None,
                                     stderr=subprocess.PIPE if wait else None)

    if isinstance(cmd, list):
        cmd = " ".join(cmd)

    if wait:

        out = []
        skip_waiting = False

        if communicate:
            input = sin if sin is None else sin.encode()
            if input is not None and len(input) > 0:
                if fLOG is not None:
                    fLOG("input", [input])

            if catch_exit:
                try:
                    if sys.version_info[0] == 2:
                        stdoutdata, stderrdata = pproc.communicate(input=input)
                    else:
                        stdoutdata, stderrdata = pproc.communicate(
                            input=input, timeout=timeout)
                except SystemExit as e:
                    raise RunCmdException("SystemExit raised (3)") from e
            else:
                if sys.version_info[0] == 2:
                    stdoutdata, stderrdata = pproc.communicate(input=input)
                else:
                    stdoutdata, stderrdata = pproc.communicate(
                        input=input, timeout=timeout)

            out = decode_outerr(stdoutdata, encoding, encerror, cmd)
            err = decode_outerr(stderrdata, encoding, encerror, cmd)
        else:
            if catch_exit:
                raise NotImplementedError(
                    "catch_exit and not communicate are incompatible options")
            if sin is not None and len(sin) > 0:
                raise Exception(
                    "communicate should be True to send something on stdin")
            stdout, stderr = pproc.stdout, pproc.stderr

            if secure is None:
                for line in stdout:
                    decol = decode_outerr(line, encoding, encerror, cmd)
                    if fLOG is not None:
                        fLOG(decol.strip("\n\r"))

                    out.append(decol.strip("\n\r"))
                    if stdout.closed:
                        break
                    if stop_waiting_if is not None and stop_waiting_if(decol):
                        skip_waiting = True
                        break
            else:
                last = []
                while pproc.poll() is None:
                    if os.path.exists(secure):
                        with open(secure, "r") as f:
                            lines = f.readlines()
                        if len(lines) > len(last):
                            for line in lines[len(last):]:
                                if fLOG is not None:
                                    fLOG(line.strip("\n\r"))
                                out.append(line.strip("\n\r"))
                            last = lines
                        if stop_waiting_if is not None and len(
                                last) > 0 and stop_waiting_if(last[-1]):
                            skip_waiting = True
                            break
                    time.sleep(0.1)

            if not skip_waiting:
                pproc.wait()

            out = "\n".join(out)
            temp = err = stderr.read()
            try:
                err = decode_outerr(temp, encoding, encerror, cmd)
            except:
                err = decode_outerr(temp, encoding, "ignore", cmd)

            stdout.close()
            stderr.close()

        err = err.replace("\r\n", "\n")
        if fLOG is not None:
            fLOG("end of execution", cmd)

        if len(err) > 0 and log_error and fLOG is not None:
            fLOG("error (log)\n%s" % err)

        if change_path is not None:
            os.chdir(current)

        if sys.platform.startswith("win"):
            return out.replace("\r\n", "\n"), err.replace("\r\n", "\n")
        else:
            return out, err
    else:

        if change_path is not None:
            os.chdir(current)

        return "", ""


def run_script(script, *l):
    """
    run a script
    @param      script      script to execute
    @param      l           other parameters
    @return                 out,err: content of stdout stream and stderr stream
    """
    if not os.path.exists(script):
        raise PQHException("file %s not found" % script)
    py = get_interpreter_path()
    cmd = "%s %s" % (py, script)
    if len(l) > 0:
        typstr = str  # unicode#
        cmd += " " + " ".join([typstr(x) for x in l])
    out, err = run_cmd(cmd)
    return out, err
