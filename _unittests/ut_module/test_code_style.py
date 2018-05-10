"""
@brief      test log(time=284s)
"""

import sys
import os
import unittest
import warnings


try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import check_pep8


class TestCodeStyle(unittest.TestCase):

    def test_style_src(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2 or "Anaconda" in sys.executable \
                or "condavir" in sys.executable:
            warnings.warn(
                "skipping test_code_style because of Python 2 or " + sys.executable)
            return

        thi = os.path.abspath(os.path.dirname(__file__))
        src_ = os.path.normpath(os.path.join(thi, "..", "..", "src"))
        check_pep8(src_, fLOG=fLOG,
                   pylint_ignore=('C0103', 'C1801', 'R0201', 'R1705', 'W0108', 'W0613',
                                  'W0201', 'W0212', 'W0603', 'W0622',
                                  'W0511', 'C0412', 'R1702', 'E0702',
                                  'W0640', 'C0111', 'R0914', 'C0302',
                                  'W0703', 'C0325', 'R1703', 'R0915',
                                  'R0912', 'W0123', 'R0913', 'R0912',
                                  'R0911', 'R0916', 'C0200', 'W0223',
                                  'W0122', 'E1003'),
                   skip=["ftp_transfer_files.py:374: [E731]",
                         "_nbconvert_config.py:",
                         "convert_doc_sphinx_helper.py:31: [E402]",
                         "magic_class.py:12: [E402]",
                         "windows_scripts.py:724",
                         "sphinxm_convert_doc_sphinx_helper.py:1425: [E901]",
                         "Redefining built-in 'open'",
                         "Redefining built-in 'StringIO'",
                         "Redefining built-in 'FileNotFoundError'",
                         "Redefining built-in 'format'",
                         "benchmark.py:241",
                         "encryption_cli.py:13",
                         "encryption_cli.py:56",
                         "Redefining built-in 'ConnectionResetError'",
                         "Unable to import 'urllib2'",
                         "Unable to import 'httplib'",
                         "Unable to import 'urlparse'",
                         "Unable to import 'StringIO'",
                         #
                         "bokeh_plot.py",
                         "sphinx_rst_builder.py",
                         "Unused variable 'bokeh'",
                         "Unused variable 'plt'",
                         "Unused variable 'toctitle'",
                         "sphinx_template_extension.py:121: W0123: Use of eval",
                         "sphinx_runpython_extension.py:99",
                         "sphinx_runpython_extension.py:106",
                         "sphinx_runpython_extension.py:107",
                         "sphinx_runpython_extension.py:154",
                         "sphinx_runpython_extension.py:190",
                         "sphinx_runpython_extension.py:189",
                         "sphinx_runpython_extension.py:519",
                         "download_helper.py:95",
                         "download_helper.py:105",
                         "file_tree_node.py:384",
                         "ftp_transfer.py",
                         "ftp_transfer_mock.py:19",
                         "Redefining name 'fLOG' from outer scope",
                         "default_conf.py",
                         "Instance of '_MemoryBuilder' has no ",
                         "sphinx_runpython_extension.py:159",
                         "sphinx_postcontents_extension.py174",
                         "Use % formatting in logging functions",
                         "Class 'BlogPostListDirective' has no 'blogpostlist' member",
                         "sphinx_autosignature.py:78",
                         "import_object_helper.py:50",
                         "Instance of 'BlogPost' has no '",
                         'blog_post.py:121',
                         "server_helper.py:31",
                         "Module 'sys' has no 'real_prefix'",
                         "Unable to import 'src.pyquickhelper.pycode.get_pip'",
                         "utils_tests_private.py:321",
                         "unittestclass.py",
                         "clean_helper.py:11",
                         "Redefining name 'rss_update_run_server' from outer scope",
                         "Unable to import 'pysvn'",
                         "pygit_helper.py:782",
                         "internet_helper.py:107",
                         "synchelper.py:428",
                         "synchelper.py:429",
                         "winzipfile.py:73",
                         "process_notebooks.py:817",
                         "Instance of '_AdditionalVisitDepart' has no '",
                         "Instance of '_WriterWithCustomDirectives' has no ",
                         "_nbconvert_preprocessor.py:14",
                         "js_helper.py:186",
                         "No name 'brown' in module 'sphinx.util.console'",
                         "Redefining argument with the local name 'dir'",
                         "pysvn_helper.py:53",
                         "pygit_helper.py:74",
                         "pypi_helper.py:8",
                         "No name 'svg2png' in module 'cairosvg'",
                         "process_notebooks.py:1099",
                         "sphinxm_convert_doc_helper.py:325: W0612",
                         "sphinxm_convert_doc_helper.py:395: R1710",
                         "No name 'bold' in module 'sphinx.util.console'",
                         "No name 'darkgreen' in module 'sphinx.util.console'",
                         "Redefining name 'HTMLTranslator' from outer scope",
                         "Redefining name 'LaTeXTranslator' from outer scope",
                         "Unused variable 'sphinx.builders.latex.transforms'",
                         "Class 'Theme' has no 'themes' member",
                         "sphinxm_mock_app.py:110: R1706",
                         "sphinxm_mock_app.py:334: E1101",
                         "Instance of 'MockSphinxApp' has no '_added_objects' member",
                         "sphinxm_mock_app.py:384: E0211",
                         "sphinx_main.py:458: E1111",
                         "sphinx_main.py:758: R1704",
                         "utils_sphinx_doc.py:1071: R1704",
                         "utils_sphinx_doc.py:1771: C0112",
                         "utils_sphinx_doc_helpers.py:779: W0102",
                         "utils_sphinx_doc_helpers.py:912: W0631",
                         "sphinx_postcontents_extension.py:159: W0612",
                         "sphinx_postcontents_extension.py:174: W1302",
                         "sphinx_bigger_extension.py:78: W1505",
                         "import_object_helper.py:20: W0211",
                         "gitlab_helper.py:88",
                         "history_helper.py:256: R1710",
                         "jenkins_server.py:193: W0221",
                         "jenkins_server.py:170: E1101",
                         "jenkins_helper.py:58: W0102",
                         "magic_parser.py:166: C0123",
                         "magic_parser.py:168: C0123",
                         "js_helper.py:55: W0102",
                         "js_helper.py:43: W0621",
                         "sphinxm_convert_doc_sphinx_helper.py:604: W0231",
                         "sphinxm_convert_doc_sphinx_helper.py:634: W0231",
                         "sphinxm_convert_doc_sphinx_helper.py:845: W0231",
                         "sphinxm_convert_doc_sphinx_helper.py:873: W0231",
                         "sphinxm_convert_doc_sphinx_helper.py:940: W0231",
                         "sphinxm_convert_doc_sphinx_helper.py:1326",
                         "sphinxm_convert_doc_sphinx_helper.py:1348: W0221",
                         "Unused import sphinx.builders.latex.transforms",
                         "utils_sphinx_doc.py:126: W0621",
                         "utils_sphinx_doc.py:279: W0621",
                         "utils_sphinx_doc.py:685: W0102",
                         "utils_sphinx_doc.py:908: W0621",
                         "_my_doxypy.py:373: W0612",
                         "_my_doxypy.py:571: W0621",
                         "__init__.py:1: R0401",
                         ])

    def test_style_test(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2 or "Anaconda" in sys.executable \
                or "condavir" in sys.executable:
            warnings.warn(
                "skipping test_code_style because of Python 2 or " + sys.executable)
            return

        thi = os.path.abspath(os.path.dirname(__file__))
        test = os.path.normpath(os.path.join(thi, "..", ))
        check_pep8(test, fLOG=fLOG, neg_filter="temp_.*",
                   max_line_length=200,
                   pylint_ignore=('C0111', 'C0103', 'R0914', 'W0212', 'C0413', 'W0621',
                                  'W0703', 'W0622', 'W0122', 'R0912', 'R0201',
                                  'W0613', 'C0123', 'W0640', 'E0202', 'C0412',
                                  'R1702', 'W0612', 'C0411', 'E1101', 'C0122',
                                  'W0201', 'E0702', 'W1503', 'C0102', 'W0223',
                                  'W0611', 'R1705', 'W0631', 'W0102'),
                   skip=["src' imported but unused",
                         "skip_' imported but unused",
                         "skip__' imported but unused",
                         "skip___' imported but unused",
                         "2test_download_pip.py",
                         "[E402] module ",
                         "Unused import src",
                         "Unused variable 'skip_",
                         "imported as skip_",
                         "Unable to import 'StringIO'",
                         "Redefining built-in 'open'",
                         "Do not use `len(SEQUENCE)`",
                         "test_file_tree_node.py:43: W0613: Unused argument 'root'",
                         "Unused variable 'fig'",
                         "ut_sphinxext\\data",
                         "ut_helpgen\\data",
                         "ut_sphinxext/data",
                         "ut_helpgen/data",
                         "Unused argument 'node'",
                         "Redefining built-in 'FileNotFoundError'",
                         "test_check_pep8_sample.py:39",
                         ])


if __name__ == "__main__":
    unittest.main()
