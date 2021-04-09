# -*- coding:utf-8 -*-
"""
@file
@brief Simple class to store and retrieve files through an API.
"""
import os
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel  # pylint: disable=E0611
from .filestore_sqlite import SqlLite3FileStore


class Item(BaseModel):
    name: Optional[str]  # pylint: disable=E1136
    format: Optional[str]  # pylint: disable=E1136
    team: Optional[str]  # pylint: disable=E1136
    project: Optional[str]  # pylint: disable=E1136
    version: Optional[str]  # pylint: disable=E1136
    content: Optional[str]  # pylint: disable=E1136
    password: str


class Metric(BaseModel):
    name: Optional[str]
    project: Optional[str]
    password: str


class Query(BaseModel):
    name: Optional[str]  # pylint: disable=E1136
    team: Optional[str]  # pylint: disable=E1136
    project: Optional[str]  # pylint: disable=E1136
    version: Optional[str]  # pylint: disable=E1136
    password: str


def create_fast_api_app(db_path, password):
    """
    Creates a :epkg:`REST` application based on :epkg:`FastAPI`.

    :return: app
    """
    store = SqlLite3FileStore(db_path)

    async def get_root():
        return {"pyquickhelper": "FastAPI to load and query files"}

    async def submit(item: Item, request: Request):
        if item.password != password:
            raise HTTPException(status_code=401, detail="Wrong password")
        kwargs = dict(name=item.name, format=item.format,
                      team=item.team, project=item.project,
                      version=item.version, content=item.content)
        kwargs['metadata'] = dict(client=request.client)
        res = store.submit(**kwargs)
        if 'content' in res:
            del res['content']
        return res

    async def metrics(query: Metric, request: Request):
        if query.password != password:
            raise HTTPException(status_code=401, detail="Wrong password")
        res = list(store.enumerate_data(
            name=query.name, project=query.project, join=True))
        return res

    async def query(query: Query, request: Request):
        if query.password != password:
            raise HTTPException(status_code=401, detail="Wrong password")
        res = list(store.enumerate(name=query.name, team=query.team,
                                   project=query.project, version=query.version))
        return res

    app = FastAPI()
    app.get("/")(get_root)
    app.post("/submit/")(submit)
    app.post("/metrics/")(metrics)
    app.post("/query/")(query)
    return app


def create_app():
    """
    Creates an instance of application class returned
    by @see fn create_fast_api_app. It checks that
    environment variables ``PYQUICKHELPER_FASTAPI_PWD``
    and ``PYQUICKHELPER_FASTAPI_PATH`` are set up with
    a password and a filename. Otherwise, the function
    raised an exception.

    Inspired from the guidelines
    `uvicorn/deployment <https://www.uvicorn.org/deployment/>`_,
    `(2) <https://www.uvicorn.org/deployment/#running-programmatically>`_.
    Some command lines:

    ::

        uvicorn --factory pyquickhelper.server.filestore_fastapi:create_app --port 8798
                --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem
        gunicorn --keyfile=./key.pem --certfile=./cert.pem -k uvicorn.workers.UvicornWorker
                 --factory pyquickhelper.server.filestore_fastapi:create_app --port 8798

    ::

        nohup python -m uvicorn --factory pyquickhelper.server.filestore_fastapi:create_app
              --port xxxx --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem
              --host xx.xxx.xx.xxx --ssl-keyfile-password xxxx > fastapi.log &

    ::

        uvicorn.run("pyquickhelper.server.filestore_fastapi:create_app",
                    host="127.0.0.1", port=8798, log_level="info", factory=True)

    ::

        openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
    """
    if "PYQUICKHELPER_FASTAPI_PWD" not in os.environ:
        raise RuntimeError(
            "Environment variable PYQUICKHELPER_FASTAPI_PWD is missing.")
    if "PYQUICKHELPER_FASTAPI_PATH" not in os.environ:
        raise RuntimeError(
            "Environment variable PYQUICKHELPER_FASTAPI_PATH is missing.")
    app = create_fast_api_app(os.environ['PYQUICKHELPER_FASTAPI_PATH'],
                              os.environ['PYQUICKHELPER_FASTAPI_PWD'])
    return app
