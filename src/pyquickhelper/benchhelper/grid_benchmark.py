# -*- coding: utf-8 -*-
"""
@file
@brief Grid benchmark.
"""

from time import perf_counter
from ..loghelper import noLOG
from .benchmark import BenchMark


class GridBenchMark(BenchMark):
    """
    Compares a couple of machine learning models.
    """

    def __init__(self, name, datasets, clog=None, fLOG=noLOG, path_to_images=".",
                 cache_file=None, repetition=1, progressbar=None, **params):
        """
        @param      name            name of the test
        @param      datasets        list of dictionary of dataframes
        @param      clog            see @see cl CustomLog or string
        @param      fLOG            logging function
        @param      params          extra parameters
        @param      path_to_images  path to images
        @param      cache_file      cache file
        @param      repetition      repetition of the experiment (to get confidence interval)
        @param      progressbar     relies on *tqdm*, example *tnrange*

        If *cache_file* is specified, the class will store the results of the
        method :meth:`bench <pyquickhelper.benchhelper.benchmark.GridBenchMark.bench>`.
        On a second run, the function load the cache
        and run modified or new run (in *param_list*).

        *datasets* should be a dictionary with dataframes a values
        with the following keys:

        * ``'X'``: features
        * ``'Y'``: labels (optional)
        """
        BenchMark.__init__(self, name=name, datasets=datasets, clog=clog,
                           fLOG=fLOG, path_to_images=path_to_images,
                           cache_file=cache_file, progressbar=progressbar,
                           **params)

        if not isinstance(datasets, list):
            raise TypeError("datasets must be a list")  # pragma: no cover
        for i, df in enumerate(datasets):
            if not isinstance(df, dict):
                raise TypeError(  # pragma: no cover
                    "Every dataset must be a dictionary, {0}th is not.".format(i))
            if "X" not in df:
                raise KeyError(  # pragma: no cover
                    "Dictionary {0} should contain key 'X'.".format(i))
            if "di" in df:
                raise KeyError(  # pragma: no cover
                    "Dictionary {0} should not contain key 'di'.".format(i))
            if "name" not in df:
                raise KeyError(  # pragma: no cover
                    "Dictionary {0} should not contain key 'name'.".format(i))
            if "shortname" not in df:
                raise KeyError(  # pragma: no cover
                    "Dictionary {0} should not contain key 'shortname'.".format(i))
        self._datasets = datasets
        self._repetition = repetition

    def init_main(self):
        """
        initialisation
        """
        skip = {"X", "Y", "weight", "name", "shortname"}
        self.fLOG("[MlGridBenchmark.init] begin")
        self._datasets_info = []
        self._results = []
        for i, dd in enumerate(self._datasets):
            X = dd["X"]
            N = X.shape[0]
            Nc = X.shape[1]
            info = dict(Nrows=N, Nfeat=Nc)
            for k, v in dd.items():
                if k not in skip:
                    info[k] = v
            self.fLOG(
                "[MlGridBenchmark.init] dataset {0}: {1}".format(i, info))
            self._datasets_info.append(info)

        self.fLOG("[MlGridBenchmark.init] end")

    def init(self):
        """
        Skips it.
        """
        pass  # pragma: no cover

    def run(self, params_list):
        """
        Runs the benchmark.
        """
        self.init_main()
        self.fLOG("[MlGridBenchmark.bench] start")
        self.fLOG("[MlGridBenchmark.bench] number of datasets",
                  len(self._datasets))
        self.fLOG("[MlGridBenchmark.bench] number of experiments",
                  len(params_list))

        unique = set()
        for i, pars in enumerate(params_list):
            if "name" not in pars:
                raise KeyError(  # pragma: no cover
                    "Dictionary {0} must contain key 'name'.".format(i))
            if "shortname" not in pars:
                raise KeyError(  # pragma: no cover
                    "Dictionary {0} must contain key 'shortname'.".format(i))
            if pars["name"] in unique:
                raise ValueError(  # pragma: no cover
                    "'{0}' is duplicated.".format(pars["name"]))
            unique.add(pars["name"])
            if pars["shortname"] in unique:
                raise ValueError(  # pragma: no cover
                    "'{0}' is duplicated.".format(pars["shortname"]))
            unique.add(pars["shortname"])

        # Multiplies the experiments.
        full_list = []
        for i in range(len(self._datasets)):
            for pars in params_list:
                pc = pars.copy()
                pc["di"] = i
                full_list.append(pc)

        # Runs the bench
        res = BenchMark.run(self, full_list)

        self.fLOG("[MlGridBenchmark.bench] end")
        return res

    def bench(self, **params):
        """
        run an experiment multiple times,
        parameter *di* is the dataset to use
        """
        if "di" not in params:
            raise KeyError(
                "key 'di' is missing from params")  # pragma: no cover
        results = []

        for iexp in range(self._repetition):

            di = params["di"]
            shortname_model = params["shortname"]
            name_model = params["name"]
            shortname_ds = self._datasets[di]["shortname"]
            name_ds = self._datasets[di]["name"]

            cl = perf_counter()
            ds, appe, pars = self.preprocess_dataset(di, **params)
            split = perf_counter() - cl

            cl = perf_counter()
            output = self.bench_experiment(ds, **pars)
            train = perf_counter() - cl

            cl = perf_counter()
            metrics, appe_ = self.predict_score_experiment(ds, output)
            test = perf_counter() - cl

            metrics["time_preproc"] = split
            metrics["time_train"] = train
            metrics["time_test"] = test
            metrics["_btry"] = "{0}-{1}".format(shortname_model, shortname_ds)
            metrics["_iexp"] = iexp
            metrics["model_name"] = name_model
            metrics["ds_name"] = name_ds
            appe.update(appe_)
            appe["_iexp"] = iexp
            metrics.update(appe)

            appe["_btry"] = metrics["_btry"]
            if "_i" in metrics:
                del metrics["_i"]
            results.append((metrics, appe))

        return results

    def preprocess_dataset(self, dsi, **params):
        """
        split the dataset into train and test

        @param      dsi         dataset index
        @param      params      additional parameters
        @return                 list of (dataset (like info), dictionary for metrics, parameters)
        """
        ds = self._datasets[dsi]
        appe = self._datasets_info[dsi].copy()
        params = params.copy()
        if "di" in params:
            del params["di"]
        return ds, appe, params

    def bench_experiment(self, info, **params):
        """
        function to overload

        @param      info        dictionary with at least key ``'X'``
        @param      params      additional parameters
        @return                 output of the experiment
        """
        raise NotImplementedError()  # pragma: no cover

    def predict_score_experiment(self, info, output, **params):
        """
        function to overload

        @param      info        dictionary with at least key ``'X'``
        @param      output      output of the benchmar
        @param      params      additional parameters
        @return                 output of the experiment, tuple of dictionaries
        """
        raise NotImplementedError()  # pragma: no cover
