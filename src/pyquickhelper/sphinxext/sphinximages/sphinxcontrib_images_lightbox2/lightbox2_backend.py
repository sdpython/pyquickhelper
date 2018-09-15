"""
@file
@brief Defines the backend for directive ``image``.
"""
from ..backend import Backend


class LightBox2(Backend):
    """
    Backend for sphinx directive ``image``.
    """
    STATIC_FILES = (
        'lightbox2/css/lightbox.css',
        'lightbox2/js/jquery-1.11.0.min.js',
        'lightbox2/js/lightbox.min.js',
        'lightbox2_customize/jquery-noconflict.js',
        'lightbox2/js/lightbox.min.map',
        'lightbox2/img/close.png',
        'lightbox2/img/next.png',
        'lightbox2/img/prev.png',
        'lightbox2/img/loading.gif',
    )

    def visit_image_node_html(self, writer, node):
        "translator method"
        # make links local (for local images only)
        builder = self._app.builder
        if node['uri'] in builder.images:
            node['uri'] = '/'.join([builder.imgpath,
                                    builder.images[node['uri']]])

        if node['show_caption'] is True:
            writer.body.append(
                '''<figure class="{cls}">
            '''.format(cls=' '.join(node['classes']),))
            if node['legacy_classes']:
                writer.body.append(
                    '''<a class="{legcls}"'''.format(legcls=' '.join(node['legacy_classes']),))
            else:
                writer.body.append('''<a ''')
        else:
            writer.body.append('''<a class="{cls}"'''.format(
                cls=' '.join(node['classes']),))
        if node['target']:
            writer.body.append(' href="{0}" '.format(node['target']))
        writer.body.append(
            '''
               data-lightbox="{group}"
               href="{href}"
               title="{title}"
               data-title="{title}"
               >'''.format(group='group-%s' % node['group'] if node['group'] else node['uri'],
                           href=node['uri'],
                           title=node['title'] + node['content'],
                           ))
        writer.body.append(
            '''<img src="{src}"
                     class="{cls}"
                     width="{width}"
                     height="{height}"
                     alt="{alt}"/>
                '''.format(src=node['uri'],
                           cls='align-%s' % node['align'] if node['align'] else '',
                           width=node['size'][0],
                           height=node['size'][1],
                           alt=node['alt']))
        # , title=node['title']))

    def depart_image_node_html(self, writer, node):
        "translator method"
        writer.body.append('</a>')
        if node['show_caption'] is True:
            writer.body.append('''<figcaption>{title}</figcaption>
            '''.format(title=node['title'],))
            writer.body.append('</figure>')
