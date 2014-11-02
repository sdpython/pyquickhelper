#-*- coding: utf-8 -*-
"""
@file
@brief  @see cl FrameFunction
"""
import sys, os, inspect, threading, tkinter, io
import tkinter.font as tkFont
import tkinter.tix as tix
    
from ..loghelper.flog               import fLOG, GetLogFile
from .function_helper               import has_unknown_parameters, extract_function_information, private_adjust_parameters, private_get_function
from .storing_functions             import _private_restore, _private_store, interpret_parameter

class FrameFunction (tkinter.Frame) :
    """
    Creating a Frame window for a function.
    
    It will create an entry control for every parameter.
    If one of the parameter is 'password', the window will show only stars.
    The windows proposes to store the value and to restore them on the next call.
    This functionality is disable when 'password' is present in the list of parameters.
    """
    
    def __init__ (self, parent, 
                        function, 
                        restore         = True, 
                        width           = 100, 
                        raise_exception = False, 
                        overwrite       = None,
                        hide            = False,
                        command_leave   = None,
                        key_save        = "e") :
        """
        constructor
        @param      parent          window parent
        @param      function        function object (can be a string)
        @param      restore         if True, check if existing saved parameters are present
        @param      width           number of characters in every Entry field
        @param      raise_exception raise an exception instead of catching it
        @param      overwrite       parameters to overwrite
        @param      hide            if True, hide the window after clicking on OK
        @param      command_leave   if not None, this function will be called when clicking on Cancel or Leave
        @param      key_save        suffix to add to the filename used to store parameters
        """
        if overwrite is None:
            overwrite = { }

        tkinter.Frame.__init__ (self, parent)
        self.fdoc       = tkinter.Frame (self)
        self.fpar       = tkinter.Frame (self)
        self.flog       = tkinter.Frame (self)
        self.fbut       = tkinter.Frame (self)
        self.fpar.pack ()
        self.fbut.pack ()
        self.flog.pack ()
        self.fdoc.pack ()
        self.restore    = restore
        self.parent     = parent
        self.input      = { }
        self.types      = {}
        self.hide       = hide
        self.raise_exception = raise_exception
        self._added     = { }
        self.command_leave = command_leave
        self._suffix    = key_save
        
        # retieve previous answers
        self._history  = [ ]
        self._hpos     = -1
        
        if isinstance (function, str) :
            if self.hide :
                fLOG (__file__, function) #, OutputPrint = False)
            else :
                fLOG (__file__, function, #, OutputPrint = False, 
                            LogFile = io.StringIO ())
                            
            function = private_get_function (function)
            self.function   = function
            self.info       = extract_function_information (function)
            
        else :
            self.function   = function
            self.info       = extract_function_information (function)
            
            if self.hide :
                fLOG (__file__, self.info ["name"], #, OutputPrint = False, 
                            LogFile = io.StringIO ())
            else :
                fLOG (__file__, self.info ["name"], #, OutputPrint = False, 
                            LogFile = io.StringIO ())
            
        if restore : 
            self._history = _private_restore (self.info ["name"] + "." + self._suffix)
            if len(self._history) > 0 :
                self.info ["param"].update (self._history[-1])
                self._hpos = len(self._history)-1
            
        for k in self.info ["param"]:
            self.types [k] = self.info ["types"][k]
            if self.types [k] in [None, None.__class__] : 
                self.types [k] = str
        
        tlab = tkinter.Label(self.fdoc, text = "Help")
        tlab.pack (side = tkinter.LEFT)
        lab = tkinter.Text (self.fdoc, width = width, height = 7)
        lab.pack (side=tkinter.LEFT)
        lab.insert ("0.0", self.info ["help"])
        
        objs = [ lab, tlab ]
        
        scroll=tkinter.Scrollbar(self.fdoc)
        scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        scroll.config(command=lab.yview, width=5)
        lab.config(yscrollcommand = scroll.set)        
                
        self.fdoc.bind('<Return>', self.run_function)
        self.fdoc.bind('<Escape>', self.run_cancel)
        
        # overwrite parameters
        if overwrite is not None :
            for k in self.info ["param"] :
                if k in overwrite :
                    self.info ["param"][k] = overwrite [k]

        # optional parameters in **params
        has = has_unknown_parameters (function)
        if has and overwrite is not None :
            add = []
            for a,b in overwrite.items () :
                if a not in self.info ["param"] :
                    add.append ((a,b))
            for a,b in add :
                self.info ["param"][a] = b
                self.types [a] = type (b)
                
        params = inspect.getargspec(function)[0]
        self._added = [ _ for _ in self.info ["param"] if _ not in params]
        
        self.fpar.bind('<Return>', self.run_function)
        self.fpar.bind('<Escape>', self.run_cancel)
                        
        # next
        line = 0
        for k in sorted (self.info ["param"]) :
            if k in self._added : continue
            lab = tkinter.Label (self.fpar, text = k)
            lab.grid (row = line, column = 0)
            
            if k in ["password", "password1", "password2", "password3"] :
                lab = tkinter.Entry (self.fpar, width = width, show = "*")
            else :
                lab = tkinter.Entry (self.fpar, width = width)
            
            lab.grid (row = line, column = 1)
            if self.info ["param"][k] is not None :
                lab.insert ("0", str (self.info ["param"][k]))
            self.input [k] = lab
            objs.append(lab)
            line += 1

        # optional
        for k in sorted (self.info ["param"]) :
            if k not in self._added : continue
            lab = tkinter.Label (self.fpar, text = k)
            lab.grid (row = line, column = 0)
            
            if k in ["password", "password1", "password2", "password3"] :
                lab = tkinter.Entry (self.fpar, width = width, show = "*")
            else :
                lab = tkinter.Entry (self.fpar, width = width)
            
            lab.grid (row = line, column = 1)
            if self.info ["param"][k] is not None :
                lab.insert ("0", str (self.info ["param"][k]))
            self.input [k] = lab
            objs.append(lab)
            line += 1

        # next
        tex = tkinter.Text (self.flog, width = int(width*3/2), height = 15)
        tex.pack ()
        self.LOG = tex
        tex.config (font = tkFont.Font (family = "Courrier New", size = 8))
        
        self.cancel = tkinter.Button (self.fbut, text = "cancel or leave")
        self.run    = tkinter.Button (self.fbut, text = "     run       ")
        self.cancel.pack (side = tkinter.LEFT)
        self.run.pack (side = tkinter.LEFT)
        
        self.cancel.config (command = self.run_cancel)
        self.run.config (command = self.run_function)
        private_adjust_parameters (self.info ["param"])
        self._already = False
        
        # up, down
        self.bup   = tkinter.Button (self.fbut, text = "up")
        self.bdown = tkinter.Button (self.fbut, text = "down")
        self.bup.pack (side = tkinter.LEFT)
        self.bdown.pack (side = tkinter.LEFT)
        self.bup.config (command = self.history_up)
        self.bdown.config (command = self.history_down)
        
        # keys
        for obj in objs + [ tex, parent, self, self.bup, self.bdown, self.run, self.cancel, self.fdoc ] :
            obj.bind("<Up>", self.history_up)        
            obj.bind("<Down>", self.history_down)        
            obj.bind("<Return>", self.run_function)        
            obj.bind("<Escape>", self.run_cancel)        
        
    def update (self):
        """
        update the parameters (ie ``self.info``)
        """
        for k in self.input :
            self.input[k].delete(0, tkinter.END)
            self.input[k].insert ("0", str (self.info ["param"].get(k,"")))
        
    def history_up(self, *args) :
        """
        look back in the history of used parameters and change the parameters
        """
        if len(self._history) > 0 :
            self._hpos = (self._hpos+1) % len(self._history)
            self.info ["param"].update (self._history[self._hpos])
            self.update()
        
    def history_down(self, *args):
        """
        look forward in the history of used parameters and change the parameters
        """
        if len(self._history) > 0 :
            self._hpos = (self._hpos+len(self._history)-1) % len(self._history)
            self.info ["param"].update (self._history[self._hpos])
            self.update()
            
    def stop_thread(self):
        """
        stops the function execution
        """
        if "thread_started" in self.__dict__ :
            for th in self.thread_started :
                if th.is_alive():
                    if not th.daemon :
                        raise Exception("the thread is not daemon, this case should not happen")
                    th._stop()
            
    def destroy(self) :
        """
        Stops the thread and destroy the function
        
        The behaviour of method 
        `Thread._stop <http://hg.python.org/cpython/file/3.4/Lib/threading.py>`_
        changed in Python 3.4,
        see the `discussion <https://groups.google.com/forum/#!topic/comp.lang.python/sXXwTh9EHsI>`_.
        """
        self.stop_thread()
        if self.command_leave is not None :
            f = self.command_leave
            self.command_leave = None
            f()
        else :
            try:
                tkinter.Frame.destroy(self)
            except Exception as e :
                if "application has been destroyed" in str(e) :
                    os._exit(0)
            
    def run_cancel(self, *args) :
        """
        cancel
        """
        if self.command_leave is not None :
            f = self.command_leave
            self.command_leave = None
            f()
        else :
            self.parent.destroy()
        
    def get_parameters (self) :
        """
        returns the parameters in a dictionary
        
        @return     dictionary
        """
        res = { }
        for k,v in self.input.items () :
            s = v.get ()
            s = s.strip ()
            if len (s) == 0 : s = None
            ty = self.types [k]
            res[k] = interpret_parameter(ty, s)
        return res
                
    def get_title (self) :
        """
        @return self.info ["name"]
        """
        return self.info ["name"]
        
    def refresh (self) :
        """
        refresh the screen
        """
        temp = self.LOG.get ("0.0", "end")
        log  = GetLogFile().getvalue ()
        log  = log [len(temp):]
        
        try :
            self.LOG.insert ("end", log)
        except :
            self.LOG.insert ("end", "\n".join (repr (log).split ("\n")))
        self.LOG.see ("end")

        if self._already :
            self.after (1000, self.refresh)
        else :
            self.run.config (state = tkinter.NORMAL)
            if self.hide :
                self.parent.destroy ()
        
    def run_function (self, *args) :
        """
        run the function
        """
        if self.hide :  self.parent.withdraw ()
        else :          self.run.config (state = tkinter.DISABLED)
        self._already = True
        
        res = self.get_parameters ()
        if self.restore :
            _private_store (self.info ["name"] + "." + self._suffix, res)
            
        self._history.append(res)
        
        for k in sorted (res) :
            if k in ["password", "password1", "password2", "password3"] :
                fLOG ("parameter ", k, " = ****")
            else :
                fLOG ("parameter ", k, " = ", res [k], " type ", type(res[k]))
        fLOG ("------------------------")
        
        self.after (100, self.refresh)
        th = FrameFunction_ThreadFunction (self, res)
        th.daemon=True
        th.start ()
        if "thread_started" not in self.__dict__ :
            self.thread_started = []
        self.thread_started.append(th)
        
    @staticmethod
    def open_window(func, 
                    top_level_window = None,
                    params = None,
                    key_save = "f") :
                                
        """
        Open a tkinter window to run a function. It adds entries for the parameters,
        it displays the help associated to this function,
        and it allows use to run the function in a window frame. 
        Logs are also displayed.
        It also memorizes the latest values used (stored in <user>/TEMP folder).
        
        @param      func                    function (function object)
        @param      top_level_window        if you want this window to depend on a top level window from tkinter
        @param      params                  if not None, overwrite values for some parameters
        @param      key_save                suffix added to the file used to store the parameters
        
        The window looks like:
        @image images/open_window_function.png
        
        Example:
        @code
        FrameFunction.open_window (file_head)
        @endcode
        """
        param   = params if params != None else {  }

        root = top_level_window if top_level_window is not None else tkinter.Tk ()
        ico  = os.path.realpath (os.path.join (os.path.split (__file__) [0], "project_ico.ico"))
        fr   = FrameFunction (root, func, overwrite = param, hide = False)
        fr.pack ()
        root.title (fr.get_title ())
        if ico is not None and top_level_window is None and sys.platform.startswith("win") :
            root.wm_iconbitmap(ico)
        if top_level_window is None : fr.focus_set()
        root.focus_set()
        fr.mainloop ()
        
class FrameFunction_ThreadFunction (threading.Thread) :
    """
    class associated to FrameFunction, it runs the function
    is a separate thread (in order to be able to stop its execution
    from the interface).
    """
    
    def __init__ (self, framewindow, parameter) :
        """
        constructor
        """
        threading.Thread.__init__(self)# ne pas oublier cette ligne
        self.framewindow = framewindow
        self.parameter   = parameter
        
    def run (self) :
        """
        run the thread
        """
        if "function" in self.framewindow.__dict__ :
            function = self.framewindow.function
        else :
            function = None
        param = self.parameter # self.framewindow.info ["param"]
        
        if function is not None :
            if not self.framewindow.raise_exception :
                try : 
                    ret = function (**param)
                except Exception as e :
                    fLOG ("------------------------------ END with exception")
                    fLOG (type (e))
                    fLOG (str (e))
                    ret = None
                    fLOG ("------------------------------ details")
                    import traceback
                    st = traceback.format_exc()
                    fLOG(st)
            else :
                ret = function (**param)
        else :
            ret = None
        
        fLOG ("END")
        fLOG ("result:")
        fLOG(ret)
        self.framewindow._already = False
                        
def open_window_function (  func, 
                            top_level_window = None,
                            params = None,
                            key_save = "f") :

    """
    Open a tkinter window to run a function. It adds entries for the parameters,
    it displays the help associated to this function,
    and it allows use to run the function in a window frame. 
    Logs are also displayed.
    It also memorizes the latest values used (stored in ``<user>/TEMP folder``).
    
    @param      func                    function (function object)
    @param      top_level_window        if you want this window to depend on a top level window from tkinter
    @param      params                  if not None, overwrite values for some parameters
    @param      key_save                suffix added to the file used to store the parameters
    
    The window looks like:
    @image images/open_window_function.png
    
    @example(open a tkinter windows to run a function)
    @code
    open_window_function (test_regular_expression)
    @endcode
    
    The functions opens a window which looks like the following one:
    
    @image images/open_function.png
        
    The parameters ``key_save`` can be ignored but if you use this function
    with different parameters, they should all appear after a couple of runs.
    That is because the function uses ``key_save`` ot unique the file uses
    to store the values for the parameters used in previous execution.
    @endexample
    """
    FrameFunction.open_window ( func = func,
                                top_level_window = top_level_window, 
                                params = params,
                                key_save = key_save )

        
