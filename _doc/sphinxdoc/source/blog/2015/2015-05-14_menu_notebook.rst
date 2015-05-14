

.. blogpost::
    :title: Add a custom menu to the notebook
    :keywords: script, menu
    :date: 2015-05-14
    :categories: notebook, automation
    
    The function :func:`add_notebook_menu <pyquickhelper.ipythonhelper.helper_in_notebook.add_notebook_menu>`
    add HTML and Javascript to the notebook to create links to all sections in 
    the notebook::
    
        from pyquickhelper.ipythonhelper import add_notebook_menu
        add_notebook_menu(menu_id="main_menu")    
        
    You can see what it looks like in notebook
    :ref:`exempleoffixmenurst`.
    The trick consists in running::
    
        from pyquickhelper.ipythonhelper import add_notebook_menu
        add_notebook_menu(format="rst")
        
    The menu can be then copy pasted into a text cell.
    It won't be refreshed anymore but it will be converted 
    as part of the notebook into RST, HTML or slides format.
    