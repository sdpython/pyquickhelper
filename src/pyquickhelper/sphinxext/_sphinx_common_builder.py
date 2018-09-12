# -*- coding: utf-8 -*-
"""
@file
@brief Common functions for :epkg:`Sphinx` writers.
"""
import hashlib
import os
import re
import urllib.request
import shutil
import sys


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
        else:
            atts['src'] = uri
            atts['alt'] = node.get('alt', uri)

        # Makes a local copy of the image
        if 'src' in atts:
            if image_dest is None:
                builder = self.builder  # pylint: disable=E1101
                srcdir = builder.srcdir
                outdir = builder.outdir
                current = os.path.dirname(os.path.join(
                    srcdir, builder.current_docname))
                if current is None or not os.path.exists(current):
                    raise FileNotFoundError(
                        "Unable to find document '{0}'".format(current))
                current_dest = os.path.dirname(
                    os.path.join(outdir, builder.current_docname))
                fold = current_dest
            else:
                fold = image_dest

            full = os.path.join(srcdir, atts['src'])
            ext = os.path.splitext(atts['src'])[-1]
            name = self.hash_md5_readfile(full) + ext

            if not os.path.exists(fold):
                os.makedirs(fold)

            dest = os.path.join(fold, name)
            if not os.path.exists(dest):
                shutil.copy(full, dest)
            atts['src'] = name
            atts['full'] = full
            atts['dest'] = dest
        elif 'data' in atts:
            raise NotImplementedError()
        else:
            raise ValueError("No image was found.")

        # image size
        if 'width' in node:
            atts['width'] = node['width']
        if 'height' in node:
            atts['height'] = node['height']
        if 'scale' in node:
            import PIL
            if 'width' not in node or 'height' not in node:
                imagepath = urllib.request.url2pathname(uri)
                try:
                    img = PIL.Image.open(
                        imagepath.encode(sys.getfilesystemencoding()))
                except (IOError, UnicodeEncodeError):
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
