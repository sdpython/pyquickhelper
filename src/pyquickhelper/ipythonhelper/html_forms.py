"""
@file
@brief Some functions to interact better with Notebook
"""

import re

_reg_var = re.compile("^[a-zA-Z_]([a-zA-Z_0-9]*)$")


def open_html_form(params, title='', key_save="",
                   style="background-color:gainsboro; padding:2px; border:0px;",
                   raw=False, hook=None):
    """
    The function displays a form onto a notebook,
    it requires a notebook to be open.

    @param      params          dictionary of parameters (see comment below)
    @param      title           titre of the added box
    @param      style           style of the form
    @param      key_save        name of the variable to add to the notebook (as a dictionary)
    @param      raw             returns the raw HTML and not ``HTML( text )``
    @param      hook            an instruction as a string which will be executed if the button is clicked (None for none)
    @return                     HTML

    The code comes from
    `IPython Notebook: Javascript/Python Bi-directional Communication
    <https://jakevdp.github.io/blog/2013/06/01/ipython-notebook-javascript-python-communication/>`_.
    When the notebook is converted into a HTML document, the values in the form do not appear.
    This behaviour is expected in case one of the field contains a password. On a notebook, it
    gives the following result:

    .. exref::
        :title: Open a add a form in a notebook to ask parameters to a user

        .. image:: images/form.png

        Cell 1::

            from pyquickhelper.ipythonhelper import open_html_form
            params = { "module":, "version":"v..." }
            open_html_form (params, title="try the password *", key_save="form1")

        Cell 2::

            print(form1)

        We can execute a simple action after the button *Ok* is pressed. This second trick
        comes from `this notebook <https://raw.githubusercontent.com/fluxtream/fluxtream-ipy/master/
        Communication%20between%20kernel%20and%20javascript%20in%20iPython%202.0.ipynb>`_.
        The code displays whatever comes from function ``custom_action`` in this case.
        You should return ``""`` to display nothing.

        ::

            def custom_action(x):
                x["combined"] = x["first_name"] + " " + x["last_name"]
                return x

            params = { "first_name":"", "last_name":"" }
            open_html_form(params, title="enter your name", key_save="my_address",
                           hook="custom_action(my_address)")

    The function generates javascript based on the keys the dictionary ``params`` contains.
    The keys must follows the same as a javascript identifier (no space).
    """
    global _reg_var
    for k in params:
        if not _reg_var.match(k):
            raise KeyError(  # pragma: no cover
                "keys in params must look like a variable, it is not the case for "
                "'{}'.".format(k))

    row = """<br />{0} <input type="{3}" id="{2}{0}" value="{1}" size="80" />"""

    rows = ["""<div style="{0}"><b>{1}</b>""".format(style, title)]
    for k, v in sorted(params.items()):
        if k.startswith("password"):
            typ = "password"
        else:
            typ = "text"
        rows.append(row.format(k, "" if v is None else str(v), key_save, typ))
    rows.append(
        """<br /><button onclick="set_value{0}()">Ok</button></div>""".format(key_save))
    if hook is not None:
        rows.append("<div id='out%s'></div>" % key_save.replace("_", ""))

    rows.append("""<script type="text/Javascript">""")
    rows.append("function %scallback(msg) {" % key_save)
    rows.append("   var ret = msg.content.data['text/plain'];")
    rows.append("   $('#out%s').text(ret);" % key_save.replace("_", ""))
    rows.append("}")
    rows.append("function set_value__KEY__(){".replace("__KEY__", key_save))

    rows.append("   command='%s = {' ;" % key_save)
    for k, v in sorted(params.items()):
        rows.append(
            """   var {0}{1}var_value = document.getElementById('{0}{1}').value;""".format(key_save, k))
        rows.append("""   command += '"{0}":"' + """.format(k) +
                    "{0}{1}var_value".format(key_save, k) + """ + '",';""")
    rows.append("""   command += '}';""")
    rows.append("""   var kernel = IPython.notebook.kernel;""")
    rows.append("""   kernel.execute(command);""")
    if hook is not None:
        rows.append("""   kernel.execute('%s', {iopub: {output: %scallback}}, {silent: false});""" % (
            hook, key_save))
    rows.append("""}""")
    rows.append("</script>")

    text = "\n".join(rows)

    if raw:
        return text
    from IPython.display import HTML  # pragma: no cover
    return HTML(text)  # pragma: no cover
