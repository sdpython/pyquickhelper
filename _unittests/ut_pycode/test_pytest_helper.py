"""
@brief      test tree node (time=5s)
"""
import os
import unittest

from pyquickhelper.pycode import ExtTestCase, get_temp_folder, run_test_function, TestExecutionError

test_content = """
def test_right():
    assert True

def test_wrong():
    assert False

def not_a_test():
    assert False

def test_not_a_test(a):
    assert False
"""


class TestPyTestHelper(ExtTestCase):

    def test_pytest_helper(self):
        temp = get_temp_folder(__file__, "temp_pytest_helper")
        test_file = os.path.join(temp, "test_file.py")
        with open(test_file, "w") as f:
            f.write(test_content)

        try:
            run_test_function(test_file, stop_first=True)
        except TestExecutionError as e:
            self.assertIn(
                "Function 'test_wrong' from module 'test_file'", str(e))

        try:
            run_test_function(test_file, stop_first=False)
        except Exception as e:
            self.assertIn(
                "Function 'test_wrong' from module 'test_file'", str(e))
            self.assertIn("Test module 'test_file' failed", str(e))

        try:
            run_test_function(test_file, stop_first=False, pattern="rrrr")
        except Exception as e:
            self.assertIn("o function found in", str(e))


if __name__ == "__main__":
    unittest.main()
