# -*- coding: utf-8 -*-
"""
@file
@brief Implements function @see fn run_cmd.
"""
import sys
import os
import pprint
import subprocess
import textwrap
import traceback
import pickle
from multiprocessing import Pool, freeze_support


def execute_script(code, folder=None, filename="_temp_custom_run_script_.py", check=True):
    """
    Executes a :epkg:`python` script in a separate process.

    @param      code        python script
    @param      folder      write the script in a folder then runs it,
                            it None, the function uses a Pool to execute
                            the script
    @param      filename    name of the scrit to write
    @param      check       checks that the output is not empty
    @return                 dictionary with local variables
    """
    addition = textwrap.dedent("""
        loc = locals().copy()
        try:
            data = {'__file__': __file__}
        except NameError:
            data = {}
        import pickle
        for k, v in loc.items():
            if v is None or isinstance(v, (str, int, float, tuple, list, dict, set)):
                try:
                    pickle.dumps(v)
                except Exception:
                    # not pickable
                    continue
                data[k] = v
        __CHECK__
        pkl = pickle.dumps(data)
    """)
    if check:
        checkc = textwrap.dedent("""
        if len(data) == 0:
            import pprint
            raise RuntimeError("data cannot be empty.\\n{}".format(pprint.pformat(loc)))
        """)
    else:
        checkc = ""
    addition = addition.replace("__CHECK__", checkc)
    new_code = "\n".join([code, "", addition])
    if folder is None:
        try:
            obj = compile(new_code, '', 'exec')
        except Exception:
            excs = traceback.format_exc()
            return {'ERROR': excs, 'code': new_code}
        lo = {}
        gl = {}
        try:
            exec(obj, gl, lo)
        except Exception:
            excs = traceback.format_exc()
            return {'ERROR': excs, 'code': new_code}

        pkl = lo['pkl']
        loc = pickle.loads(pkl)
        return loc
    else:
        name = os.path.join(folder, filename)
        data = name + ".pkl"
        new_code = new_code + \
            "\nwith open('{}', 'wb') as f: f.write(pkl)".format(
                data.replace("\\", "/"))
        with open(name, "w", encoding="utf-8") as f:
            f.write(new_code)
        cmdl = "{0} -u {1}".format(sys.executable, name)
        proc = subprocess.Popen(cmdl, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        _, errs = proc.communicate()
        if errs:
            return {'ERROR': errs.decode('utf-8', errors="ignore")}
        with open(data, "rb") as f:
            loc = pickle.load(f)
        return loc


def execute_script_get_local_variables(script, folder=None,
                                       filename="_temp_custom_run_script_.py",
                                       check=True):
    """
    Executes a script and returns the local variables.

    @param      script      filename or code
    @param      folder      write the script in a folder then runs it,
                            it None, the function uses a Pool to execute
                            the script
    @param      filename    name of the scrit to write
    @param      check       checks that the output is not empty
    @return                 dictionary
    """
    if "\n" not in script and os.path.exists(script):
        with open(script, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = script

    if folder is None:
        with Pool(1, None, None, None) as p:
            res = p.map(execute_script, [content])
        if len(res) != 1:
            raise RuntimeError("Something went wrong with content\n{}".format(
                content))
        return res[0]
    else:
        return execute_script(content, folder, filename, check=check)


def dictionary_as_class(dico):
    """
    Every key of dictionary ``dico`` becomes
    a member of a dummy class.

    @param      dico        dictionary
    @return                 class
    """
    class dummy_class:
        def __str__(self):
            data = {k: v for k, v in self.__dict__.items()
                    if not k.startswith("_")}
            return pprint.pformat(data)

    du = dummy_class()

    for k, v in dico.items():
        if not isinstance(k, str):
            raise TypeError("Key '{}' must be a string.".format(k))
        setattr(du, k, v)
    return du


if __name__ == '__main__':
    freeze_support()
