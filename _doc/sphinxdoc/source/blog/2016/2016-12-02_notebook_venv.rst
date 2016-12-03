

.. blogpost::
    :title: Open the notebook from a virtual environment
    :keywords: jupyter, virtual environment
    :date: 2016-12-02
    :categories: notebook
    
    On Windows, I did not check on Linux,
    the short cut ``jupyter-notebook.exe`` is not present
    in the virtual environment. Here is a simple python 
    program to launch the notebook server from
    the virtual environement.
    
    ::
    
        import os
        import sys
        ndir = os.path.abspath(os.path.join(os.path.dirname(__file__), "folder_for_notebooks"))
        sys.argv = [sys.argv[0], "--notebook-dir=%s" % ndir]
        from notebook import notebookapp as app
        app.launch_new_instance()
        
    And then::
    
        python -u your_launch.py
    