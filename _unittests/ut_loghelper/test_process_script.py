"""
@brief      test log(time=2s)
"""
import sys
import unittest
import textwrap

from pyquickhelper.pycode import ExtTestCase, get_temp_folder, skipif_appveyor
from pyquickhelper.loghelper.process_script import execute_script, execute_script_get_local_variables
from pyquickhelper.loghelper.process_script import dictionary_as_class


class TestRunScript(ExtTestCase):

    @skipif_appveyor("job stuck")
    def test_run_script(self):
        code = textwrap.dedent("""
            import os
            res = dict(a = os.getcwd())
        """)
        exe = execute_script(code)
        self.assertIsInstance(exe, dict)
        self.assertIn('res', exe)

    @skipif_appveyor("job stuck")
    def test_run_script_error(self):
        code = textwrap.dedent("""
            import os
            res = dict('a' = os.getcwd())
        """)
        exe = execute_script(code)
        self.assertIsInstance(exe, dict)
        self.assertIn('ERROR', exe)

    @skipif_appveyor("job stuck")
    def test_run_script_error2(self):
        code = textwrap.dedent("""
            import os
            res = dict(a = os.getcwd() + 3)
        """)
        exe = execute_script(code)
        self.assertIsInstance(exe, dict)
        self.assertIn('ERROR', exe)

    @skipif_appveyor("job stuck")
    def test_run_script_process(self):
        code = textwrap.dedent("""
            import os
            res = dict(a = os.getcwd())
        """)
        exe = execute_script_get_local_variables(code)
        self.assertIsInstance(exe, dict)
        self.assertIn('res', exe)

    @skipif_appveyor("job stuck")
    def test_run_script_process_check(self):
        code = textwrap.dedent("""
            import os
            res = dict(a = os.getcwd())
            import sys
            sys.path.append("-azerty-")
        """)
        exe = execute_script_get_local_variables(code)
        self.assertIsInstance(exe, dict)
        self.assertIn('res', exe)
        self.assertNotIn("-azerty-", sys.path)
        du = dictionary_as_class(exe)

    def test_dummy_class(self):
        cl = dictionary_as_class(dict(d1="e", r=4))
        st = str(cl)
        self.assertEqual(st, "{'d1': 'e', 'r': 4}")

    def test_dummy_class_drop(self):
        cl = dictionary_as_class(dict(d1="e", r=4))
        st = str(cl)
        self.assertEqual(st, "{'d1': 'e', 'r': 4}")
        cl = cl.drop("d1")
        st = str(cl)
        self.assertEqual(st, "{'r': 4}")

    @skipif_appveyor("job stuck")
    def test_run_script_popen(self):
        temp = get_temp_folder(__file__, "temp_run_script_popen")
        code = textwrap.dedent("""
            import os
            res = dict(a = os.getcwd())
        """)
        exe = execute_script(code, folder=temp)
        self.assertIsInstance(exe, dict)
        self.assertIn('res', exe)
        self.assertIn('__file__', exe)


if __name__ == "__main__":
    unittest.main()
