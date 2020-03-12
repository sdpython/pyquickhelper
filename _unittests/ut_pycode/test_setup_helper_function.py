"""
@brief      test tree node (time=1s)
"""
import unittest
from textwrap import dedent

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pycode.setup_helper import modifies_init_file


class TestSetupHelperFunction(ExtTestCase):

    def test_modifies_init_file(self):
        init = dedent('''
            # f
            __version__ = "1.2.4"
            ''')
        v = modifies_init_file(init, '65')
        self.assertIn('__version__ = "1.2.65"', v)

        init = dedent('''
            # f
            __version__ = '1.2.4'
            ''')
        v = modifies_init_file(init, '65')
        self.assertIn("__version__ = '1.2.65'", v)

        init = dedent('''
            # f
            __version__ = '1'
            ''')
        v = modifies_init_file(init, '65')
        self.assertIn("__version__ = '1.65'", v)

        init = dedent('''
            # f
            __version__ = '1.2.3.4'
            ''')
        v = modifies_init_file(init, '65')
        self.assertIn("__version__ = '1.2.3.65'", v)

        init = dedent('''
            # f
            __versifon__ = '1.2.3.4'
            ''')
        self.assertRaise(lambda: modifies_init_file(init, '65'), ValueError)


if __name__ == "__main__":
    unittest.main()
