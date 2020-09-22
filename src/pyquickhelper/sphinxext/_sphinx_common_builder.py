# -*- coding: utf-8 -*-
"""
@file
@brief Common functions for :epkg:`Sphinx` writers.
"""
import hashlib
import os
import re
import glob
import urllib.request
import shutil
import sys
import logging
from .sphinximages.sphinxtrib.images import get_image_extension
from ..filehelper import get_url_content_timeout, InternetException


class CommonSphinxWriterHelpers:
    """
    Common functions used in @see cl RstTranslator
    and @see cl MdTranslator.
    """

    def hash_md5_readfile(self, filename):
        """
        Computes a hash of a file.
        @param      filename    filename
        @return                 string
        """
        with open(filename, 'rb') as f:
            m = hashlib.md5()
            readBytes = 1024 ** 2  # read 1024 bytes per time
            totalBytes = 0
            while readBytes:
                readString = f.read(readBytes)
                m.update(readString)
                readBytes = len(readString)
                totalBytes += readBytes
        res = m.hexdigest()
        if len(res) > 20:
            res = res[:20]
        return res

    def base_visit_image(self, node, image_dest=None):
        """
        Processes an image. By default, it writes the image on disk.
        Inspired from
        `visit_image <https://github.com/docutils-mirror/docutils/blob/master/docutils/writers/html4css1/__init__.py#L1019>`_
        implemented in :epkg:`docutils`.

        @param      node        image node
        @param      image_dest  image destination (location where they will be copied)
        @return                 attributes
        """
        atts = {}
        uri = node['uri']

        # place SVG and SWF images in an <object> element
        types = {'.svg': 'image/svg+xml',
                 '.swf': 'application/x-shockwave-flash'}
        ext = os.path.splitext(uri)[1].lower()
        if ext in ('.svg', '.swf'):
            atts['data'] = uri
            atts['type'] = types[ext]

        atts['src'] = uri
        atts['alt'] = node.get('alt', uri)

        env = self.builder.env  # pylint: disable=E1101
        if hasattr(env, 'remote_images') and atts['src'] in env.remote_images:
            atts['src'] = env.remote_images[atts['src']]

        # Makes a local copy of the image
        if 'src' in atts:
            builder = self.builder  # pylint: disable=E1101
            srcdir = builder.srcdir
            if srcdir == "IMPOSSIBLE:TOFIND":
                srcdir = None
            if image_dest is None:
                outdir = builder.outdir
                if builder.current_docname and builder.current_docname != "<<string>>":
                    if srcdir is None:
                        current = os.path.dirname(builder.current_docname)
                    else:
                        current = os.path.dirname(os.path.join(
                            srcdir, builder.current_docname))
                    if current is None or not os.path.exists(current):
                        raise FileNotFoundError(  # pragma: no cover
                            "Unable to find document '{0}' current_docname='{1}'"
                            "".format(current, builder.current_docname))
                    dest = os.path.dirname(os.path.join(
                        outdir, builder.current_docname))
                    fold = outdir
                else:
                    # current_docname is None which means
                    # no file should be created
                    fold = None
            else:
                fold = image_dest

            if atts['src'].startswith('http:') or atts['src'].startswith('https:'):
                name = hashlib.sha1(atts['src'].encode()).hexdigest()
                ext = get_image_extension(atts['src'])
                remote = True
            else:
                full = os.path.join(
                    srcdir, atts['src']) if srcdir else atts['src']

                if '*' in full:
                    files = glob.glob(full)
                    if len(files) == 0:
                        raise FileNotFoundError(  # pragma: no cover
                            "Unable to find any file matching pattern "
                            "'{}'.".format(full))
                    full = files[0]

                if not os.path.exists(full):
                    this = os.path.abspath(os.path.dirname(__file__))
                    repl = os.path.join(
                        this, "sphinximages", "sphinxtrib", "missing.png")
                    logger = logging.getLogger("image")
                    logger.warning(
                        "[image] unable to find image '{0}', replaced by '{1}'".format(full, repl))
                    full = repl

                ext = os.path.splitext(full)[-1]
                name = self.hash_md5_readfile(full) + ext
                remote = False

            if fold is not None and not os.path.exists(fold):
                os.makedirs(fold)

            dest = os.path.join(fold, name) if fold else None
            if dest is not None and '*' in dest:
                raise RuntimeError(  # pragma: no cover
                    "Wrong destination '{} // {}' image_dest='{}' atts['src']='{}' "
                    "srcdir='{}' full='{}'.".format(
                        fold, name, image_dest, atts['src'], srcdir, full))

            if dest is not None:
                if not os.path.exists(dest):
                    if remote:
                        if atts.get('download', False):
                            # Downloads the image
                            try:
                                get_url_content_timeout(
                                    atts['src'], output=dest, encoding=None, timeout=20)
                                full = atts['src']
                            except InternetException as e:  # pragma: no cover
                                logger = logging.getLogger("image")
                                logger.warning(
                                    "[image] unable to get content for url '{0}' due to '{1}'"
                                    "".format(atts['src'], e))
                                this = os.path.abspath(
                                    os.path.dirname(__file__))
                                full = os.path.join(
                                    this, "sphinximages", "sphinxtrib", "missing.png")
                                shutil.copy(full, dest)
                        else:
                            name = atts['src']
                            full = name
                            dest = name
                    else:
                        if ':' in dest and len(dest) > 2:
                            dest = dest[:2] + dest[2:].replace(':', '_')
                            ext = os.path.splitext(dest)[-1]
                            if ext not in ('.png', '.jpg'):
                                dest += '.png'
                        try:
                            shutil.copy(full, dest)
                        except (FileNotFoundError, OSError) as e:
                            raise FileNotFoundError(  # pragma: no cover
                                "Unable to copy from '{0}' to '{1}'.".format(full, dest)) from e
                        full = dest
                else:
                    full = dest
            else:
                name = atts['src']
                full = name
                dest = name

            atts['src'] = name
            atts['full'] = full
            atts['dest'] = dest
        else:
            raise ValueError(  # pragma: no cover
                "No image was found in node (class='{1}')\n{0}".format(
                    node, self.__class__.__name__))

        # image size
        if 'width' in node:
            atts['width'] = node['width']
        if 'height' in node:
            atts['height'] = node['height']
        if 'download' in node:
            atts['download'] = node['download']
        if 'scale' in node:
            import PIL
            if 'width' not in node or 'height' not in node:
                imagepath = urllib.request.url2pathname(uri)
                try:
                    img = PIL.Image.open(
                        imagepath.encode(sys.getfilesystemencoding()))
                except (IOError, UnicodeEncodeError):  # pragma: no cover
                    pass  # TODO: warn?
                else:
                    self.settings.record_dependencies.add(  # pylint: disable=E1101
                        imagepath.replace('\\', '/'))
                    if 'width' not in atts:
                        atts['width'] = '%dpx' % img.size[0]
                    if 'height' not in atts:
                        atts['height'] = '%dpx' % img.size[1]
            for att_name in 'width', 'height':
                if att_name in atts:
                    match = re.match(r'([0-9.]+)(\S*)$', atts[att_name])
                    atts[att_name] = '%s%s' % (
                        float(match.group(1)) * (float(node['scale']) / 100),
                        match.group(2))

        style = []
        for att_name in 'width', 'height':
            if att_name in atts:
                if re.match(r'^[0-9.]+$', atts[att_name]):
                    # Interpret unitless values as pixels.
                    atts[att_name] += 'px'
                style.append('%s: %s;' % (att_name, atts[att_name]))

        if style:
            atts['style'] = ' '.join(style)

        if 'align' in node:
            atts['class'] = 'align-%s' % node['align']

        return atts
