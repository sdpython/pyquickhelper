"""
@file
@brief Modified version of `runipy.notebook_runner <https://github.com/paulgb/runipy/blob/master/runipy/notebook_runner.py>`_.
"""

from queue import Empty
import os
from time import sleep

from IPython.nbformat.current import NotebookNode
from IPython.kernel import KernelManager

from ..loghelper.flog import noLOG


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
                    fLOG = noLOG):

        """
        constuctor

        @param      nb              notebook as JSON
        @param      profile_dir     profile directory
        @param      working_dir     working directory
        @param      fLOG            logging function
        """
        self.km = KernelManager()
        self.fLOG = fLOG
        args = []

        if profile_dir:
            args.append('--profile-dir=%s' % os.path.abspath(profile_dir))

        cwd = os.getcwd()

        if working_dir:
            os.chdir(working_dir)

        self.km.start_kernel(extra_arguments = args)

        os.chdir(cwd)

        self.kc = self.km.client()
        self.kc.start_channels()
        #self.kc.wait_for_ready()
        self.nb = nb

    def shutdown_kernel(self):
        """
        shut down kernel
        """
        self.fLOG('-- shutdown kernel')
        self.kc.stop_channels()
        self.km.shutdown_kernel(now=True)

    def run_cell(self, cell):
        '''
        Run a notebook cell and update the output of that cell in-place.
        '''
        self.fLOG('-- running cell:\n%s\n' % cell.input)
        self.kc.execute(cell.input)
        reply = self.kc.get_shell_msg()
        status = reply['content']['status']
        if status == 'error':
            traceback_text = 'Cell raised uncaught exception: \n' + \
                '\n'.join(reply['content']['traceback'])
            self.fLOG(traceback_text)
        else:
            self.fLOG('-- cell returned')

        outs = list()
        while True:
            try:
                msg = self.kc.get_iopub_msg(timeout=1)
                if msg['msg_type'] == 'status':
                    if msg['content']['execution_state'] == 'idle':
                        break
            except Empty:
                # execution state should return to idle before the queue becomes empty,
                # if it doesn't, something bad has happened
                raise

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
                    out.text = content['data']

            elif msg_type in ('display_data', 'pyout'):
                for mime, data in content['data'].items():
                    try:
                        attr = self.MIME_MAP[mime]
                    except KeyError:
                        raise NotImplementedError('unhandled mime type: %s' % mime)

                    setattr(out, attr, data)
                    
            elif msg_type == 'pyerr':
                out.ename = content['ename']
                out.evalue = content['evalue']
                out.traceback = content['traceback']

            elif msg_type == 'clear_output':
                outs = list()
                continue
            else:
                raise NotImplementedError('unhandled iopub message: %s' % msg_type)
            outs.append(out)
        cell['outputs'] = outs

        raw = [ ]
        for _ in outs:
            try:
                t = _.text
                raw.append(t)
            except AttributeError:
                continue

        self.fLOG("\n".join(raw))

        if status == 'error':
            raise NotebookError("CELL:\n{0}\n\nTRACE:\n{1}".format(cell.input, traceback_text))
        return outs

    def iter_code_cells(self):
        '''
        Iterate over the notebook cells containing code.
        '''
        for ws in self.nb.worksheets:
            for cell in ws.cells:
                if cell.cell_type == 'code':
                    yield cell

    def run_notebook(self,
                    skip_exceptions=False,
                    progress_callback=None,
                    additional_path=None,
                    valid = None):
        '''
        Run all the cells of a notebook in order and update
        the outputs in-place.

        If ``skip_exceptions`` is set, then if exceptions occur in a cell, the
        subsequent cells are run (by default, the notebook execution stops).

        @param      skip_exceptions     skip exception
        @param      progress_callback   call back function
        @param      additional_path     additional paths (as a list or None if none)
        @param      valid               if not None, valid is a function which returns wether or not the cell should be executed or not
        '''
        if additional_path is not None:
            if not isinstance(additional_path, list):
                raise TypeError("additional_path should be a list not: "  +str(additional_path))
            code = ["import sys"]
            for p in additional_path:
                code.append("sys.path.append(r'{0}')".format(p))
            cell = "\n".join(code)
            try:
                self.kc.execute(cell)
            except NotebookError:
                if not skip_exceptions:
                    raise

        for i, cell in enumerate(self.iter_code_cells()):
            if valid is not None and not valid(cell.input) :
                continue
            try:
                self.run_cell(cell)
            except NotebookError as e:
                if not skip_exceptions:
                    raise
                else:
                    raise Exception("issue when executing:\n{0}".format(cell))
            if progress_callback:
                progress_callback(i)

    def count_code_cells(self):
        '''
        @return the number of code cells in the notebook
        '''
        return sum(1 for _ in self.iter_code_cells())