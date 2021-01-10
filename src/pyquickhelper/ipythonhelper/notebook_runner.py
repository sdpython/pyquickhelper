"""
@file
@brief Modified version of `runipy.notebook_runner
<https://github.com/paulgb/runipy/blob/master/runipy/notebook_runner.py>`_.
"""

import base64
import os
import re
import time
import platform
import warnings
from queue import Empty
from time import sleep
from collections import Counter
from io import StringIO, BytesIO
from nbformat import NotebookNode, writes
from nbformat.reader import reads
from ..imghelper.svg_helper import svg2img, PYQImageException
from ..loghelper.flog import noLOG


class NotebookError(Exception):
    """
    Raised when the execution fails.
    """
    pass


class NotebookKernelError(Exception):
    """
    Raised when
    `wait_for_ready <https://github.com/jupyter/jupyter_client/blob/master/
    jupyter_client/blocking/client.py#L84>`_ fails.
    """
    pass


class NotebookRunner(object):

    """
    The kernel communicates with mime-types while the notebook
    uses short labels for different cell types. We'll use this to
    map from kernel types to notebook format types.

    This classes executes a notebook end to end.

    .. index:: kernel, notebook

    The class can use different kernels. The next links gives more
    information on how to create or test a kernel:

    * `jupyter_kernel_test <https://github.com/jupyter/jupyter_kernel_test>`_
    * `simple_kernel <https://github.com/dsblank/simple_kernel>`_

    .. faqref::
        :title: Do I need to shutdown the kernel after running a notebook?

        .. index:: travis

        If the class is instantiated with *kernel=True*, a kernel will
        be started. It must be shutdown otherwise the program might
        be waiting for it for ever. That is one of the reasons why the
        travis build does not complete. The build finished but cannot terminate
        until all kernels are shutdown.
    """

    # . available output types
    MIME_MAP = {
        'image/jpeg': 'jpeg',
        'image/png': 'png',
        'image/gif': 'gif',
        'text/plain': 'text',
        'text/html': 'html',
        'text/latex': 'latex',
        'application/javascript': 'html',
        'image/svg+xml': 'svg',
    }

    def __init__(self, nb, profile_dir=None, working_dir=None,
                 comment="", fLOG=noLOG, theNotebook=None, code_init=None,
                 kernel_name="python", log_level="30", extended_args=None,
                 kernel=False, filename=None, replacements=None, detailed_log=None,
                 startup_timeout=300):
        """
        @param      nb              notebook as :epkg:`JSON`
        @param      profile_dir     profile directory
        @param      working_dir     working directory
        @param      comment         additional information added to error message
        @param      theNotebook     if not None, populate the variable *theNotebook* with this value in the notebook
        @param      code_init       to initialize the notebook with a python code as if it was a cell
        @param      fLOG            logging function
        @param      log_level       Choices: (0, 10, 20, 30=default, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
        @param      kernel_name     kernel name, it can be None
        @param      extended_args   others arguments to pass to the command line
                                    (`--KernelManager.autorestar=True` for example),
                                    see :ref:`l-ipython_notebook_args` for a full list
        @param      kernel          *kernel* is True by default, the notebook can be run, if False,
                                    the notebook can be read but not run
        @param      filename        to add the notebook file if there is one in error messages
        @param      replacements    replacements to make in every cell before running it,
                                    dictionary ``{ string: string }``
        @param      detailed_log    to log detailed information when executing the notebook, this should be a function
                                    with the same signature as ``print`` or None
        @param      startup_timeout wait for this long for the kernel to be ready,
                                    see `wait_for_ready
                                    <https://github.com/jupyter/jupyter_client/blob/master/
                                    jupyter_client/blocking/client.py#L84>`_

        .. versionchanged:: 1.8
            Parameter *startup_timeout* was added.
        """
        if kernel:
            try:
                from jupyter_client import KernelManager
            except ImportError:  # pragma: no cover
                from ipykernel import KernelManager

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=DeprecationWarning)
                self.km = KernelManager(
                    kernel_name=kernel_name) if kernel_name is not None else KernelManager()
        else:
            self.km = None
        self.detailed_log = detailed_log
        self.fLOG = fLOG
        self.theNotebook = theNotebook
        self.code_init = code_init
        self._filename = filename if filename is not None else "memory"
        self.replacements = replacements
        self.init_args = dict(
            profile_dir=profile_dir, working_dir=working_dir,
            comment=comment, fLOG=fLOG, theNotebook=theNotebook, code_init=code_init,
            kernel_name="python", log_level="30", extended_args=None,
            kernel=kernel, filename=filename, replacements=replacements)
        args = []

        if profile_dir:
            args.append('--profile-dir=%s' % os.path.abspath(profile_dir))
        if log_level:
            args.append('--log-level=%s' % log_level)

        if extended_args is not None and len(extended_args) > 0:
            for opt in extended_args:
                if not opt.startswith("--"):
                    raise SyntaxError(
                        "every option should start with '--': " + opt)
                if "=" not in opt:
                    raise SyntaxError(  # pragma: no cover
                        "every option should be assigned a value: " + opt)
                args.append(opt)

        if kernel:
            cwd = os.getcwd()

            if working_dir:
                os.chdir(working_dir)

            if self.km is not None:
                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings(
                            "ignore", category=ResourceWarning)
                        self.km.start_kernel(extra_arguments=args)
                except Exception as e:  # pragma: no cover
                    raise NotebookKernelError(
                        "Failure with args: {0}\nand error:\n{1}".format(args, str(e))) from e

                if platform.system() == 'Darwin':
                    # see http://www.pypedia.com/index.php/notebook_runner
                    # There is sometimes a race condition where the first
                    # execute command hits the kernel before it's ready.
                    # It appears to happen only on Darwin (Mac OS) and an
                    # easy (but clumsy) way to mitigate it is to sleep
                    # for a second.
                    sleep(1)

            if working_dir:
                os.chdir(cwd)

            self.kc = self.km.client()
            self.kc.start_channels(stdin=False)
            try:
                self.kc.wait_for_ready(timeout=startup_timeout)
            except RuntimeError as e:  # pragma: no cover
                # We wait for one second.
                sleep(startup_timeout)
                self.kc.stop_channels()
                self.km.shutdown_kernel()
                self.km = None
                self.kc = None
                self.nb = nb
                self.comment = comment
                raise NotebookKernelError(
                    "Wait_for_ready fails (timeout={0}).".format(startup_timeout)) from e
        else:
            self.km = None
            self.kc = None
        self.nb = nb
        self.comment = comment

    def __del__(self):
        """
        We close the kernel.
        """
        if self.km is not None:
            del self.km
        if self.kc is not None:
            del self.kc

    def to_json(self, filename=None, encoding="utf8"):
        """
        Converts the notebook into :epkg:`JSON`.

        @param      filename        filename or stream
        @param      encoding        encoding
        @return                     Json string if filename is None, None otherwise
        """
        if isinstance(filename, str):
            with open(filename, "w", encoding=encoding) as payload:
                self.to_json(payload)
                return None

        if filename is None:
            st = StringIO()
            st.write(writes(self.nb))
            return st.getvalue()

        filename.write(writes(self.nb))
        return None

    def copy(self):
        """
        Copies the notebook (just the content).

        @return         instance of @see cl NotebookRunner
        """
        st = StringIO()
        self.to_json(st)
        args = self.init_args.copy()
        for name in ["theNotebook", "filename"]:
            if name in args:
                del args[name]
        nb = reads(st.getvalue())
        return NotebookRunner(nb, **args)

    def __add__(self, nb):
        """
        Merges two notebooks together, returns a new none.

        @param      nb      notebook
        @return             new notebook
        """
        c = self.copy()
        c.merge_notebook(nb)
        return c

    def shutdown_kernel(self):
        """
        Shuts down kernel.
        """
        self.fLOG('-- shutdown kernel')
        if self.kc is None:
            raise ValueError(  # pragma: no cover
                "No kernel was started, specify kernel=True when initializing the instance.")
        self.kc.stop_channels()
        self.km.shutdown_kernel(now=True)

    def clean_code(self, code):
        """
        Cleans the code before running it, the function comment out
        instruction such as ``show()``.

        @param      code        code (string)
        @return                 cleaned code
        """
        has_bokeh = "bokeh." in code or "from bokeh" in code or "import bokeh" in code
        if code is None:
            return code

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
            if self.replacements is not None:
                for k, v in self.replacements.items():
                    line = line.replace(k, v)
            res.append(line)
            if show_is_last:
                res.append('"nothing to show"')
        return "\n".join(res)

    @staticmethod
    def get_cell_code(cell):
        """
        Returns the code of a cell.

        @param      cell        a cell or a string
        @return                 boolean (=iscell), string
        """
        if isinstance(cell, str):
            iscell = False
            return iscell, cell

        iscell = True
        try:
            return iscell, cell.source
        except AttributeError:  # pragma: no cover
            return iscell, cell.input

    def run_cell(self, index_cell, cell, clean_function=None, max_nbissue=15):
        '''
        Runs a notebook cell and update the output of that cell inplace.

        :param index_cell: index of the cell
        :param cell: cell to execute
        :param clean_function: cleaning function to apply to the code before running it
        :param max_nbissue: number of times an issue can be raised before stopping
        :return: output of the cell
        '''
        if self.detailed_log:
            self.detailed_log("[run_cell] index_cell={0} clean_function={1}".format(
                index_cell, clean_function))
        iscell, codei = NotebookRunner.get_cell_code(cell)

        self.fLOG('-- running cell:\n%s\n' % codei)
        if self.detailed_log:
            self.detailed_log(
                '[run_cell] code=\n                        {0}'.format(
                    "\n                        ".join(codei.split("\n"))))

        code = self.clean_code(codei)
        if clean_function is not None:
            code = clean_function(code)
        if self.detailed_log:
            self.detailed_log(
                '    cleaned code=\n                        {0}'.format(
                    "\n                        ".join(code.split("\n"))))
        if len(code) == 0:
            return ""
        if self.kc is None:
            raise ValueError(  # pragma: no cover
                "No kernel was started, specify kernel=True when initializing the instance.")
        self.kc.execute(code)

        reply = self.kc.get_shell_msg()
        reason = None
        try:
            status = reply['content']['status']
        except KeyError:  # pragma: no cover
            status = 'error'
            reason = "no status key in reply['content']"

        if status == 'error':
            ansi_escape = re.compile(r'\x1b[^m]*m')
            try:
                tr = [ansi_escape.sub('', _)
                      for _ in reply['content']['traceback']]
            except KeyError:  # pragma: no cover
                tr = (["No traceback, available keys in reply['content']"] +
                      list(reply['content']))
            traceback_text = '\n'.join(tr)
            self.fLOG("[nberror]\n", traceback_text)
            if self.detailed_log:
                self.detailed_log('[run_cell] ERROR=\n    {0}'.format(
                    "\n    ".join(traceback_text.split("\n"))))
        else:
            traceback_text = ''
            self.fLOG('-- cell returned')

        outs = list()
        nbissue = 0
        statuses = [status]
        while True:
            try:
                msg = self.kc.get_iopub_msg(timeout=1)
                if msg['msg_type'] == 'status':
                    if msg['content']['execution_state'] == 'idle':
                        status = 'ok'
                        statuses.append(status)
                        break
                statuses.append(status)
            except Empty as e:  # pragma: no cover
                # execution state should return to idle before
                # the queue becomes empty,
                # if it doesn't, something bad has happened
                status = "error"
                statuses.append(status)
                reason = "exception Empty was raised (%r)" % e
                nbissue += 1
                if nbissue > max_nbissue:
                    # the notebook is empty
                    return ""
                else:
                    continue

            content = msg['content']
            msg_type = msg['msg_type']
            if self.detailed_log:
                self.detailed_log('    msg_type={0}'.format(msg_type))

            out = NotebookNode(output_type=msg_type, metadata=dict())

            if 'execution_count' in content:
                if iscell:
                    cell['execution_count'] = content['execution_count']
                out.execution_count = content['execution_count']

            if msg_type in ('status', 'pyin', 'execute_input'):
                continue

            if msg_type == 'stream':
                out.name = content['name']
                # in msgspec 5, this is name, text
                # in msgspec 4, this is name, data
                if 'text' in content:
                    out.text = content['text']
                else:
                    out.data = content['data']

            elif msg_type in ('display_data', 'pyout', 'execute_result'):
                out.data = content['data']

            elif msg_type in ('pyerr', 'error'):
                out.ename = content['ename']
                out.evalue = content['evalue']
                out.traceback = content['traceback']
                out.name = 'stderr'

            elif msg_type == 'clear_output':
                outs = list()
                continue

            elif msg_type in ('comm_open', 'comm_msg', 'comm_close'):
                # widgets in a notebook
                out.data = content["data"]
                out.comm_id = content["comm_id"]

            else:
                dcontent = "\n".join("{0}={1}".format(k, v)
                                     for k, v in sorted(content.items()))
                raise NotImplementedError(  # pragma: no cover
                    "Unhandled iopub message: '{0}'\n--CONTENT--\n{1}".format(msg_type, dcontent))

            outs.append(out)
            if self.detailed_log:
                self.detailed_log('    out={0}'.format(type(out)))
                if hasattr(out, "data"):
                    self.detailed_log('    out={0}'.format(out.data))

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
        if self.detailed_log:
            self.detailed_log('    sraw=\n                        {0}'.format(
                              "\n                        ".join(sraw.split("\n"))))

        def reply2string(reply):
            sreply = []
            for k, v in sorted(reply.items()):
                if isinstance(v, dict):
                    temp = []
                    for _, __ in sorted(v.items()):
                        temp.append("    [{0}]={1}".format(_, str(__)))
                    v_ = "\n".join(temp)
                    sreply.append("reply['{0}']=dict\n{1}".format(k, v_))
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
            mes = ("FILENAME\n{10}:1:1 - cell:{11}\n{7}\nCELL status={8}, reason='{9}' -- {4} "
                   "length={5} -- {6}:\n-----------------\n"
                   "content={12}\nmsg_type: {13} nbissue={14}"
                   "\nstatuses={15}"
                   "\n-----------------\n{0}"
                   "\n-----------------\nTRACE:\n{1}\nRAW:\n{2}REPLY:\n{3}")
            raise NotebookError(mes.format(
                code, traceback_text, sraw, sreply, index_cell,  # 0-4
                len(code), scode, self.comment, status, reason,  # 5-9
                self._filename, index_cell, content, msg_type, nbissue,  # 10-14
                statuses))  # 15
        if self.detailed_log:
            self.detailed_log('[run_cell] status={0}'.format(status))
        return outs

    def to_python(self):
        """
        Converts the notebook into python.

        @return         string
        """
        rows = []
        for cell in self.iter_cells():
            if cell.cell_type == "code":
                codei = NotebookRunner.get_cell_code(cell)[1]
                rows.append(codei)
            elif cell.cell_type in ("markdown", "raw"):
                content = cell.source
                lines = content.split("\n")
                for line in lines:
                    if line.startswith("#"):
                        rows.append("###")
                        rows.append(line)
                    else:
                        rows.append("# " + line)
            else:
                # No text, no code.
                rows.append("# cell.type = {0}".format(cell.cell_type))
            rows.append("")
        return "\n".join(rows)

    def iter_code_cells(self):
        '''
        Iterates over the notebook cells containing code.
        '''
        for cell in self.iter_cells():
            if cell.cell_type == 'code':
                yield cell

    def iter_cells(self):
        '''
        Iterates over the notebook cells.
        '''
        if hasattr(self.nb, "worksheets"):
            for ws in self.nb.worksheets:
                for cell in ws.cells:
                    yield cell
        else:
            for cell in self.nb.cells:
                yield cell

    def first_cell(self):
        """
        Returns the first cell.
        """
        for cell in self.iter_cells():
            return cell

    def _cell_container(self):
        """
        Returns a cells container, it may change according to the format.

        @return     cell container
        """
        if hasattr(self.nb, "worksheets"):
            last = None
            for ws in self.nb.worksheets:
                last = ws
            if last is None:
                raise NotebookError("no cell container")  # pragma: no cover
            return last.cells
        return self.nb.cells

    def __len__(self):
        """
        Returns the number of cells, it iterates on cells
        to get this information and does cache the information.

        @return         int
        """
        return sum(1 for _ in self.iter_cells())

    def cell_type(self, cell):
        """
        Returns the cell type.

        @param      cell        from @see me iter_cells
        @return                 type
        """
        return cell.cell_type

    def cell_metadata(self, cell):
        """
        Returns the cell metadata.

        @param      cell        cell
        @return                 metadata
        """
        return cell.metadata

    def _check_thumbnail_tuple(self, b):
        """
        Checks types for a thumbnail.

        @param      b       tuple   image, format
        @return             b

        The function raises an exception if the type is incorrect.
        """
        if not isinstance(b, tuple):
            raise TypeError(  # pragma: no cover
                "tuple expected, not {0}".format(type(b)))
        if len(b) != 2:
            raise TypeError(  # pragma: no cover
                "tuple expected of lengh 2, not {0}".format(len(b)))
        if b[1] == "svg":
            if not isinstance(b[0], str):
                raise TypeError(
                    "str expected for svg, not {0}".format(type(b[0])))
        elif b[1] in ("vnd.plotly.v1+html", "vnd.bokehjs_exec.v0+json",
                      "vnd.bokehjs_load.v0+json", 'vnd.plotly.v1+json'):
            # Don't know how to extract a snippet out of this.
            pass
        else:
            if not isinstance(b[0], bytes):
                raise TypeError(
                    "bytes expected for images, not {0}-'{1}'\n{2}".format(type(b[0]), b[1], b))
        return b

    def create_picture_from(self, text, format, asbytes=True, context=None):
        """
        Creates a picture from text.

        @param      text        the text
        @param      format      text, json, ...
        @param      context     (str) indication on the content of text (error, ...)
        @param      asbytes     results as bytes or as an image
        @return                 tuple (picture, format) or PIL.Image (if asbytes is False)

        The picture will be bytes, the format png, bmp...
        The size of the picture will depend on the text.
        The longer, the bigger. The method relies on matplotlib
        and then convert the image into a PIL image.

        HTML could be rendered with QWebPage from PyQt (not implemented).
        """
        if not isinstance(text, (str, bytes)):
            text = str(text)
            if "\n" not in text:
                rows = []
                for i in range(0, len(text), 20):
                    end = min(i + 20, len(text))
                    rows.append(text[i:end])
                text = "\n".join(text)
        if len(text) > 200:
            text = text[:200]
        size = len(text) // 10
        figsize = (3 + size, 3 + size)
        lines = text.replace("\t", " ").replace("\r", "").split("\n")

        import matplotlib.pyplot as plt
        from matplotlib.textpath import TextPath
        from matplotlib.font_manager import FontProperties
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        fp = FontProperties(size=200)

        dx = 0
        dy = 0
        for i, line in enumerate(lines):
            if len(line.strip()) > 0:
                ax.text(0, -dy, line, fontproperties=fp, va='top')
                tp = TextPath((0, -dy), line, prop=fp)
                bb = tp.get_extents()
                dy += bb.height
                dx = max(dx, bb.width)

        ratio = abs(dx) / max(abs(dy), 1)
        ratio = max(min(ratio, 3), 1)
        fig.set_size_inches(int((1 + size) * ratio), 1 + size)
        ax.set_xlim([0, dx])
        ax.set_ylim([-dy, 0])
        ax.set_axis_off()
        sio = BytesIO()
        fig.savefig(sio, format="png")
        plt.close()

        if asbytes:
            b = sio.getvalue(), "png"
            self._check_thumbnail_tuple(b)
            return b
        try:
            from PIL import Image
        except ImportError:  # pragma: no cover
            import Image
        img = Image.open(sio)
        return img

    def cell_image(self, cell, image_from_text=False):
        """
        Returns the cell image or None if not found.

        @param      cell            cell to examine
        @param      image_from_text produce an image even if it is not one
        @return                     None for no image or a list of tuple (image as bytes, extension)
                                    for each output of the cell
        """
        kind = self.cell_type(cell)
        if kind != "code":
            return None
        results = []
        for output in cell.outputs:
            if output["output_type"] in {"execute_result", "display_data"}:
                data = output["data"]
                for k, v in data.items():
                    if k == "text/plain":
                        if image_from_text:
                            b = self.create_picture_from(
                                v, "text", context=output["output_type"])
                            results.append(b)
                    elif k == "application/javascript":
                        if image_from_text:
                            b = self.create_picture_from(v, "js")
                            results.append(b)
                    elif k == "application/json":
                        if image_from_text:
                            b = self.create_picture_from(v, "json")
                            results.append(b)
                    elif k == "image/svg+xml":
                        if not isinstance(v, str):
                            raise TypeError(
                                "This should be str not '{0}' (=SVG).".format(type(v)))
                        results.append((v, "svg"))
                    elif k == "text/html":
                        if image_from_text:
                            b = self.create_picture_from(v, "html")
                            results.append(b)
                    elif k == "text/latex":
                        if image_from_text:
                            b = self.create_picture_from(v, "latex")
                            results.append(b)
                    elif k == "application/vnd.jupyter.widget-view+json":
                        # see http://ipywidgets.readthedocs.io/en/latest/embedding.html
                        if "model_id" not in v:
                            raise KeyError(  # pragma: no cover
                                "model_id is missing from {0}".format(v))
                        model_id = v["model_id"]
                        self.fLOG(
                            "[application/vnd.jupyter.widget-view+json] not rendered", model_id)
                    elif k in {"image/png", "image/jpg", "image/jpeg", "image/gif"}:
                        if not isinstance(v, bytes):
                            v = base64.b64decode(v)
                        if not isinstance(v, bytes):
                            raise TypeError(  # pragma: no cover
                                "This should be bytes not '{0}' (=IMG:{1}).".format(type(v), k))
                        results.append((v, k.split("/")[-1]))
                    elif k in ("text/vnd.plotly.v1+html", "application/vnd.plotly.v1+json",
                               "application/vnd.bokehjs_exec.v0+json",
                               "application/vnd.bokehjs_load.v0+json"):
                        results.append((v, k.split("/")[-1]))
                    else:
                        raise NotImplementedError(  # pragma: no cover
                            "cell type: {0}\nk={1}\nv={2}\nCELL:\n{3}".format(
                                kind, k, v, cell))
            elif output["output_type"] == "error":
                vl = output["traceback"]
                if image_from_text:
                    for v in vl:
                        b = self.create_picture_from(
                            v, "text", context="error")
                        results.append(b)
            elif output["output_type"] == "stream":
                v = output["text"]
                if image_from_text:
                    b = self.create_picture_from(v, "text")
                    results.append(b)
            else:
                raise NotImplementedError(  # pragma: no cover
                    "cell type: {0}\noutput type: {1}\nOUT:\n{2}\nCELL:\n{3}"
                    "".format(kind, output["output_type"], output, cell))
        if len(results) > 0:
            res = self._merge_images(results)
            if res[0] is None:
                return None
            self._check_thumbnail_tuple(res)
            return res
        return None

    def cell_height(self, cell):
        """
        Approximates the height of a cell by its number of lines it contains.

        @param      cell        cell
        @return                 number of cell
        """
        kind = self.cell_type(cell)
        if kind == "markdown":
            content = cell.source
            lines = content.split("\n")
            nbs = sum(1 + len(line) // 80 for line in lines)
            return nbs
        if kind == "raw":
            content = cell.source
            lines = content.split("\n")
            nbs = sum(1 + len(line) // 80 for line in lines)
            return nbs
        if kind == "code":
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
                        elif k == "application/json":
                            # rough estimation
                            try:
                                nbl += len(v.split("{"))
                            except AttributeError:
                                nbl += len(v) // 5 + 1
                        elif k == "image/svg+xml":
                            nbl += len(v) // 5
                        elif k == "text/html":
                            nbl += len(v.split("\n"))
                        elif k == "text/latex":
                            nbl += len(v.split("\\\\")) * 2
                        elif k in {"image/png", "image/jpg", "image/jpeg", "image/gif"}:
                            nbl += len(v) // 50
                        elif k == "application/vnd.jupyter.widget-view+json":
                            nbl += 5
                        elif k in ("text/vnd.plotly.v1+html",
                                   "application/vnd.plotly.v1+json",
                                   "application/vnd.bokehjs_load.v0+json",
                                   "application/vnd.bokehjs_exec.v0+json"):
                            nbl += 10
                        else:
                            fmt = "Unable to guess heigth for cell type: '{0}'\nk='{1}'\nv='{2}'\nCELL:\n{3}"
                            raise NotImplementedError(
                                fmt.format(kind, k, v, cell))
                elif output["output_type"] == "stream":
                    v = output["text"]
                    nbl += len(v.split("\n"))
                elif output["output_type"] == "error":
                    v = output["traceback"]
                    nbl += len(v)
                else:
                    raise NotImplementedError(  # pragma: no cover
                        "cell type: {0}\noutput type: {1}\nOUT:\n{2}\nCELL:\n{3}"
                        .format(kind, output["output_type"], output, cell))

            return nbl

        raise NotImplementedError(  # pragma: no cover
            "cell type: {0}\nCELL:\n{1}".format(kind, cell))

    def add_tag_slide(self, max_nb_cell=4, max_nb_line=25):
        """
        Tries to add tags for a slide show when they are too few.

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

    def run_notebook(self, skip_exceptions=False, progress_callback=None,
                     additional_path=None, valid=None, clean_function=None,
                     context=None):
        '''
        Runs all the cells of a notebook in order and update
        the outputs in-place.

        If ``skip_exceptions`` is set, then if exceptions occur in a cell, the
        subsequent cells are run (by default, the notebook execution stops).

        @param      skip_exceptions     skip exception
        @param      progress_callback   call back function
        @param      additional_path     additional paths (as a list or None if none)
        @param      valid               if not None, valid is a function which returns whether
                                        or not the cell should be executed or not, if the function
                                        returns None, the execution of the notebooks and skip
                                        the execution of the other cells
        @param      clean_function      function which cleans a cell's code before executing
                                        it (None for None)
        @return                         dictionary with statistics

        The function adds the local variable ``theNotebook`` with
        the absolute file name of the notebook.
        Function *valid* can return *None* to stop the execution of the notebook
        before this cell.
        '''
        if self.detailed_log:
            self.detailed_log(
                "[run_notebook] Starting execution of '{0}'".format(self._filename))
        # additional path
        if additional_path is not None:
            if not isinstance(additional_path, list):
                raise TypeError(  # pragma: no cover
                    "Additional_path should be a list not: " + str(additional_path))
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
        cl = time.perf_counter()
        for i, cell in enumerate(self.iter_code_cells()):
            nbcell += 1
            codei = NotebookRunner.get_cell_code(cell)[1]
            if valid is not None:
                r = valid(codei)
                if r is None:
                    break
                if not r:
                    continue
            try:
                nbrun += 1
                self.run_cell(i, cell, clean_function=clean_function)
                nbnerr += 1
            except Empty as er:
                raise RuntimeError(  # pragma: no cover
                    "{0}\nissue when executing:\n{1}".format(self.comment, codei)) from er
            except NotebookError as e:
                if not skip_exceptions:
                    raise
                raise RuntimeError(  # pragma: no cover
                    "Issue when executing:\n{0}".format(codei)) from e
            if progress_callback:
                progress_callback(i)
        etime = time.perf_counter() - cl
        res = dict(nbcell=nbcell, nbrun=nbrun, nbvalid=nbnerr, time=etime)
        if self.detailed_log:
            self.detailed_log(
                "[run_notebook] end execution of '{0}'".format(self._filename))
            self.detailed_log(
                "[run_notebook] execution time: {0}".format(etime))
            self.detailed_log("[run_notebook] statistics : {0}".format(res))
        return res

    def count_code_cells(self):
        '''
        Returns the number of code cells in the notebook.
        '''
        return sum(1 for _ in self.iter_code_cells())

    def merge_notebook(self, nb):
        """
        Appends notebook *nb* to this one.

        @param      nb      notebook or list of notebook (@see cl NotebookRunner)
        @return             number of added cells

        .. faqref::
            :title: How to merge notebook?

            The following code merges two notebooks into the first one
            and stores the result unto a file.

            ::

                from pyquickhelper.ipythonhelper import read_nb
                nb1 = read_nb("<file1>", kernel=False)
                nb2 = read_nb("<file2>", kernel=False)
                nb1.merge_notebook(nb2)
                nb1.to_json(outfile)
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

    def get_description(self):
        """
        Gets summary and description of this notebook.
        We expect the first cell to contain a title and a description
        of its content.

        @return             header, description
        """
        def split_header(s, get_header=True):
            s = s.lstrip().rstrip()
            parts = s.splitlines()
            if parts[0].startswith('#'):
                if get_header:
                    header = re.sub('#+\\s*', '', parts.pop(0))
                    if not parts:
                        return header, ''
                else:
                    header = ''
                rest = '\n'.join(parts).lstrip().split('\n\n')
                desc = rest[0].replace('\n', ' ')
                return header, desc

            if get_header:
                if parts[0].startswith(('=', '-')):
                    parts = parts[1:]
                header = parts.pop(0)
                if parts and parts[0].startswith(('=', '-')):
                    parts.pop(0)
                if not parts:
                    return header, ''
            else:
                header = ''
            rest = '\n'.join(parts).lstrip().split('\n\n')
            desc = rest[0].replace('\n', ' ')
            return header, desc

        first_cell = self.first_cell()

        if not first_cell['cell_type'] == 'markdown':
            raise ValueError(  # pragma: no cover
                "The first cell is not in markdown but '{0}' filename='{1}'.".format(
                    first_cell['cell_type'], self._filename))

        header, desc = split_header(first_cell['source'])
        if not desc and len(self.nb['cells']) > 1:
            second_cell = self.nb['cells'][1]
            if second_cell['cell_type'] == 'markdown':
                _, desc = split_header(second_cell['source'], False)

        reg_link = "(\\[(.*?)\\]\\(([^ ]*)\\))"
        reg = re.compile(reg_link)
        new_desc = reg.sub("\\2", desc)
        if "http://" in new_desc or "https://" in new_desc:
            raise ValueError(  # pragma: no cover
                "Wrong regular expression in '{2}':\n{0}\nMODIFIED:\n{1}".format(
                    desc, new_desc, self._filename))
        return header, new_desc.replace('"', "")

    def get_thumbnail(self, max_width=200, max_height=200, use_default=False):
        """
        Processes the notebook and creates one picture based on the outputs
        to illustrate a notebook.

        @param      max_width       maximum size of the thumbnail
        @param      max_height      maximum size of the thumbnail
        @param      use_default     force using a default image even if an even is present
        @return                     string (:epkg:`SVG`) or Image (:epkg:`PIL`)
        """
        images = []
        cells = list(self.iter_cells())
        cells.reverse()
        for cell in cells:
            c = self.cell_image(cell, False)
            if c is not None and len(c) > 0 and len(c[0]) > 0 and c[1] not in (
                    "vnd.plotly.v1+html", "vnd.bokehjs_exec.v0+json",
                    "vnd.bokehjs_load.v0+json"):
                self._check_thumbnail_tuple(c)
                images.append(c)
        if not use_default and len(images) == 0:
            for cell in cells:
                c = self.cell_image(cell, True)
                if c is not None and len(c) > 0 and len(c[0]) > 0:
                    self._check_thumbnail_tuple(c)
                    images.append(c)
                    if len(c[0]) >= 1000:
                        break
        if use_default:
            images = []
        if len(images) == 0:
            # no image, we need to consider the default one
            no_image = os.path.join(
                os.path.dirname(__file__), 'no_image_nb.png')
            with open(no_image, "rb") as f:
                c = (f.read(), "png")
                self._check_thumbnail_tuple(c)
                images.append(c)

        # select the image
        if len(images) == 0:
            raise ValueError(  # pragma: no cover
                "There should be at least one image.")
        if len(images) == 1:
            image = images[0]
        else:
            # maybe later we'll implement a different logic
            # we pick the last one
            image = images[0]

        # zoom
        if image[1] in ("vnd.plotly.v1+html", "vnd.bokehjs_exec.v0+json", "vnd.bokehjs_load.v0+json"):
            return None
        if image[1] == 'svg':
            try:
                img = svg2img(image[0])
            except PYQImageException:  # pragma: no cover
                # Enable to convert SVG.
                return None
            return self._scale_image(img, image[1], max_width=max_width, max_height=max_height)
        img = self._scale_image(
            image[0], image[1], max_width=max_width, max_height=max_height)
        return img

    def _scale_image(self, in_bytes, format=None, max_width=200, max_height=200):
        """
        Scales an image with the same aspect ratio centered in an
        image with a given max_width and max_height.

        @param      in_bytes        image as bytes
        @param      format          indication of the format (can be empty)
        @param      max_width       maximum size of the thumbnail
        @param      max_height      maximum size of the thumbnail
        @return                     Image (PIL)
        """
        # local import to avoid testing dependency on PIL:
        try:
            from PIL import Image
        except ImportError:  # pragma: no cover
            import Image

        if isinstance(in_bytes, tuple):
            in_bytes = in_bytes[0]
        if isinstance(in_bytes, bytes):
            img = Image.open(BytesIO(in_bytes))
        elif isinstance(in_bytes, Image.Image):
            img = in_bytes
        else:
            raise TypeError(  # pragma: no cover
                "bytes expected, not {0} - format={1}".format(
                    type(in_bytes), format))
        width_in, height_in = img.size
        scale_w = max_width / float(width_in)
        scale_h = max_height / float(height_in)

        if height_in * scale_w <= max_height:
            scale = scale_w
        else:
            scale = scale_h

        if scale >= 1.0:
            return img

        width_sc = int(round(scale * width_in))
        height_sc = int(round(scale * height_in))

        # resize the image and center
        img.thumbnail((width_sc, height_sc), Image.ANTIALIAS)
        thumb = Image.new('RGB', (max_width, max_height), (255, 255, 255))
        pos_insert = ((max_width - width_sc) // 2,
                      (max_height - height_sc) // 2)
        thumb.paste(img, pos_insert)
        return thumb

    def _merge_images(self, results):
        """
        Merges images defined by (buffer, format).
        The method uses PIL to merge images when possible.

        @return                     ``[ (image, format) ]``
        """
        if len(results) == 1:
            results = results[0]
            self._check_thumbnail_tuple(results)
            return results
        if len(results) == 0:
            return None

        formats_counts = Counter(_[1] for _ in results)
        if len(formats_counts) == 1:
            format = results[0][1]
        else:
            items = sorted(((v, k)
                            for k, v in formats_counts.items()), reverse=False)
            for it in items:
                format = it
                break

        results = [_ for _ in results if _[1] == format]
        if format == "svg":
            return ("\n".join(_[0] for _ in results), format)

        # local import to avoid testing dependency on PIL:
        try:
            from PIL import Image
        except ImportError:  # pragma: no cover
            import Image

        dx = 0.
        dy = 0.
        over = 0.7
        imgs = []
        for in_bytes, _ in results:
            img = Image.open(BytesIO(in_bytes))
            imgs.append(img)
            dx = max(dx, img.size[0])
            dy += img.size[1] * over

        new_im = Image.new('RGB', (int(dx), int(dy)), (220, 220, 220))
        for img in imgs:
            dy -= img.size[1] * over
            new_im.paste(img, (0, max(int(dy), 0)))

        if max(dx, dy) > 0:
            image_buffer = BytesIO()
            new_im.save(image_buffer, "PNG")
            b = image_buffer.getvalue(), "png"
            return b
        b = None, "png"
        return b
