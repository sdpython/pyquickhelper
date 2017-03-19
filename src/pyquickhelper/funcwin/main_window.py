# -*- coding: utf-8 -*-
"""
@file

@brief  building windows to use a function and specify its parameter based on a python function
"""
from .tk_window import create_tixtk
from .frame_function import FrameFunction
from .storing_functions import get_icon

import os
import sys
if sys.version_info[0] == 2:
    import Tkinter as tkinter
    import Tix as tix
else:
    import tkinter
    import tkinter.tix as tix


class MainFrame(tkinter.Frame):

    """
    Creating a Frame window to select within a list of functions

    @see cl FrameFunction

    The class requires to run ``tix.Tk()`` and not ``tkinter.Tk()``. Otherwise,
    you will see the following error:
    @code
    _tkinter.TclError: invalid command name "tixComboBox"
    @endcode

    It is required by the use of ``ComboBox``.
    @see fn main_loop_functions to see what the window will look like.
    """

    def __init__(self, parent, functions, first=None, restore=True, width=100,
                 raise_exception=False, overwrite=None, hide=False):
        """
        constructor
        @param      parent          window parent
        @param      functions       dictionary with a list of functions { name: function }
        @param      first           first function to select
        @param      restore         if True, check if existing saved parameters are present
        @param      width           number of characters in every Entry field
        @param      raise_exception raise an exception instead of catching it
        @param      overwrite       parameters to overwrite
        @param      hide            if True, hide the window after clicking on OK
        """
        if overwrite is None:
            overwrite = {}
        tkinter.Frame.__init__(self, parent)
        self.kparent = parent
        self.fsel = tkinter.Frame(self)
        self.ffun = tkinter.Frame(self)
        hline = tkinter.Frame(self, height=10, width=800, bg="blue")
        self.fsel.pack()
        hline.pack()
        self.ffun.pack()
        self.parent = parent

        self.varcombo = tix.StringVar()
        self.combo = tix.ComboBox(self.fsel, editable=1, dropdown=1, variable=self.varcombo,
                                  command=self.change_selection,
                                  options="listbox.height %d label.width %d entry.width %d" % (25, 30, 50))
        # put the text zone in read only mode
        self.combo.entry.config(state='readonly')
        for i, k in enumerate(sorted(functions)):
            self.combo.insert(i, k)
        self.combo.pack()
        self.functionsDict = functions

        if first is None:
            keys = sorted(functions.keys())
            first = keys[0]
        firstFunction = functions[first]

        self.params = {"restore": restore, "width": width,
                       "raise_exception": raise_exception,
                       "overwrite": overwrite, "hide": hide}

        self.varcombo.set(first)
        self.change_frame_function(firstFunction)

    def run_cancel(self, *args):
        """
        cancel
        """
        try:
            self.kparent.destroy()
        except Exception as e:
            if "application has been destroyed" in str(e):
                return
            else:
                raise e

        if "selected" in self.__dict__ and "server" in self.selected.__name__:
            # trick: the server does not close itself
            # forcing to close
            # sys.exit() can only be used from the main thread
            os._exit(0)

    def get_title(self):
        """
        return the default title
        @return     string
        """
        return self.frameWindow.get_title()

    def change_frame_function(self, function):
        """
        update the frame FrameWindow to select a new function

        @param    function      a function (a pointer)
        """
        if "selected" not in self.__dict__ or function != self.selected:
            self.selected = function

        if hasattr(self, "frameWindow"):
            self.frameWindow.pack_forget()

        self.frameWindow = FrameFunction(self.ffun,
                                         function,
                                         restore=self.params["restore"],
                                         width=self.params["width"],
                                         raise_exception=self.params[
                                             "raise_exception"],
                                         overwrite=self.params["overwrite"],
                                         hide=self.params["hide"],
                                         command_leave=self.run_cancel)
        self.frameWindow.pack()
        self.frameWindow.focus_set()

    def change_selection(self, event):
        """
        functions called when the selection changes
        """
        st = self.varcombo.get()
        if "functionsDict" in self.__dict__:
            self.change_frame_function(self.functionsDict[st])


def main_loop_functions(functions, first=None, restore=True, width=100,
                        raise_exception=False, overwrite=None, hide=False, title=None,
                        ico=None, init_pos=None, mainloop=True):
    """
    uses @see cl MainFrame as the main window

    @param      functions       dictionary with a list of functions { name: function }
    @param      first           first function to select
    @param      restore         if True, check if existing saved parameters are present
    @param      width           number of characters in every Entry field
    @param      raise_exception raise an exception instead of catching it
    @param      overwrite       parameters to overwrite
    @param      hide            if True, hide the window after clicking on OK
    @param      title           if not None, overwrite the default title
    @param      ico             (str) an icon or None
    @param      init_pos        location of the window *(x,y)* or None
    @param      mainloop        run the mainloop
    @return                     main window

    .. exref::
        :title: Open a window to run a function from a predefined list of functions

        @code
        functions = {   "test_regular_expression":test_regular_expression,
                        "test_edit_distance":file_grep,
                        "file_head":file_head }
        main_loop_functions ( functions, title = "title: TestMakeWindow2")
        @endcode

        @image images/open_functionl.png

    """
    if overwrite is None:
        overwrite = {}

    ico = get_icon() if ico is None else ico
    root = create_tixtk()
    root.iconbitmap(ico)
    fr = MainFrame(parent=root, functions=functions, first=first, restore=restore,
                   width=width, raise_exception=raise_exception, overwrite=overwrite,
                   hide=hide)
    fr.pack()
    root.title(fr.get_title() if title is None else title)
    if init_pos is not None:
        root.geometry('+%d+%d' % init_pos)
    if mainloop:
        fr.mainloop()
    return fr
