"""
@file
@brief Helpers for sphinx extensions.
"""


def try_add_config_value(app, name, default, rebuild, type_s=()):
    """
    Add a variables in the config file if it does not have it yet.

    @param      app         Sphinx application
    @param      name        name of the variable
    @param      default     default value
    @param      rebuild     see below
    @param      type_s      expected types
    @return                 True if added, False if already present.

    Rebuilds can be (source: `Sphinx.add_config_value
    <http://www.sphinx-doc.org/en/stable/extdev/appapi.html#sphinx.application.Sphinx.add_config_value>`_):

    * 'env' if a change in the setting only takes effect when a document
      is parsed - this means that the whole environment must be rebuilt.
    * 'html' if a change in the setting needs a full rebuild of HTML documents.
    * '' if a change in the setting will not need any special rebuild.

    """
    if name in app.config:
        return False
    app.add_config_value(name, default, rebuild, type_s)
    return True
