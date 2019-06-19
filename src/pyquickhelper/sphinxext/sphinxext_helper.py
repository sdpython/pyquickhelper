"""
@file
@brief Helpers for sphinx extensions.
"""
import os


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


def get_env_state_info(self):
    """
    Retrieves an environment and a docname inside a directive.

    @param      self        self inside a :epkg:`Sphinx` directive
    @return                 env, docname, lineno
    """
    if hasattr(self, 'env') and self.env is not None:
        env = self.env
    elif hasattr(self.state.document.settings, "env"):
        env = self.state.document.settings.env
    else:
        env = None

    reporter = self.state.document.reporter
    try:
        docname, lineno = reporter.get_source_and_line(self.lineno)
    except AttributeError:
        docname = lineno = None

    if docname is not None:
        docname = docname.replace("\\", "/").split("/")[-1]
    res = {'env': env, 'reporter_docname': docname,
           'docname': env.docname,
           'lineno': lineno, 'state_document': self.state.document,
           'location': self.state_machine.get_source_and_line(self.lineno)}
    if hasattr(self, 'app'):
        res['srcdic'] = self.app.builder.srcdir
    if hasattr(self, 'builder'):
        res['srcdic'] = self.builder.srcdir
    if env is not None:
        here = os.path.dirname(env.doc2path("HERE"))
        if "IMPOSSIBLE:TOFIND" not in here:
            res['HERE'] = here

    for k in res:
        if isinstance(res[k], str):
            res[k] = res[k].replace("\\", "/")
        elif isinstance(res[k], tuple):
            res[k] = (res[k][0].replace("\\", "/"), res[k][1])
    return res
