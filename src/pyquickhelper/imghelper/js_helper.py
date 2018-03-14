"""
@file
@brief Helpers around images and :epkg:`javascript`.

.. versionadded:: 1.7
"""


def run_js_fct(script, required=None):
    """
    Assuming *script* contains some :epkg:`javascript`
    which produces :epkg:`SVG`. This functions runs
    the code.

    @param  script      :epkg:`javascript`
    @param  required    required libraries
    @return             :epkg:`python` function

    The module relies on :epkg:`js2py`.
    """
    from js2py import eval_js, require
    if required:
        if not isinstance(required, list):
            required = [required]
        for r in required:
            require(r)
    fct = eval_js(script)
    return fct
