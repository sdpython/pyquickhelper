"""
@file
@brief Tools to convert images.
"""
import glob


def images2pdf(images, output, fLOG=None):
    """
    Merges multiples images into one single pdf.
    Relies on :epkg:`img2pdf`. If an image name contains
    ``'*'``, the function assumes it is a pattern and
    uses :epkg:`*py:glob`.

    :param images: images to merge, it can be a comma separated values
    :param output: output filename or stream
    :param fLOG: logging function

    .. cmdref::
        :title: Merge images into PDF
        :cmd: -m pyquickhelper images2pdf --help

        Merges one or several images into a single
        PDF document.
    """
    from img2pdf import convert

    if isinstance(images, str):
        if ',' in images:
            images = images.split(',')
        else:
            images = [images]  # pragma: no cover
    elif not isinstance(images, list):
        raise TypeError("Images must be a list.")  # pragma: no cover

    all_images = []
    for img in images:
        if "*" in img:
            names = glob.glob(img)
            all_images.extend(names)
        else:
            all_images.append(img)

    if fLOG is not None:  # pragma: no cover
        for i, img in enumerate(all_images):
            fLOG("[images2pdf] {}/{} '{}'".format(i + 1, len(all_images), img))

    if isinstance(output, str):
        st = open(output, 'wb')
        close = True
    else:  # pragma: no cover
        close = False
        st = output

    convert(all_images, outputstream=st, with_pdfrw=False)

    if close:
        st.close()

    return all_images
