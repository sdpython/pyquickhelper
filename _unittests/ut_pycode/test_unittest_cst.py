"""
@brief      test tree node (time=3s)
"""
import unittest
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pycode.unittest_cst import compress_cst, decompress_cst


class TestUnitTestCst(ExtTestCase):

    def test_compress_cst(self):
        data = {'values': [0.5, 6.9]}
        res = compress_cst(data, 20)
        expected = [b'/Td6WFoAAATm1rRGAgAh',
                    b'ARYAAAB0L+WjAQAVeyJ2',
                    b'YWx1ZXMiOiBbMC41LCA2',
                    b'LjldfQAAAKCzDzOeal0o',
                    b'AAEuFlYJVd8ftvN9AQAA',
                    b'AAAEWVo=']
        self.assertEqual(expected, res)

    def test_compress_decompress_cst(self):
        data = {'values': [0.5, 6.9]}
        res = compress_cst(data, 20)
        des = decompress_cst(res)
        self.assertEqual(data, des)


if __name__ == "__main__":
    unittest.main()
