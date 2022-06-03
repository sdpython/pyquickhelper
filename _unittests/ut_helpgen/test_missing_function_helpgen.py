"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
from pyquickhelper.pycode import ExtTestCase, skipif_vless, skipif_azure, skipif_appveyor
from pyquickhelper.helpgen.utils_sphinx_config import NbImage
from pyquickhelper.helpgen.post_process import remove_character_under32
from pyquickhelper.helpgen.utils_sphinx_doc import useless_class_UnicodeStringIOThreadSafe, doc_checking
from pyquickhelper.helpgen.default_conf import get_default_stylesheet, get_default_javascript, custom_setup
from pyquickhelper.helpgen.utils_sphinx_doc_helpers import example_function_latex
from pyquickhelper.helpgen._fake_function_to_documentation import f1, f2, f3, f4, f5, f6
from pyquickhelper.helpgen.sphinx_main import _import_conf_extract_parameter
from pyquickhelper.helpgen.sphinx_helper import everything_but_python
from pyquickhelper.helpgen.rst_converters import correct_indentation
from pyquickhelper.helpgen.sphinxm_mock_app import MockSphinxApp
from pyquickhelper.helpgen.utils_sphinx_config import _NbImage, getsitepackages
from pyquickhelper.helpgen.sphinx_main_verification import SphinxVerificationException
from pyquickhelper.helpgen.helpgen_exceptions import HelpGenException


class TestMissingFunctionsHelpgen(ExtTestCase):

    def test_nb_image(self):
        r = NbImage("completion.png")
        self.assertTrue(r is not None)
        self.assertRaise(lambda: NbImage("_completion.png"), FileNotFoundError)
        self.assertRaise(lambda: _NbImage("_completion.png"), FileNotFoundError)
        r = _NbImage("completion.png")
        self.assertTrue(r is not None)

    def test_remove_character_under32(self):
        s = "a\na\r"
        s2 = remove_character_under32(s)
        self.assertEqual(s2, 'a a ')

    def test_utils_sphinx_doc(self):
        useless_class_UnicodeStringIOThreadSafe()
        doc_checking()

    def test_default_conf(self):
        self.assertNotEmpty(get_default_stylesheet())
        self.assertNotEmpty(get_default_javascript())
        app = MockSphinxApp.create()[0]
        res = custom_setup(app, "x")
        self.assertNotEmpty(res)

    def test_example_function_latex(self):
        example_function_latex()

    def test_fake(self):
        f1(3, 4)
        f2(3, 4)
        f3(3, 4)
        f4(3, 4)
        f5(3, 4)
        f6(3, 4)

    @skipif_vless((3, 6), "AttributeError: 'PosixPath' object has no attribute 'rfind'")
    @skipif_vless((3, 7), "TypeError: __new__() missing 2 required positional")
    @skipif_azure("ModuleNotFoundError: No module named 'pyquickhelper'")
    @skipif_appveyor("missing miktex")
    def test_sphinx_main(self):
        all_tocs, build_paths, parameters, html_static_paths = [], [], [], []
        root = os.path.join(os.path.dirname(__file__), '..',
                            '..', '_doc', 'sphinxdoc', 'source')
        root = os.path.normpath(os.path.abspath(root))
        self.assertExists(root)
        folds = root
        root = os.path.join(folds, '..', '..', '..')
        root_source = os.path.join(folds, '..', 'source')
        build = os.path.join(folds, '..', 'build')
        _import_conf_extract_parameter(root, root_source, folds, build, "",
                                       all_tocs, build_paths, parameters,
                                       html_static_paths, None)
        self.assertNotEmpty(all_tocs)
        self.assertNotEmpty(build_paths)
        self.assertNotEmpty(parameters)
        self.assertNotEmpty(html_static_paths)
        self.assertNotIn('conf', sys.modules)

    def test_everything_but_python(self):
        self.assertFalse(everything_but_python('__pycache__/u.py'))
        self.assertFalse(everything_but_python('u.pyc'))
        self.assertFalse(everything_but_python('u.py'))
        self.assertTrue(everything_but_python('u.pfy'))

    def test_correct_indentation(self):
        text = """
            Comment
            =======

                cool
        """
        new_text = correct_indentation(text)
        ded = text.replace("            ", "")
        self.assertEqual(ded.strip(" \n\r"), new_text.strip(" \n\r"))

    def test_getsitepackages(self):
        res = getsitepackages()
        self.assertIsInstance(res, list)

    def test_SphinxVerificationException(self):
        exc = SphinxVerificationException([])
        self.assertNotEmpty(exc)
        exc = HelpGenException('msg')
        self.assertNotEmpty(exc)


if __name__ == "__main__":
    unittest.main()
