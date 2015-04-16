# -*- coding: utf-8 -*-
"""
@file
@brief  Common functions used for @see cl FrameFunction and @see cl FrameParams.
"""
import sys
import os
import copy
import datetime
import hashlib

from ..loghelper.convert_helper import str_to_datetime
from ..loghelper.flog import fLOG, guess_machine_parameter

if sys.version_info[0] == 2:
    from codecs import open


def _private_store(function_name, param):
    """
    Store the parameters into a file, the function adds the parameter in a new line.
    It a parameter is a password (name=password, the password will be encrypted using sha1).

    @param      function_name       name of the function (a unique string, the function is not called)
    @param      param               (dict) list of parameters

    The function replaces every end of line into ``#*###n####*#``.
    """
    param = copy.copy(param)

    rem = []
    for r in param:
        if r.startswith("_"):
            rem.append(r)
    for r in rem:
        del param[r]

    values = guess_machine_parameter()
    filename = os.path.join(
        values["TEMP"], function_name + ".pyquickhelper.txt")
    fLOG("FrameWindows: storing parameters in file: ",
         os.path.abspath(filename))

    if "password" in param or \
            "password1" in param or \
            "password2" in param or \
            "password3" in param:
        param = param.copy()
        for k in ["password", "password1", "password2", "password3"]:
            if k in param:
                param[k] = hashlib.sha1(param[k].encode("utf8")).hexdigest()
        fLOG(
            "this class contains a parameter 'password' --> it will be encrypted")

    history = _private_restore(function_name, pwd=False)

    found = None
    for i, v in enumerate(history):
        if v == param:
            found = i
            break

    if found is not None:
        fLOG("removing one element from history")
        del history[found]
    else:
        fLOG("history length ", len(history))

    history.append(param)

    with open(filename, "w", encoding="utf8") as f:
        for param in history:
            spar = str(param).replace("\n", "#*###n####*#")
            f.write(spar + "\n")


def _private_restore(function_name, pwd=True):
    """
    restore the parameters stored by _private_store,
    returns a list of dictionaries (one of each line stored by _private_store

    @param      function_name       name of the function (a unique string, the function is not called)
    @param      pwd                 empty every password
    @return                         list of dictionaries

    The function replaces every substring ``#*###n####*#`` y end of line.
    """
    values = guess_machine_parameter()
    filename = os.path.join(
        values["TEMP"], function_name + ".pyquickhelper.txt")
    if not os.path.exists(filename):
        fLOG("FrameWindows: unable to find file ", os.path.abspath(filename))
        return []

    fLOG("FrameWindows: loading parameters from file: ",
         os.path.abspath(filename))
    f = open(filename, "r", encoding="utf8")
    s = f.readlines()
    f.close()

    ans = []
    try:
        for line in s:
            ev = eval(line.replace("#*###n####*#", "\n"))
            if pwd:
                if "password3" in ev:
                    ev["password3"] = ""
                if "password2" in ev:
                    ev["password2"] = ""
                if "password1" in ev:
                    ev["password1"] = ""
                if "password" in ev:
                    ev["password"] = ""
            ans.append(ev)
    except Exception as e:
        raise Exception("problem in file " + filename) from e

    return ans


def get_icon():
    """
    returns a filename corresponding the pyquickhelper icon
    @return     filename
    """
    ico = os.path.realpath(
        os.path.join(os.path.split(__file__)[0], "project_ico.ico"))
    return ico


def interpret_parameter(ty, s):
    """
    interprets a parameter

    @param      ty      type (the return type)
    @param      s       value to interpret (a string)
    @return             value
    """

    try:
        if ty in [bool]:
            return s in [True, "True", "true", "TRUE", "1", 1]
        elif ty == datetime.datetime:
            if s is None or len(s) == 0 or s == "None":
                return None
            else:
                return str_to_datetime(s)
        elif ty in [int, float, str]:
            return ty(s)
        elif ty in [None]:
            return None
        elif s == "None":
            return None
        else:
            try:
                return eval(s)
            except Exception as ee:
                fLOG("unable to evaluation ", ee)
                return None
    except Exception:
        fLOG("unable to process value ", ty, " v= ", s, " --> ", None)
        return None
