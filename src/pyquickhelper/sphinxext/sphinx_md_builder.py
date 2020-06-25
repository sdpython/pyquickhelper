# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to output the documentation in :epkg:`Markdown`
or *MD*. It is inspired from `restbuilder
<https://bitbucket.org/birkenfeld/sphinx-contrib/src/6f417e74a22dadb9e0370696f219e63f1b196344/restbuilder/?at=default>`_.
I replicate its license here:

::

    Copyright (c) 2012-2013 by Freek Dijkstra <software@macfreek.nl>.
    Some rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

.. versionadded:: 1.8
"""
import os
import textwrap
from os import path
from sphinx.util import logging
from docutils.io import StringOutput
from sphinx.builders import Builder
from sphinx.util.osutil import ensuredir
from docutils import nodes, writers
from sphinx import addnodes
from sphinx.locale import admonitionlabels, versionlabels, _
from sphinx.writers.text import TextTranslator, MAXWIDTH, STDINDENT
from ._sphinx_common_builder import CommonSphinxWriterHelpers
from .sphinx_downloadlink_extension import visit_downloadlink_node_md, depart_downloadlink_node_md


class MdTranslator(TextTranslator, CommonSphinxWriterHelpers):
    """
    Defines a :epkg:`MD` translator.
    """

    def __init__(self, builder, document):
        if not hasattr(builder, "config"):
            raise TypeError(  # pragma: no cover
                "Builder has no config: {}".format(type(builder)))
        TextTranslator.__init__(self, document, builder)

        newlines = builder.config.text_newlines
        if newlines == 'windows':
            self.nl = '\r\n'
        elif newlines == 'native':
            self.nl = os.linesep
        else:
            self.nl = '\n'
        self.sectionchars = builder.config.text_sectionchars
        self.states = [[]]
        self.stateindent = [0]
        self.list_counter = []
        self.sectionlevel = 0
        self._table = []
        if self.builder.config.md_indent:
            self.indent = self.builder.config.md_indent
        else:
            self.indent = STDINDENT
        self.wrapper = textwrap.TextWrapper(
            width=STDINDENT, break_long_words=False, break_on_hyphens=False)

    def log_unknown(self, type, node):
        logger = logging.getLogger("MdBuilder")
        logger.warning("%s(%s) unsupported formatting" % (type, node))

    def wrap(self, text, width=STDINDENT):
        self.wrapper.width = width
        return self.wrapper.wrap(text)

    def add_text(self, text):
        self.states[-1].append((-1, text))

    def new_state(self, indent=STDINDENT):
        self.states.append([])
        self.stateindent.append(indent)

    def end_state(self, wrap=True, end=[''], first=None):
        content = self.states.pop()
        maxindent = sum(self.stateindent)
        indent = self.stateindent.pop()
        result = []
        toformat = []

        def do_format():
            if not toformat:
                return
            if wrap:
                res = self.wrap(''.join(toformat), width=MAXWIDTH - maxindent)
            else:
                res = ''.join(toformat).splitlines()
            if end:
                res += end
            result.append((indent, res))

        for itemindent, item in content:
            if itemindent == -1:
                toformat.append(item)
            else:
                do_format()
                result.append((indent + itemindent, item))
                toformat = []

        do_format()

        if first is not None and result:
            itemindent, item = result[0]
            if item:
                result.insert(0, (itemindent - indent, [first + item[0]]))
                result[1] = (itemindent, item[1:])

        self.states[-1].extend(result)

    def visit_document(self, node):
        self.new_state(0)

    def depart_document(self, node):
        self.end_state()
        self.body = self.nl.join(line and (' ' * indent + line)
                                 for indent, lines in self.states[0]
                                 for line in lines)

    def visit_highlightlang(self, node):
        raise nodes.SkipNode

    def visit_section(self, node):
        self._title_char = self.sectionchars[self.sectionlevel]
        self.sectionlevel += 1

    def depart_section(self, node):
        self.sectionlevel -= 1

    def visit_topic(self, node):
        self.new_state(0)

    def depart_topic(self, node):
        self.end_state()

    visit_sidebar = visit_topic
    depart_sidebar = depart_topic

    def visit_rubric(self, node):
        self.new_state(0)
        self.add_text('-[ ')

    def depart_rubric(self, node):
        self.add_text(' ]-')
        self.end_state()

    def visit_compound(self, node):
        # self.log_unknown("compount", node)
        pass

    def depart_compound(self, node):
        pass

    def visit_glossary(self, node):
        # self.log_unknown("glossary", node)
        pass

    def depart_glossary(self, node):
        pass

    def visit_title(self, node):
        if isinstance(node.parent, nodes.Admonition):
            self.add_text(node.astext() + ': ')
            raise nodes.SkipNode
        self.new_state(0)

    def depart_title(self, node):
        if isinstance(node.parent, nodes.section):
            prefix = "#" * self.sectionlevel
        else:
            prefix = "#" * 6
        text = prefix + ' ' + ''.join(x[1]
                                      for x in self.states.pop() if x[0] == -1)
        self.stateindent.pop()
        self.states[-1].append((0, ['', text, '']))

    def visit_subtitle(self, node):
        # self.log_unknown("subtitle", node)
        pass

    def depart_subtitle(self, node):
        pass

    def visit_attribution(self, node):
        self.add_text('-- ')

    def depart_attribution(self, node):
        pass

    def visit_desc(self, node):
        self.new_state(0)

    def depart_desc(self, node):
        self.end_state()

    def visit_desc_signature(self, node):
        if node.parent['objtype'] in ('class', 'exception', 'method', 'function'):
            self.add_text('**')
        else:
            self.add_text('``')

    def depart_desc_signature(self, node):
        if node.parent['objtype'] in ('class', 'exception', 'method', 'function'):
            self.add_text('**')
        else:
            self.add_text('``')

    def visit_desc_name(self, node):
        # self.log_unknown("desc_name", node)
        pass

    def depart_desc_name(self, node):
        pass

    def visit_desc_addname(self, node):
        # self.log_unknown("desc_addname", node)
        pass

    def depart_desc_addname(self, node):
        pass

    def visit_desc_type(self, node):
        # self.log_unknown("desc_type", node)
        pass

    def depart_desc_type(self, node):
        pass

    def visit_desc_returns(self, node):
        self.add_text(' -> ')

    def depart_desc_returns(self, node):
        pass

    def visit_desc_parameterlist(self, node):
        self.add_text('(')
        self.first_param = 1

    def depart_desc_parameterlist(self, node):
        self.add_text(')')

    def visit_desc_parameter(self, node):
        if not self.first_param:
            self.add_text(', ')
        else:
            self.first_param = 0
        self.add_text(node.astext())
        raise nodes.SkipNode

    def visit_desc_optional(self, node):
        self.add_text('[')

    def depart_desc_optional(self, node):
        self.add_text(']')

    def visit_desc_annotation(self, node):
        content = node.astext()
        if len(content) > MAXWIDTH:
            h = int(MAXWIDTH / 3)
            content = content[:h] + " ... " + content[-h:]
            self.add_text(content)
            raise nodes.SkipNode

    def depart_desc_annotation(self, node):
        pass

    def visit_refcount(self, node):
        pass

    def depart_refcount(self, node):
        pass

    def visit_desc_content(self, node):
        self.new_state(self.indent)

    def depart_desc_content(self, node):
        self.end_state()

    def visit_figure(self, node):
        self.new_state(self.indent)

    def depart_figure(self, node):
        self.end_state()

    def visit_caption(self, node):
        # self.log_unknown("caption", node)
        pass

    def depart_caption(self, node):
        pass

    def visit_productionlist(self, node):
        self.new_state(self.indent)
        names = []
        for production in node:
            names.append(production['tokenname'])
        maxlen = max(len(name) for name in names)
        for production in node:
            if production['tokenname']:
                self.add_text(production['tokenname'].ljust(maxlen) + ' ::=')
                lastname = production['tokenname']
            else:
                self.add_text('%s    ' % (' ' * len(lastname)))
            self.add_text(production.astext() + self.nl)
        self.end_state(wrap=False)
        raise nodes.SkipNode

    def visit_seealso(self, node):
        self.new_state(self.indent)

    def depart_seealso(self, node):
        self.end_state(first='')

    def visit_footnote(self, node):
        self._footnote = node.children[0].astext().strip()
        self.new_state(len(self._footnote) + self.indent)

    def depart_footnote(self, node):
        self.end_state(first='[%s] ' % self._footnote)

    def visit_citation(self, node):
        if len(node) and isinstance(node[0], nodes.label):
            self._citlabel = node[0].astext()
        else:
            self._citlabel = ''
        self.new_state(len(self._citlabel) + self.indent)

    def depart_citation(self, node):
        self.end_state(first='[%s] ' % self._citlabel)

    def visit_label(self, node):
        raise nodes.SkipNode

    def visit_option_list(self, node):
        # self.log_unknown("option_list", node)
        pass

    def depart_option_list(self, node):
        pass

    def visit_option_list_item(self, node):
        self.new_state(0)

    def depart_option_list_item(self, node):
        self.end_state()

    def visit_option_group(self, node):
        self._firstoption = True

    def depart_option_group(self, node):
        self.add_text('     ')

    def visit_option(self, node):
        if self._firstoption:
            self._firstoption = False
        else:
            self.add_text(', ')

    def depart_option(self, node):
        pass

    def visit_option_string(self, node):
        # self.log_unknown("option_string", node)
        pass

    def depart_option_string(self, node):
        pass

    def visit_option_argument(self, node):
        self.add_text(node['delimiter'])

    def depart_option_argument(self, node):
        pass

    def visit_description(self, node):
        # self.log_unknown("description", node)
        pass

    def depart_description(self, node):
        pass

    def visit_tabular_col_spec(self, node):
        raise nodes.SkipNode

    def visit_colspec(self, node):
        self._table[0].append(node['colwidth'])
        raise nodes.SkipNode

    def visit_tgroup(self, node):
        # self.log_unknown("tgroup", node)
        pass

    def depart_tgroup(self, node):
        pass

    def visit_thead(self, node):
        # self.log_unknown("thead", node)
        pass

    def depart_thead(self, node):
        pass

    def visit_tbody(self, node):
        self._table.append('sep')

    def depart_tbody(self, node):
        pass

    def visit_row(self, node):
        self._table.append([])

    def depart_row(self, node):
        pass

    def visit_entry(self, node):
        if hasattr(node, 'morerows') or hasattr(node, 'morecols'):
            raise NotImplementedError(  # pragma: no cover
                'Column or row spanning cells are not implemented.')
        self.new_state(0)

    def depart_entry(self, node):
        text = self.nl.join(self.nl.join(x[1]) for x in self.states.pop())
        self.stateindent.pop()
        self._table[-1].append(text)

    def visit_table(self, node):
        if self._table:
            raise NotImplementedError('Nested tables are not supported.')
        self.new_state(0)
        self._table = [[]]

    def depart_table(self, node):
        lines = self._table[1:]
        fmted_rows = []
        colwidths = self._table[0]
        realwidths = colwidths[:]
        separator = 0
        # don't allow paragraphs in table cells for now
        for line in lines:
            if line == 'sep':
                separator = len(fmted_rows)
            else:
                cells = []
                for i, cell in enumerate(line):
                    try:
                        par = self.wrap(cell, width=int(colwidths[i]))
                    except (IndexError, ValueError):
                        par = self.wrap(cell)
                    if par:
                        maxwidth = max(map(len, par))
                    else:
                        maxwidth = 0
                    if i >= len(realwidths):
                        realwidths.append(maxwidth)
                    elif isinstance(realwidths[i], str):
                        realwidths[i] = maxwidth
                    else:
                        realwidths[i] = max(realwidths[i], maxwidth)
                    cells.append(par)
                fmted_rows.append(cells)

        def writesep(char='-'):
            out = []
            for width in realwidths:
                out.append('---')
            self.add_text(' | '.join(out) + self.nl)

        def writerow(row):
            lines = zip(*row)
            for line in lines:
                out = []
                for i, cell in enumerate(line):
                    if cell:
                        out.append(cell)
                    else:
                        out.append('')
                self.add_text(' | '.join(out) + self.nl)

        for i, row in enumerate(fmted_rows):
            if separator and i == separator:
                writesep('-')
            writerow(row)
        self._table = []
        self.end_state(wrap=False)

    def visit_acks(self, node):
        self.new_state(0)
        self.add_text(', '.join(n.astext()
                                for n in node.children[0].children) + '.')
        self.end_state()
        raise nodes.SkipNode

    def visit_simpleimage(self, node):
        self.visit_image(node)

    def depart_simpleimage(self, node):
        self.depart_image(node)

    def visit_image(self, node):
        self.new_state(0)
        atts = self.base_visit_image(node, self.builder.md_image_dest)
        alt = atts.get("alt", "")
        uri = atts.get('uri', atts['src'])
        width = atts.get('width', '').replace('px', '').replace("auto", "")
        height = atts.get('height', '').replace('px', '').replace("auto", "")
        style = " ={0}x{1}".format(width, height)
        if style == " =x":
            style = ""
        text = "![{0}]({1}{2})".format(alt, uri, style)
        self.add_text(text)

    def depart_image(self, node):
        self.end_state(wrap=False, end=None)

    def visit_transition(self, node):
        indent = sum(self.stateindent)
        self.new_state(0)
        self.add_text('=' * (MAXWIDTH - indent))
        self.end_state()
        raise nodes.SkipNode

    def visit_bullet_list(self, node):
        self.list_counter.append(-1)

    def depart_bullet_list(self, node):
        self.list_counter.pop()

    def visit_enumerated_list(self, node):
        self.list_counter.append(0)

    def depart_enumerated_list(self, node):
        self.list_counter.pop()

    def visit_definition_list(self, node):
        self.list_counter.append(-2)

    def depart_definition_list(self, node):
        self.list_counter.pop()

    def visit_list_item(self, node):
        if self.list_counter[-1] == -1:
            # bullet list
            self.new_state(self.indent)
        elif self.list_counter[-1] == -2:
            # definition list
            pass
        else:
            # enumerated list
            self.list_counter[-1] += 1
            self.new_state(len(str(self.list_counter[-1])) + self.indent)

    def depart_list_item(self, node):
        if self.list_counter[-1] == -1:
            self.end_state(first='* ', end=None)
        elif self.list_counter[-1] == -2:
            pass
        else:
            self.end_state(first='%s. ' % self.list_counter[-1], end=None)

    def visit_definition_list_item(self, node):
        self._li_has_classifier = len(node) >= 2 and \
            isinstance(node[1], nodes.classifier)

    def depart_definition_list_item(self, node):
        pass

    def visit_term(self, node):
        self.new_state(0)

    def depart_term(self, node):
        if not self._li_has_classifier:
            self.end_state(end=None)

    def visit_termsep(self, node):
        self.add_text(', ')
        raise nodes.SkipNode

    def visit_classifier(self, node):
        self.add_text(' : ')

    def depart_classifier(self, node):
        self.end_state(end=None)

    def visit_definition(self, node):
        self.new_state(self.indent)

    def depart_definition(self, node):
        self.end_state()

    def visit_field_list(self, node):
        # self.log_unknown("field_list", node)
        pass

    def depart_field_list(self, node):
        pass

    def visit_field(self, node):
        self.new_state(0)

    def depart_field(self, node):
        self.end_state(end=None)

    def visit_field_name(self, node):
        self.add_text(':')

    def depart_field_name(self, node):
        self.add_text(':')
        content = node.astext()
        self.add_text((16 - len(content)) * ' ')

    def visit_field_body(self, node):
        self.new_state(self.indent)

    def depart_field_body(self, node):
        self.end_state()

    def visit_centered(self, node):
        pass

    def depart_centered(self, node):
        pass

    def visit_hlist(self, node):
        # self.log_unknown("hlist", node)
        pass

    def depart_hlist(self, node):
        pass

    def visit_hlistcol(self, node):
        # self.log_unknown("hlistcol", node)
        pass

    def depart_hlistcol(self, node):
        pass

    def visit_admonition(self, node):
        self.new_state(0)

    def depart_admonition(self, node):
        self.end_state()

    def _visit_admonition(self, node):
        self.new_state(self.indent)

    def _make_depart_admonition(name):
        def depart_admonition(self, node):
            self.end_state(first=admonitionlabels[name] + ': ')
        return depart_admonition

    visit_attention = _visit_admonition
    depart_attention = _make_depart_admonition('attention')
    visit_caution = _visit_admonition
    depart_caution = _make_depart_admonition('caution')
    visit_danger = _visit_admonition
    depart_danger = _make_depart_admonition('danger')
    visit_error = _visit_admonition
    depart_error = _make_depart_admonition('error')
    visit_hint = _visit_admonition
    depart_hint = _make_depart_admonition('hint')
    visit_important = _visit_admonition
    depart_important = _make_depart_admonition('important')
    visit_note = _visit_admonition
    depart_note = _make_depart_admonition('note')
    visit_tip = _visit_admonition
    depart_tip = _make_depart_admonition('tip')
    visit_warning = _visit_admonition
    depart_warning = _make_depart_admonition('warning')

    def visit_literal_block(self, node):
        self.add_text("```")
        self.new_state(0)

    def depart_literal_block(self, node):
        self.add_text(self.nl)
        self.add_text('```')
        self.end_state(wrap=False)

    def visit_doctest_block(self, node):
        self.new_state(0)

    def depart_doctest_block(self, node):
        self.end_state(wrap=False)

    def visit_line_block(self, node):
        self.new_state(0)

    def depart_line_block(self, node):
        self.end_state(wrap=False)

    def visit_line(self, node):
        # self.log_unknown("line", node)
        pass

    def depart_line(self, node):
        pass

    def visit_compact_paragraph(self, node):
        pass

    def depart_compact_paragraph(self, node):
        pass

    def visit_paragraph(self, node):
        if not isinstance(node.parent, nodes.Admonition) or \
                isinstance(node.parent, addnodes.seealso):
            self.new_state(0)

    def depart_paragraph(self, node):
        if not isinstance(node.parent, nodes.Admonition) or \
                isinstance(node.parent, addnodes.seealso):
            self.end_state()

    def visit_target(self, node):
        raise nodes.SkipNode

    def visit_index(self, node):
        raise nodes.SkipNode

    def visit_substitution_definition(self, node):
        raise nodes.SkipNode

    def visit_pending_xref(self, node):
        if node.get('refexplicit'):
            text = '[%s](%s.md#%s)' % (
                node.astext(), node['refdoc'], node['reftarget'])
        else:
            text = '[%s](%s.md#%s)' % (
                node['reftarget'], node['refdoc'], node['reftarget'])
        self.add_text(text)
        raise nodes.SkipNode

    def depart_pending_xref(self, node):
        raise NotImplementedError("Error")

    def visit_reference(self, node):
        def clean_refuri(uri):
            ext = os.path.splitext(uri)[-1]
            link = uri if ext != '.rst' else uri[:-4]
            return link

        if 'refuri' not in node:
            if 'name' in node.attributes:
                self.add_text('[!%s]' % node['name'])
            elif 'refid' in node and node['refid']:
                self.add_text('[!%s]' % node['refid'])
            else:
                self.log_unknown(type(node), node)
        elif 'internal' not in node and 'name' in node.attributes:
            self.add_text('[%s](%s)' %
                          (node['name'], clean_refuri(node['refuri'])))
            raise nodes.SkipNode
        elif 'internal' not in node and 'names' in node.attributes:
            anchor = node['names'][0] if len(
                node['names']) > 0 else node['refuri']
            self.add_text('[%s](%s)' %
                          (anchor, clean_refuri(node['refuri'])))
            raise nodes.SkipNode
        elif 'reftitle' in node:
            name = node['name'] if 'name' in node else node.astext()
            self.add_text('[%s](%s)' %
                          (name, clean_refuri(node['refuri'])))
            raise nodes.SkipNode
        else:
            name = node['name'] if 'name' in node else node.astext()
            self.add_text('[%s](%s)' % (name, node['refuri']))
            raise nodes.SkipNode
        if 'internal' in node:
            raise nodes.SkipNode

    def depart_reference(self, node):
        if 'refuri' not in node:
            pass  # Don't add these anchors
        elif 'internal' not in node:
            # Don't add external links (they are automatically added by the reST spec)
            pass
        elif 'reftitle' in node:
            pass

    def visit_download_reference(self, node):
        self.log_unknown("download_reference", node)

    def depart_download_reference(self, node):
        pass

    def visit_emphasis(self, node):
        self.add_text('*')

    def depart_emphasis(self, node):
        self.add_text('*')

    def visit_literal_emphasis(self, node):
        self.add_text('*')

    def depart_literal_emphasis(self, node):
        self.add_text('*')

    def visit_strong(self, node):
        self.add_text('**')

    def depart_strong(self, node):
        self.add_text('**')

    def visit_abbreviation(self, node):
        self.add_text('')

    def depart_abbreviation(self, node):
        if node.hasattr('explanation'):
            self.add_text(' (%s)' % node['explanation'])

    def visit_title_reference(self, node):
        # self.log_unknown("title_reference", node)
        self.add_text('*')

    def depart_title_reference(self, node):
        self.add_text('*')

    def visit_literal(self, node):
        self.add_text('``')

    def depart_literal(self, node):
        self.add_text('``')

    def visit_subscript(self, node):
        self.add_text('_')

    def depart_subscript(self, node):
        pass

    def visit_superscript(self, node):
        self.add_text('^')

    def depart_superscript(self, node):
        pass

    def visit_footnote_reference(self, node):
        self.add_text('[%s]' % node.astext())
        raise nodes.SkipNode

    def visit_citation_reference(self, node):
        self.add_text('[%s]' % node.astext())
        raise nodes.SkipNode

    def visit_Text(self, node):
        self.add_text(node.astext())

    def depart_Text(self, node):
        pass

    def visit_generated(self, node):
        # self.log_unknown("generated", node)
        pass

    def depart_generated(self, node):
        pass

    def visit_inline(self, node):
        # self.log_unknown("inline", node)
        pass

    def depart_inline(self, node):
        pass

    def visit_problematic(self, node):
        self.add_text('>>')

    def depart_problematic(self, node):
        self.add_text('<<')

    def visit_system_message(self, node):
        self.new_state(0)
        self.add_text('<SYSTEM MESSAGE: %s>' % node.astext())
        self.end_state()
        raise nodes.SkipNode

    def visit_comment(self, node):
        raise nodes.SkipNode

    def visit_meta(self, node):
        # only valid for HTML
        raise nodes.SkipNode

    def visit_raw(self, node):
        if 'text' in node.get('format', '').split():
            self.add_text(node.astext())
        raise nodes.SkipNode

    def visit_issue(self, node):
        self.add_text('(issue *')
        self.add_text(node['text'])

    def depart_issue(self, node):
        self.add_text('*)')

    def eval_expr(self, expr):
        md = True
        rst = False
        html = False
        latex = False
        if not(rst or html or latex or md):
            raise ValueError("One of them should be True")  # pragma: no cover
        try:
            ev = eval(expr)
        except Exception as e:  # pragma: no cover
            raise ValueError(
                "Unable to interpret expression '{0}'".format(expr))
        return ev

    def visit_only(self, node):
        ev = self.eval_expr(node.attributes['expr'])
        if ev:
            pass
        else:
            raise nodes.SkipNode

    def depart_only(self, node):
        ev = self.eval_expr(node.attributes['expr'])
        if ev:
            pass
        else:
            # The program should not necessarily be here.
            pass

    def visit_CodeNode(self, node):
        self.add_text('.. CodeNode.' + self.nl)

    def depart_CodeNode(self, node):
        pass

    def visit_downloadlink_node(self, node):
        visit_downloadlink_node_md(self, node)

    def depart_downloadlink_node(self, node):
        depart_downloadlink_node_md(self, node)

    def visit_runpythonthis_node(self, node):
        # for unit test.
        pass

    def depart_runpythonthis_node(self, node):
        # for unit test.
        pass

    def visit_inheritance_diagram(self, node):
        pass

    def depart_inheritance_diagram(self, node):
        pass

    def unknown_visit(self, node):
        raise NotImplementedError(
            "Unknown node: '{0}' - '{1}'".format(node.__class__.__name__, node))


class MdBuilder(Builder):
    """
    Defines a :epkg:`MD` builder.
    """
    name = 'md'
    format = 'md'
    file_suffix = '.md'
    link_suffix = None  # defaults to file_suffix
    default_translator_class = MdTranslator

    def __init__(self, *args, **kwargs):
        """
        Constructor, add a logger.
        """
        Builder.__init__(self, *args, **kwargs)
        self.logger = logging.getLogger("MdBuilder")

    def init(self):
        """
        Load necessary templates and perform initialization.
        """
        if self.config.md_file_suffix is not None:
            self.file_suffix = self.config.md_file_suffix
        if self.config.md_link_suffix is not None:
            self.link_suffix = self.config.md_link_suffix
        if self.link_suffix is None:
            self.link_suffix = self.file_suffix

        # Function to convert the docname to a markdown file name.
        def file_transform(docname):
            return docname + self.file_suffix

        # Function to convert the docname to a relative URI.
        def link_transform(docname):
            return docname + self.link_suffix

        if self.config.md_file_transform is not None:
            self.file_transform = self.config.md_file_transform
        else:
            self.file_transform = file_transform
        if self.config.md_link_transform is not None:
            self.link_transform = self.config.md_link_transform
        else:
            self.link_transform = link_transform
        self.md_image_dest = self.config.md_image_dest

    def get_outdated_docs(self):  # pragma: no cover
        """
        Return an iterable of input files that are outdated.
        This method is taken from ``TextBuilder.get_outdated_docs()``
        with minor changes to support ``(confval, md_file_transform))``.
        """
        for docname in self.env.found_docs:
            if docname not in self.env.all_docs:
                yield docname
                continue
            sourcename = path.join(self.env.srcdir, docname +
                                   self.file_suffix)
            targetname = path.join(self.outdir, self.file_transform(docname))

            try:
                targetmtime = path.getmtime(targetname)
            except Exception:
                targetmtime = 0
            try:
                srcmtime = path.getmtime(sourcename)
                if srcmtime > targetmtime:
                    yield docname
            except EnvironmentError:
                # source doesn't exist anymore
                pass

    def get_target_uri(self, docname, typ=None):
        return self.link_transform(docname)

    def prepare_writing(self, docnames):
        self.writer = MdWriter(self)

    def get_outfilename(self, pagename):  # pragma: no cover
        """
        Overwrite *get_target_uri* to control file names.
        """
        return "{0}/{1}.md".format(self.outdir, pagename).replace("\\", "/")

    def write_doc(self, docname, doctree):
        destination = StringOutput(encoding='utf-8')
        self.current_docname = docname
        self.writer.write(doctree, destination)
        ctx = None
        self.handle_page(docname, ctx, event_arg=doctree)

    def handle_page(self, pagename, addctx, templatename=None,
                    outfilename=None, event_arg=None):  # pragma: no cover
        if templatename is not None:
            raise NotImplementedError("templatename must be None.")
        outfilename = self.get_outfilename(pagename)
        ensuredir(path.dirname(outfilename))
        with open(outfilename, 'w', encoding='utf-8') as f:
            f.write(self.writer.output)

    def finish(self):
        pass


class MdWriter(writers.Writer):
    """
    Defines a :epkg:`MD` writer.
    """
    supported = ('text',)
    settings_spec = ('No options here.', '', ())
    settings_defaults = {}
    translator_class = MdTranslator

    output = None

    def __init__(self, builder):
        writers.Writer.__init__(self)
        self.builder = builder

    def translate(self):
        visitor = self.builder.create_translator(self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.body


def setup(app):
    """
    Initializes the :epkg:`MD` builder.
    """
    app.add_builder(MdBuilder)
    app.add_config_value('md_file_suffix', ".md", 'env')
    app.add_config_value('md_link_suffix', None, 'env')
    app.add_config_value('md_file_transform', None, 'env')
    app.add_config_value('md_link_transform', None, 'env')
    app.add_config_value('md_indent', STDINDENT, 'env')
    app.add_config_value('md_image_dest', None, 'env')
