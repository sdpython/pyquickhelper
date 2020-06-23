
class Estimator:
    """
    Dummy estimator.

    :param lr: learning rate
    :param alph: gradient coefficient
    """

    def __init__(self, lr=0.1, alpha=0.2, beta=0.3):
        self.lr = lr
        self.alpha = alpha
        self.beta = beta


class Estimator2:
    """
    Dummy estimator.

    :param beta: doc beta
    """

    def __init__(self, lr=0.1, alpha=0.2, beta=0.3):
        """
        constructor

        :param lr: learning rate
        :param alp: misspelled
        """
        self.lr = lr
        self.alpha = alpha
        self.beta = beta


class Estimator3:
    """
    Ordinary least squares Linear Regression.
    LinearRegression fits a linear model with coefficients w = (w1, ..., wp)
    to minimize the residual sum of squares between the observed targets in
    the dataset, and the targets predicted by the linear approximation.

    Parameters
    ----------
    fit_intercep : bool, default=True
        Whether to calculate the intercept for this model. If set
        to False, no intercept will be used in calculations
        (i.e. data is expected to be centered).
    normalize : bool, default=False
        This parameter is ignored when ``fit_intercept`` is set to False.
        If True, the regressors X will be normalized before regression by
        subtracting the mean and dividing by the l2-norm.
        If you wish to standardize, please use
        :class:`sklearn.preprocessing.StandardScaler` before calling ``fit`` on
        an estimator with ``normalize=False``.
    copy_X : bool, default=True
        If True, X will be copied; else, it may be overwritten.
    n_jobs : int, default=None
        The number of jobs to use for the computation. This will only provide
        speedup for n_targets > 1 and sufficient large problems.
        ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
        ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
        for more details.

    Attributes
    ----------

    coef_ : array of shape (n_features, ) or (n_targets, n_features)
        Estimated coefficients for the linear regression problem.
        If multiple targets are passed during the fit (y 2D), this
        is a 2D array of shape (n_targets, n_features), while if only
        one target is passed, this is a 1D array of length n_features.
    rank_ : int
        Rank of matrix `X`. Only available when `X` is dense.
    singular_ : array of shape (min(X, y),)
        Singular values of `X`. Only available when `X` is dense.
    intercept_ : float or array of shape (n_targets,)
        Independent term in the linear model. Set to 0.0 if
        `fit_intercept = False`.
    """

    def __init__(self, fit_intercept=True, normalize=False, copy_X=True, n_jobs=None):
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.copy_X = copy_X
        self.n_jobs = n_jobs
