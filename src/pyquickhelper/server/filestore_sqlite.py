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

    def _get_column_table(self, table):
        cur = self.con_.cursor()
        res = cur.execute("PRAGMA table_info(%s);" % table)
        res = cur.fetchall()
        return res

    def _check_same_column(self, table, columns):
        cols = self._get_column_table(table)
        names = [_[1] for _ in cols]
        return names == columns

    def _create(self):
        """
        Creates the database if it does not exists.
        """
        self.con_ = sqlite3.connect(self.path_)
        cur = self.con_.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        res = cur.fetchall()
        commit = False
        if ('files',) not in res:
            cur.execute(
                '''CREATE TABLE files
                   (id INTEGER PRIMARY KEY, date TEXT, name TEXT,
                    format TEXT, metadata TEXT, team TEXT,
                    project TEXT, version TEXT, content BLOB)''')
            commit = True

        if (('data',) in res and not self._check_same_column(
                "data", ["id", "idfile", "name", "value", "date", "comment"])):
            cur.execute("DROP TABLE data;")
            self.con_.commit()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            res = cur.fetchall()

        if ('data',) not in res:
            cur.execute(
                '''CREATE TABLE data
                   (id INTEGER PRIMARY KEY, idfile INTEGER,
                    name TEXT, value REAL, date TEXT, comment TEXT)''')
            commit = True
        if commit:
            self.con_.commit()

    def submit(self, name, content, format=None, date=None, metadata=None,
               team=None, project=None, version=None):
        """
        Submits a file to the database.

        :param name: filename
        :param content: file content (it can be a dataframe)
        :param format: format
        :param date: date, by default now
        :param metadata: addition information
        :param team: another name
        :param project: another name
        :param version: version
        :return: added data as a dictionary (no content)
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

    def submit_data(self, idfile, name, value, date=None, comment=None):
        """
        Submits data to the database.

        :param idfile: refers to database files
        :param date: date, by default now
        :param name: name
        :param value: data value
        :param comment: additional comment
        :return: added data
        """
        if date is None:
            date = datetime.now()
        date = date.isoformat()
        if comment is None:
            comment = ""

        fields = ['idfile', 'date', 'name', 'value', 'comment']
        values = [idfile, date, name, value, comment]
        sqlite_insert_blob_query = """
            INSERT INTO data (%s) VALUES (%s)""" % (
            ",".join(fields), ",".join("%r" % v for v in values))
        cur = self.con_.cursor()
        cur.execute(sqlite_insert_blob_query)
        self.con_.commit()

    def _enumerate(self, condition, fields):
        cur = self.con_.cursor()
        query = '''SELECT %s FROM files %s %s''' % (
            ",".join(fields),
            "WHERE" if len(condition) > 0 else "",
            " AND ".join(condition))
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

    def enumerate_data(self, idfile=None, name=None, join=False,
                       project=None):
        """
        Queries the database, enumerates the results.

        :param idfile: file identifier
        :param name: value name, None if not specified
        :param join: join with the table *files*
        :param project: filter by project
        :return: results
        """
        fields2 = ['name', 'project', 'team', 'version']

        record = dict(name=name, idfile=idfile, project=project)
        cond = []
        for k, v in record.items():
            if v is None:
                continue
            if join:
                if k in fields2:
                    if not join:
                        raise RuntimeError(
                            "join must be true if metrics are "
                            "filtered by project.")
                    cond.append('B.%s="%s"' % (k, v))
                else:
                    cond.append('data.%s="%s"' % (k, v))
            else:
                cond.append('%s="%s"' % (k, v))

        cur = self.con_.cursor()
        if join:
            fields = ["data.id", "idfile", "data.name", "data.date",
                      "data.value", "data.comment"]
            query = '''
                SELECT %s, %s
                FROM data INNER JOIN files AS B on B.id = idfile
                %s %s''' % (
                ",".join(fields),
                ",".join(map(lambda s: "B.%s" % s, fields2)),
                "WHERE" if len(cond) > 0 else "",
                " AND ".join(cond))
        else:
            fields = ["id", "idfile", "name", "date", "value", "comment"]
            query = '''SELECT %s FROM data %s %s''' % (
                ",".join(fields), "WHERE" if len(cond) > 0 else "",
                " AND ".join(cond))
        res = cur.execute(query)

        if join:
            fields = ([s.replace('data.', '') for s in fields] +
                      ['name_f', 'project', 'team', 'version'])
        for line in res:
            res = {k: v for k, v in zip(fields, line)  # pylint: disable=R1721
                   if v is not None}
            yield res
