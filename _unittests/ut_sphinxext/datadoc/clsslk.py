
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
