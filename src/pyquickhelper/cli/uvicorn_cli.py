"""
@file
@brief Simplified function versions.
"""
import os


def uvicorn_app(path="dummy_db.db3", pwd="dummy", port=8798, host="127.0.0.1"):
    """
    Runs a uvicorn application. It should be used for testing
    not for production. Use ``host:post/redoc`` or
    ``host:post/docs`` to get a web page in order to
    submit files.

    :param path: filename for the databse
    :param pwd: password
    :param host: host
    :param port: port

    .. cmdref::
        :title: Runs a uvicorn application
        :cmd: -m pyquickhelper uvicorn_app --help

        Runs a uvicorn application.
    """
    from ..server.filestore_fastapi import create_app  # pylint: disable=W0611
    import uvicorn
    os.environ['PYQUICKHELPER_FASTAPI_PWD'] = pwd
    os.environ['PYQUICKHELPER_FASTAPI_PATH'] = path
    uvicorn.run("pyquickhelper.server.filestore_fastapi:create_app",
                host=host, port=port, log_level="info", factory=True)
