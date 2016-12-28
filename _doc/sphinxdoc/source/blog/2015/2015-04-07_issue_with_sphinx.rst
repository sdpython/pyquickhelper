
.. blogpost::
    :title: Sphinx fails because of some weird encoding
    :keywords: sphinx, issue, encoding, BOM, utf-8
    :date: 2015-04-07
    :categories: documentation

    I have been generating many times the documentation of this module
    and I can tell I went through many errors due to encoding,
    French accents may be sometimes painful to deal with.
    However, I now check every time that every file I produce has
    either no encoding, either is encoded with
    `utf-8 <http://en.wikipedia.org/wiki/UTF-8>`_
    and no `BOM <http://en.wikipedia.org/wiki/Byte_order_mark>`_.
    After I checked that, I'm sure the error come from something else.

    The issue I had with Sphinx is not necessarily a crash but also
    a label which was not takein into account.
    This label was written on the first line of the line.
    I replaced that label by a comment (``.. comment.``).
    The comment showed on the generated HTML page but it disappear
    after I removed the BOM from the original RST file.
