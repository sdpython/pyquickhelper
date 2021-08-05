# -*- coding: utf-8 -*-
"""
@file
@brief Freely inspired from
`Showing Side-by-Side Diffs in Jupyter
<https://skeptric.com/python-diffs/>`_.
"""
import difflib
import re
from itertools import zip_longest
import html


whitespace = re.compile('\\s+')
end_sentence = re.compile('\\n+')


def _tokenize(s):
    '''Split a string into tokens'''
    return whitespace.split(s)


def _untokenize(ts):
    '''Join a list of tokens into a string'''
    return ' '.join(ts)


def _sentencize(s):
    '''Split a string into a list of sentences'''
    return end_sentence.split(s)


def _unsentencise(ts):
    '''Join a list of sentences into a string'''
    return '. '.join(ts)


def _html_unsentencise(ts):
    '''Joing a list of sentences into HTML for display'''
    return ''.join(f'<p>{t}</p>' for t in ts)


def _mark_text(text):
    return f'<span style="color: red;">{text}</span>'


def _mark_span(text):
    return [_mark_text(token) for token in text]


def _mark_span(text):
    if len(text) > 0:
        text[0] = '<span style="background: #69E2FB;">' + text[0]
        text[-1] += '</span>'
    return text


def _markup_diff(a, b, mark=_mark_span, default_mark=None, isjunk=None):
    """
    Returns a and b with any differences processed by mark.
    Junk is ignored by the differ.
    """
    if default_mark is None:
        default_mark = lambda x: x
    seqmatcher = difflib.SequenceMatcher(
        isjunk=isjunk, a=a, b=b, autojunk=False)
    out_a, out_b = [], []
    for tag, a0, a1, b0, b1 in seqmatcher.get_opcodes():
        markup = default_mark if tag == 'equal' else mark
        out_a += markup(a[a0:a1])
        out_b += markup(b[b0:b1])
    return out_a, out_b


def align_seqs(a, b, fill=''):
    """
    Aligns two sequences of strings after comparing them.
    """
    out_a, out_b = [], []
    seqmatcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for _, a0, a1, b0, b1 in seqmatcher.get_opcodes():
        delta = (a1 - a0) - (b1 - b0)
        out_a += a[a0:a1] + [fill] * max(-delta, 0)
        out_b += b[b0:b1] + [fill] * max(delta, 0)
    return out_a, out_b


def _html_sidebyside(a, b):
    out = '<div style="display: grid;grid-template-columns: 1fr 1fr;grid-gap: 20px;">\n'
    for left, right in zip_longest(a, b, fillvalue=''):
        out += f'<p><tt>{left}</tt></p>'
        out += f'<p><tt>{right}</tt></p>\n'
    out += '</div>'
    return out


def html_diffs(a, b):
    """
    Comparares two strings and renders the
    results as HTML.
    """
    a = html.escape(a)
    b = html.escape(b)

    out_a, out_b = [], []
    for sent_a, sent_b in zip(*align_seqs(_sentencize(a), _sentencize(b))):
        mark_a, mark_b = _markup_diff(_tokenize(sent_a), _tokenize(sent_b))
        out_a.append(_untokenize(mark_a))
        out_b.append(_untokenize(mark_b))

    return _html_sidebyside(out_a, out_b)
