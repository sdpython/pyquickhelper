# -*- coding: utf-8 -*-
"""
@file
@brief Implements function @see fn run_cmd.
"""
import sys
import os
import time
import subprocess
import threading
import warnings
import re
import queue
from .flog_fake_classes import PQHException


class RunCmdException(Exception):
    """
    Raised by function @see fn run_cmd.
    """
    pass


def get_interpreter_path():
    """
    Returns the interpreter path.
    """
    if sys.platform.startswith("win"):
        return sys.executable.replace("pythonw.exe", "python.exe")
    else:
        return sys.executable


def split_cmp_command(cmd, remove_quotes=True):
    """
    Splits a command line.

    @param      cmd             command line
    @param      remove_quotes   True by default
    @return                     list
    """
    if isinstance(cmd, str):
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
    Decodes the output or the error after running a command line instructions.

    @param      outerr      output or error
    @param      encoding    encoding (if None, it is replaced by ascii)
    @param      encerror    how to handle errors
    @param      msg         to add to the exception message
    @return                 converted string
    """
    if encoding is None:
        encoding = "ascii"
    typstr = str
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


def skip_run_cmd(cmd, sin="", shell=True, wait=False, log_error=True,
                 stop_running_if=None, encerror="ignore",
                 encoding="utf8", change_path=None, communicate=True,
                 preprocess=True, timeout=None, catch_exit=False, fLOG=None,
                 timeout_listen=None, tell_if_no_output=None, prefix_log=None):
    """
    Has the same signature as @see fn run_cmd but does nothing.
    """
    return "", ""


def run_cmd(cmd, sin="", shell=sys.platform.startswith("win"), wait=False, log_error=True,
            stop_running_if=None, encerror="ignore", encoding="utf8",
            change_path=None, communicate=True, preprocess=True, timeout=None,
            catch_exit=False, fLOG=None, tell_if_no_output=None, prefix_log=None):
    """
    Runs a command line and wait for the result.

    @param      cmd                 command line
    @param      sin                 sin: what must be written on the standard input
    @param      shell               if True, cmd is a shell command (and no command window is opened)
    @param      wait                call ``proc.wait``
    @param      log_error           if log_error, call fLOG (error)
    @param      stop_running_if     the function stops waiting if some condition is fulfilled.
                                    The function received the last line from the logs.
                                    Signature: ``stop_waiting_if(last_out, last_err) -> bool``.
                                    The function must return True to stop waiting.
                                    This function can also be used to intercept the standard output
                                    and the standard error while running.
    @param      encerror            encoding errors (ignore by default) while converting the output into a string
    @param      encoding            encoding of the output
    @param      change_path         change the current path if  not None (put it back after the execution)
    @param      communicate         use method `communicate
                                    <https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate>`_
                                    which is supposed to be safer, parameter ``wait`` must be True
    @param      preprocess          preprocess the command line if necessary (not available on Windows)
                                    (False to disable that option)
    @param      timeout             when data is sent to stdin (``sin``), a timeout is needed to avoid
                                    waiting for ever (*timeout* is in seconds)
    @param      catch_exit          catch *SystemExit* exception
    @param      fLOG                logging function (if not None, bypass others parameters)
    @param      tell_if_no_output   tells if there is no output every *tell_if_no_output* seconds
    @param      prefix_log          add a prefix to a line before printing it
    @return                         content of stdout, stdres  (only if wait is True)

    .. exref::
        :title: Run a program using the command line

        ::

            from pyquickhelper.loghelper import run_cmd
            out, err = run_cmd("python setup.py install", wait=True)

    If you are using this function to run :epkg:`git` function, parameter ``shell`` must be True.
    The function catches *SystemExit* exception.
    See `Constantly print Subprocess output while process is running
    <http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running/4417735>`_.
    If *wait* is False, the function returns the started process.
    ``__exit__`` should be called if wait if False.
    Parameter *prefix_log* was added.
    """
    if prefix_log is None:
        prefix_log = ""
    if fLOG is not None:
        if isinstance(cmd, (list, tuple)):
            fLOG(prefix_log + "[run_cmd] execute", " ".join(cmd))
        else:
            fLOG(prefix_log + "[run_cmd] execute", cmd)

    if change_path is not None:
        current = os.getcwd()
        os.chdir(change_path)

    if sys.platform.startswith("win"):
        cmdl = cmd
    else:
        cmdl = split_cmp_command(cmd) if preprocess else cmd

    if catch_exit:
        try:
            pproc = subprocess.Popen(cmdl,
                                     shell=shell,
                                     stdin=subprocess.PIPE if sin is not None and len(
                                         sin) > 0 else None,
                                     stdout=subprocess.PIPE if wait else None,
                                     stderr=subprocess.PIPE if wait else None)
        except SystemExit as e:
            if change_path is not None:
                os.chdir(current)
            raise RunCmdException("SystemExit raised (1)") from e

    else:
        pproc = subprocess.Popen(cmdl,
                                 shell=shell,
                                 stdin=subprocess.PIPE if sin is not None and len(
                                     sin) > 0 else None,
                                 stdout=subprocess.PIPE if wait else None,
                                 stderr=subprocess.PIPE if wait else None)

    pproc.__enter__()
    if isinstance(cmd, list):
        cmd = " ".join(cmd)

    if wait:
        skip_out_err = False
        out = []
        err = []
        err_read = False
        skip_waiting = False

        if communicate:
            # communicate is True
            if tell_if_no_output is not None:
                raise NotImplementedError(
                    "tell_if_no_output is not implemented when communicate is True")
            if stop_running_if is not None:
                raise NotImplementedError(
                    "stop_running_if is not implemented when communicate is True")
            input = sin if sin is None else sin.encode()
            if input is not None and len(input) > 0:
                if fLOG is not None:
                    fLOG(prefix_log + "[run_cmd] input", [input])

            if catch_exit:
                try:
                    stdoutdata, stderrdata = pproc.communicate(
                        input=input, timeout=timeout)
                except SystemExit as e:
                    if change_path is not None:
                        os.chdir(current)
                    raise RunCmdException("SystemExit raised (2)") from e
            else:
                stdoutdata, stderrdata = pproc.communicate(
                    input=input, timeout=timeout)

            out = decode_outerr(stdoutdata, encoding, encerror, cmd)
            err = decode_outerr(stderrdata, encoding, encerror, cmd)
        else:
            # communicate is False: use of threads
            if sin is not None and len(sin) > 0:
                if change_path is not None:
                    os.chdir(current)
                raise Exception(
                    "communicate should be True to send something on stdin")
            stdout, stderr = pproc.stdout, pproc.stderr

            begin = time.perf_counter()
            last_update = begin
            # with threads
            (stdoutReader, stdoutQueue) = _AsyncLineReader.getForFd(
                stdout, catch_exit=catch_exit)
            (stderrReader, stderrQueue) = _AsyncLineReader.getForFd(
                stderr, catch_exit=catch_exit)
            runloop = True

            while (not stdoutReader.eof() or not stderrReader.eof()) and runloop:
                while not stdoutQueue.empty():
                    line = stdoutQueue.get()
                    decol = decode_outerr(
                        line, encoding, encerror, cmd)
                    sdecol = decol.strip("\n\r")
                    if fLOG is not None:
                        fLOG(prefix_log + sdecol)
                    out.append(sdecol)
                    last_update = time.perf_counter()
                    if stop_running_if is not None and stop_running_if(decol, None):
                        runloop = False
                        break

                while not stderrQueue.empty():
                    line = stderrQueue.get()
                    decol = decode_outerr(
                        line, encoding, encerror, cmd)
                    sdecol = decol.strip("\n\r")
                    if fLOG is not None:
                        fLOG(prefix_log + sdecol)
                    err.append(sdecol)
                    last_update = time.perf_counter()
                    if stop_running_if is not None and stop_running_if(None, decol):
                        runloop = False
                        break
                time.sleep(0.05)

                delta = time.perf_counter() - last_update
                if tell_if_no_output is not None and delta >= tell_if_no_output:
                    fLOG(prefix_log + "[run_cmd] No update in {0} seconds for cmd: {1}".format(
                        "%5.1f" % (last_update - begin), cmd))
                    last_update = time.perf_counter()
                full_delta = time.perf_counter() - begin
                if timeout is not None and full_delta > timeout:
                    runloop = False
                    fLOG(prefix_log + "[run_cmd] Timeout after {0} seconds for cmd: {1}".format(
                        "%5.1f" % full_delta, cmd))
                    break

            if runloop:
                # Waiting for async readers to finish...
                stdoutReader.join()
                stderrReader.join()

                # Waiting for process to exit...
                returnCode = pproc.wait()
                err_read = True

                if returnCode != 0:
                    if change_path is not None:
                        os.chdir(current)
                    try:
                        # we try to close the ressources
                        stdout.close()
                        stderr.close()
                    except Exception as e:
                        warnings.warn(
                            "Unable to close stdout and sterr.", RuntimeWarning)
                    if catch_exit:
                        mes = "SystemExit raised with error code {0}\nCMD:\n{1}\nCWD:\n{2}\n#---OUT---#\n{3}\n#---ERR---#\n{4}"
                        raise RunCmdException(mes.format(
                            returnCode, cmd, os.getcwd(), "\n".join(out), "\n".join(err)))
                    raise subprocess.CalledProcessError(returnCode, cmd)

                if not skip_waiting:
                    pproc.wait()
            else:
                out.append("[run_cmd] killing process.")
                fLOG(
                    prefix_log + "[run_cmd] killing process because stop_running_if returned True.")
                pproc.kill()
                err_read = True
                fLOG(prefix_log + "[run_cmd] process killed.")
                skip_out_err = True

            out = "\n".join(out)
            if skip_out_err:
                err = "Process killed."
            else:
                if err_read:
                    err = "\n".join(err)
                else:
                    temp = err = stderr.read()
                    try:
                        err = decode_outerr(temp, encoding, encerror, cmd)
                    except Exception:
                        err = decode_outerr(temp, encoding, "ignore", cmd)
                stdout.close()
                stderr.close()

        # same path for whether communicate is False or True
        err = err.replace("\r\n", "\n")
        if fLOG is not None:
            fLOG(prefix_log + "end of execution", cmd)

        if len(err) > 0 and log_error and fLOG is not None:
            if "\n" in err:
                fLOG(prefix_log + "[run_cmd] stderr (log)")
                for eline in err.split("\n"):
                    fLOG(prefix_log + eline)
            else:
                fLOG(prefix_log + "[run_cmd] stderr (log)\n%s" % err)

        if change_path is not None:
            os.chdir(current)

        pproc.__exit__(None, None, None)
        if sys.platform.startswith("win"):
            if err is not None:
                err = err.strip("\n\r\t ")
            return out.replace("\r\n", "\n"), err.replace("\r\n", "\n")
        else:
            if err is not None:
                err = err.strip("\n\r\t ")
            return out, err
    else:

        if change_path is not None:
            os.chdir(current)

        return pproc, None


def parse_exception_message(exc):
    """
    Parses the message embedded in an exception and returns the standard output and error
    if it can be found.

    @param      exc     exception coming from @see fn run_cmd
    @return             out, err
    """
    mes = str(exc)
    reg = re.compile(".*#---OUT---#(.*)#---ERR---#(.*)", re.DOTALL)
    find = reg.search(mes.replace("\r", ""))
    if find:
        gr = find.groups()
        out, err = gr[0], gr[1]
        return out.strip("\n "), err.strip("\n ")
    else:
        return None, None


def run_script(script, *args, **kwargs):
    """
    Runs a script.

    @param      script      script to execute or command line starting with ``-m``
    @param      args        other parameters
    @param      kwargs      sent to @see fn run_cmd
    @return                 out,err: content of stdout stream and stderr stream

    .. versionchanged:: 1.8
        Add *kwargs*, allows command line starting with ``-m``.
    """
    if not script.startswith('-m') and not os.path.exists(script):
        raise PQHException("file %s not found" % script)
    py = get_interpreter_path()
    cmd = "%s %s" % (py, script)
    if len(args) > 0:
        typstr = str
        cmd += " " + " ".join([typstr(x) for x in args])
    out, err = run_cmd(cmd, **kwargs)
    return out, err


class _AsyncLineReader(threading.Thread):

    def __init__(self, fd, outputQueue, catch_exit):
        threading.Thread.__init__(self)

        assert isinstance(outputQueue, queue.Queue)
        assert callable(fd.readline)

        self.fd = fd
        self.catch_exit = catch_exit
        self.outputQueue = outputQueue

    def run(self):
        if self.catch_exit:
            try:
                for _ in map(self.outputQueue.put, iter(self.fd.readline, b'')):
                    pass
            except SystemExit as e:
                self.outputQueue.put(str(e))
                raise RunCmdException("SystemExit raised (3)") from e
        else:
            for _ in map(self.outputQueue.put, iter(self.fd.readline, b'')):
                pass

    def eof(self):
        return not self.is_alive() and self.outputQueue.empty()

    @classmethod
    def getForFd(cls, fd, start=True, catch_exit=False):
        q = queue.Queue()
        reader = cls(fd, q, catch_exit)

        if start:
            reader.start()

        return reader, q
