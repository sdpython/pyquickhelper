"""
Small configuration to test sphinx.
"""
extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'pyquickhelper_unittest'
copyright = 'none'
version = '0.1'
exclude_patterns = []
pygments_style = 'sphinx'
html_theme = 'classic'
html_static_path = ['_static']
latex_documents = [
    ('index', 'pyq-video.tex', 'pyq-video Documentation', 'any', 'manual')]
man_pages = [('index', 'pyq-video', 'pyq-video Documentation', ['any'], 1)]
texinfo_documents = [('index', 'pyq-video', 'pyq-video Documentation',
                      'any', 'pyq-video', 'description', '...')]
preamble = '''
\\usepackage{movie15}
'''
latex_elements = {'papersize': 'a4', 'pointsize': '10pt',
                  'preamble': preamble,
                  }
