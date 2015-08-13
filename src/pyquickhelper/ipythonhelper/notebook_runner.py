"""
@file
@brief Modified version of `runipy.notebook_runner <https://github.com/paulgb/runipy/blob/master/runipy/notebook_runner.py>`_.
"""

import os
import re
import time
import io
import sys
from queue import Empty


try:
    from nbformat.v3 import NotebookNode
    from nbformat import writes
    from jupyter_client import KernelManager
except ImportError:
    from IPython.nbformat.v3 import NotebookNode
    from IPython.nbformat import writes
    from IPython.kernel import KernelManager
from ..loghelper.flog import noLOG

if sys.version_info[0] == 2:
    from codecs import open


class NotebookError(Exception):

    """
    custom exception
    """
    pass


class NotebookRunner(object):

    """
    The kernel communicates with mime-types while the notebook
    uses short labels for different cell types. We'll use this to
    map from kernel types to notebook format types.

    This classes executes a notebook end to end.
    """

    #. available output types
    MIME_MAP = {
        'image/jpeg': 'jpeg',
        'image/png': 'png',
        'text/plain': 'text',
        'text/html': 'html',
        'text/latex': 'latex',
        'application/javascript': 'html',
        'image/svg+xml': 'svg',
    }

    def __init__(self, nb, profile_dir=None, working_dir=None,
                 comment="", fLOG=noLOG, theNotebook=None, code_init=None):
        """
        constuctor

        @param      nb              notebook as JSON
        @param      profile_dir     profile directory
        @param      working_dir     working directory
        @param      comment         additional information added to error message
        @param      theNotebook     if not None, populate the variable *theNotebook* with this value in the notebook
        @param      code_init       to initialize the notebook with a python code as if it was a cell
        @param      fLOG            logging function

        .. versionchanged:: 1.1
            Parameters *theNotebook*, *code_init* were added.
        """
        self.km = KernelManager()
        self.fLOG = fLOG
        self.theNotebook = theNotebook
        self.code_init = code_init
        args = []

        if profile_dir:
            args.append('--profile-dir=%s' % os.path.abspath(profile_dir))

        cwd = os.getcwd()

        if working_dir:
            os.chdir(working_dir)

        self.km.start_kernel(extra_arguments=args)

        os.chdir(cwd)

        self.kc = self.km.client()
        self.kc.start_channels()
        # if it does not work, it probably means IPython < 3
        self.kc.wait_for_ready()
        self.nb = nb
        self.comment = comment

    def to_json(self, filename, encoding="utf8"):
        """
        convert the notebook into json

        @param      filename       filename or stream
        """
        if isinstance(filename, str  # unicode#
                      ):
            with open(filename, "w", encoding=encoding) as payload:
                self.to_json(payload)
        else:
            filename.write(writes(self.nb))

    @staticmethod
    def read_json(js, profile_dir=None, encoding="utf8"):
        """
        read a notebook from a JSON stream or string

        @param      js              string or stream
        @param      profile_dir     profile directory
        @param      encoding        encoding for the notebooks
        @return                     instance of @see cl NotebookRunner
        """
        if isinstance(js, str  # unicode#
                      ):
            st = io.StringIO(js)
        else:
            st = js
        from .notebook_helper import read_nb
        return read_nb(st, profile_dir=profile_dir, encoding=encoding)

    def copy(self):
        """
        copy the notebook (just the content)

        @return         instance of @see cl NotebookRunner

        .. versionadded:: 1.1
        """
        st = io.StringIO()
        self.to_json(st)
        return NotebookRunner.read_json(st.getvalue())

    def __add__(self, nb):
        """
        merges two notebooks together, returns a new none

        @param      nb      notebook
        @return             new notebook
        """
        c = self.copy()
        c.merge_notebook(nb)
        return c

    def shutdown_kernel(self):
        """
        shut down kernel
        """
        self.fLOG('-- shutdown kernel')
        self.kc.stop_channels()
        self.km.shutdown_kernel(now=True)

    def clean_code(self, code):
        """
        clean the code before running it, the function comment out
        instruction such as ``show()``

        @param      code        code (string)
        @return                 cleaned code
        """
        has_bokeh = "bokeh." in code or "from bokeh" in code or "import bokeh" in code
        if code is None:
            return code
        else:
            lines = [_.strip("\n\r").rstrip(" \t") for _ in code.split("\n")]
            res = []
            show_is_last = False
            for line in lines:
                if line.replace(" ", "") == "show()":
                    line = line.replace("show", "#show")
                    show_is_last = True
                elif has_bokeh and line.replace(" ", "") == "output_notebook()":
                    line = line.replace("output_notebook", "#output_notebook")
                else:
                    show_is_last = False
                res.append(line)
                if show_is_last:
                    res.append('"nothing to show"')
            return "\n".join(res)

    @staticmethod
    def get_cell_code(cell):
        """
        return the code of a cell

        @param      cell        a cell or a string
        @return                 boolean (=iscell), string
        """
        if isinstance(cell, str  # unicode#
                      ):
            iscell = False
            return iscell, cell
        else:
            iscell = True
            try:
                return iscell, cell.source
            except AttributeError:
                return iscell, cell.input

    def run_cell(self, index_cell, cell, clean_function=None):
        '''
        Run a notebook cell and update the output of that cell in-place.

        @param      index_cell          index of the cell
        @param      cell                cell to execute
        @param      clean_function      cleaning function to apply to the code before running it
        @return                         output of the cell
        '''
        iscell, codei = NotebookRunner.get_cell_code(cell)

        self.fLOG('-- running cell:\n%s\n' % codei)

        code = self.clean_code(codei)
        if clean_function is not None:
            code = clean_function(code)
        if len(code) == 0:
            return ""
        self.kc.execute(code)

        reply = self.kc.get_shell_msg()
        reason = None
        try:
            status = reply['content']['status']
        except KeyError:
            status = 'error'
            reason = "no status key in reply['content']"

        if status == 'error':
            ansi_escape = re.compile(r'\x1b[^m]*m')
            try:
                tr = [ansi_escape.sub('', _)
                      for _ in reply['content']['traceback']]
            except KeyError:
                tr = ["No traceback, available keys in reply['content']"] + \
                    [_ for _ in reply['content']]
            traceback_text = '\n'.join(tr)
            self.fLOG("ERR:\n", traceback_text)
        else:
            traceback_text = ''
            self.fLOG('-- cell returned')

        outs = list()
        nbissue = 0
        while True:
            try:
                msg = self.kc.get_iopub_msg(timeout=1)
                if msg['msg_type'] == 'status':
                    if msg['content']['execution_state'] == 'idle':
                        break
            except Empty:
                # execution state should return to idle before the queue becomes empty,
                # if it doesn't, something bad has happened
                status = "error"
                reason = "exception Empty was raised"
                nbissue += 1
                if nbissue > 10:
                    # the notebook is empty
                    return ""
                else:
                    continue

            content = msg['content']
            msg_type = msg['msg_type']

            # IPython 3.0.0-dev writes pyerr/pyout in the notebook format but uses
            # error/execute_result in the message spec. This does the translation
            # needed for tests to pass with IPython 3.0.0-dev
            notebook3_format_conversions = {
                'error': 'pyerr',
                'execute_result': 'pyout'
            }
            msg_type = notebook3_format_conversions.get(msg_type, msg_type)

            out = NotebookNode(output_type=msg_type)

            if 'execution_count' in content:
                if iscell:
                    cell['prompt_number'] = content['execution_count']
                out.prompt_number = content['execution_count']

            if msg_type in ('status', 'pyin', 'execute_input'):
                continue

            elif msg_type == 'stream':
                out.stream = content['name']
                # in msgspec 5, this is name, text
                # in msgspec 4, this is name, data
                if 'text' in content:
                    out.text = content['text']
                else:
                    out.data = content['data']

            elif msg_type in ('display_data', 'pyout'):
                out.data = content['data']

            elif msg_type == 'pyerr':
                out.ename = content['ename']
                out.evalue = content['evalue']
                out.traceback = content['traceback']

            elif msg_type == 'clear_output':
                outs = list()
                continue

            elif msg_type == 'comm_open' or msg_type == 'comm_msg':
                # widgets in a notebook
                out.data = content["data"]
                out.comm_id = content["comm_id"]

            else:
                dcontent = "\n".join("{0}={1}".format(k, v)
                                     for k, v in sorted(content.items()))
                raise NotImplementedError(
                    'unhandled iopub message: %s' % msg_type + "\nCONTENT:\n" + dcontent)

            outs.append(out)

        if iscell:
            cell['outputs'] = outs

        raw = []
        for _ in outs:
            try:
                t = _.data
            except AttributeError:
                continue

            # see MIMEMAP to see the available output type
            for k, v in t.items():
                if k.startswith("text"):
                    raw.append(v)

        sraw = "\n".join(raw)
        self.fLOG(sraw)

        def reply2string(reply):
            sreply = []
            for k, v in sorted(reply.items()):
                if isinstance(v, dict):
                    temp = []
                    for _, __ in sorted(v.items()):
                        temp.append("    [{0}]={1}".format(_, str(__)))
                    v = "\n".join(temp)
                    sreply.append("reply['{0}']=dict\n{1}".format(k, v))
                else:
                    sreply.append("reply['{0}']={1}".format(k, str(v)))
            sreply = "\n".join(sreply)
            return sreply

        if status == 'error':
            sreply = reply2string(reply)
            if len(code) < 5:
                scode = [code]
            else:
                scode = ""
            raise NotebookError("{7}\nCELL status={8}, reason={9} -- {4} length={5} -- {6}:\n-----------------\n{0}\n-----------------\nTRACE:\n{1}\nRAW:\n{2}REPLY:\n{3}".format(
                code, traceback_text, sraw, sreply, index_cell, len(code), scode, self.comment, status, reason))
        return outs

    def iter_code_cells(self):
        '''
        Iterate over the notebook cells containing code.
        '''
        for cell in self.iter_cells():
            if cell.cell_type == 'code':
                yield cell

    def iter_cells(self):
        '''
        Iterate over the notebook cells.
        '''
        if hasattr(self.nb, "worksheets"):
            for ws in self.nb.worksheets:
                for cell in ws.cells:
                    yield cell
        else:
            for cell in self.nb.cells:
                yield cell

    def _cell_container(self):
        """
        returns a cells container, it may change according to the format

        @return     cell container
        """
        if hasattr(self.nb, "worksheets"):
            last = None
            for ws in self.nb.worksheets:
                last = ws
            if last is None:
                raise NotebookError("no cell container")
            return last.cells
        else:
            return self.nb.cells

    def __len__(self):
        """
        return the number of cells, it iterates on cells
        to get this information and does cache the information

        @return         int

        .. versionadded:: 1.1
        """
        return sum(1 for _ in self.iter_cells())

    def cell_type(self, cell):
        """
        returns the cell type

        @param      cell        from @see me iter_cells
        @return                 type
        """
        return cell.cell_type

    def cell_metadata(self, cell):
        """
        returns the cell metadata

        @param      cell        cell
        @return                 metadata
        """
        return cell.metadata

    def cell_height(self, cell):
        """
        approximate the height of a cell by its number of lines it contains

        @param      cell        cell
        @return                 number of cell
        """
        kind = self.cell_type(cell)
        if kind == "markdown":
            content = cell.source
            lines = content.split("\n")
            nbs = sum(1 + len(line) // 80 for line in lines)
            return nbs
        elif kind == "code":
            content = cell.source
            lines = content.split("\n")
            nbl = len(lines)

            for output in cell.outputs:
                if output["output_type"] == "execute_result" or \
                        output["output_type"] == "display_data":
                    data = output["data"]
                    for k, v in data.items():
                        if k == "text/plain":
                            nbl += len(v.split("\n"))
                        elif k == "application/javascript":
                            # rough estimation
                            nbl += len(v.split("\n")) // 2
                        elif k == "image/svg+xml":
                            nbl += len(v) // 5
                        elif k == "text/html":
                            nbl += len(v.split("\n"))
                        elif k == "image/png" or k == "image/jpg" or k == "image/jpeg":
                            nbl += len(v) // 50
                        else:
                            raise NotImplementedError("cell type: {0}\nk={1}\nv={2}\nCELL:\n{3}".format(kind,
                                                                                                        k, v, cell))
                elif output["output_type"] == "stream":
                    v = output["text"]
                    nbl += len(v.split("\n"))
                elif output["output_type"] == "error":
                    v = output["traceback"]
                    nbl += len(v)
                else:
                    raise NotImplementedError("cell type: {0}\noutput type: {1}\nOUT:\n{2}\nCELL:\n{3}"
                                              .format(kind, output["output_type"], output, cell))

            return nbl

        else:
            raise NotImplementedError(
                "cell type: {0}\nCELL:\n{1}".format(kind, cell))

    def add_tag_slide(self, max_nb_cell=8, max_nb_line=25):
        """
        tries to add tags for a slide show when they are too few

        @param      max_nb_cell     maximum number of cells within a slide
        @param      max_nb_line     maximum number of lines within a slide
        @return                     list of modified cells { #slide: (kind, reason, cell) }
        """
        res = {}
        nbline = 0
        nbcell = 0
        for i, cell in enumerate(self.iter_cells()):
            meta = cell.metadata
            if "slideshow" in meta:
                st = meta["slideshow"]["slide_type"]
                if st in ["slide", "subslide"]:
                    nbline = 0
                    nbcell = 0
            else:
                if cell.cell_type == "markdown":
                    content = cell.source
                    if content.startswith("# ") or \
                       content.startswith("## ") or \
                       content.startswith("### "):
                        meta["slideshow"] = {'slide_type': 'slide'}
                        nbline = 0
                        nbcell = 0
                        res[i] = ("slide", "section", cell)

            dh = self.cell_height(cell)
            dc = 1
            new_nbline = nbline + dh
            new_cell = dc + nbcell
            if "slideshow" not in meta:
                if new_cell > max_nb_cell or \
                   new_nbline > max_nb_line:
                    res[i] = (
                        "subslide", "{0}-{1} <-> {2}-{3}".format(nbcell, nbline, dc, dh), cell)
                    nbline = 0
                    nbcell = 0
                    meta["slideshow"] = {'slide_type': 'subslide'}

            nbline += dh
            nbcell += dc

        return res

    def run_notebook(self,
                     skip_exceptions=False,
                     progress_callback=None,
                     additional_path=None,
                     valid=None,
                     clean_function=None):
        '''
        Run all the cells of a notebook in order and update
        the outputs in-place.

        If ``skip_exceptions`` is set, then if exceptions occur in a cell, the
        subsequent cells are run (by default, the notebook execution stops).

        @param      skip_exceptions     skip exception
        @param      progress_callback   call back function
        @param      additional_path     additional paths (as a list or None if none)
        @param      valid               if not None, valid is a function which returns wether or not the cell should be executed or not
        @param      clean_function      function which cleans a cell's code before executing it (None for None)
        @return                         dictionary with statistics

        .. versionchanged:: 1.1
            The function adds the local variable ``theNotebook`` with
            the absolute file name of the notebook.
        '''
        # additional path
        if additional_path is not None:
            if not isinstance(additional_path, list):
                raise TypeError(
                    "additional_path should be a list not: " + str(additional_path))
            code = ["import sys"]
            for p in additional_path:
                code.append("sys.path.append(r'{0}')".format(p))
            cell = "\n".join(code)
            self.run_cell(-1, cell)

        # we add local variable theNotebook
        if self.theNotebook is not None:
            cell = "theNotebook = r'''{0}'''".format(self.theNotebook)
            self.run_cell(-1, cell)

        # initialisation with a code not inside the notebook
        if self.code_init is not None:
            self.run_cell(-1, self.code_init)

        # execution of the notebook
        nbcell = 0
        nbrun = 0
        nbnerr = 0
        cl = time.clock()
        for i, cell in enumerate(self.iter_code_cells()):
            nbcell += 1
            iscell, codei = NotebookRunner.get_cell_code(cell)
            if valid is not None and not valid(codei):
                continue
            try:
                nbrun += 1
                self.run_cell(i, cell, clean_function=clean_function)
                nbnerr += 1
            except Empty as er:
                raise Exception(
                    "{0}\nissue when executing:\n{1}".format(self.comment, codei)) from er
            except NotebookError as e:
                if not skip_exceptions:
                    raise
                else:
                    raise Exception(
                        "issue when executing:\n{0}".format(codei)) from e
            if progress_callback:
                progress_callback(i)
        etime = time.clock() - cl
        return dict(nbcell=nbcell, nbrun=nbrun, nbvalid=nbnerr, time=etime)

    def count_code_cells(self):
        '''
        @return the number of code cells in the notebook

        .. versionadded:: 1.1
        '''
        return sum(1 for _ in self.iter_code_cells())

    def merge_notebook(self, nb):
        """
        append notebook *nb* to this one

        @param      nb      notebook or list of notebook (@see cl NotebookRunner)
        @return             number of added cells

        @example(How to merge notebook?)
        The following code merges two notebooks into the first one
        and stores the result unto a file.

        @code
        from pyquickhelper.ipythonhelper import read_nb
        nb1 = read_nb("<file1>")
        nb2 = read_nb("<file2>")
        nb1.merge_notebook(nb2)
        nb1.to_json(outfile)
        @endcode
        @endexample

        .. versionadded:: 1.1
        """
        if isinstance(nb, list):
            s = 0
            for n in nb:
                s += self.merge_notebook(n)
            return s
        else:
            last = self._cell_container()
            s = 0
            for cell in nb.iter_cells():
                last.append(cell)
                s += 1
            return s
