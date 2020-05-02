# -*- coding: utf-8 -*-
"""
@file
@brief :epkg:`Sphinx` extension for images.
"""
__author__ = 'Tomasz Czyż <tomaszczyz@gmail.com>'
__license__ = "Apache 2"

import os
import sys
import copy
import uuid
import hashlib
import functools
import logging
import sphinx
from sphinx.util.osutil import copyfile
from sphinx.util import status_iterator
from sphinx.util.console import brown
try:
    from docutils.parsers.rst import Directive
except ImportError:
    from sphinx.util.compat import Directive
from sphinx.util.osutil import ensuredir
from docutils import nodes
from docutils.parsers.rst import directives
import requests
from .. import LightBox2


STATICS_DIR_NAME = '_static'


DEFAULT_CONFIG = dict(
    backend='LightBox2',
    default_image_width='100%',
    default_image_height='auto',
    default_group=None,
    default_show_title=False,
    download=False,
    requests_kwargs={},
    cache_path='_images',
    override_image_directive=False,
    show_caption=False,
)


class image_node(nodes.image, nodes.General, nodes.Element):
    ":epkg:`sphinx` node"
    pass


class gallery_node(nodes.image, nodes.General, nodes.Element):
    ":epkg:`sphinx` node"
    pass


def directive_boolean(value):
    "local function"
    if not value.strip():
        raise ValueError("No argument provided but required")
    if value.lower().strip() in ["yes", "1", 1, "true", "ok"]:
        return True
    elif value.lower().strip() in ['no', '0', 0, 'false', 'none']:
        return False
    else:
        raise ValueError(u"Please use on of: yes, true, no, false. "
                         u"Do not use `{}` as boolean.".format(value))


def get_image_extension(uri):
    """
    Guesses an extension for an image.
    """
    exts = {'.jpg', '.png', '.svg', '.bmp'}
    for ext in exts:
        if uri.endswith(ext):
            return ext
    for ext in exts:
        if ext in uri:
            return ext
    for ext in exts:
        if (ext[1:] + "=true") in uri:
            return ext
        if ('?' + ext[1:]) in uri:
            return ext
    logger = logging.getLogger('image')
    logger.warning("[image] unable to guess extension for '{0}'".format(uri))
    return ''


class ImageDirective(Directive):
    '''
    Directive which overrides default sphinx directive.
    It's backward compatibile and it's adding more cool stuff.
    '''

    align_values = ('left', 'center', 'right')

    def align(self):
        # This is not callable as self.align.  It cannot make it a
        # staticmethod because we're saving an unbound method in
        # option_spec below.
        return directives.choice(self, ImageDirective.align_values)

    has_content = True
    required_arguments = True

    option_spec = {
        'width': directives.length_or_percentage_or_unitless,
        'height': directives.length_or_unitless,
        'strech': directives.choice,

        'group': directives.unchanged,
        'class': directives.class_option,  # or str?
        'alt': directives.unchanged,
        'target': directives.unchanged,
        'download': directive_boolean,
        'title': directives.unchanged,
        'align': align,
        'show_caption': directive_boolean,
        'legacy_class': directives.class_option,
    }

    def run(self):
        env = self.state.document.settings.env
        conf = env.app.config.images_config

        # TODO get defaults from config
        group = self.options.get('group',
                                 conf['default_group'] if conf['default_group'] else uuid.uuid4())
        classes = self.options.get('class', '')
        width = self.options.get('width', conf['default_image_width'])
        height = self.options.get('height', conf['default_image_height'])
        alt = self.options.get('alt', '')
        target = self.options.get('target', '')
        title = self.options.get(
            'title', '' if conf['default_show_title'] else None)
        align = self.options.get('align', '')
        show_caption = self.options.get('show_caption', False)
        legacy_classes = self.options.get('legacy_class', '')

        # TODO get default from config
        download = self.options.get('download', conf['download'])

        # parse nested content
        # TODO: something is broken here, not parsed as expected
        description = nodes.paragraph()
        content = nodes.paragraph()
        content += [nodes.Text("%s" % x) for x in self.content]
        self.state.nested_parse(content, 0, description)

        img = image_node()

        try:
            is_remote = self.is_remote(self.arguments[0])
        except ValueError as e:
            this = os.path.abspath(os.path.dirname(__file__))
            repl = os.path.join(this, "missing.png")
            self.arguments[0] = repl
            is_remote = self.is_remote(self.arguments[0])
            logger = logging.getLogger('image')
            logger.warning("[image] {0}, replaced by '{1}'".format(e, repl))

        if is_remote:
            img['remote'] = True
            if download:
                img['uri'] = os.path.join('_images', hashlib.sha1(
                    self.arguments[0].encode()).hexdigest())
                img['uri'] += get_image_extension(self.arguments[0])
                img['remote_uri'] = self.arguments[0]
                env.remote_images[img['remote_uri']] = img['uri']
                env.images.add_file('', img['uri'])
            else:
                img['uri'] = self.arguments[0]
                img['remote_uri'] = self.arguments[0]
        else:
            img['uri'] = self.arguments[0]
            img['remote'] = False
            env.images.add_file('', img['uri'])

        img['content'] = description.astext()
        img['target'] = target

        if title is None:
            img['title'] = ''
        elif title:
            img['title'] = title
        else:
            img['title'] = img['content']
            img['content'] = ''

        img['show_caption'] = show_caption
        img['legacy_classes'] = legacy_classes
        img['group'] = group
        img['size'] = (width, height)
        img['width'] = width
        img['height'] = height
        img['classes'] += classes
        img['alt'] = alt
        img['align'] = align
        img['download'] = download
        return [img]

    def is_remote(self, uri):
        "local function"
        uri = uri.strip()
        env = self.state.document.settings.env
        if self.state.document.settings._source is not None:
            app_directory = os.path.dirname(
                os.path.abspath(self.state.document.settings._source))
        else:
            app_directory = None

        if uri[0] == '/':
            return False
        if uri[0:7] == 'file://':
            return False
        if os.path.isfile(os.path.join(env.srcdir, uri)):
            return False
        if app_directory and os.path.isfile(os.path.join(app_directory, uri)):
            return False
        if '://' in uri:
            return True
        raise ValueError('Image URI `{}` have to be local relative or '
                         'absolute path to image, or remote address.'
                         .format(uri))


def install_backend_static_files(app, env):
    "local function"
    STATICS_DIR_PATH = os.path.join(app.builder.outdir, STATICS_DIR_NAME)
    dest_path = os.path.join(STATICS_DIR_PATH, 'sphinxtrib-images',
                             app.sphinxtrib_images_backend.__class__.__name__)
    files_to_copy = app.sphinxtrib_images_backend.STATIC_FILES

    for source_file_path in status_iterator(files_to_copy,
                                            'Copying static files for images...', brown, len(files_to_copy)):

        dest_file_path = os.path.join(dest_path, source_file_path)

        if not os.path.exists(os.path.dirname(dest_file_path)):
            ensuredir(os.path.dirname(dest_file_path))

        source_file_path = os.path.join(os.path.dirname(
            sys.modules[app.sphinxtrib_images_backend.__class__.__module__].__file__),
            source_file_path)

        copyfile(source_file_path, dest_file_path)

        if dest_file_path.endswith('.js'):
            name = os.path.relpath(dest_file_path, STATICS_DIR_PATH)
            try:
                # Sphinx >= 1.8
                app.add_js_file(name)
            except AttributeError:
                # Sphinx < 1.8
                app.add_javascript(name)
        elif dest_file_path.endswith('.css'):
            name = os.path.relpath(dest_file_path, STATICS_DIR_PATH)
            try:
                # Sphinx >= 1.8
                app.add_css_file(name)
            except AttributeError:
                # Sphinx < 1.8
                app.add_stylesheet(name)


def download_images(app, env):
    """
    Downloads images before running the documentation.

    @param      app     :epkg:`Sphinx` application
    @param      env     environment
    """
    logger = logging.getLogger("image")
    conf = app.config.images_config
    for src in status_iterator(env.remote_images,
                               'Downloading remote images...', brown,
                               len(env.remote_images)):
        dst = os.path.join(env.srcdir, env.remote_images[src])
        dirn = os.path.dirname(dst)
        ensuredir(dirn)
        if not os.path.isfile(dst):

            logger.info('{} -> {} (downloading)'.format(src, dst))
            with open(dst, 'wb') as f:
                # TODO: apply reuqests_kwargs
                try:
                    f.write(requests.get(src,
                                         **conf['requests_kwargs']).content)
                except requests.ConnectionError:
                    logger.info("Cannot download `{}`".format(src))
        else:
            logger.info('{} -> {} (already in cache)'.format(src, dst))


def configure_backend(app):
    "local function"
    global DEFAULT_CONFIG

    config = copy.deepcopy(DEFAULT_CONFIG)
    config.update(app.config.images_config)
    app.config.images_config = config

    # ensuredir(os.path.join(app.env.srcdir, config['cache_path']))

    # html builder
    # self.relfn2path(imguri, docname)

    backend_name_or_callable = config['backend']
    if callable(backend_name_or_callable):
        pass
    elif backend_name_or_callable == "LightBox2":
        backend = LightBox2
    else:
        raise TypeError("images backend is configured improperly. It is `{}` (type:`{}`).".format(
            backend_name_or_callable, type(backend_name_or_callable)))

    backend = backend(app)

    # remember the chosen backend for processing. Env and config cannot be used
    # because sphinx try to make a pickle from it.
    app.sphinxtrib_images_backend = backend

    logger = logging.getLogger("image")
    logger.info('Initiated images backend: ', nonl=True)
    logger.info('`{}:{}`'.format(
        backend.__class__.__module__, backend.__class__.__name__))

    def backend_methods(node, output_type):
        "local function"
        def backend_method(f):
            "local function"
            @functools.wraps(f)
            def inner_wrapper(writer, node):
                "local function"
                return f(writer, node)
            return inner_wrapper
        signature = '_{}_{}'.format(node.__name__, output_type)
        return (backend_method(getattr(backend, 'visit' + signature, getattr(backend, 'visit_' + node.__name__ + '_fallback'))),
                backend_method(getattr(backend, 'depart' + signature, getattr(backend, 'depart_' + node.__name__ + '_fallback'))))

    # add new node to the stack
    # connect backend processing methods to this node
    app.add_node(image_node, **{output_type: backend_methods(image_node, output_type)
                                for output_type in ('html', 'latex', 'man', 'texinfo', 'text', 'epub')})

    app.add_directive('thumbnail', ImageDirective)
    if config['override_image_directive']:
        app.add_directive('image', ImageDirective)
    app.env.remote_images = {}


def setup(app):
    """setup for :epkg:`sphinx` extension"""
    global DEFAULT_CONFIG
    app.add_config_value('images_config', DEFAULT_CONFIG, 'env')
    app.connect('builder-inited', configure_backend)
    app.connect('env-updated', download_images)
    app.connect('env-updated', install_backend_static_files)
    return {'version': sphinx.__version__, 'parallel_read_safe': True}
