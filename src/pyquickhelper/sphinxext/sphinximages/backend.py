"""
@file
@brief Backend API for sphinx directive *image*.
"""


class Backend(object):
    """
    Backend API for sphinx directive *image*.
    """
    STATIC_FILES = ()

    def __init__(self, app):
        self._app = app

    def visit_image_node_fallback(self, writer, node):
        "translator method"
        writer.visit_image(node)

    def depart_image_node_fallback(self, writer, node):
        "translator method"
        writer.depart_image(node)
