"""
@file
@brief :epkg:`pytest` is sometimes slow. This file provides helpers to
easily run test function.
"""
import os
import importlib
import re
import warnings
import time
from traceback import format_exc
from inspect import signature


class TestExecutionError(RuntimeError):
    """
    Raised when the execution of a test fails.
    """

    def __init__(self, module, name, exc):
        """
        @param      module      module
        @param      name        function name
        @param      exc         exception
        """
        if name is None and isinstance(exc, list):
            msg = "Test module '{}' failed\n---\n{}".format(
                module.__name__, "\n---\n".join(str(_) for _ in exc))
            RuntimeError.__init__(self, msg)
        elif name is not None:
            msg = "Function '{}' from module '{}' failed due to '{}'\n{}".format(
                name, module.__name__, exc, format_exc())
            RuntimeError.__init__(self, msg)
        else:
            raise RuntimeError(  # pragma: no cover
                "Unknown test error.")


def run_test_function(module, pattern="^test_.*", stop_first=False, verbose=False, fLOG=print):
    """
    Runs test functions from *module*.

    :param module: module (string or module)
    :param pattern: function pattern
    :param stop_first: stops at the first error or run all of them
    :param verbose: prints out the name of the functions
    :param fLOG: logging function

    The following piece of code could also be used to
    run all tests not using any parameter.

    ::

        fcts = [v for k, v in locals().items() if k.startswith('test_')]
        for fct in fcts:
            print("run", fct.__name__)
            try:
                fct()
            except Exception as e:
                if 'missing' in str(e):
                    print(e)
                    continue
                raise e
    """
    if isinstance(module, str):
        module_path = module
        module = os.path.splitext(module)[0]
        _, module_name = os.path.split(os.path.splitext(module)[0])
        with warnings.catch_warnings(record=False):
            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            if spec is None:
                raise ImportError(  # pragma: no cover
                    "Cannot import module '{}' from '{}'.".format(
                        module_name, module_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
    if module is None:
        raise ValueError(  # pragma: no cover
            "module must be specified.")

    reg = re.compile(pattern)
    fcts = []
    for name, fct in module.__dict__.items():
        if not reg.search(name):
            continue
        if not callable(fct):
            continue  # pragma: no cover
        sig = signature(fct)
        if sig.parameters:
            continue
        fcts.append((name, fct))

    excs = []
    tested = []
    i = 0
    for name, fct in fcts:

        t0 = time.perf_counter()
        with warnings.catch_warnings(record=False):
            try:
                fct()
                exc = None
            except Exception as e:
                exc = TestExecutionError(module, name, e)
                if stop_first:
                    raise exc
                excs.append(exc)
        dt = time.perf_counter() - t0
        if verbose:
            fLOG(  # pragma: no cover
                "[run_test_function] {}/{}: {} '{}' in {:0.000}s".format(
                    i + 1, len(fcts), 'OK' if exc is None else '--', name, dt))
        tested.append(name)
        i += 1

    if len(excs) > 0:
        raise TestExecutionError(module, None, excs)
    if len(tested) == 0:
        raise ValueError(
            "No function found in '{}' with pattern '{}'.".format(module, pattern))
