#-*- coding: utf-8 -*-
"""
@file

@brief  building windows to use a function and specify its parameter based on a python function
"""
import os, tkinter
import tkinter.tix as tix

from .frame_function        import FrameFunction
from .storing_functions     import get_icon

class MainFrame(tkinter.Frame) :
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

    def __init__ (self, parent,
                        functions,
                        first           = None,
                        restore         = True,
                        width           = 100,
                        raise_exception = False,
                        overwrite       = None,
                        hide            = False) :
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
        tkinter.Frame.__init__ (self, parent)
        self.kparent    = parent
        self.fsel       = tkinter.Frame (self)
        self.ffun       = tkinter.Frame (self)
        hline           = tkinter.Frame(self,height=10,width=800,bg="blue")
        self.fsel.pack ()
        hline.pack()
        self.ffun.pack ()
        self.parent     = parent

        self.varcombo = tix.StringVar()
        self.combo = tix.ComboBox(self.fsel,
                                        editable=1,
                                        dropdown=1,
                                        variable=self.varcombo,
                                        command = self.change_selection,
                                        options="listbox.height %d label.width %d entry.width %d" % (25, 30, 50))
        self.combo.entry.config(state='readonly')  ## met la zone de texte en lecture seule
        for i,k in enumerate(sorted(functions)) :
            self.combo.insert(i, k)
        self.combo.pack()
        self.functionsDict = functions

        if first is None :
            keys = list (functions.keys())
            keys.sort()
            first = keys[0]
        firstFunction = functions[first]

        self.params = { "restore":restore,
                        "width":width,
                        "raise_exception":raise_exception,
                        "overwrite":overwrite,
                        "hide":hide }

        self.varcombo.set(first)
        self.change_frame_function (firstFunction)

    def run_cancel(self, *args) :
        """
        cancel
        """
        try :
            self.kparent.destroy()
        except Exception as e :
            if "application has been destroyed" in str(e) :
                return
            else :
                raise e

        if "selected" in self.__dict__ and "server" in self.selected.__name__ :
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

    def change_frame_function (self, function):
        """
        update the frame FrameWindow to select a new function

        @param    function      a function (a pointer)
        """
        if "selected" not in self.__dict__ or function != self.selected :
            self.selected = function

        if "frameWindow" in self.__dict__ :
            self.frameWindow.pack_forget()

        self.frameWindow = FrameFunction (self.ffun,
                        function,
                        restore         = self.params["restore"],
                        width           = self.params["width"],
                        raise_exception = self.params["raise_exception"],
                        overwrite       = self.params["overwrite"],
                        hide            = self.params["hide"],
                        command_leave   = self.run_cancel)
        self.frameWindow.pack()
        self.frameWindow.focus_set()

    def change_selection(self, event) :
        """
        functions called when the selection changes
        """
        st = self.varcombo.get()
        if "functionsDict" in self.__dict__ :
            self.change_frame_function(self.functionsDict[st])


def main_loop_functions (  functions,
                        first           = None,
                        restore         = True,
                        width           = 100,
                        raise_exception = False,
                        overwrite       = None,
                        hide            = False,
                        title           = None,
                        ico             = None) :
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

    @example(open a window to run a function from a predefined list of functions)
    @code
    functions = {   "test_regular_expression":test_regular_expression,
                    "test_edit_distance":file_grep,
                    "file_head":file_head }
    main_loop_functions ( functions, title = "title: TestMakeWindow2")
    @endcode

    @image images/open_functionl.png

    @endexample
    """
    if overwrite is None:
        overwrite = {}

    ico = get_icon() if ico is None else ico
    root = tix.Tk ()
    root.wm_iconbitmap(ico)
    fr   = MainFrame (  parent          = root,
                        functions       = functions,
                        first           = first,
                        restore         = restore,
                        width           = width,
                        raise_exception = raise_exception,
                        overwrite       = overwrite,
                        hide            = hide)
    fr.pack ()
    root.title (fr.get_title () if title is None else title)
    fr.mainloop ()