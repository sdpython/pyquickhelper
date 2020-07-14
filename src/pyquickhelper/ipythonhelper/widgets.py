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

import copy


class StaticWidget(object):

    """
    Base Class for Static Widgets
    """

    def __init__(self, name=None, divclass=None):
        """
        constructor

        @param      name        name
        @param      divclass    class for div section
        """
        self.name = name
        if divclass is None:
            self.divargs = ""
        else:
            self.divargs = 'class:"{0}"'.format(divclass)

    def __repr__(self):
        """
        operator, call method html
        """
        return self.html()

    def _repr_html_(self):
        """
        operator, call method html
        """
        return self.html()

    def html(self):
        "abstract method"
        raise NotImplementedError(  # pragma: no cover
            "This should overriden.")

    def copy(self):
        """
        calls deepcopy

        @return     copy of self
        """
        return copy.deepcopy(self)

    def renamed(self, name):
        """
        rename *name* if *name* is an attribute

        @return     object
        """
        if (self.name is not None) and (self.name != name):
            obj = self.copy()
        else:
            obj = self
        obj.name = name
        return obj


class RangeWidget(StaticWidget):

    """
    Range (slider) widget

    The class overloads :meth:`html <pyquickhelper.ipythonhelper.widgets.RangeWidget.html>`
    and :meth:`values <pyquickhelper.ipythonhelper.widgets.RangeWidget.values>`.
    """
    slider_html = ('<b>{name}:</b> <input type="range" name="{name}" '
                   'min="{range[0]}" max="{range[1]}" step="{range[2]}" '
                   'value="{default}" style="{style}" '
                   'oninput="interactUpdate(this.parentNode);" '
                   'onchange="interactUpdate(this.parentNode);">')

    def __init__(self, min, max, step=1, name=None,
                 default=None, width=350, divclass=None,
                 show_range=False):
        """
        @param      min         min value
        @param      max         max value
        @param      step        step
        @param      name        name
        @param      default     default value
        @param      width       width in pixel
        @param      divclass    class for div section
        @param      show_range  boolean
        """
        StaticWidget.__init__(self, name, divclass)
        self.datarange = (min, max, step)
        self.width = width
        self.show_range = show_range
        if default is None:
            self.default = min
        else:
            self.default = default

    def values(self):
        """
        @return     all possible values
        """
        min, max, step = self.datarange
        import numpy as np
        return np.arange(min, max + step, step)

    def html(self):
        """
        HTML code

        @return     string HTML
        """
        style = ""

        if self.width is not None:
            style += "width:{0}px".format(self.width)

        output = self.slider_html.format(name=self.name, range=self.datarange,
                                         default=self.default, style=style)
        if self.show_range:
            output = "{0} {1} {2}".format(self.datarange[0],
                                          output,
                                          self.datarange[1])
        return output


class DropDownWidget(StaticWidget):

    """
    drop down list
    """

    #: template 1
    select_html = ('<b>{name}:</b> <select name="{name}" '
                   'onchange="interactUpdate(this.parentNode);"> '
                   '{options}'
                   '</select>'
                   )

    #: template 2
    option_html = ('<option value="{value}" '
                   '{selected}>{label}</option>')

    def __init__(self, values, name=None,
                 labels=None, default=None, divclass=None,
                 delimiter="      "):
        """
        @param      values      values for the list
        @param      name        name of the object
        @param      labels      ?
        @param      default     default value
        @param      divclass    class for div section
        @param      delimiter   delimiter
        """
        StaticWidget.__init__(self, name, divclass)
        self._values = values
        self.delimiter = delimiter
        if labels is None:
            labels = map(str, values)
        elif len(labels) != len(values):
            raise ValueError("length of labels must match length of values")
        self.labels = labels

        if default is None:
            self.default = values[0]
        elif default in values:
            self.default = default
        else:
            raise ValueError(  # pragma: no cover
                "if specified, default must be in values")

    def _single_option(self, label, value):
        """
        private
        """
        if value == self.default:
            selected = ' selected '
        else:
            selected = ''
        return self.option_html.format(label=label,
                                       value=value,
                                       selected=selected)

    def values(self):
        """
        return all possible values
        """
        return self._values

    def html(self):
        """
        return HTML string
        """
        options = self.delimiter.join(
            [self._single_option(label, value)
             for (label, value) in zip(self.labels, self._values)]
        )
        return self.select_html.format(name=self.name,
                                       options=options)


class RadioWidget(StaticWidget):

    """
    radio button
    """

    #: template 1
    radio_html = ('<input type="radio" name="{name}" value="{value}" '
                  '{checked} '
                  'onchange="interactUpdate(this.parentNode);">')

    def __init__(self, values, name=None,
                 labels=None, default=None, divclass=None,
                 delimiter="      "):
        """
        @param      values      values for the list
        @param      name        name of the object
        @param      labels      ?
        @param      default     default value
        @param      divclass    class for div section
        @param      delimiter   delimiter
        """
        StaticWidget.__init__(self, name, divclass)
        self._values = values
        self.delimiter = delimiter

        if labels is None:
            labels = map(str, values)
        elif len(labels) != len(values):
            raise ValueError("length of labels must match length of values")
        self.labels = labels

        if default is None:
            self.default = values[0]
        elif default in values:
            self.default = default
        else:
            raise ValueError(  # pragma: no cover
                "if specified, default must be in values: default={0}, values={1}".format(
                    default, values))

    def _single_radio(self, value):
        """
        private
        """
        if value == self.default:
            checked = 'checked="checked"'
        else:
            checked = ''
        return self.radio_html.format(name=self.name, value=value,
                                      checked=checked)

    def values(self):
        """
        return all the possible values
        """
        return self._values

    def html(self):
        """
        return HTML string
        """
        preface = '<b>{name}:</b> '.format(name=self.name)
        return preface + self.delimiter.join(
            ["{0}: {1}".format(label, self._single_radio(value))
             for (label, value) in zip(self.labels, self._values)])
