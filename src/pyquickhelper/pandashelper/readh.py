#-*- coding:utf-8 -*-
"""
@file
@brief Various ways to import data into a dataframe
"""
import sys
import zipfile
from ..loghelper.url_helper import get_url_content
from ..filehelper import read_content_ufs


if sys.version_info[0] == 2:
    from StringIO import StringIO
    BytesIO = StringIO
    FileNotFoundError = Exception
else:
    from io import StringIO, BytesIO


def read_url(url, **args):
    """
    the function reads data from a url, it expects a flat file,
    the function does not consider the data to download as a stream,
    it first downloads everything

    @param      url     url
    @param      args    parameter given to function `read_csv <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.io.parsers.read_csv.html>`_
    @return             a DataFrame

    @example(create a pandas DataFrame from a file on internet)
    @code
    url = "http://www.xavierdupre.fr/enseignement/complements/marathon.txt"
    df = read_url(url, sep="\t", names=["ville", "annee", "temps","secondes"])
    @endcode
    @endexample
    """
    import pandas
    text = get_url_content(url)
    return pandas.read_csv(StringIO(text), **args)


def read_csv(filepath_or_buffer, compression=None, fvalid=None, **params):
    """
    read a file from a file, it adds the compression zip
    which was removed in the latest version,
    see `read_csv <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html>`_

    @param      filepath_or_buffer      filepath or buffer
    @param      compression             see `read_csv <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html>`_
    @param      params                  see `read_csv <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html>`_
    @param      fvalid                  if the zip file contains many files, this function
                                        validates which one must be returned based on its name,
                                        the function returns the content of the file in that case (bytes)
    @return                             dataframe or a dictionary (name, dataframe)

    See blog post :ref:`blogpost_read_csv`.
    """
    import pandas
    if isinstance(filepath_or_buffer, str  # unicode#
                  ) and (compression == "zip" or (compression is None and filepath_or_buffer.endswith(".zip"))):
        content = read_content_ufs(filepath_or_buffer, asbytes=True)
        with zipfile.ZipFile(BytesIO(content)) as myzip:
            infos = myzip.infolist()
            if not infos:
                raise FileNotFoundError(
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
                        raise FileNotFoundError(
                            "empty file {0} in {1}".format(name, filepath_or_buffer))
                    text = text.decode(
                        encoding=params.get('encoding', 'ascii'))
                    st = StringIO(text)
                    try:
                        df = pandas.read_csv(
                            st, compression=compression, **params)
                    except pandas.parser.CParserError as e:
                        lines = text.split("\n")
                        end = min(len(lines), 5)
                        mes = "Parsing errors in {0}, first lines:\n{1}".format(
                            name, "\n".join(lines[:end]))
                        raise Exception(mes) from e
                    res[name] = df
            return res if len(res) > 1 else list(res.values())[0]
    else:
        return pandas.read_csv(filepath_or_buffer, compression=compression, **params)
