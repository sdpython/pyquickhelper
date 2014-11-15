"""
@file
@brief Some functions to interact better with Notebook
"""

import os

def open_html_form (params,
            title='',
            key_save = "",
            style="background-color:gainsboro; width:600px; padding:10px;",
            raw = False):
    """
    the function displays a form onto a notebook,
    it requires a notebook to be open

    @param      params          dictionary of parameters
    @param      title           titre of the added box
    @param      style           style of the form
    @param      key_save        name of the variable to add to the notebook (as a dictionary)
    @param      raw             returns the raw HTML and not ``HTML( text )``
    @return                     HTML

    The code comes from
    `IPython Notebook: Javascript/Python Bi-directional Communication <https://jakevdp.github.io/blog/2013/06/01/ipython-notebook-javascript-python-communication/>`_.
    When the notebook is converted into a HTML document, the values in the form do not appear.
    This behaviour is expected in case one of the field contains a password.

    .. versionadded:: 0.9
    """

    row = """<td><td>{0}</td><td><input type="{3}" id="{2}{0}" value="{1}" /></td></tr>"""

    rows = [ """<div style="{0}">{1} <table border="0">""".format(style, title, key_save) ]
    for k,v in sorted(params.items()):
        if k.startswith("password") : typ = "password"
        else: typ = "text"
        rows.append ( row.format(k, "" if v is None else str(v), key_save, typ ) )
    rows.append( """</table><button onclick="set_value{0}()">Ok</button></div>""".format(key_save) )

    rows.append("""<script type="text/Javascript">""")
    rows.append("function set_value__KEY__(){".replace("__KEY__",key_save))

    rows.append("   command='%s = {' ;" % key_save)
    for k,v in sorted(params.items()):
        rows.append( """   var {0}{1}var_value = document.getElementById('{0}{1}').value;""".format(key_save,k) )
        rows.append( """   command += '"{0}":"' + """.format(k) + "{0}{1}var_value".format(key_save,k) + """ + '",';""" )
    rows.append("""   command += '}';""")
    rows.append("""   var kernel = IPython.notebook.kernel;""")
    rows.append("""   kernel.execute(command);""")
    rows.append("""}""")
    rows.append("</script>")

    text = "\n".join(rows)

    if raw :
        return text
    else :
        from IPython.display import HTML
        return HTML(text)