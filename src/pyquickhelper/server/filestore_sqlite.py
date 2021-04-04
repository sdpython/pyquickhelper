# -*- coding:utf-8 -*-
"""
@file
@brief Simple class to store and retrieve files with a sqlite3 detabase.
"""
import os
import io
import sqlite3
import json
from datetime import datetime
import pandas


class SqlLite3FileStore:
    """
    Simple file storage implemented with :epkg:`python:sqlite3`.

    :param path: location of the database.
    """

    def __init__(self, path="_file_store_.db3"):
        self.path_ = path
        self._create()

    def _create(self):
        """
        Creates the database if it does not exists.
        """
        self.con_ = sqlite3.connect(self.path_)
        cur = self.con_.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        res = cur.fetchall()
        if ('files',) not in res:
            cur.execute(
                '''CREATE TABLE files
                   (id INTEGER PRIMARY KEY, date TEXT, name TEXT,
                    format TEXT, metadata TEXT, team TEXT,
                    project TEXT, version TEXT, content BLOB)''')
            self.con_.commit()

    def add(self, name, content, format=None, date=None, metadata=None,
            team=None, project=None, version=None):
        """
        Adds a file to the database.

        :param name: filename
        :param content: file content (it can be a dataframe)
        :param format: format
        :param date: date, by default now
        :param metadata: addition information
        :param team: another name
        :param project: another name
        :param version: version
        """
        if date is None:
            date = datetime.now()
        date = date.isoformat()
        if isinstance(metadata, dict):
            metadata = json.dumps(metadata)
        elif metadata is not None:
            raise TypeError(
                "metadata must be None or a dictionary.")
        if isinstance(content, pandas.DataFrame):
            st = io.StringIO()
            content.to_csv(st, index=False, encoding="utf-8")
            content = st.getvalue()
            if format is None:
                format = "df"
        if format is None:
            format = os.path.splitext(name)[-1]
        record = dict(name=name, content=content, format=format,
                      metadata=metadata, team=team, project=project,
                      version=version, date=date)
        fields = []
        values = []
        for k, n in record.items():
            if n is None:
                continue
            fields.append(k)
            values.append(n.replace("\\", "\\\\").replace("'", "''"))
        sqlite_insert_blob_query = """
            INSERT INTO files (%s) VALUES (%s)""" % (
            ",".join(fields), ",".join("'%s'" % v for v in values))
        cur = self.con_.cursor()
        cur.execute(sqlite_insert_blob_query)
        self.con_.commit()
        output = dict(name=name, format=format,
                      metadata=metadata, team=team, project=project,
                      version=version, date=date)
        return {k: v for k, v in output.items() if v is not None}

    def _enumerate(self, condition, fields):
        cur = self.con_.cursor()
        query = '''SELECT %s FROM files WHERE %s''' % (
            ",".join(fields), " AND ".join(condition))
        res = cur.execute(query)

        for line in res:
            res = {k: v for k, v in zip(fields, line)}  # pylint: disable=R1721
            if 'format' in res and 'content' in res and res['format'] == 'df':
                st = io.StringIO(res['content'])
                df = pandas.read_csv(st, encoding="utf-8")
                res['content'] = df
            if 'metadata' in res and res['metadata']:
                res['metadata'] = json.loads(res['metadata'])
            yield res

    def enumerate_content(self, name=None, format=None, date=None, metadata=None,
                          team=None, project=None, version=None):
        """
        Queries the database, enumerates the results,
        returns the content as well.

        :param name: filename
        :param format: format
        :param date: date, by default now
        :param metadata: addition information
        :param team: another name
        :param project: another name
        :param version: version
        :return: results
        """
        record = dict(name=name, format=format,
                      metadata=metadata, team=team, project=project,
                      version=version, date=date)
        cond = []
        for k, v in record.items():
            if v is None:
                continue
            cond.append('%s="%s"' % (k, v))
        fields = ["id", "name", "format", "date", "metadata",
                  "team", "project", "version", "content"]
        for it in self._enumerate(cond, fields):
            yield it

    def enumerate(self, name=None, format=None, date=None, metadata=None,
                  team=None, project=None, version=None):
        """
        Queries the database, enumerates the results.

        :param name: filename
        :param format: format
        :param date: date, by default now
        :param metadata: addition information
        :param team: another name
        :param project: another name
        :param version: version
        :return: results
        """
        record = dict(name=name, format=format,
                      metadata=metadata, team=team, project=project,
                      version=version, date=date)
        cond = []
        for k, v in record.items():
            if v is None:
                continue
            cond.append('%s="%s"' % (k, v))
        fields = ["id", "name", "format", "date", "metadata",
                  "team", "project", "version"]
        for it in self._enumerate(cond, fields):
            yield it
