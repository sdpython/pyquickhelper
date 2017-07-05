# -*- coding: utf-8 -*-
"""
@file
@brief Defines runpython directives.
See `Tutorial: Writing a simple extension <http://sphinx-doc.org/extdev/tutorial.html>`_

.. versionadded:: 1.2
"""
import sys
import os
import sphinx
from docutils import nodes, core
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList
from sphinx.util.nodes import nested_parse_with_titles
import traceback
from ..loghelper.flog import run_cmd
from ..texthelper.texts_language import TITLES

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


class RunPythonCompileError(Exception):
    """
    exception raised when a piece of code
    included in the documentation does not compile
    """
    pass


class RunPythonExecutionError(Exception):
    """
    exception raised when a piece of code
    included in the documentation raises en exception
    """
    pass


def run_python_script(script, params=None, comment=None, setsysvar=None, process=False, exception=False):
    """
    Execute a script python as a string.

    @param  script      python script
    @param  params      params to add before the execution
    @param  comment     message to add in a exception when the script fails
    @param  setsysvar   if not None, add a member to module *sys*, set up this variable to True,
                        if is remove after the execution
    @param  process     run the script in a separate process
    @param  exception   expects an exception to be raised,
                        fails if it is not, the function returns no output and the
                        error message
    @return             stdout, stderr

    If the execution throws an exception such as
    ``NameError: name 'math' is not defined`` after importing
    the module ``math``. It comes from the fact
    the domain name used by the function
    `exec <https://docs.python.org/3/library/functions.html#exec>`_
    contains the declared objects. Example:

    ::

        import math
        def coordonnees_polaires(x,y):
            rho     = math.sqrt(x*x+y*y)
            theta   = math.atan2 (y,x)
            return rho, theta
        coordonnees_polaires(1, 1)

    The code can be modified into:

    ::

        def fake_function():
            import math
            def coordonnees_polaires(x,y):
                rho     = math.sqrt(x*x+y*y)
                theta   = math.atan2 (y,x)
                return rho, theta
            coordonnees_polaires(1, 1)
        fake_function()

    .. versionchanged:: 1.3
        Parameters *setsysvar*, *process* were added.

    .. versionchanged:: 1.5
        Parameter *exception* was added.
    """
    if params is None:
        params = {}

    if process:
        cmd = sys.executable
        header = ["import sys"]
        if setsysvar:
            header.append("sys.{0} = True".format(setsysvar))
        add = 0
        for path in sys.path:
            if path.endswith("source") or path.endswith("source/") or path.endswith("source\\"):
                header.append("sys.path.append('{0}')".format(
                    path.replace("\\", "\\\\")))
                add += 1
        if add == 0:
            for path in sys.path:
                if path.endswith("src") or path.endswith("src/") or path.endswith("src\\"):
                    header.append("sys.path.append('{0}')".format(
                        path.replace("\\", "\\\\")))
                    add += 1
        if add == 0:
            # we did not find any path linked to the copy of the current module
            # in the documentation
            # we assume the first path of sys.path is part of the unit test
            path = sys.path[0]
            path = os.path.join(path, "..", "..", "src")
            if os.path.exists(path):
                header.append("sys.path.append('{0}')".format(
                    path.replace("\\", "\\\\")))
                add += 1
        if add == 0:
            raise RunPythonExecutionError(
                "unable to find a path to add:\n{0}".format("\n".join(sys.path)))
        header.append('')
        script = "\n".join(header) + script
        sin = script
        try:
            out, err = run_cmd(cmd, script, wait=True)
            return out, err
        except Exception as ee:
            if not exception:
                message = "SCRIPT:\n{0}\nPARAMS\n{1}\nCOMMENT\n{2}\nERR\n{3}\nOUT\n{4}\nEXC\n{5}".format(
                    script, params, comment, "", str(ee), ee)
                raise RunPythonExecutionError(message) from ee
            else:
                return str(ee), str(ee)
    else:

        try:
            obj = compile(script, "", "exec")
        except Exception as ec:
            if comment is None:
                comment = ""
            message = "SCRIPT:\n{0}\nPARAMS\n{1}\nCOMMENT\n{2}".format(
                script, params, comment)
            raise RunPythonCompileError(message) from ec

        loc = locals()
        for k, v in params.items():
            loc[k] = v
        loc["__dict__"] = params

        kout = sys.stdout
        kerr = sys.stderr
        sout = StringIO()
        serr = StringIO()
        sys.stdout = sout
        sys.stderr = serr

        if setsysvar is not None:
            sys.__dict__[setsysvar] = True

        try:
            exec(obj, globals(), loc)
        except Exception as ee:
            if setsysvar is not None:
                del sys.__dict__[setsysvar]
            if comment is None:
                comment = ""
            gout = sout.getvalue()
            gerr = serr.getvalue()
            sys.stdout = kout
            sys.stderr = kerr

            import traceback
            excs = traceback.format_exc()
            lines = excs.split("\n")
            excs = "\n".join(
                _ for _ in lines if "sphinx_runpython_extension.py" not in _)

            if not exception:
                message = "SCRIPT:\n{0}\nPARAMS\n{1}\nCOMMENT\n{2}\nERR\n{3}\nOUT\n{4}\nEXC\n{5}\nTRACEBACK\n{6}".format(
                    script, params, comment, gout, gerr, ee, excs)
                raise RunPythonExecutionError(message) from ee
            else:
                return (gout + "\n" + gerr), (gerr + "\n" + excs)

        if setsysvar is not None:
            del sys.__dict__[setsysvar]

        gout = sout.getvalue()
        gerr = serr.getvalue()
        sys.stdout = kout
        sys.stderr = kerr
        return gout, gerr


class runpython_node(nodes.Structural, nodes.Element):

    """
    defines *runpython* node
    """
    pass


class RunPythonDirective(Directive):

    """
    extracts script to run described by ``.. runpython::``
    and modifies the documentation

    .. exref::
        :title: A python script which generates documentation

        The following code prints the version of Python
        on the standard output. It is added to the documentation::

            .. runpython::
                :showcode:

                import sys
                print("sys.version_info=", str(sys.version_info))

        If give the following results:

        .. runpython::

            import sys
            print("sys.version_info=", str(sys.version_info))

        Options *showcode* can be used to display the code.
        The option *rst* will assume the output is in RST format and must be
        interpreted. *showout* will complement the RST output with the raw format.

    The directive has a couple of options:

    * ``:indent:<int>`` to indent the output
    * ``:showcode:`` to show the code before its output
    * ``:rst:`` to interpret the output, otherwise, it is considered as raw text
    * ``:sin:<text_for_in>`` which text to display before the code (by default *In*)
    * ``:sout:<text_for_in>`` which text to display before the output (by default *Out*)
    * ``:showout`` if *:rst:* is set up, this flag adds the raw rst output to check what is happening
    * ``:sphinx:`` by default, function `nested_parse_with_titles <http://sphinx-doc.org/extdev/markupapi.html?highlight=nested_parse>`_ is
      used to parse the output of the script, if this option is set to false,
      `public_doctree <http://code.nabla.net/doc/docutils/api/docutils/core/docutils.core.publish_doctree.html>`_.
    * ``:setsysvar:`` adds a member to *sys* module, the module can act differently based on that information,
      if the value is left empty, *sys.enable_disabled_documented_pieces_of_code* will be be set up to *True*.
    * ``:process:`` run the script in an another process
    * ``:exception:`` the code throws an exception but it expected. The error is displayed.

    Option *rst* can be used the following way::

        .. runpython::
            :rst:

            for l in range(0,10):
                print("**line**", "*" +str(l)+"*")
                print('')

    Which displays interpreted RST:

    .. runpython::
        :rst:

        for l in range(0,10):
            print("**line**", "*" +str(l)+"*")
            print('')

    If the directive produces RST text to be included later in the documentation,
    it is able to interpret
    `docutils directives <http://docutils.sourceforge.net/docs/ref/rst/directives.html>`_
    and `Sphinx directives <http://sphinx-doc.org/rest.html>`_
    with function `nested_parse_with_titles <http://sphinx-doc.org/extdev/markupapi.html?highlight=nested_parse>`_

    Unless *process* option is enabled, global variables cannot be used.

    .. versionchanged:: 1.3
        Titles, references or label are now allowed.

    .. versionchanged:: 1.5
        Exception is now caught. It fails if no error is thrown.
    """
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'indent': directives.unchanged,
        'showcode': directives.unchanged,
        'showout': directives.unchanged,
        'rst': directives.unchanged,
        'sin': directives.unchanged,
        'sout': directives.unchanged,
        'sphinx': directives.unchanged,
        'sout2': directives.unchanged,
        'setsysvar': directives.unchanged,
        'process': directives.unchanged,
        'exception': directives.unchanged,
    }
    has_content = True
    runpython_class = runpython_node

    def run(self):
        """
        extracts the information in a dictionary,
        run the script

        @return      a list of nodes
        """
        # settings
        sett = self.state.document.settings
        language_code = sett.language_code
        lineno = self.lineno

        # add the instance to the global settings
        if hasattr(sett, "out_runpythonlist"):
            sett.out_runpythonlist.append(self)

        # env
        if hasattr(self.state.document.settings, "env"):
            env = self.state.document.settings.env
        else:
            env = None

        if env is None:
            docname = "___unknown_docname___"
        else:
            docname = env.docname

        # post
        bool_set = (True, 1, "True", "1", "true")
        bool_set_ = (True, 1, "True", "1", "true", '')
        p = {
            'showcode': 'showcode' in self.options,
            'showout': 'showout' in self.options,
            'rst': 'rst' in self.options,
            'sin': self.options.get('sin', TITLES[language_code]["In"]),
            'sout': self.options.get('sout', TITLES[language_code]["Out"]),
            'sout2': self.options.get('sout2', TITLES[language_code]["Out2"]),
            'sphinx': 'sphinx' not in self.options or self.options['sphinx'] in bool_set,
            'setsysvar': self.options.get('setsysvar', None),
            'process': 'process' in self.options and self.options['process'] in bool_set_,
            'exception': 'exception' in self.options and self.options['exception'] in bool_set_,
        }

        if p['setsysvar'] is not None and len(p['setsysvar']) == 0:
            p['setsysvar'] = 'enable_disabled_documented_pieces_of_code'
        dind = 0 if p['rst'] else 4
        p['indent'] = int(self.options.get("indent", dind))

        # run the script
        name = "run_python_script_{0}".format(id(p))
        if p['process']:
            content = ["if True:"]
        else:
            content = ["def {0}():".format(name)]
        for line in self.content:
            content.append("    " + line)
        if not p['process']:
            content.append("{0}()".format(name))
        script = "\n".join(content)
        script_disp = "\n".join(self.content)

        # if an exception is raised, the documentation should report
        # a warning
        # return [document.reporter.warning('messagr', line=self.lineno)]

        out, err = run_python_script(script,
                                     comment='  File "{0}", line {1}'.format(
                                         docname, lineno),
                                     setsysvar=p['setsysvar'], process=p[
                                         "process"],
                                     exception=p['exception'])

        if out is not None:
            out = out.rstrip(" \n\r\t")
        if err is not None:
            err = err.rstrip(" \n\r\t")
        content = out
        if len(err) > 0:
            content += "\n\nERROR:\n\n" + err

        # add member
        self.exe_class = p.copy()
        self.exe_class.update(dict(out=out, err=err, script=script))

        # add indent
        def add_indent(content, nbind):
            lines = content.split("\n")
            if nbind > 0:
                lines = [(" " * nbind + _) for _ in lines]
            content = "\n".join(lines)
            return content

        content = add_indent(content, p['indent'])

        # build node
        node = self.__class__.runpython_class(rawsource=content,
                                              indent=p["indent"],
                                              showcode=p["showcode"],
                                              rst=p["rst"],
                                              sin=p["sin"],
                                              sout=p["sout"])

        if p["showcode"]:
            pin = nodes.paragraph(text=p["sin"])
            pcode = nodes.literal_block(script_disp, script_disp)
            node += pin
            node += pcode
        elif len(self.options.get('sout', '')) == 0:
            p["sout"] = ''
            p["sout2"] = ''

        if p["rst"]:
            settings_overrides = {}
            try:
                sett.output_encoding
            except KeyError:
                settings_overrides["output_encoding"] = "unicode"
            # try:
            #     sett.doctitle_xform
            # except KeyError:
            #     settings_overrides["doctitle_xform"] = True
            try:
                sett.warning_stream
            except KeyError:
                settings_overrides["warning_stream"] = StringIO()
            #'initial_header_level': 2,

            if len(p["sout"]) > 0:
                node += nodes.paragraph(text=p["sout"])

            try:
                if p['sphinx']:
                    st = StringList(content.replace("\r", "").split("\n"))
                    nested_parse_with_titles(self.state, st, node)
                    dt = None
                else:
                    dt = core.publish_doctree(
                        content, settings=sett,
                        settings_overrides=settings_overrides)
            except Exception as e:
                tab = content
                content = ["::"]
                st = StringIO()
                traceback.print_exc(file=st)
                content.append("")
                trace = st.getvalue()
                trace += "\n----------------------OPT\n" + str(p)
                trace += "\n----------------------EXC\n" + str(e)
                trace += "\n----------------------SETT\n" + str(sett)
                trace += "\n----------------------ENV\n" + str(env)
                trace += "\n----------------------DOCNAME\n" + str(docname)
                trace += "\n----------------------CODE\n"
                content.extend("    " + _ for _ in trace.split("\n"))
                content.append("")
                content.append("")
                content.extend("    " + _ for _ in tab.split("\n"))
                content = "\n".join(content)
                pout = nodes.literal_block(content, content)
                node += pout
                dt = None

            if dt is not None:
                for ch in dt.children:
                    node += ch

        if not p["rst"] or p["showout"]:
            text = p["sout2"] if p["rst"] else p["sout"]
            if len(text) > 0:
                pout2 = nodes.paragraph(text=text)
                node += pout2
            pout = nodes.literal_block(content, content)
            node += pout

        p['runpython'] = node

        # classes
        node['classes'] += "-runpython"
        ns = [node]
        return ns


def visit_runpython_node(self, node):
    """
    what to do when visiting a node runpython
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    pass


def depart_runpython_node(self, node):
    """
    what to do when leaving a node runpython
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    pass


def setup(app):
    """
    setup for ``runpython`` (sphinx)
    """
    app.add_config_value('out_runpythonlist', [], 'env')
    if hasattr(app, "add_mapping"):
        app.add_mapping('runpython', runpython_node)

    app.add_node(runpython_node,
                 html=(visit_runpython_node, depart_runpython_node),
                 latex=(visit_runpython_node, depart_runpython_node),
                 text=(visit_runpython_node, depart_runpython_node))

    app.add_directive('runpython', RunPythonDirective)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
