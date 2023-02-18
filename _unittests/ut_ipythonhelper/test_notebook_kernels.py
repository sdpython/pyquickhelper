"""
@brief      test log(time=4s)

notebook test
"""

import sys
import os
import unittest
import warnings

from pyquickhelper.loghelper import fLOG
from pyquickhelper.ipythonhelper import find_notebook_kernel, install_jupyter_kernel, get_notebook_kernel, remove_kernel
from pyquickhelper.pycode import is_travis_or_appveyor, skipif_appveyor


class TestNotebookKernels(unittest.TestCase):

    def test_notebook_kernels_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        kern = "python" + str(sys.version_info[0])
        res = find_notebook_kernel()
        self.assertTrue(isinstance(res, dict))
        for k, v in sorted(res.items()):
            fLOG(k, type(v), v)
        self.assertTrue(kern in res)

    @skipif_appveyor("Message: 'Installed kernelspec %s in %s'")
    def test_notebook_kernel_install(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ("travis", "circleci"):
            # permission issue on linux.
            return

        kern = "ut_" + sys.executable.replace("\\", "/").replace("/", "_").replace(
            ".", "_").replace(":", "") + "_" + str(sys.version_info[0])
        kern = kern.lower()
        try:
            loc = install_jupyter_kernel(kernel_name=kern)
        except PermissionError as e:
            warnings.warn(
                f"Unable to install a new kernel with this user: {e}")
            return
        fLOG("i", loc)
        if kern not in loc:
            raise AssertionError(
                f"do not match '{kern}' not in '{loc}'")
        self.assertTrue(os.path.exists(loc))
        res = get_notebook_kernel(kern)
        fLOG("i", res)

        remove_kernel(kern)
        kernels = find_notebook_kernel()
        self.assertTrue(kern not in kernels)


if __name__ == "__main__":
    unittest.main()
