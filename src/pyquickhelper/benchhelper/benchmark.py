"""
@file
@brief Helpers to benchmark something

.. versionadded:: 1.5
"""
import os
import sys
from datetime import datetime
from time import clock
from ..loghelper import noLOG, CustomLog
from ..texthelper import apply_template


if sys.version_info[0] == 2:
    from codecs import open


class BenchMark:
    """
    Class to help benchmarking. You should overwrite method
    *init*, *bench*, *end*, *graphs*.
    """

    def __init__(self, name, clog=None, fLOG=noLOG, path_to_images=".", **params):
        """
        initialisation

        @param      name            name of the test
        @param      clog            @see cl CustomLog or string
        @param      fLOG            logging function
        @param      params          extra parameters
        @param      path_to_images  path to images
        """
        self._fLOG = fLOG
        self._name = name

        if isinstance(clog, CustomLog):
            self._clog = clog
        elif clog is None:
            self._clog = None
        else:
            self._clog = CustomLog(clog)
        self._params = params
        self._path_to_images = path_to_images

    def init(self):
        """
        initialisation, overwrite this method
        """
        pass

    def bench(self, **params):
        """
        run the benchmark, overwrite this method

        @param      params      parameters
        @return                 metrics as a dictionary
        """
        pass

    def end(self):
        """
        clean, overwrite this method
        """
        pass

    def graphs(self, path_to_images):
        """
        builds graphs after the benchmark was run

        @param      path_to_images
        """
        return []

    @property
    def Name(self):
        """
        Return the name of the benchmark.
        """
        return self._name

    def fLOG(self, *l, **p):
        """
        Log something.
        """
        if self._clog:
            self._clog(*l, **p)
        if self._fLOG:
            self._fLOG(*l, **p)

    def run(self, params_list):
        """
        Run the benchmark.

        @param      param_list      list of dictionaries
        """
        if not isinstance(params_list, list):
            raise TypeError("params_list must be a list")
        for di in params_list:
            if not isinstance(di, dict):
                raise TypeError("params_list must be a list of dictionaries")

        self.fLOG("[BenchMark.run] init {0} do".format(self.Name))
        self.init()
        self.fLOG("[BenchMark.run] init {0} done".format(self.Name))

        self.fLOG("[BenchMark.run] start {0}".format(self.Name))
        self._metrics = []
        for i, di in enumerate(params_list):
            self.fLOG(
                "[BenchMark.run] {0}/{1}: {2}".format(i + 1, len(params_list), di))
            dt = datetime.now()
            cl = clock()
            met = self.bench(**di)
            cl = clock() - cl
            dt = datetime.now() - dt
            if not isinstance(met, dict):
                raise TypeError("metrics should be a dictionary")
            if "_time" in met:
                raise KeyError("key _time should not be the returned metrics")
            if "_span" in met:
                raise KeyError("key _span should not be the returned metrics")
            if "_i" in met:
                raise KeyError("key _i should not be the returned metrics")
            if "_name" in met:
                raise KeyError("key _name should not be the returned metrics")
            met["_time"] = cl
            met["_span"] = dt
            met["_i"] = i
            met["_name"] = self.Name
            self._metrics.append(met)
            self.fLOG(
                "[BenchMark.run] {0}/{1} end {2}".format(i + 1, len(params_list), met))

        self.fLOG("[BenchMark.run] graph {0} do".format(self.Name))
        self._graphs = self.graphs(self._path_to_images)
        if self._graphs is None or not isinstance(self._graphs, list):
            raise TypeError("Method graphs does not return anything.")
        self.fLOG("[BenchMark.run] graph {0} done".format(self.Name))

        self.fLOG("[BenchMark.run] end {0} do".format(self.Name))
        self.end()
        self.fLOG("[BenchMark.run] end {0} done".format(self.Name))

    @property
    def Metrics(self):
        """
        Return the metrics.
        """
        if not hasattr(self, "_metrics"):
            raise KeyError("Method run was not run, no metris was found.")
        return self._metrics

    def to_df(self):
        """
        Converts the metrics into a dataframe.

        @return       dataframe
        """
        import pandas
        df = pandas.DataFrame(self.Metrics)
        col1 = list(sorted(_ for _ in df.columns if _.startswith("_")))
        col2 = list(sorted(_ for _ in df.columns if not _.startswith("_")))
        return df[col1 + col2]

    def report(self, css=None, template=None, engine="mako", filecsv=None,
               filehtml=None, params_html=None):
        """
        Produces a report.

        @param      css         css (will take the default one if empty)
        @param      template    template (Mako or Jinja2)
        @param      engine      Mako or Jinja2
        @param      filehtml    report will written in this file if not None
        @param      filecsv     metrics will be written as a flat table
        @param      params_html parameter to send to function `to_html <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_html.html>`_
        @return                 result (string)
        """
        if template is None:
            template = BenchMark.default_template
        if css is None:
            css = BenchMark.default_css
        if params_html is None:
            params_html = dict()
            params_html["float_format"] = "%1.3f"
            params_html["index"] = False
        res = apply_template(template, dict(
            css=css, bench=self, params_html=params_html))
        if filehtml is not None:
            with open(filehtml, "w", encoding="utf-8") as f:
                f.write(res)
        if filecsv is not None:
            self.to_df().to_csv(filecsv, encoding="utf-8", index=False)
        return res

    @property
    def Graphs(self):
        """
        Returns images of graphs.
        """
        if not hasattr(self, "_graphs"):
            raise KeyError("unable to find _graphs")
        return self._graphs

    default_css = """
    """

    default_template = """
                <html>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
                <style>
                ${css}
                </style>
                <body>
                <h1> ${bench.Name}</h1>
                <h2>Metrics</h2>
                ${bench.to_df().to_html(**params_html)}
                % if len(bench.Graphs) > 0:
                <h2>Graphs</h2>
                % for gr in bench.Graphs:
                <img src="${gr.name}" />
                % endfor
                % endif
                </body>
                </html>
                """.replace("                ", "")
