"""
@file
@brief Helpers to benchmark something
"""
import os
from datetime import datetime
from time import perf_counter
import pickle
from ..loghelper import noLOG, CustomLog, fLOGFormat
from ..loghelper.flog import get_relative_path
from ..pandashelper import df2rst
from ..texthelper import apply_template


class BenchMark:
    """
    Class to help benchmarking. You should overwrite method
    *init*, *bench*, *end*, *graphs*.
    """

    def __init__(self, name, clog=None, fLOG=noLOG, path_to_images=".",
                 cache_file=None, pickle_module=None, progressbar=None,
                 **params):
        """
        @param      name            name of the test
        @param      clog            @see cl CustomLog or string
        @param      fLOG            logging function
        @param      params          extra parameters
        @param      path_to_images  path to images
        @param      cache_file      cache file
        @param      pickle_module   pickle or dill if you need to serialize functions
        @param      progressbar     relies on *tqdm*, example *tnrange*

        If *cache_file* is specified, the class will store the results of the
        method :meth:`bench <pyquickhelper.benchhelper.benchmark.GridBenchMark.bench>`.
        On a second run, the function load the cache
        and run modified or new run (in *params_list*).
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
        self._pickle = pickle_module if pickle_module is not None else pickle
        self._progressbar = progressbar
        self._tracelogs = []

    ##
    # methods to overwrite
    ##

    def init(self):
        """
        Initialisation. Overwrite this method.
        """
        raise NotImplementedError(
            "It should be overwritten.")  # pragma: no cover

    def bench(self, **params):
        """
        Runs the benchmark. Overwrite this method.

        @param      params      parameters
        @return                 metrics as a dictionary, appendix as a dictionary

        The results of this method will be cached if a *cache_file* was specified in the constructor.
        """
        raise NotImplementedError(
            "It should be overwritten.")  # pragma: no cover

    def end(self):
        """
        Cleans. Overwrites this method.
        """
        raise NotImplementedError(
            "It should be overwritten.")  # pragma: no cover

    def graphs(self, path_to_images):
        """
        Builds graphs after the benchmark was run.

        @param      path_to_images      path to images
        @return                         a list of LocalGraph

        Every returned graph must contain a function which creates
        the graph. The function must accepts two parameters *ax* and
        *text*. Example:

        ::

            def local_graph(ax=None, text=True, figsize=(5,5)):
                vx = ...
                vy = ...
                btrys = set(df["_btry"])
                ymin = df[vy].min()
                ymax = df[vy].max()
                decy = (ymax - ymin) / 50
                colors = cm.rainbow(numpy.linspace(0, 1, len(btrys)))
                if len(btrys) == 0:
                    raise ValueError("The benchmark is empty.")
                if ax is None:
                    fig, ax = plt.subplots(1, 1, figsize=figsize)
                    ax.grid(True)
                for i, btry in enumerate(sorted(btrys)):
                    subset = df[df["_btry"]==btry]
                    if subset.shape[0] > 0:
                        subset.plot(x=vx, y=vy, kind="scatter", label=btry, ax=ax, color=colors[i])
                    if text:
                        tx = subset[vx].mean()
                        ty = subset[vy].mean()
                        ax.text(tx, ty + decy, btry, size='small',
                                color=colors[i], ha='center', va='bottom')
                ax.set_xlabel(vx)
                ax.set_ylabel(vy)
                return ax
        """
        return []

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

        def __init__(self, func_gen, filename=None, title=None, root=None):
            """
            @param      func_gen        function generating the graph
            @param      filename        filename
            @param      title           title
            @param      root            path should be relative to this one
            """
            if func_gen is None:
                raise ValueError("func_gen cannot be None")  # pragma: no cover
            if filename is not None:
                self.filename = filename
            if title is not None:
                self.title = title
            self.root = root
            self.func_gen = func_gen

        def plot(self, ax=None, text=True, **kwargs):
            """
            Draws the graph again.

            @param      ax          axis
            @param      text        add text on the graph
            @param      kwargs      additional parameters
            @return                 axis
            """
            return self.func_gen(ax=ax, text=text, **kwargs)

        def add(self, name, value):
            """
            Adds an attribute.

            @param      name        name of the attribute
            @param      value       value
            """
            setattr(self, name, value)

        def to_html(self):
            """
            Renders as :epkg:`HTML`.
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
                raise NotImplementedError(
                    "only files are allowed")  # pragma: no cover

        def to_rst(self):
            """
            Renders as :ekg:`rst`.
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
                raise NotImplementedError(
                    "only files are allowed")  # pragma: no cover

    @property
    def Name(self):
        """
        Returns the name of the benchmark.
        """
        return self._name

    def fLOG(self, *args, **kwargs):
        """
        Logs something.
        """
        self._tracelogs.append(fLOGFormat("\n", *args, **kwargs).strip("\n"))
        if self._clog:
            self._clog(*args, **kwargs)
        if self._fLOG:
            self._fLOG(*args, **kwargs)
        if hasattr(self, "_progressbars") and self._progressbars and len(self._progressbars) > 0:
            br = self._progressbars[-1]
            br.set_description(fLOGFormat(
                "\n", *args, **kwargs).strip("\n").split("\n")[0])
            br.refresh()

    def run(self, params_list):
        """
        Runs the benchmark.

        @param      params_list     list of dictionaries
        """
        if not isinstance(params_list, list):
            raise TypeError("params_list must be a list")  # pragma: no cover
        for di in params_list:
            if not isinstance(di, dict):
                raise TypeError(  # pragma: no cover
                    "params_list must be a list of dictionaries")

        # shared variables
        cached = {}
        meta = dict(level="BenchMark", name=self.Name, nb=len(
            params_list), time_begin=datetime.now())
        self._metadata = []
        self._metadata.append(meta)
        nb_cached = 0

        # cache
        def cache_():
            "local function"
            if self._cache_file is not None and os.path.exists(self._cache_file):
                self.fLOG("[BenchMark.run] retrieve cache '{0}'".format(
                    self._cache_file))
                with open(self._cache_file, "rb") as f:
                    cached.update(self._pickle.load(f))
                self.fLOG("[BenchMark.run] number of cached run: {0}".format(
                    len(cached["params_list"])))
            else:
                if self._cache_file is not None:
                    self.fLOG("[BenchMark.run] cache not found '{0}'".format(
                        self._cache_file))
                cached.update(dict(metrics=[], appendix=[], params_list=[]))
            self.uncache(cached)

        # run
        def run_(pgar):
            "local function"
            nonlocal nb_cached
            self._metrics = []
            self._appendix = []

            self.fLOG("[BenchMark.run] init {0} do".format(self.Name))
            self.init()
            self.fLOG("[BenchMark.run] init {0} done".format(self.Name))
            self.fLOG("[BenchMark.run] start {0}".format(self.Name))

            for i in pgbar:
                di = params_list[i]

                # check the cache
                if i < len(cached["params_list"]) and cached["params_list"][i] == di:
                    can = True
                    for v in cached.values():
                        if i >= len(v):
                            # cannot cache
                            can = False
                            break

                    if can:
                        # can, it  checks a file is present
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
                cl = perf_counter()
                tu = self.bench(**di)
                cl = perf_counter() - cl

                if isinstance(tu, tuple):
                    tus = [tu]
                elif isinstance(tu, list):
                    tus = tu
                else:
                    raise TypeError(  # pragma: no cover
                        "return of method bench must be a tuple of a list")

                # checkings
                for tu in tus:
                    met, app = tu
                    if len(tu) != 2:
                        raise TypeError(  # pragma: no cover
                            "Method run should return a tuple with 2 elements.")
                    if "_btry" not in met:
                        raise KeyError(  # pragma: no cover
                            "Metrics should contain key '_btry'.")
                    if "_btry" not in app:
                        raise KeyError(  # pragma: no cover
                            "Appendix should contain key '_btry'.")

                for met, app in tus:
                    met["_date"] = dt
                    dt = datetime.now() - dt
                    if not isinstance(met, dict):
                        raise TypeError(  # pragma: no cover
                            "metrics should be a dictionary")
                    if "_time" in met:
                        raise KeyError(  # pragma: no cover
                            "key _time should not be the returned metrics")
                    if "_span" in met:
                        raise KeyError(  # pragma: no cover
                            "key _span should not be the returned metrics")
                    if "_i" in met:
                        raise KeyError(  # pragma: no cover
                            "key _i should not be in the returned metrics")
                    if "_name" in met:
                        raise KeyError(  # pragma: no cover
                            "key _name should not be the returned metrics")
                    met["_time"] = cl
                    met["_span"] = dt
                    met["_i"] = i
                    met["_name"] = self.Name
                    self._metrics.append(met)
                    app["_i"] = i
                    self._appendix.append(app)
                    self.fLOG(
                        "[BenchMark.run] {0}/{1} end {2}".format(i + 1, len(params_list), met))

        def graph_():
            "local function"
            self.fLOG("[BenchMark.run] graph {0} do".format(self.Name))
            self._graphs = self.graphs(self._path_to_images)
            if self._graphs is None or not isinstance(self._graphs, list):
                raise TypeError(  # pragma: no cover
                    "Method graphs does not return anything.")
            for tu in self._graphs:
                if not isinstance(tu, self.LocalGraph):
                    raise TypeError(  # pragma: no cover
                        "Method graphs should return a list of LocalGraph.")
            self.fLOG("[BenchMark.run] graph {0} done".format(self.Name))
            self.fLOG("[BenchMark.run] Received {0} graphs.".format(
                len(self._graphs)))
            self.fLOG("[BenchMark.run] end {0} do".format(self.Name))
            self.end()
            self.fLOG("[BenchMark.run] end {0} done".format(self.Name))
            meta["time_end"] = datetime.now()
            meta["nb_cached"] = nb_cached

        # write information about run experiments
        def final_():
            "local function"
            if self._cache_file is not None:
                self.fLOG("[BenchMark.run] save cache '{0}'".format(
                    self._cache_file))
                cached = dict(metrics=self._metrics,
                              appendix=self._appendix, params_list=params_list)
                with open(self._cache_file, "wb") as f:
                    self._pickle.dump(cached, f)
                for di in self._metrics:
                    look = "{0}.{1}.clean_cache".format(
                        self._cache_file, di["_btry"])
                    with open(look, "w") as f:
                        f.write(
                            "Remove this file if you want to force a new run.")
                    self.fLOG("[BenchMark.run] wrote '{0}'.".format(look))

                self.fLOG("[BenchMark.run] done.")

        progress = self._progressbar if self._progressbar is not None else range
        functions = [cache_, run_, graph_, final_]
        pgbar0 = progress(0, len(functions))
        if self._progressbar:
            self._progressbars = [pgbar0]
        for i in pgbar0:
            if i == 1:
                pgbar = progress(len(params_list))
                if self._progressbar:
                    self._progressbars.append(pgbar)
                functions[i](pgbar)
                if self._progressbar:
                    self._progressbars.pop()
            else:
                functions[i]()

        self._progressbars = None
        return self._metrics, self._metadata

    @property
    def Metrics(self):
        """
        Returns the metrics.
        """
        if not hasattr(self, "_metrics"):
            raise KeyError(  # pragma: no cover
                "Method run was not run, no metrics was found.")
        return self._metrics

    @property
    def Metadata(self):
        """
        Returns the metrics.
        """
        if not hasattr(self, "_metadata"):
            raise KeyError(  # pragma: no cover
                "Method run was not run, no metadata was found.")
        return self._metadata

    @property
    def Appendix(self):
        """
        Returns the metrics.
        """
        if not hasattr(self, "_appendix"):
            raise KeyError(  # pragma: no cover
                "Method run was not run, no metadata was found.")
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
                    cols.append(self._convert(df, i, c, d, df.loc[i, c]))
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
                    lambda s: ':ref:`{0} <l-{1}-{0}>`'.format(s, self.Name))
            else:
                raise ValueError(  # pragma: no cover
                    "Format should be rst or html.")
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
                    cols.append(self._convert(df, i, c, d, df.loc[i, c]))
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
                raise ValueError(  # pragma: no cover
                    "Format should be rst or html.")
        return df[col1 + col2]

    def report(self, css=None, template_html=None, template_rst=None, engine="mako", filecsv=None,
               filehtml=None, filerst=None, params_html=None, title=None, description=None):
        """
        Produces a report.

        @param      css             css (will take the default one if empty)
        @param      template_html   template HTML (:epkg:`mako` or :epkg:`jinja2`)
        @param      template_rst    template RST (:epkg:`mako` or :epkg:`jinja2`)
        @param      engine          ``'mako``' or '``jinja2'``
        @param      filehtml        report will written in this file if not None
        @param      filecsv         metrics will be written as a flat table
        @param      filerst         metrics will be written as a RST table
        @param      params_html     parameter to send to function :epkg:`pandas:DataFrame.to_html`
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
            title = self.Name  # pragma: no cover
        if "escape" not in params_html:
            params_html["escape"] = False

        for gr in self.Graphs:
            gr.add("root", os.path.dirname(filehtml))

        # I don't like that too much as it is not multithreaded.
        # Avoid truncation.
        import pandas

        if description is None:
            description = ""  # pragma: no cover

        contents = {'df': self.to_df()}

        # HTML
        if template_html is not None and len(template_html) > 0:
            old_width = pandas.get_option('display.max_colwidth')
            pandas.set_option('display.max_colwidth', None)
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
            pandas.set_option('display.max_colwidth', None)

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
            raise KeyError("unable to find _graphs")  # pragma: no cover
        return self._graphs

    default_css = """
                .datagrid table { border-collapse: collapse; border-spacing: 0; width: 100%;
                        table-layout: fixed; font-family: Verdana; font-size: 12px;
                        word-wrap: break-word; }

                .datagrid thead {
                  cursor: pointer;
                  background: #c9dff0;
                }
                .datagrid thead tr th {
                  font-weight: bold;
                  padding: 12px 30px;
                  padding-left: 12px;
                }
                .datagrid thead tr th span {
                  padding-right: 10px;
                  background-repeat: no-repeat;
                  text-align: left;
                }

                .datagrid tbody tr {
                  color: #555;
                }
                .datagrid tbody td {
                  text-align: center;
                  padding: 10px 5px;
                }
                .datagrid tbody th {
                  text-align: left;
                  padding: 10px 5px;
                }
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
                % for met, app in zip(bench.Metrics, bench.Appendix):
                    <h3 id="${app["_i"]}">${app["_btry"]}</h3>
                    <ul>
                    % for k, v in sorted(app.items()):
                        % if isinstance(v, str) and "\\n" in v:
                            <li>I <b>${k}</b>: <pre>${v}</pre></li>
                        % else:
                            <li>I <b>${k}</b>: ${v}</li>
                        % endif
                    % endfor
                    % for k, v in sorted(met.items()):
                        % if isinstance(v, str) and "\\n" in v:
                            <li>M <b>${k}</b>: <pre>${v}</pre></li>
                        % else:
                            <li>M <b>${k}</b>: ${v}</li>
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

                .. _lb-${bench.Name}:

                ${title}
                ${"=" * len(title)}

                .. contents::
                    :local:

                ${description}

                Metadata
                --------

                ${df2rst(bench.meta_to_df(convert=True, add_link=True, format="rst"), index=True, list_table=True)}

                Metrics
                --------

                ${df2rst(bench.to_df(convert=True, add_link=True, format="rst"), index=True, list_table=True)}

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

                % for met, app in zip(bench.Metrics, bench.Appendix):

                .. _l-${bench.Name}-${app["_i"]}:

                ${app["_btry"]}
                ${"+" * len(app["_btry"])}

                % for k, v in sorted(app.items()):
                    % if isinstance(v, str) and "\\n" in v:
                * I **${k}**:
                  ::

                    ${"\\n    ".join(v.split("\\n"))}

                    % else:
                * M **${k}**: ${v}
                    % endif
                % endfor

                % for k, v in sorted(met.items()):
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
