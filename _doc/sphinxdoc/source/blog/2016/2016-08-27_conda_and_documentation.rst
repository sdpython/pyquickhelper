
.. blogpost::
    :title: Generate the documentation on Anaconda
    :keywords: documentation, Anaconda
    :date: 2016-08-27
    :categories: documentation

    On Anaconda, the documentation generation fails for
    two reasons. The first one is the current version of *Sphinx* *(1.4.1)*
    and *pyquickhelper* requires *>= 1.4.5*. After fixing it
    with *pip*, the following exception happens (only on Anaconda)
    on a virtual environment:

    ::

          File ".....\pyquickhelper_UT_35_conda\_venv\lib\site-packages\sphinx\ext\imgmath.py", line 244, in html_visit_displaymath
            self.builder.config.math_number_all)
          File ".....\pyquickhelper_UT_35_conda\_venv\lib\site-packages\sphinx\config.py", line 368, in __getattr__
            raise AttributeError('No such config value: %s' % name)
        AttributeError: No such config value: math_number_all

    This variable ``math_number_all`` is set up but the error still happens.
    In that case, you can just fix the original file
    ``site-packages\sphinx\ext\imgmath.py``:

    ::

        v = self.builder.config.math_number_all if hasattr(self.builder.config, 'math_number_all') else False
        latex = wrap_displaymath(node['latex'], None, v)
