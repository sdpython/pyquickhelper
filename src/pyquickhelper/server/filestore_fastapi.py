# -*- coding:utf-8 -*-
"""
@file
@brief Simple class to store and retrieve files through an API.
"""
import os
import io
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel  # pylint: disable=E0611
from .filestore_sqlite import SqlLite3FileStore


class Item(BaseModel):
    name: Optional[str]  # pylint: disable=E1136
    format: Optional[str]  # pylint: disable=E1136
    team: Optional[str]  # pylint: disable=E1136
    project: Optional[str]  # pylint: disable=E1136
    version: Optional[int]  # pylint: disable=E1136
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
    version: Optional[int]  # pylint: disable=E1136
    password: str


class QueryL(BaseModel):
    name: Optional[str]  # pylint: disable=E1136
    team: Optional[str]  # pylint: disable=E1136
    project: Optional[str]  # pylint: disable=E1136
    version: Optional[int]  # pylint: disable=E1136
    limit: Optional[int]  # pylint: disable=E1136
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

    async def content(query: QueryL, request: Request):
        if query.password != password:
            raise HTTPException(status_code=401, detail="Wrong password")
        if query.limit is None:
            limit = 5
        else:
            limit = query.limit
        res = []
        for r in store.enumerate_content(
                name=query.name, team=query.team, project=query.project,
                version=query.version):
            if len(res) >= limit:
                break
            if "content" in r:
                content = r['content']
                if hasattr(content, 'to_csv'):
                    st = io.StringIO()
                    content.to_csv(st, index=False, encoding="utf-8")
                    r['content'] = st.getvalue()
            res.append(r)
        return res

    app = FastAPI()
    app.get("/")(get_root)
    app.post("/submit/")(submit)
    app.post("/content/")(content)
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


def _get_password(password, env="PYQUICKHELPER_FASTAPI_PWD"):
    if password is None:
        password = os.environ.get(env, None)
    if password is None:
        raise RuntimeError(
            "password must be specified or environement variable "
            "'PYQUICKHELPER_FASTAPI_PWD'.")
    return password


def _post_request(client, url, data, suffix, timeout=None):
    if client is None:
        import requests
        resp = requests.post("%s/%s" % (url.strip('/'), suffix), data=data,
                             timeout=timeout)
    else:
        resp = client.post("/%s/" % suffix, json=data)
    if resp.status_code != 200:
        del data['content']
        del data['password']
        raise RuntimeError(
            "Post request failed due to %r\ndata=%r." % (resp, data))
    return resp


def fast_api_submit(df, client=None, url=None, name=None, team=None,
                    project=None, version=None, password=None):
    """
    Stores a dataframe into a local stores.

    :param df: dataframe
    :param client: for unittest purpose
    :param url: API url (can be None if client is not)
    :param name: name
    :param team: team
    :param project: project
    :param version: version
    :param password: password for the submission
    :return: response
    """
    password = _get_password(password)
    st = io.StringIO()
    df.to_csv(st, index=False, encoding="utf-8")
    data = dict(team=team, project=project, version=version,
                password=password, content=st.getvalue(),
                name=name, format="df")
    return _post_request(client, url, data, "submit")


def fast_api_query(client=None, url=None, name=None, team=None,
                   project=None, version=None, password=None,
                   as_df=False):
    """
    Retrieves the list of dataframe based on partial information.

    :param client: for unittest purpose
    :param url: API url (can be None if client is not)
    :param name: name
    :param team: team
    :param project: project
    :param version: version
    :param password: password for the submission
    :return: response
    """
    password = _get_password(password)
    data = dict(team=team, project=project, version=version,
                password=password, name=name)
    resp = _post_request(client, url, data, "query")
    if as_df:
        import pandas
        return pandas.DataFrame(resp.json())
    return resp.json()


def fast_api_content(client=None, url=None, name=None, team=None,
                     project=None, version=None, limit=5,
                     password=None, as_df=True):
    """
    Retrieves the dataframes based on partial information.
    Enumerates a list of dataframes.

    :param client: for unittest purpose
    :param url: API url (can be None if client is not)
    :param name: name
    :param team: team
    :param project: project
    :param version: version
    :param limit: maximum number of dataframes to retrieve
    :param as_df: returns the content as a dataframe
    :param password: password for the submission
    :return: list of dictionary, content is a dataframe
    """
    password = _get_password(password)
    data = dict(team=team, project=project, version=version,
                password=password, name=name, limit=limit)
    resp = _post_request(client, url, data, "content")
    res = resp.json()
    if as_df:
        import pandas

        for r in res:
            content = r.get('content', None)
            if content is None:
                continue
            if 'format' in r and r['format'] == 'df':
                st = io.StringIO(r['content'])
                df = pandas.read_csv(st, encoding="utf-8")
                r['content'] = df
    return res
