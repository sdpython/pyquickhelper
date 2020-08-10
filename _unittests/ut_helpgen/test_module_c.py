"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
import warnings
from textwrap import dedent
from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.loghelper import run_cmd
from pyquickhelper.pycode import ExtTestCase, get_temp_folder
from pyquickhelper.helpgen.utils_sphinx_doc_helpers import add_file_rst_template, import_module
from pyquickhelper.helpgen.utils_sphinx_doc import copy_source_files, add_file_rst


class TestModuleC(ExtTestCase):

    content_c = dedent("""
        #include <stdio.h>
        #include <stdexcept>
        #include "Python.h"

        struct module_state {
            PyObject *error;
        };

        #define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

        const char * module_name = "stdchelper_demo" ;

        static PyObject* cdemo(PyObject *self, PyObject* unicode)
        {
            if (unicode == NULL) {
                struct module_state *st = GETSTATE(self);
                PyErr_SetString(st->error, "Null pointer is not allowed.");
                return 0;
            }

            const Py_UNICODE *uni;
            if (!PyArg_ParseTuple(unicode, "u", &uni))
                return NULL;
            PyObject* res = PyLong_FromLong(wcslen(uni));
            Py_INCREF(res);
            return res;
        }

        static int stdchelper_demo_module_traverse(PyObject *m, visitproc visit, void *arg) {
            Py_VISIT(GETSTATE(m)->error);
            return 0;
        }

        static int stdchelper_demo_module_clear(PyObject *m) {
            Py_CLEAR(GETSTATE(m)->error);
            return 0;
        }

        static PyMethodDef fonctions [] = {
          {"cdemo",  cdemo, METH_VARARGS, "Returns the length of a string."},
          {NULL, NULL}
        } ;

        static struct PyModuleDef moduledef = {
                PyModuleDef_HEAD_INIT,
                module_name,
                "Helper for IO with C++.",
                sizeof(struct module_state),
                fonctions,
                NULL,
                stdchelper_demo_module_traverse,
                stdchelper_demo_module_clear,
                NULL
        };

        #ifdef __cplusplus
        extern "C" {
        #endif


        PyObject *
        PyInit_stdchelper_demo(void)
        {
            PyObject* m ;
            m = PyModule_Create(&moduledef);
            if (m == NULL)
                return NULL;

            struct module_state *st = GETSTATE(m);
            if (st == NULL)
                throw new std::runtime_error("GETSTATE returns null.");

            st->error = PyErr_NewException("stdchelper_demo.Error", NULL, NULL);
            if (st->error == NULL) {
                Py_DECREF(m);
                return NULL;
            }

            return m ;
        }

        #ifdef __cplusplus
        }
        #endif
    """)

    @unittest.skipIf(sys.version_info[:2] != (3, 7), "no test file to use")
    @unittest.skipIf(sys.platform != "win32", "no test file to use")
    def test_module_c(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        vers = "%d%d" % sys.version_info[:2]
        file = os.path.join(path, "data", "pyd",
                            "stdchelper.cp%s-win_amd64.pyd" % vers)
        if os.path.exists(file):
            mo = import_module(
                None, file, fLOG, additional_sys_path=None, first_try=True)
            self.assertIsInstance(mo, tuple)
            self.assertEqual(len(mo), 2)
            self.assertTrue(hasattr(mo[0], '__doc__'))
            if 'stdchelper' in sys.modules:
                del sys.modules['stdchelper']

        temp = get_temp_folder(__file__, "temp_module_c")
        store_obj = {}
        actions = copy_source_files(os.path.dirname(file), temp, fLOG=fLOG)
        store_obj = {}
        indexes = {}
        add_file_rst(temp, store_obj, actions, fLOG=fLOG,
                     rootrep=("module_c.", ""), indexes=indexes)
        self.assertNotEmpty(store_obj)
        self.assertEqual(len(store_obj), 4)
        if len(actions) != 2:
            raise Exception("{0}\n{1}".format(
                len(actions), "\n".join(str(_) for _ in actions)))
        self.assertEqual(len(indexes), 1)

    def test_compile_module(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_compile_module")
        source = os.path.join(temp, "cdemo.cpp")
        init = os.path.join(temp, "__init__.py")
        setup = os.path.join(temp, "setup.py")
        with open(source, "w") as f:
            f.write(TestModuleC.content_c)
        with open(init, "w") as f:
            pass

        setup_content = dedent("""
            from distutils.core import setup, Extension
            module1 = Extension('stdchelper_demo', sources=['{0}'])
            setup (name = 'ccdemo', version = '1.0',
                   description = 'This is a demo package.',
                   ext_modules = [module1])
            """.format(source.replace("\\", "/")))
        with open(setup, "w") as f:
            f.write(setup_content)

        cmd = "{0} {1} build_ext --inplace".format(sys.executable, setup)
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG, change_path=temp)
        if "error" in out or "error" in err:
            out_ = out.replace("-Werror=format-security", "")
            if "error" in out_:
                raise Exception(
                    "Unable to compile\n--OUT--\n{0}\n--ERR--\n{1}".format(out, err))
        if sys.platform == "win32":
            name = "stdchelper_demo.cp%d%d-win_amd64.pyd" % sys.version_info[:2]
        elif sys.platform == "darwin":
            if sys.version_info[:2] <= (3, 7):
                name = "stdchelper_demo.cpython-%d%dm-darwin.so" % sys.version_info[:2]
            else:
                name = "stdchelper_demo.cpython-%d%d-darwin.so" % sys.version_info[:2]
        else:
            if sys.version_info[:2] <= (3, 7):
                name = "stdchelper_demo.cpython-%d%dm-x86_64-linux-gnu.so" % sys.version_info[:2]
            else:
                name = "stdchelper_demo.cpython-%d%d-x86_64-linux-gnu.so" % sys.version_info[:2]
        fullname = os.path.join(temp, name)
        if not os.path.exists(fullname):
            files = os.listdir(os.path.dirname(fullname))
            raise FileNotFoundError(
                "Unable to find '{0}' (platform '{1}')\nFound:\n{2}".format(
                    fullname, sys.platform, "\n".join(files)))
        mo = import_module(None, fullname, fLOG,
                           additional_sys_path=None, first_try=True)
        self.assertIsInstance(mo, tuple)
        self.assertEqual(len(mo), 2)
        self.assertTrue(hasattr(mo[0], '__doc__'))

        if 'stdchelper_demo' in sys.modules:
            del sys.modules['stdchelper_demo']

        temp2 = get_temp_folder(__file__, "temp_compile_module2")
        store_obj = {}
        actions = copy_source_files(temp, temp2, fLOG=fLOG)
        store_obj = {}
        indexes = {}
        add_file_rst(temp2, store_obj, actions, fLOG=fLOG,
                     rootrep=("stdchelper_demo.", ""), indexes=indexes)
        if sys.platform == "darwin":
            warnings.warn(
                "add_file_rst does not work yet on MacOSX for C++ modules.")
            return
        self.assertNotEmpty(store_obj)
        self.assertEqual(len(store_obj), 1)
        if len(actions) not in (3, 4):
            raise Exception("{0}\n{1}".format(
                len(actions), "\n".join(str(_) for _ in actions)))
        self.assertEqual(len(indexes), 1)


if __name__ == "__main__":
    unittest.main()
