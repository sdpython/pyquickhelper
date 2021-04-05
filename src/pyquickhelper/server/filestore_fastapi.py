# -*- coding:utf-8 -*-
"""
@file
@brief Simple class to store and retrieve files through an API.
"""
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from .filestore_sqlite import SqlLite3FileStore


class Item(BaseModel):
    name: Optional[str]  # pylint: disable=E1136
    format: Optional[str]  # pylint: disable=E1136
    team: Optional[str]  # pylint: disable=E1136
    project: Optional[str]  # pylint: disable=E1136
    version: Optional[str]  # pylint: disable=E1136
    content: Optional[str]  # pylint: disable=E1136
    password: str


class Query(BaseModel):
    name: str
    password: str


def create_fast_api_app(db_path, password):
    """
    Creates a :epkg:`REST` application based on :epkg:`FastAPI`.

    :return: app
    """
    store = SqlLite3FileStore(db_path)

    async def get_root():
        return {"pyquickhelper": "FastAPI to load and query files"}

    async def add(item: Item, request: Request):
        if item.password != password:
            raise HTTPException(status_code=401, detail="Wrong password")
        kwargs = dict(name=item.name, format=item.format,
                      team=item.team, project=item.project,
                      version=item.version, content=item.content)
        kwargs['metadata'] = dict(client=request.client)
        res = store.add(**kwargs)
        if 'content' in res:
            del res['content']
        return res

    async def query(query: Query, request: Request):
        if query.password != password:
            raise HTTPException(status_code=401, detail="Wrong password")
        res = list(store.enumerate_data(name=query.name, join=True))
        return res

    app = FastAPI()
    app.get("/")(get_root)
    app.post("/add/")(add)
    app.post("/query/")(query)
    return app
