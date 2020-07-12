# -*- coding:utf-8 -*-
"""
@file
@brief Various ways to import data into a dataframe
"""
import zipfile
from io import StringIO, BytesIO
from ..filehelper import read_content_ufs


def read_csv(filepath_or_buffer, compression=None, fvalid=None, **params):
    """
    Reads a file from a file, it adds the compression zip
    which was removed in the latest version,
    see :epkg:`pandas:read_csv`.

    @param      filepath_or_buffer      filepath or buffer
    @param      compression             see :epkg:`pandas:read_csv`
    @param      params                  see :epkg:`pandas:read_csv`
    @param      fvalid                  if the zip file contains many files, this function
                                        validates which one must be returned based on its name,
                                        the function returns the content of the file in that case (bytes)
    @return                             dataframe or a dictionary (name, dataframe)

    See blog post :ref:`blogpost_read_csv`.
    """
    import pandas
    if isinstance(filepath_or_buffer, str) and \
       (compression == "zip" or (compression is None and
                                 filepath_or_buffer.endswith(".zip"))):
        content = read_content_ufs(filepath_or_buffer, asbytes=True)
        with zipfile.ZipFile(BytesIO(content)) as myzip:
            infos = myzip.infolist()
            if not infos:
                raise FileNotFoundError(  # pragma: no cover
                    "unable to find a file in " + filepath_or_buffer)
            res = {}
            for info in infos:
                name = info.filename
                with myzip.open(name, "r") as f:
                    text = f.read()
                if fvalid is not None and not fvalid(name):
                    res[name] = text
                else:
                    if text is None:
                        raise FileNotFoundError(  # pragma: no cover
                            "Empty file '{0}' in '{1}'".format(
                                name, filepath_or_buffer))
                    text = text.decode(
                        encoding=params.get('encoding', 'ascii'))
                    st = StringIO(text)
                    try:
                        df = pandas.read_csv(
                            st, compression=compression, **params)
                    except pandas.errors.ParserError as e:  # pragma: no cover
                        lines = text.split("\n")
                        end = min(len(lines), 5)
                        mes = "Parsing errors in '{0}', first lines:\n{1}".format(
                            name, "\n".join(lines[:end]))
                        raise Exception(mes) from e
                    res[name] = df
            return res if len(res) > 1 else list(res.values())[0]
    else:
        return pandas.read_csv(  # pragma: no cover
            filepath_or_buffer, compression=compression, **params)
