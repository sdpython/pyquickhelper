

.. blogpost::
    :title: Sphinx extensions
    :keywords: sphinx, extensions
    :date: 2015-12-12
    :categories: sphinx

    The following repository 
    `birkenfeld/sphinx-contrib/ <https://bitbucket.org/birkenfeld/sphinx-contrib/src/284d5b04263c07857bbc3cf743136f9cfba0f170?at=default>`_
    contains many useful extensions
    to improve the rendering of 
    `Sphinx <http://sphinx-doc.org/>`_ documentation:
    
    * `imagesvg <https://pypi.python.org/pypi/sphinxcontrib-imagesvg/>`_: to include svg figures
    * `jsdemo <https://pypi.python.org/pypi/sphinxcontrib-imagesvg/>`_: to demo javascript and HTML
    
    .. demo::

       <button>Click me!</button>   
       
    The following extension replaces the search bar by an entry which 
    mimicks autocompletion by showing results as the user is typing:
    
    * `lunrsearch <https://github.com/rmcgibbo/sphinxcontrib-lunrsearch>`_
    
    Their are now part of the default configuration
    proposed by this module. See :ref:`set_sphinx_variables <pyquickhelper.helpgen.default_conf.set_sphinx_variables>`.
    
       