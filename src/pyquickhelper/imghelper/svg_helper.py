"""
@file
@brief Helpers around images and :epkg:`SVG`.

.. versionadded:: 1.7
"""
import xml.etree.ElementTree as ET
from io import BytesIO
from .excs import PYQImageException


def guess_svg_size(svg):
    """
    Guesses the dimension of a :epkg:`SVG` image.

    @param      svg     :epkg:`SVG` description
    @return             size (x, y)
    """
    mx, my = 0, 0
    tree = ET.fromstring(svg)
    for elt in tree.iter():
        for k, v in elt.attrib.items():
            if k in ('x', 'cx', 'width'):
                mx = max(0, int(v))
            elif k in ('rx',):
                mx = max(0, 2 * int(v))
            elif k in ('y', 'cy', 'height'):
                my = max(0, int(v))
            elif k in ('ry',):
                my = max(0, 2 * int(v))
    return (mx, my)


def svg2img(svg, dpi=None, scale=1., **kwargs):
    """
    Converts an image in :epkg:`SVG` format.

    @param  svg     svg
    @param  dpi     image resolution
    @param  scale   scale
    @param  kwargs  additional parameters
    @return         image

    The module relies on the following dependencies:

    * :epkg:`cairosvg`
    * :epkg:`Pillow`
    """
    kwargs = {}
    if dpi:
        kwargs['dpi'] = dpi
    if scale not in (None, 1., 1):
        kwargs['scale'] = scale
    from cairosvg import svg2png
    img = BytesIO()
    try:
        svg2png(svg, write_to=img, **kwargs)
    except (ValueError, OSError) as e:
        if svg.startswith('<svg>'):
            size = guess_svg_size(svg)
            head = '<svg width="{}" height="{}">'.format(*size)
            svg = head + svg[5:]
            return svg2img(svg, **kwargs)
        raise PYQImageException(  # pragma: no cover
            "width and height must be specified. "
            "This might be the error.") from e
    png = img.getvalue()
    st = BytesIO(png)
    from PIL import Image
    return Image.open(st)
