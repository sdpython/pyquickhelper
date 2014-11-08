#-*- coding:utf-8 -*-
"""
@file
@brief Various ways to import data into a dataframe
"""
import io
from ..loghelper.url_helper import get_url_content


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
    return pandas.read_csv(io.StringIO(text), **args)