# -*- coding: utf-8 -*-
"""
@file
@brief Defines runpython directives.
See `Tutorial: Writing a simple extension <http://sphinx-doc.org/extdev/tutorial.html>`_

.. versionadded:: 1.2
"""
from .texts_language import TITLES
import sys
from docutils import nodes, core
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList
from sphinx.util.nodes import nested_parse_with_titles
import traceback

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


def run_python_script(script, params={}, comment=None):
    """
    execute a script python as a string

    @param  script      python script
    @param  params      params to add before the execution
    @param  comment     message to add in a exception when the script fails
    @return             stdout, stderr
    """
    try:
        obj = compile(script, "", "exec")
    except Exception as ec:
        if comment is None:
            comment = ""
        message = "SCRIPT:\n{0}\nPARAMS\n{1}\nCOMMENT\n{1}".format(
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

    try:
        exec(obj, globals(), loc)
    except Exception as ee:
        if comment is None:
            comment = ""
        gout = sout.getvalue()
        gerr = serr.getvalue()
        message = "SCRIPT:\n{0}\nPARAMS\n{1}\nCOMMENT\n{2}\nERR\n{3}\nOUT\n{4}\nEXC\n{5}".format(
            script, params, comment, gout, gerr, ee)
        raise RunPythonExecutionError(message) from ee

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

    @example(A python script which generates documentation)
    The following code prints the version of Python
    on the standard output. It is added to the documentation::

        .. runpython::
            :showcode:

            import sys
            print("sys.version_info=",str(sys.version_info))

    If give the following results:

    .. runpython::
        :showcode:

        import sys
        print("sys.version_info=",str(sys.version_info))

    @endexample

    The directive has three options:
        * ``:indent:<int>`` to indent the output
        * ``:showcode:`` to show the code before its output
        * ``:rst:`` to interpret the output, otherwise, it is considered as raw text
        * ``:sin:<text_for_in>`` which text to display before the code (by default *In*)
        * ``:sout:<text_for_in>`` which text to display before the output (by default *Out*)
        * ``:showout`` if *:rst:* is set up, this flag adds the raw rst output to check what is happening
        * ``:sphinx:`` by default, function `nested_parse_with_titles <http://sphinx-doc.org/extdev/markupapi.html?highlight=nested_parse>`_ is
          used to parse the output of the script, if this option is set to false,
          `public_doctree <http://code.nabla.net/doc/docutils/api/docutils/core/docutils.core.publish_doctree.html>`_.

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

    .. versionchanged:: 1.3
        Titles, references or label are now allowed.
    """
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'indent': directives.unchanged,
                   'showcode': directives.unchanged,
                   'showout': directives.unchanged,
                   'rst': directives.unchanged,
                   'sin': directives.unchanged,
                   'sout': directives.unchanged,
                   'sphinx': directives.unchanged,
                   'sout2': directives.unchanged,
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
        p = {
            'showcode': 'showcode' in self.options,
            'showout': 'showout' in self.options,
            'rst': 'rst' in self.options,
            'sin': self.options.get('sin', TITLES[language_code]["In"]),
            'sout': self.options.get('sout', TITLES[language_code]["Out"]),
            'sout2': self.options.get('sout2', TITLES[language_code]["Out2"]),
            'sphinx': 'sphinx' not in self.options or self.options['sphinx'] in bool_set,
        }
        dind = 0 if p['rst'] else 4
        p['indent'] = int(self.options.get("indent", dind))

        # run the script
        content = ["if True:"]
        for line in self.content:
            content.append("    " + line)
        script = "\n".join(content)
        script_disp = "\n".join(self.content)

        # if an exception is raised, the documentation should report
        # a warning
        # return [document.reporter.warning('messagr', line=self.lineno)]

        out, err = run_python_script(
            script, comment='  File "{0}", line {1}'.format(docname, lineno))
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
            pin = nodes.paragraph(text=p["sout"])
            node += pin

        if p["rst"]:
            settings_overrides = {}
            try:
                v = sett.output_encoding
            except KeyError:
                settings_overrides["output_encoding"] = "unicode"
            try:
                v = sett.doctitle_xform
            except KeyError:
                settings_overrides["doctitle_xform"] = True
            try:
                v = sett.warning_stream
            except KeyError:
                settings_overrides["warning_stream"] = StringIO()
            #'initial_header_level': 2,

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
            pout2 = nodes.paragraph(text=p["sout2"])
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
