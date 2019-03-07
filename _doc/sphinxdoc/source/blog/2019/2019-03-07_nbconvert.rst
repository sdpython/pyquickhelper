
.. blogpost::
    :title: nbconvert, tornado, incompatibilities
    :keywords: nbconvert, tornado
    :date: 2019-03-07
    :categories: module

    !epkg:`tornado` was recently released in version 6.0.
    It introduced an incompabilities with all existing versions
    of :epkg:`nbconvert` (<= 0.4.1).

    ::

        AttributeError: module 'tornado.web' has no attribute 'asynchronous'

    Beside, :epkg:`nbconvert` still does not include the following
    `PR 910 <https://github.com/jupyter/nbconvert/pull/910>`_
    which handles a fix to handle :epkg:`svg` figures in latex
    export. That's why I forked the project and created a branch
    where both issues are fixed:
    `sdpython/nbconvert <https://github.com/sdpython/nbconvert>`_.
    To install it:

    ::

        pip install git+https://github.com/sdpython/nbconvert.git
