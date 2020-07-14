"""
@file
@brief Helpers for CI.
"""


def is_travis_or_appveyor(env=None):
    """
    Tells if is a *travis* environment or *appveyor*.

    @param      env         checks that a environment variable is set up.
    @return                 ``'travis'``, ``'appveyor'``, ``'circleci'``
                            or ``'azurepipe'`` or ``None``

    The function should rely more on environement variables
    ``CI``, ``TRAVIS``, ``APPVEYOR``, ``AZURE_HTTP_USER_AGENT``.

    .. versionadded:: 1.8
        Parameter *env* was added.
    """
    import sys
    if "travis" in sys.executable:
        return "travis"  # pragma: no cover
    import os
    if os.environ.get("USERNAME", os.environ.get("USER", None)) == "appveyor" or \
       os.environ.get("APPVEYOR", "").lower() in ("true", "1"):
        return "appveyor"  # pragma: no cover
    if os.environ.get('CIRCLECI', "undefined") != "undefined":
        return "circleci"  # pragma: no cover
    if os.environ.get('AZURE_HTTP_USER_AGENT', 'undefined') != 'undefined':
        return "azurepipe"  # pragma: no cover
    if env is not None:
        for k in env:
            if k in os.environ and os.environ[k]:
                return k
    return None
