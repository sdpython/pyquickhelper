
.. blogpost::
    :title: Slow imports and code to investigate
    :keywords: import, speed
    :date: 2019-03-10
    :categories: import

    I notice that the following code was very slow:

    ::

        import pyquickhelper.__main__ as m
        m.main(['clean_files', '--help'])

    I wrote the following code to detect which import was
    the reason behind in order to delay this import
    wherever possible. I found two. The first is ``pip``
    which I could easily delay. The second one
    was surprinsigly ``sphinxcontrib.websupport``
    which takes 75% of the import time. The code
    relies on the fact that :epkg:`Python`
    does not import twice the same package.

    .. runpython::
        :showcode:
        :process:

        def f1():
            from sphinxcontrib.websupport.utils import is_commentable

        def f2():
            from sphinx.application import Sphinx

        def myf():
            import pyquickhelper.__main__ as m
            m.main(['clean_files', '--help'])

        import cProfile
        import re
        import cProfile, pstats, io
        from pstats import SortKey
        pr = cProfile.Profile()
        pr.enable()

        f1()
        f2()
        myf()

        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
