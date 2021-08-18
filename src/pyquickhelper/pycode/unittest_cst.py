"""
@file
@brief Helpers to compress constant used in unit tests.
"""
import base64
import json
import lzma


def compress_cst(data, length=70, as_text=False):
    """
    Transform a huge constant into a sequence of compressed binary strings.

    :param data: data
    :param length: line length
    :param as_text: returns the results as text
    :return: results

    .. runpython::
        :showcode:

        from pyquickhelper.pycode.unittest_cst import compress_cst

        data = {'values': [0.5, 6.9]}
        print(compress_cst(data))
    """
    js = json.dumps(data)
    data_js = js.encode("utf-8")
    data_out = lzma.compress(data_js)
    data64 = base64.b64encode(data_out)
    bufs = []
    pos = 0
    while pos < len(data64):
        if pos + length < len(data64):
            bufs.append(data64[pos:pos+length])
            pos += length
        else:
            bufs.append(data64[pos:])
            pos = len(data64)
    if as_text:
        return pprint.pformat(bufs)
    return bufs


def decompress_cst(data):
    """
    Transform a huge constant produced by function @see fn compress_cst
    into the original value.

    :param data: data
    :param length: line length
    :param as_text: returns the results as text
    :return: results

    .. runpython::
        :showcode:

        from pyquickhelper.pycode.unittest_cst import compress_cst, decompress_cst

        data = {'values': [0.5, 6.9]}
        cp = compress_cst(data)
        back = decompress_cst(cp)
        print(back)
    """
    if isinstance(data, list):
        data = b"".join(data)
    data64 = base64.b64decode(data)
    data_in = lzma.decompress(data64)
    dec = data_in.decode('utf-8')
    return json.loads(dec)
