# -*- coding: utf-8 -*-
"""
@file

@brief  defines @see cl FrameParams
"""
from .tk_window import create_tk
from .function_helper import private_adjust_parameters
from .storing_functions import _private_restore, _private_store, interpret_parameter

import sys
import os
if sys.version_info[0] == 2:
    import Tkinter as tkinter
else:
    import tkinter


class FrameParams (tkinter.Frame):

    """
    creating a Frame window for a list of parameters
    """

    def __init__(self, parent,
                 restore=True,
                 width=100,
                 raise_exception=False,
                 params=None,
                 help="",
                 key_save="",
                 command_leave=None):
        """
        constructor
        @param      parent          window parent
        @param      restore         if True, check if existing saved parameters are present
        @param      width           number of characters in every Entry field
        @param      raise_exception raise an exception instead of catching it
        @param      params          parameters to overwrite
        @param      help            help to display
        @param      key_save        to make unique the file storing and restoring the parameters
        @param      command_leave   if not None, this function will be called when clicking on Cancel or Leave
        """
        if params is None:
            params = {}

        tkinter.Frame.__init__(self, parent)
        self.fdoc = tkinter.Frame(self)
        self.fpar = tkinter.Frame(self)
        self.fbut = tkinter.Frame(self)
        self.fpar.pack()
        self.fbut.pack()
        self.fdoc.pack()
        self.restore = restore
        self.parent = parent
        self.input = {}
        self.types = {}
        self.raise_exception = raise_exception
        self._added = {}
        self.key_save = key_save
        self.command_leave = command_leave

        # retrieve previous answers
        self._history = []
        self._hpos = -1

        self.info = {"name": "FrameParams", "param": params,
                     "help": help, "key_save": key_save}

        objs = []
        typstr = str  # unicode#

        if restore:
            self._history = _private_restore(
                ".".join([self.info["name"], self.info["key_save"]]))
            if len(self._history) > 0:
                self.info["param"].update(self._history[-1])
                self._hpos = len(self._history) - 1

        for k in self.info["param"]:
            self.types[k] = self.info["param"][k].__class__
            if self.types[k] in [None, None.__class__]:
                self.types[k] = typstr

        # documentation
        tlab = tkinter.Label(self.fdoc, text="Help")
        tlab.pack(side=tkinter.LEFT)
        lab = tkinter.Text(self.fdoc, width=width, height=7)
        lab.pack(side=tkinter.LEFT)
        lab.insert("0.0", self.info["help"])
        objs.append(lab)
        objs.append(tlab)

        scroll = tkinter.Scrollbar(self.fdoc)
        scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        scroll.config(command=lab.yview, width=5)
        lab.config(yscrollcommand=scroll.set)

        # next
        line = 0
        for k in sorted(self.info["param"]):
            if k in self._added:
                continue
            lab = tkinter.Label(self.fpar, text=k)
            lab.grid(row=line, column=0)

            if k in ["password", "password1", "password2", "password3"]:
                lab = tkinter.Entry(self.fpar, width=width, show="*")
            else:
                lab = tkinter.Entry(self.fpar, width=width)

            lab.grid(row=line, column=1)
            if self.info["param"][k] is not None:
                lab.insert("0", typstr(self.info["param"][k]))
            self.input[k] = lab
            objs.append(lab)
            line += 1

        # optional
        for k in sorted(self.info["param"]):
            if k not in self._added:
                continue
            lab = tkinter.Label(self.fpar, text=k)
            lab.grid(row=line, column=0)

            if k in ["password", "password1", "password2", "password3"]:
                lab = tkinter.Entry(self.fpar, width=width, show="*")
            else:
                lab = tkinter.Entry(self.fpar, width=width)

            lab.grid(row=line, column=1)
            if self.info["param"][k] is not None:
                lab.insert("0", typstr(self.info["param"][k]))
            self.input[k] = lab
            objs.append(lab)
            line += 1

        # next: button
        self.cancel = tkinter.Button(self.fbut, text="cancel or leave")
        self.run = tkinter.Button(self.fbut, text="     ok       ")
        self.cancel.pack(side=tkinter.LEFT)
        self.run.pack(side=tkinter.LEFT)
        self.run.bind('<Return>', self.run_function)
        self.run.bind('<Escape>', self.run_cancel)

        self.cancel.config(command=self.run_cancel)
        self.run.config(command=self.run_function)
        private_adjust_parameters(self.info["param"])
        self._already = False

        # up, down
        self.bup = tkinter.Button(self.fbut, text="up")
        self.bdown = tkinter.Button(self.fbut, text="down")
        self.bup.pack(side=tkinter.LEFT)
        self.bdown.pack(side=tkinter.LEFT)
        self.bup.config(command=self.history_up)
        self.bdown.config(command=self.history_down)

        # keys
        for obj in objs + \
                [parent, self, self.bup, self.bdown, self.run, self.cancel, self.fdoc]:
            obj.bind("<Up>", self.history_up)
            obj.bind("<Down>", self.history_down)
            obj.bind("<Return>", self.run_function)
            obj.bind("<Escape>", self.run_cancel)

    def update(self):
        """
        update the parameters (ie ``self.info``)
        """
        typstr = str  # unicode#
        for k in self.input:
            self.input[k].delete(0, tkinter.END)
            self.input[k].insert("0", typstr(self.info["param"].get(k, "")))

    def history_up(self, *args):
        """
        look back in the history (log of used parameters)
        and update the parameters
        """
        if len(self._history) > 0:
            self._hpos = (self._hpos + 1) % len(self._history)
            self.info["param"].update(self._history[self._hpos])
            self.update()

    def history_down(self, *args):
        """
        look forward in the history (log of used parameters)
        and update the parameters
        """
        if len(self._history) > 0:
            self._hpos = (
                self._hpos + len(self._history) - 1) % len(self._history)
            self.info["param"].update(self._history[self._hpos])
            self.update()

    def run_cancel(self, *args):
        """
        what to do when Cancel is pressed
        """
        self.info["param"]["__cancel__"] = True
        if self.command_leave is not None:
            self.command_leave()
        else:
            self.parent.destroy()

    def get_parameters(self):
        """
        returns the parameters

        @return     dictionary
        """
        res = {}
        for k, v in self.input.items():
            s = v.get()
            s = s.strip()
            if len(s) == 0:
                s = None
            ty = self.types[k]
            res[k] = interpret_parameter(ty, s)
        return res

    def get_title(self):
        """
        return the title

        @return self.info ["name"]
        """
        return self.info["name"]

    def refresh(self):
        """
        refresh the screen
        """
        if self._already:
            self.after(1000, self.refresh)
        else:
            self.run.config(state=tkinter.NORMAL)
            if True:
                self.parent.destroy()

    def run_function(self, *args):
        """
        run the function
        """
        if True:
            self.parent.withdraw()
        else:
            self.run.config(state=tkinter.DISABLED)
        self._already = True

        res = self.get_parameters()
        if self.restore:
            _private_store(
                ".".join([self.info["name"], self.info["key_save"]]), res)

        self.info["param"].update(res)
        self.parent.destroy()

    @staticmethod
    def open_window(params,
                    help_string="",
                    title="",
                    top_level_window=None,
                    key_save="",
                    do_not_open=False):
        """
        Open a tkinter window to set up parameters.
        It adds entries for the parameters,
        it displays the help given to this function.
        It also memorizes the latest values used (stored in ``<user>/TEMP folder``).

        @param      help_string             help to de displayed
        @param      top_level_window        if you want this window to depend on a top level window from tkinter
        @param      params                  if not None, overwrite values for some parameters,
                                            it will be updated by the function (= returned value)
        @param      key_save                parameters are saved and restore from a file, key_save will make this file unique
        @param      title                   title of the window
        @param      do_not_open             do not open the window, let you do it
        @return                             new parameters (or a the Windows object if *do_not_open* is True)

        @warning If the string "__cancel__" is present in the results, it means the users clicked on cancel.

        The window looks like:
        @image images/open_window_params.png

        Example:
        @code
        params =  {"velib_key": "", "contract":"Paris"}
        newparams = FrameParams.open_window (params, "fetch data from Velib website")
        @endcode

        .. versionchanged:: 1.0
            Parameter *do_not_open* was added.
        """
        param = params if params is not None else {}

        root = top_level_window if top_level_window is not None else create_tk()
        ico = os.path.realpath(
            os.path.join(os.path.split(__file__)[0], "project_ico.ico"))
        fr = FrameParams(
            root, params=param, help=help_string, key_save=key_save)
        fr.pack()
        root.title(title)
        if ico is not None and top_level_window is None and sys.platform.startswith(
                "win"):
            root.wm_iconbitmap(ico)
        if top_level_window is None:
            fr.focus_set()
        root.focus_set()

        if do_not_open:
            return fr
        else:
            fr.mainloop()
            return param


def open_window_params(params,
                       help_string="",
                       title="",
                       top_level_window=None,
                       key_save="",
                       do_not_open=False):
    """
    Open a tkinter window to set up parameters.
    It adds entries for the parameters,
    it displays the help given to this function.
    It also memorizes the latest values used (stored in <user>/TEMP folder).

    @param      help_string             help to de displayed
    @param      top_level_window        if you want this window to depend on a top level window from tkinter
    @param      params                  if not None, overwrite values for some parameters,
                                            it will be updated by the function (= returned value)
    @param      key_save                parameters are saved and restore from a file, key_save will make this file unique
    @param      title                   title of the window
    @param      do_not_open             do not open the window, let you do it
    @return                             new parameters (or a the Windows object if *do_not_open* is True)

    @warning If the string "__cancel__" is present in the results, it means the users clicked on cancel.

    The window looks like:
    @image images/open_window_params.png

    .. exref::
        :title: Open a tkinter window to ask parameters to a user

        @code
        params = { "user": os.environ.get("USERNAME", os.environ["USER"]),
                "password":"" }
        newparams = open_window_params (params, title="try the password *", help_string = "unit test", key_save="my_key")
        @endcode

        The program opens a window like the following one:

        @image images/open_params.png

        The parameters ``key_save`` can be ignored but if you use this function
        with different parameters, they should all appear after a couple of runs.
        That is because the function uses ``key_save`` ot unique the file uses
        to store the values for the parameters used in previous execution.

    Password are not stored in a text file. You must type them again next time.

    .. versionchanged:: 1.0
        Parameter *do_not_open* was added.
    """
    return FrameParams.open_window(params=params,
                                   help_string=help_string,
                                   title=title,
                                   top_level_window=top_level_window,
                                   key_save=key_save,
                                   do_not_open=do_not_open)
