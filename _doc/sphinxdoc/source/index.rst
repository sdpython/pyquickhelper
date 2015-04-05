.. project_name documentation documentation master file, created by
   sphinx-quickstart on Fri May 10 18:35:14 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyquickhelper documentation
===========================


.. image:: https://travis-ci.org/sdpython/pyquickhelper.svg?branch=master
    :target: https://travis-ci.org/sdpython/pyquickhelper
    :alt: Build status
    
.. image:: https://badge.fury.io/py/pyquickhelper.svg
    :target: http://badge.fury.io/py/pyquickhelper
    
.. image:: http://img.shields.io/pypi/dm/pyquickhelper.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/pyquickhelper



**Links:** `pypi <https://pypi.python.org/pypi/pyquickhelper/>`_, 
`github <https://github.com/sdpython/pyquickhelper>`_,
`documentation <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html>`_, 
`wheel <http://www.xavierdupre.fr/site2013/index_code.html#pyquickhelper>`_,
`travis <https://travis-ci.org/sdpython/pyquickhelper>`_,
:ref:`blog <ap-main-0>`

Functionalities
---------------

    * simple forms in notebooks (see :func:`open_html_form <pyquickhelper.ipythonhelper.html_forms.open_html_form>`)
    * help generation including notebook conversion (see :func:`generate_help_sphinx <pyquickhelper.helpgen.sphinx_main.generate_help_sphinx>`)
    * folder synchronization (see :func:`pyquickhelper.synchronize_folder <pyquickhelper.filehelper.synchelper.synchronize_folder>`)
    * logging (see :func:`fLOG <pyquickhelper.loghelper.flog.fLOG>`)
    * help running unit tests (see :func:`main <pyquickhelper.unittests.utils_tests.main>`)
    * simple server to server sphinx documentation (see :func:`run_doc_server <pyquickhelper.serverdoc.documentation_server.run_doc_server>`)
    * function to create and delete jobs on `Jenkins <https://jenkins-ci.org/>`_, see :class:`JenkinsExt <pyquickhelper.jenkinshelper.jenkins_server.JenkinsExt>`
    * :class:`MagicCommandParser <pyquickhelper.ipythonhelper.magic_parser.MagicCommandParser>`, 
      :class:`MagicClassWithHelpers <pyquickhelper.ipythonhelper.magic_class.MagicClassWithHelpers>` to help 
      creating magic command for IPython notebooks,
      the parser tries to interpret values passed to the magic commands
    * function :func:`rst2html <pyquickhelper.helpgen.convert_doc_helper.rst2html>` to convert RST into HTML
    * Sphinx directive :class:`BlogPostDirective <pyquickhelper.helpgen.sphinx_blog_extension.BlogPostDirective>` 
      to add a drective ``blogpost`` into the docutmention
    
Navigation
----------

The most simple way is with *pip*: ``pip install pyquickhelper``. 
Others options are described at: :ref:`l-moreinstall`.
    

+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`l-modules`     |  :ref:`l-functions` | :ref:`l-classes`    | :ref:`l-methods`   | :ref:`l-staticmethods` | :ref:`l-properties`                            |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`modindex`      |  :ref:`l-example`   | :ref:`search`       | :ref:`l-license`   | :ref:`l-changes`       | :ref:`l-README`                                |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`genindex`      |  :ref:`l-FAQ`       | :ref:`l-notebooks`  |                    | :ref:`l-statcode`      | `Unit Test Coverage <coverage/index.html>`_    |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+


.. toctree::
    :maxdepth: 2

    indexmenu
