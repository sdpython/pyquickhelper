"""
@file
@brief Check code style.

.. versionadded:: 1.8
"""
import os
from .utils_tests_helper import check_pep8


def _run_cmd_filter(name):
    if "yaml_helper_yaml.py" in name:
        return True
    if "test_yaml.py" in name:
        return True
    return False


def _private_test_style_src(fLOG, run_lint, verbose=False, pattern=".*[.]py$"):
    thi = os.path.abspath(os.path.dirname(__file__))
    src_ = os.path.normpath(os.path.join(thi, "..", ".."))
    check_pep8(src_, fLOG=fLOG, run_lint=run_lint, verbose=verbose, pattern=pattern,
               run_cmd_filter=_run_cmd_filter,
               pylint_ignore=('C0103', 'C1801', 'R0201', 'R1705', 'W0108', 'W0613',
                              'W0201', 'W0212', 'W0603', 'W0622',
                              'W0511', 'C0412', 'R1702', 'E0702',
                              'W0640', 'C0111', 'R0914', 'C0302',
                              'W0703', 'C0325', 'R1703', 'R0915',
                              'R0912', 'W0123', 'R0913', 'R0912',
                              'R0911', 'R0916', 'C0200', 'W0223',
                              'W0122', 'E1003', 'R0205', 'E0001',
                              'W0143', 'W0107', 'C0415', 'W1202',
                              'W0707', 'R1725'),
               skip=["windows_scripts.py",
                     "Redefining built-in 'format'",
                     "bokeh_plot.py",
                     "sphinx_md_builder.py",
                     "sphinx_rst_builder.py",
                     "Unused variable 'bokeh'",
                     "Unused variable 'plt'",
                     "Unused variable 'toctitle'",
                     "ftp_transfer.py",
                     "Redefining name 'fLOG' from outer scope",
                     "Instance of '_MemoryBuilder' has no ",
                     "Use % formatting in logging functions",
                     "Class 'BlogPostListDirective' has no 'blogpostlist' member",
                     "Instance of 'BlogPost' has no '",
                     "Unable to import 'pyquickhelper.pycode.get_pip'",
                     "Redefining name 'rss_update_run_server' from outer scope",
                     "Unable to import 'pysvn'",
                     "Instance of '_AdditionalVisitDepart' has no '",
                     "Instance of '_WriterWithCustomDirectives' has no ",
                     "No name 'brown' in module 'sphinx.util.console'",
                     "Redefining argument with the local name 'dir'",
                     "No name 'svg2png' in module 'cairosvg'",
                     "No name 'bold' in module 'sphinx.util.console'",
                     "No name 'darkgreen' in module 'sphinx.util.console'",
                     "Redefining name 'HTMLTranslator' from outer scope",
                     "Redefining name 'LaTeXTranslator' from outer scope",
                     "Unused variable 'sphinx.builders.latex.transforms'",
                     "Class 'Theme' has no 'themes' member",
                     "Instance of 'MockSphinxApp' has no '_added_objects' member",
                     "Unused import sphinx.builders.latex.transforms",
                     "Unable to import 'pyquickhelper.helpgen.sphinxm_mock_app'",
                     "No name 'sphinxm_mock_app' in module 'pyquickhelper.helpgen'",
                     "W0641: Possibly unused variable",
                     "[E731] do not assign a lambda expression, use a def",
                     "cli_helper.py:196",
                     "magic_parser.py:154: C0123: Using type() instead of isinstance()",
                     "sphinxm_convert_doc_sphinx_helper.py:1595: [E128]",
                     ])


def _private_test_style_test(fLOG, run_lint, verbose=False, pattern=".*[.]py$"):
    thi = os.path.abspath(os.path.dirname(__file__))
    test_ = os.path.normpath(os.path.join(thi, "..", "..", '..', '_unittests'))
    check_pep8(test_, fLOG=fLOG, neg_pattern="((temp[0-9]?_.*)|(.*((_venv)|(sphinxdoc)|([.]git)|(__pycache__)).*))",
               pattern=pattern, max_line_length=200, run_lint=run_lint, verbose=verbose,
               run_cmd_filter=_run_cmd_filter,
               pylint_ignore=('C0111', 'C0103', 'R0914', 'W0212', 'C0413', 'W0621',
                              'W0703', 'W0622', 'W0122', 'R0912', 'R0201',
                              'W0613', 'C0123', 'W0640', 'E0202', 'C0412',
                              'R1702', 'W0612', 'C0411', 'E1101', 'C0122',
                              'W0201', 'E0702', 'W1503', 'C0102', 'W0223',
                              'W0611', 'R1705', 'W0631', 'W0102', 'R0205',
                              'W0107', 'C0415', 'W1202', 'W0707', 'R1725'),
               skip=["skip_' imported but unused",
                     "skip__' imported but unused",
                     "skip___' imported but unused",
                     "2test_download_pip.py",
                     "[E402] module ",
                     "Unused variable 'skip_",
                     "imported as skip_",
                     "Unable to import 'StringIO'",
                     "Redefining built-in 'open'",
                     "Do not use `len(SEQUENCE)`",
                     "Unused variable 'fig'",
                     "ut_sphinxext\\data",
                     "ut_helpgen\\data",
                     "ut_sphinxext/data",
                     "ut_helpgen/data",
                     "Unused argument 'node'",
                     "Redefining built-in 'FileNotFoundError'",
                     "Unable to import 'pyquickhelper",
                     "Unable to import 'jyquickhelper",
                     "Unable to import 'exsig'",
                     "Unable to import 'pyquickhelper.helpgen.sphinxm_mock_app'",
                     "Unable to import 'pyquickhelper.jenkinshelper",
                     "Unable to import 'pyquickhelper",
                     "No name 'sphinxm_mock_app' in module 'pyquickhelper.helpgen'",
                     "test_yaml.py:333: [E501]",
                     "test_yaml.py:337: [E501]",
                     "test_yaml.py:339: [E501]",
                     "test_yaml.py:345: [E501]",
                     "test_yaml.py:347: [E501]",
                     "test_yaml.py:341: [E501]",
                     "test_yaml.py:343: [E501]",
                     ])
