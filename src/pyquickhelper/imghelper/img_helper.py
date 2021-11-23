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


def _optimization_criterion(target, data, weight_above=10, weight_below=1):
    sizes = {}
    for row, width in data:
        if row not in sizes:
            sizes[row] = 0
        sizes[row] += width
    loss = 0
    for row, size in sizes.items():
        if size < target:
            loss += weight_below * (target - size)
        else:
            loss += weight_above * (size - target)
        if row > 0 and sizes.get(row, 0) == 0:
            loss += weight_below * target
    return loss


def _optimization_histogram_order(target, data, weight_above=10,
                                  weight_below=1):
    if len(data) < 6:
        # we try all permutation
        rows = [0 for d in data]
        best_loss = None
        best_rows = rows.copy()
        while rows[0] == 0:
            loss = _optimization_criterion(
                target, zip(rows, data),
                weight_above=weight_above,
                weight_below=weight_below)
            if best_loss is None or loss < best_loss:
                best_loss = loss
                best_rows = rows.copy()
            i = len(rows) - 1
            rows[i] += 1
            while i > 0 and rows[i] >= len(data):
                rows[i] = 0
                i -= 1
                rows[i] += 1
        return best_rows

    # generic case
    data_pos = [0 for i in data]
    current_row = 0
    size = data[0]
    for i in range(1, len(data)):
        if size + data[i] > target:
            current_row += 1
            size = data[i]
        else:
            size += data[i]
        data_pos[i] = current_row

    return data_pos


def concat_images(imgs, height=200, width=800,
                  weight_above=10, weight_below=1,
                  background=(0, 0, 0), out_file=None):
    """
    Concatenates images into an image with several
    rows of images.

    :param imgs: filename or Images (:epkg:`Pillow`)
    :param height: height of each row (pixels)
    :param width: width of each row (pixels)
    :param weight_above: loss when a line is too long
    :param weight_below: loss when a line is too short
    :param background: background color
    :param out_file: stores the image into this file if not None
    :return: Image (:epkg:`Pillow`)
    """
    from PIL import Image
    images = []
    for img in imgs:
        if isinstance(img, str):
            images.append(Image.open(img))
        else:
            images.append(img)

    # zoom
    images = [zoom_img(img, factor=height * 1.0 / img.size[1])
              for img in images]

    # optimization
    data = [img.size[0] for img in images]
    pos = _optimization_histogram_order(
        width, data, weight_above=weight_above, weight_below=weight_below)

    # concat
    n_rows = max(pos) + 1
    img_height = n_rows * height

    new_image = Image.new('RGB', (width, img_height), background)
    w = 0
    last_row = 0
    for row, img in zip(pos, images):
        if row != last_row:
            w = 0
        new_image.paste(img, (w, row * height))
        w += img.size[0]
        last_row = row
    if out_file is not None:
        new_image.save(out_file)
    return new_image
