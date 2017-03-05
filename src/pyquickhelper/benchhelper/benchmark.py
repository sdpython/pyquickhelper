"""
@file
@brief Helpers to benchmark something

.. versionadded:: 1.5
"""
import os
import sys
from datetime import datetime
from time import clock
import pickle
from ..loghelper import noLOG, CustomLog
from ..texthelper import apply_template
from ..pandashelper import df2rst
from ..loghelper.flog import get_relative_path


if sys.version_info[0] == 2:
    from codecs import open


class BenchMark:
    """
    Class to help benchmarking. You should overwrite method
    *init*, *bench*, *end*, *graphs*.
    """

    def __init__(self, name, clog=None, fLOG=noLOG, path_to_images=".",
                 cache_file=None, **params):
        """
        initialisation

        @param      name            name of the test
        @param      clog            @see cl CustomLog or string
        @param      fLOG            logging function
        @param      params          extra parameters
        @param      path_to_images  path to images
        @param      cache_file      cache file

        If *cache_file* is specified, the class will store the results of the
        method @see me bench. On a second run, the function load the cache
        and run modified or new run (in *param_list*).
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
        self._cache_file = cache_file

    ##
    # methods to overwrite
    ##

    def init(self):
        """
        initialisation, overwrite this method
        """
        raise NotImplementedError("It should be overwritten.")

    def bench(self, **params):
        """
        run the benchmark, overwrite this method

        @param      params      parameters
        @return                 metrics as a dictionary, appendix as a dictionary

        The results of this method will be cached if a *cache_file* was specified in the constructor.
        """
        raise NotImplementedError("It should be overwritten.")

    def end(self):
        """
        clean, overwrite this method
        """
        raise NotImplementedError("It should be overwritten.")

    def uncache(self, cache):
        """
        overwrite this method to uncache some previous run
        """
        pass

    ##
    # end of methods to overwrite
    ##

    class LocalGraph:
        """
        Information about graphs.
        """

        def __init__(self, filename=None, title=None, root=None):
            """
            constructor

            @param      filename        filename
            @param      title           title
            @param      root            path should be relative to this one
            """
            if filename is not None:
                self.filename = filename
            if title is not None:
                self.title = title
            self.root = root

        def add(self, name, value):
            """
            add an attribute

            @param      name        name of the attribute
            @param      value       value
            """
            setattr(self, name, value)

        def to_html(self):
            """
            render as html
            """
            # deal with relatif path.
            if hasattr(self, "filename"):
                attr = {}
                for k in {"title", "alt", "width", "height"}:
                    if k not in attr and hasattr(self, k):
                        attr[k if k != "title" else "alt"] = getattr(self, k)
                merge = " ".join('{0}="{1}"'.format(k, v)
                                 for k, v in attr.items())
                if self.root is not None:
                    filename = get_relative_path(
                        self.root, self.filename, exists=False, absolute=False)
                else:
                    filename = self.filename
                filename = filename.replace("\\", "/")
                return '<img src="{0}" {1}/>'.format(filename, merge)
            else:
                raise NotImplementedError("only files are allowed")

        def to_rst(self):
            """
            render as htmrst
            """
            # do not consider width or height
            # deal with relatif path
            if hasattr(self, "filename"):
                if self.root is not None:
                    filename = get_relative_path(
                        self.root, self.filename, exists=False, absolute=False)
                else:
                    filename = self.filename
                filename = filename.replace("\\", "/")
                return '.. image:: {0}'.format(filename)
            else:
                raise NotImplementedError("only files are allowed")

    def graphs(self, path_to_images):
        """
        builds graphs after the benchmark was run

        @param      path_to_images      path to images
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

        # cache

        if self._cache_file is not None and os.path.exists(self._cache_file):
            self.fLOG("[BenchMark.run] retrieve cache '{0}'".format(
                self._cache_file))
            with open(self._cache_file, "rb") as f:
                cached = pickle.load(f)
            self.fLOG("[BenchMark.run] number of cached run: {0}".format(
                len(cached["params_list"])))
        else:
            if self._cache_file is not None:
                self.fLOG("[BenchMark.run] cache not found '{0}'".format(
                    self._cache_file))
            cached = dict(metrics=[], appendix=[], params_list=[])
        self.uncache(cached)

        # run

        self._metrics = []
        self._metadata = []
        self._appendix = []

        meta = dict(level="BenchMark", name=self.Name, nb=len(
            params_list), time_begin=datetime.now())
        self._metadata.append(meta)

        self.fLOG("[BenchMark.run] init {0} do".format(self.Name))
        self.init()
        self.fLOG("[BenchMark.run] init {0} done".format(self.Name))
        self.fLOG("[BenchMark.run] start {0}".format(self.Name))
        nb_cached = 0

        for i, di in enumerate(params_list):

            # check the cache
            if i < len(cached["params_list"]) and cached["params_list"][i] == di:
                can = True
                for k, v in cached.items():
                    if i >= len(v):
                        # cannot cache
                        can = False
                        break

                if can:
                    # can, we check a file is present
                    look = "{0}.{1}.clean_cache".format(
                        self._cache_file, cached["metrics"][i]["_btry"])
                    if not os.path.exists(look):
                        can = False
                        self.fLOG(
                            "[BenchMark.run] file '{0}' was not found --> run again.".format(look))
                if can:
                    self._metrics.append(cached["metrics"][i])
                    self._appendix.append(cached["appendix"][i])
                    self.fLOG(
                        "[BenchMark.run] retrieved cached {0}/{1}: {2}".format(i + 1, len(params_list), di))
                    self.fLOG(
                        "[BenchMark.run] file '{0}' was found.".format(look))
                    nb_cached += 1
                    continue

                # cache is available

            # no cache
            self.fLOG(
                "[BenchMark.run] {0}/{1}: {2}".format(i + 1, len(params_list), di))
            dt = datetime.now()
            cl = clock()
            tu = self.bench(**di)
            met, app = tu
            cl = clock() - cl

            if not isinstance(tu, tuple):
                raise TypeError("Method run should return a tuple.")
            if len(tu) != 2:
                raise TypeError(
                    "Method run should return a tuple with 2 elements.")
            if "_btry" not in met:
                raise KeyError("Metrics should contain key '_btry'.")
            if "_btry" not in app:
                raise KeyError("Appendix should contain key '_btry'.")

            met["_date"] = dt
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
            app["_i"] = i
            self._appendix.append(app)
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
        meta["time_end"] = datetime.now()
        meta["nb_cached"] = nb_cached

        # write information about run experiments

        if self._cache_file is not None:
            self.fLOG("[BenchMark.run] save cache '{0}'".format(
                self._cache_file))
            cached = dict(metrics=self._metrics,
                          appendix=self._appendix, params_list=params_list)
            with open(self._cache_file, "wb") as f:
                pickle.dump(cached, f)
            for di in self._metrics:
                look = "{0}.{1}.clean_cache".format(
                    self._cache_file, di["_btry"])
                with open(look, "w") as f:
                    f.write("Remove this file if you want to force a new run.")
                self.fLOG("[BenchMark.run] wrote '{0}'.".format(look))

            self.fLOG("[BenchMark.run] done.")

    @property
    def Metrics(self):
        """
        Return the metrics.
        """
        if not hasattr(self, "_metrics"):
            raise KeyError("Method run was not run, no metrics was found.")
        return self._metrics

    @property
    def Metadata(self):
        """
        Return the metrics.
        """
        if not hasattr(self, "_metadata"):
            raise KeyError("Method run was not run, no metadata was found.")
        return self._metadata

    @property
    def Appendix(self):
        """
        Return the metrics.
        """
        if not hasattr(self, "_appendix"):
            raise KeyError("Method run was not run, no metadata was found.")
        return self._appendix

    def to_df(self, convert=False, add_link=False, format="html"):
        """
        Converts the metrics into a dataframe.

        @param          convert         if True, calls method *_convert* on each cell
        @param          add_link        add hyperlink
        @param          format          format for hyperlinks (html or rst)
        @return                         dataframe
        """
        import pandas
        df = pandas.DataFrame(self.Metrics)
        if convert:
            for c, d in zip(df.columns, df.dtypes):
                cols = []
                for i in range(df.shape[0]):
                    cols.append(self._convert(df, i, c, d, df.ix[i, c]))
                df[c] = cols
        col1 = list(sorted(_ for _ in df.columns if _.startswith("_")))
        col2 = list(sorted(_ for _ in df.columns if not _.startswith("_")))
        df = df[col1 + col2]
        if add_link and "_i" in df.columns:
            if format == "html":
                if "_btry" in df.columns:
                    df["_btry"] = df.apply(
                        lambda row: '<a href="#{0}">{1}</a>'.format(row["_i"], row["_btry"]), axis=1)
                df["_i"] = df["_i"].apply(
                    lambda s: '<a href="#{0}">{0}</a>'.format(s))
            elif format == "rst":
                if "_btry" in df.columns:
                    df["_btry"] = df.apply(
                        lambda row: ':ref:`{1} <l-{2}-{0}>`'.format(row["_i"], row["_btry"], self.Name), axis=1)
                df["_i"] = df["_i"].apply(
                    lambda s: ':ref:`{0} <l-{1}-{0}>'.format(s, self.Name))
            else:
                raise ValueError("Format should be rst or html.")
        return df

    def meta_to_df(self, convert=False, add_link=False, format="html"):
        """
        Converts meta data into a dataframe

        @param          convert         if True, calls method *_convert* on each cell
        @param          add_link        add hyperlink
        @param          format          format for hyperlinks (html or rst)
        @return                         dataframe
        """
        import pandas
        df = pandas.DataFrame(self.Metadata)
        if convert:
            for c, d in zip(df.columns, df.dtypes):
                cols = []
                for i in range(df.shape[0]):
                    cols.append(self._convert(df, i, c, d, df.ix[i, c]))
                df[c] = cols
        col1 = list(sorted(_ for _ in df.columns if _.startswith("_")))
        col2 = list(sorted(_ for _ in df.columns if not _.startswith("_")))
        if add_link and "_i" in df.columns:
            if format == "html":
                if "_btry" in df.columns:
                    df["_btry"] = df.apply(
                        lambda row: '<a href="#{0}">{1}</a>'.format(row["_i"], row["_btry"]), axis=1)
                df["_i"] = df["_i"].apply(
                    lambda s: '<a href="#{0}">{0}</a>'.format(s))
            elif format == "rst":
                if "_btry" in df.columns:
                    df["_btry"] = df.apply(
                        lambda row: ':ref:`{1} <l-{2}-{0}>`'.format(row["_i"], row["_btry"], self.Name), axis=1)
                df["_i"] = df["_i"].apply(
                    lambda s: ':ref:`{0} <l-{1}-{0}>'.format(s, self.Name))
            else:
                raise ValueError("Format should be rst or html.")
        return df[col1 + col2]

    def report(self, css=None, template_html=None, template_rst=None, engine="mako", filecsv=None,
               filehtml=None, filerst=None, params_html=None, title=None, description=None):
        """
        Produces a report.

        @param      css             css (will take the default one if empty)
        @param      template_html   template HTML (Mako or Jinja2)
        @param      template_rst    template RST (Mako or Jinja2)
        @param      engine          Mako or Jinja2
        @param      filehtml        report will written in this file if not None
        @param      filecsv         metrics will be written as a flat table
        @param      filerst         metrics will be written as a RST table
        @param      params_html     parameter to send to function `to_html <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_html.html>`_
        @param      title           title (Name if any)
        @param      description     add a description
        @return                     dictionary {format: content}

        You can define your own template by looking into the default ones
        defines in this class (see the bottom of this file).
        By default, HTML and RST report are generated.
        """
        if template_html is None:
            template_html = BenchMark.default_template_html
        if template_rst is None:
            template_rst = BenchMark.default_template_rst
        if css is None:
            css = BenchMark.default_css
        if params_html is None:
            params_html = dict()
        if title is None:
            title = self.Name
        if "escape" not in params_html:
            params_html["escape"] = False

        for gr in self.Graphs:
            gr.add("root", os.path.dirname(filehtml))

        # I don't like that too much as it is not multithreaded.
        # Avoid truncation.
        import pandas

        if description is None:
            description = ""

        contents = {'df': self.to_df()}

        # HTML
        if template_html is not None and len(template_html) > 0:
            old_width = pandas.get_option('display.max_colwidth')
            pandas.set_option('display.max_colwidth', -1)
            res = apply_template(template_html, dict(description=description, title=title,
                                                     css=css, bench=self, params_html=params_html))
            # Restore previous value.
            pandas.set_option('display.max_colwidth', old_width)

            if filehtml is not None:
                with open(filehtml, "w", encoding="utf-8") as f:
                    f.write(res)
            contents["html"] = res

        # RST
        if template_rst is not None and len(template_rst) > 0:
            old_width = pandas.get_option('display.max_colwidth')
            pandas.set_option('display.max_colwidth', -1)

            res = apply_template(template_rst, dict(description=description,
                                                    title=title, bench=self, df2rst=df2rst))

            # Restore previous value.
            pandas.set_option('display.max_colwidth', old_width)

            with open(filerst, "w", encoding="utf-8") as f:
                f.write(res)
            contents["rst"] = res

        # CSV
        if filecsv is not None:
            contents['df'].to_csv(
                filecsv, encoding="utf-8", index=False, sep="\t")
        return contents

    def _convert(self, df, i, col, ty, value):
        """
        Converts a value knowing its column, its type
        into something readable.

        @param      df      dataframe
        @param      i       line index
        @param      col     column name
        @param      ty      type
        @param      value   value to convert
        @return             value
        """
        return value

    @property
    def Graphs(self):
        """
        Returns images of graphs.
        """
        if not hasattr(self, "_graphs"):
            raise KeyError("unable to find _graphs")
        return self._graphs

    default_css = """
                .datagrid table { border-collapse: collapse; text-align: left; width: 100%; }
                .datagrid {font: normal 12px/150% Arial, Helvetica, sans-serif; background: #fff; overflow: hidden;
                    border: 1px solid #BBBBBB; -webkit-border-radius: 3px; -moz-border-radius: 3px; border-radius: 3px; }
                .datagrid table td, .datagrid table th { padding: 3px 10px; }
                .datagrid table thead th {background:-webkit-gradient( linear, left top, left bottom,
                    color-stop(0.05, #BBBBBB), color-stop(1, #BBBBBB) );
                    background:-moz-linear-gradient( center top, #006699 5%, #00557F 100% );
                    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699', endColorstr='#00557F');background-color:#006699;
                    color:#FFFFFF; font-size: 15px; font-weight: bold; border-left: 1px solid #0070A8; text-align: center; }
                .datagrid table thead th:first-child { border: none; }
                .datagrid table tbody td { color: #00496B; border-left: 1px solid #E1EEF4;font-size: 12px;font-weight: normal; }
                .datagrid table tbody
                .alt td { background: #E1EEF4; color: #00496B; }
                .datagrid table tbody td:first-child { border-left: none; }
                .datagrid table tbody tr:last-child td { border-bottom: none; }
                .datagrid table tfoot td div { border-top: 1px solid #006699;background: #E1EEF4;}
                .datagrid table tfoot td { padding: 0; font-size: 12px }
                .datagrid table tfoot td div{ padding: 2px; }
                .datagrid table tfoot td ul { margin: 0; padding:0; list-style: none; text-align: right; }
                .datagrid table tfoot  li { display: inline; }
                .datagrid table tfoot li a { text-decoration: none; display: inline-block;  padding: 2px 8px;
                    margin: 1px;color: #FFFFFF;border: 1px solid #006699;-webkit-border-radius: 3px;
                    -moz-border-radius: 3px; border-radius: 3px;
                    background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #006699), color-stop(1, #00557F) );
                    background:-moz-linear-gradient( center top, #006699 5%, #00557F 100% );
                    filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699', endColorstr='#00557F');
                    background-color:#006699; }
                .datagrid table tfoot ul.active,
                .datagrid table tfoot ul a:hover { text-decoration: none;border-color: #006699; color: #FFFFFF; background: none;
                    background-color:#00557F;}
                div.dhtmlx_window_active, div.dhx_modal_cover_dv { position: fixed !important; }
                .appendix pre { background-color: rgb(220,220,220); padding: 0.5em;
                                font-family: monospace; margin: 0.5em 0;
                                width: 60%;}
                """.replace("                ", "")

    default_template_html = """
                <html>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
                <style>
                ${css}
                </style>
                <body>
                <h1>${title}</h1>
                ${description}
                <ul>
                <li><a href="#metadata">Metadata</a></li>
                <li><a href="#metrics">Metrics</a></li>
                <li><a href="#graphs">Graphs</a></li>
                <li><a href="#appendix">Appendix</a></li>
                </ul>
                <h2 id="metadata">Metadata</h2>
                <div class="datagrid">
                ${bench.meta_to_df(convert=True, add_link=True).to_html(**params_html)}
                </div>
                <h2 id="metrics">Metrics</h2>
                <div class="datagrid">
                ${bench.to_df(convert=True, add_link=True).to_html(**params_html)}
                </div>
                % if len(bench.Graphs) > 0:
                <h2 id="graphs">Graphs</h2>
                % for gr in bench.Graphs:
                    ${gr.to_html()}
                % endfor
                % endif
                % if len(bench.Appendix) > 0:
                <h2 id="appendix">Appendix</h2>
                <div class="appendix">
                % for app in bench.Appendix:
                    <h3 id="${app["_i"]}">${app["_btry"]}</h3>
                    <ul>
                    % for k, v in sorted(app.items()):
                        % if isinstance(v, str) and "\\n" in v:
                            <li><b>${k}</b>: <pre>${v}</pre></li>
                        % else:
                            <li><b>${k}</b>: ${v}</li>
                        % endif
                    % endfor
                    </ul>
                % endfor
                % endif
                </div>
                </body>
                </html>
                """.replace("                ", "")

    default_template_rst = """
                ${title}
                ${"=" * len(title)}

                .. contents::
                    :local:

                Metadata
                --------

                ${df2rst(bench.meta_to_df(convert=True, add_link=True, format="rst"), index=True)}

                Metrics
                --------

                ${df2rst(bench.to_df(convert=True, add_link=True, format="rst"), index=True)}

                % if len(bench.Graphs) > 0:

                Graphs
                ------

                % for gr in bench.Graphs:
                    ${gr.to_rst()}
                % endfor

                % endif

                % if len(bench.Appendix) > 0:

                Appendix
                --------

                % for app in bench.Appendix:

                .. _l-${bench.Name}-${app["_i"]}:

                ${app["_btry"]}
                ${"+" * len(app["_btry"])}

                % for k, v in sorted(app.items()):
                    % if isinstance(v, str) and "\\n" in v:
                * **${k}**:
                  ::

                    ${"\\n    ".join(v.split("\\n"))}

                    % else:
                * **${k}**: ${v}
                    % endif
                % endfor
                % endfor
                % endif
                """.replace("                ", "")
