#-*- coding: utf-8 -*-
"""
@file
@brief  Common functions used for @see cl FrameFunction and @see cl FrameParams.
"""
import os,sys,math, re, os, copy, inspect, datetime, hashlib

from ..loghelper.convert_helper     import str_to_datetime
from ..loghelper.flog               import fLOG, guess_machine_parameter


def _private_store (function_name, param) :
    """
    Store the parameters into a file, the function adds the parameter in a new line.
    It a parameter is a password (name=password, the password will be encrypted using sha1).
    
    @param      function_name       name of the function (a unique string, the function is not called)
    @param      param               list of parameters
    
    The function replaces every end of line into ``#*###n####*#``.
    """
    param       = copy.copy (param)

    rem         = []
    for r in param : 
        if r.startswith ("_") : rem.append (r)
    for r in rem : del param [r]
        
    values   = guess_machine_parameter ()
    filename = os.path.join (values ["TEMP"], function_name + ".pyhome3.txt")
    fLOG("FrameWindows: storing parameters in file: ", os.path.abspath(filename))
    
    if "password" in param :
        param = param.copy()
        param ["password"] = hashlib.sha1(param["password"].encode("utf8")).hexdigest()
        fLOG("this class contains a parameter 'password' --> it will be encrypted")
        
    history = _private_restore (function_name, pwd = False)
    
    found = None
    for i,v in enumerate(history):
        if v == param :
            found = i
            break
    
    if found != None :
        fLOG("removing one element from history")
        del history[found]
    else :
        fLOG("history length ", len(history))
    
    history.append (param)
        
    with open (filename, "w", encoding="utf8") as f :
        for param in history :
            spar = str (param).replace("\n","#*###n####*#")
            f.write (spar + "\n")
    
def _private_restore (function_name, pwd = True) :
    """
    restore the parameters stored by _private_store,
    returns a list of dictionaries (one of each line stored by _private_store
    
    @param      function_name       name of the function (a unique string, the function is not called)
    @param      pwd                 empty every password
    @return                         list of dictionaries
    
    The function replaces every substring ``#*###n####*#`` y end of line.
    """
    values      = guess_machine_parameter ()
    filename    = os.path.join (values ["TEMP"], function_name + ".pyhome3.txt")
    if not os.path.exists (filename) :
        fLOG("FrameWindows: unable to find file ", os.path.abspath(filename))
        return []
        
    fLOG("FrameWindows: loading parameters from file: ", os.path.abspath(filename))
    f = open (filename, "r", encoding="utf8")
    s = f.readlines ()
    f.close ()
    
    ans = [ ]
    try :
        for line in s :
            ev = eval (line.replace("#*###n####*#","\n"))
            if pwd and "password" in ev : ev["password"] = ""
            ans.append(ev)
    except Exception as e :
        fLOG ("problem in file ", filename)
        raise e
    
    return ans
  
def get_icon():
    """
    returns a filename corresponding the pyhome3 icon
    @return     filename
    """
    ico = os.path.realpath (os.path.join (os.path.split (__file__) [0], "project_ico.ico"))
    return ico
    
def interpret_parameter(ty, s) :
    """
    interprets a parameter
    
    @param      ty      type (the return type)
    @param      s       value to interpet (a string)
    @return             value
    """
    
    try :
        if ty in [bool] :
            return s in [True, "True", "true", "TRUE", "1", 1]
        elif ty == datetime.datetime :
            if s == None or len(s) == 0 or s == "None" : return None
            else : return str_to_datetime(s)
        elif ty in [int, float, str] :
            return ty (s)
        elif ty in [None] :
            return None
        elif s == "None" :
            return None
        else :
            try :
                return eval (s)
            except Exception as s :
                fLOG ("unable to evaluation ", s)
                return None
    except Exception as e :
        fLOG ("unable to process value ", k, " v= ", s, " --> ", None)
        return None
    
