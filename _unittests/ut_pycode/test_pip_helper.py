"""
@brief      test tree node (time=2s)
"""
import unittest
import pandas
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pycode.pip_helper import (
    get_packages_list, package2dict, get_package_info,
    PQPipError)


class TestPipHelper(ExtTestCase):

    def test_exc(self):
        exc = PQPipError('cmd', 'out', 'err')
        msg = str(exc)
        self.assertEqual([msg.replace('\n', '')], [
                         'CMD:cmdOUT:out[piperror]err'])

    def test_pip_list(self):
        li = get_packages_list()
        dt = package2dict(li[0])
        avoid = {'py_version'}
        empty = []
        for k, v in dt.items():
            if k not in avoid:
                if k is None:
                    empty.append(k)
        self.assertEmpty(empty)
        self.assertNotEmpty(li)

    def test_pip_show(self):
        info = get_package_info("pandas")
        if "version" not in str(info):
            raise AssertionError(str(info))

        info = get_package_info("sphinx")
        if "version" not in str(info):
            raise Exception(str(info))

    def test_pip_show_all(self):
        info = get_package_info(start=0, end=2)
        df = pandas.DataFrame(info)
        self.assertNotEmpty(info)

        if __name__ == "__main__":
            info = get_package_info()
            df = pandas.DataFrame(info)
            df.to_excel("out_packages.xlsx")


if __name__ == "__main__":
    unittest.main()
