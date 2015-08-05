# -*- coding: utf-8 -*-
"""
@file
@brief Defines runpython directives.
See `Tutorial: Writing a simple extension <http://sphinx-doc.org/extdev/tutorial.html>`_

.. versionadded:: 1.2
"""
import os
import sys
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.locale import _ as _locale
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.util.nodes import set_source_info, process_index_entry
from .texts_language import TITLES
from io import StringIO


def run_python_script(script, params={}):
    """
    execute a script python as a string

    @param  script      python script
    @param  params      params to add before the execution
    @return             stdout, stderr
    """
    obj = compile(script, "", "exec")

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

    exec(obj, globals(), loc)

    sys.stdout = kout
    sys.stderr = kerr

    return sout.getvalue(), serr.getvalue()


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
    on the standard output. It it added to the documentation::

        import sys
        print("::")
        print("    " + str(sys.version_info))

    If give the following results:

    .. runpython::

        import sys
        print("::")
        print("    " + str(sys.version_info))

    @endexample
    """
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'indent': directives.unchanged,
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

        # env
        if hasattr(self.state.document.settings, "env"):
            env = self.state.document.settings.env
        else:
            env = None

        if env is None:
            # we need an access to the environment to run the script
            return []
        else:
            # otherwise, it means sphinx is running
            pass

        # settings and configuration
        config = env.config

        # post
        p = {
            'indent': int(self.options.get("indent", 1)),
        }

        # build node
        node = self.__class__.runpython_class(ids=[], indent=p["indent"])

        # we add the date
        content = self.content

        # run the script
        content = ["if True:"]
        for line in self.content:
            content.append("    " + line)
        script = "\n".join(content)
        out, err = run_python_script(script)
        content = out
        if len(err) > 0:
            content += "\n\nERROR:\n\n" + err

        # add indent
        lines = content.split("\n")
        if p['indent'] > 0:
            lines = [(" " * p['indent'] + _) for _ in lines]

        content = StringList(lines)

        # parse the content into sphinx directive, we add it to section
        paragraph = nodes.paragraph()
        self.state.nested_parse(content, self.content_offset, paragraph)
        node += paragraph
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
