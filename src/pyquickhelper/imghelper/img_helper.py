"""
@file
@brief Helpers around images.

.. versionadded:: 1.9
"""
import os
import glob
import numpy


def zoom_img(img, factor=1., max_dim=None, out_file=None, fLOG=None):
    """
    Zooms an image.

    :param img: image or filename or pattern
    :param factor: multiplies the image by this factor if not None
    :param max_dim: modifies the image, the highest dimension
        should below this number
    :param out_file: stores the image into this file if not None
    :param fLOG: logging function
    :return: image
    """
    if isinstance(img, str):
        if '*' in img:
            found = glob.glob(img)
            res = []
            for im in found:
                if out_file is None:
                    i = zoom_img(im, factor=factor, max_dim=max_dim, fLOG=fLOG)
                else:
                    of = out_file.format(os.path.split(im)[-1])
                    i = zoom_img(im, factor=factor, max_dim=max_dim,
                                 out_file=of, fLOG=fLOG)
                res.append(i)
            if len(res) == 0:
                raise FileNotFoundError(  # pragma: no cover
                    "Unable to find anything in '{}'.".format(img))
            return res
        from PIL import Image
        obj = Image.open(img)
    elif hasattr(img, 'size'):
        obj = img
    else:
        raise TypeError(  # pragma: no cover
            "Image should be a string or an image not {}.".format(type(img)))
    dx, dy = obj.size
    if max_dim is not None:
        if not isinstance(max_dim, int):
            max_dim = int(max_dim)
        facx = max_dim * 1. / max(dx, 1)
        facy = max_dim * 1. / max(dy, 1)
        factor = min(facx, facy)
    if factor is not None:
        if not isinstance(factor, float):
            factor = int(factor)
        dx = int(dx * factor + 0.5)
        dy = int(dy * factor + 0.5)
        obj = obj.resize((dx, dy))
    if out_file is not None:
        if fLOG is not None:
            fLOG("Writing '{}' dim=({},{}).".format(out_file, dx, dy))
        obj.save(out_file)
    return obj


def white_to_transparency(img, out_file=None):
    """
    Sets white color as transparency color.

    @param      img         image (:epkg:`Pillow`)
    @param      out_file    stores the image into this file if not None
    @return                 image (:epkg:`Pillow`)

    Code taken from `Using PIL to make all white pixels transparent?
    <https://stackoverflow.com/questions/765736/
    using-pil-to-make-all-white-pixels-transparent>`_.

    .. versionadded:: 1.9
    """
    from PIL import Image
    if isinstance(img, str):
        img = Image.open(img)
    x = numpy.asarray(img.convert('RGBA')).copy()

    x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(numpy.uint8)

    obj = Image.fromarray(x)
    if out_file is not None:
        obj.save(out_file)
    return obj
