"""
@file
@brief To add interactive widgets in a notebook and connect it to Python function,
Source: https://github.com/jakevdp/ipywidgets, the module was modified for Python 3
See notebook :ref:`havingaforminanotebookrst`.

Copyright (c) 2013, Jake Vanderplas
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

* Neither the name of the {organization} nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from collections import OrderedDict
import itertools
import base64


def _get_html(obj):
    """
    Get the HTML representation of an object
    """
    # TODO: use displaypub to make this more general
    from IPython import get_ipython
    ip = get_ipython()
    if ip is not None:
        png_rep = ip.display_formatter.formatters['image/png'](obj)
    else:
        png_rep = None

    if png_rep is not None:  # pragma: no cover
        # do not move this import to the root or
        # you will be exposed to the issue mentioned by
        # function fix_tkinter_issues_virtualenv
        import matplotlib.pyplot as plt
        if isinstance(obj, plt.Figure):
            plt.close(obj)  # keep from displaying twice
        new_bytes = base64.b64encode(png_rep)
        new_str = new_bytes.decode("utf8")
        return '<img src="data:image/png;base64,{0}">'.format(new_str)
    else:
        return "<p> {0} </p>".format(str(obj))

    rep = ip.display_formatter.formatters['text/html'](obj)

    if rep is not None:
        return rep
    elif hasattr(obj, '_repr_html_'):
        return obj._repr_html_()


class StaticInteract(object):

    """
    Static Interact Object

    See notebook :ref:`havingaforminanotebookrst`.

    @warning In order to be fast in the notebook, the function is called for every possible
        combination of values the controls can return. If it is a graph,
        all graphs are generared.
    """

    template = """
    <script type="text/javascript">
      var mergeNodes = function(a, b) {{
        return [].slice.call(a).concat([].slice.call(b));
      }}; // http://stackoverflow.com/questions/914783/javascript-nodelist/17262552#17262552
      function interactUpdate(div){{
         var outputs = div.getElementsByTagName("div");
         //var controls = div.getElementsByTagName("input");
         var controls = mergeNodes(div.getElementsByTagName("input"), div.getElementsByTagName("select"));
         function nameCompare(a,b) {{
            return a.getAttribute("name").localeCompare(b.getAttribute("name"));
         }}
         controls.sort(nameCompare);

         var value = "";
         for(i=0; i<controls.length; i++){{
           if((controls[i].type == "range") || controls[i].checked){{
             value = value + controls[i].getAttribute("name") + controls[i].value;
           }}
           if(controls[i].type == "select-one"){{
             value = value + controls[i].getAttribute("name") + controls[i][controls[i].selectedIndex].value;
           }}
         }}

         for(i=0; i<outputs.length; i++){{
           var name = outputs[i].getAttribute("name");
           if(name == value){{
              outputs[i].style.display = 'block';
           }} else if(name != "controls"){{
              outputs[i].style.display = 'none';
           }}
         }}
      }}
    </script>

    <div>
      {outputs}
      {widgets}
    </div>
    """

    subdiv_template = """
    <div name="{name}" style="display:{display}">
      {content}
    </div>
    """

    @staticmethod
    def _get_strrep(val):
        """
        Need to match javascript string rep
        """
        # TODO: is there a better way to do this?
        if isinstance(val, str):
            return val
        elif val % 1 == 0:
            return str(int(val))
        else:
            return str(val)

    def __init__(self, function, **kwargs):
        """
        constructor
        """
        # TODO: implement *args (difficult because of the name thing)
        # update names
        for name in kwargs:
            kwargs[name] = kwargs[name].renamed(name)

        self.widgets = OrderedDict(kwargs)
        self.function = function

    def _output_html(self):
        """
        html output

        @return     string
        """
        names = list(self.widgets)
        values = [widget.values() for widget in self.widgets.values()]
        defaults = tuple([widget.default for widget in self.widgets.values()])

        # Now reorder alphabetically by names so divnames match javascript
        names, values, defaults = zip(*sorted(zip(names, values, defaults)))

        results = [self.function(**dict(zip(names, vals)))
                   for vals in itertools.product(*values)]

        divnames = [''.join(['{0}{1}'.format(n, self._get_strrep(v))
                             for n, v in zip(names, vals)])
                    for vals in itertools.product(*values)]
        display = [vals == defaults for vals in itertools.product(*values)]

        tmplt = self.subdiv_template
        return "".join(tmplt.format(name=divname,
                                    display="block" if disp else "none",
                                    content=_get_html(result))
                       for divname, result, disp in zip(divnames, results, display))

    def _widget_html(self):
        """
        @return     string
        """
        return "\n<br>\n".join([widget.html()
                                for name, widget in sorted(self.widgets.items())])

    def html(self):
        """
        Produce the HTML output, insert results from @see me _output_html and
        @see me _widget_html and insert it into the template.

        @return     string
        """
        return self.template.format(outputs=self._output_html(),
                                    widgets=self._widget_html())

    def _repr_html_(self):
        """
        Synonym for :meth:`html <pyquickhelper.ipythonhelper.interact.StaticInteract.html>`.
        """
        return self.html()
