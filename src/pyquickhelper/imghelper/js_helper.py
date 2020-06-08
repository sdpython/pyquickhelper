"""
@file
@brief Helpers around images and :epkg:`javascript`.
See also:

* `pyduktape <https://github.com/stefano/pyduktape>`_
* `Python Mini Racer <https://github.com/sqreen/PyMiniRacer>`_
* `python-requirejs <https://github.com/wq/python-requirejs>`_

.. versionadded:: 1.7
"""
import os
from ..loghelper import run_cmd, noLOG


class NodeJsException(Exception):
    """
    Raised if :epkg:`node.js` fails.
    """
    pass


def run_js_fct(script, required=None):
    """
    Assuming *script* contains some :epkg:`javascript`
    which produces :epkg:`SVG`. This functions runs
    the code.

    @param  script      :epkg:`javascript`
    @param  required    required libraries (does not guaranteed to work)
    @return             :epkg:`python` function

    The module relies on :epkg:`js2py` and :epkg:`node.js`.
    Dependencies must be installed with :epkg:`npm`:.

    ::

        npm install babel-core babel-cli babel-preset-es2015 babel-polyfill babelify browserify babel-preset-env

    Function @see fn install_node_js_modules can be run with admin right for that.
    :epkg:`js2py` tries to convert a dependency into :epkg:`Python`
    """
    from js2py import eval_js, require, node_import  # pylint: disable=W0621
    # To skip npm installation.
    node_import.DID_INIT = True
    if required:
        if not isinstance(required, list):
            required = [required]
        for r in required:
            require(r)
    fct = eval_js(script)
    return fct


def install_node_js_modules(dest, module_list=None, fLOG=noLOG):
    """
    Installs missing dependencies to compile a convert a :epkg:`javascript`
    libraries.

    @param      dest        installation folder
    @param      module_list list of modules to install
    @param      fLOG        logging function

    If *module_list is None*, it is replaced by:

    ::

        ['babel-core', 'babel-cli', 'babel-preset-env',
         'babel-polyfill', 'babelify', 'browserify',
         'babel-preset-es2015']
    """
    if module_list is None:
        module_list = ['babel-core', 'babel-cli', 'babel-preset-env',
                       'babel-polyfill', 'babelify', 'browserify',
                       'babel-preset-es2015']
    dir_name = dest
    node_modules = os.path.join(dir_name, "node_modules")
    should = [os.path.join(node_modules, n) for n in module_list]
    if any(map(lambda x: not os.path.exists(x), should)):
        cmds = ['npm install ' + ' '.join(module_list)]
        errs = []
        for cmd in cmds:
            fLOG("[install_node_js_modules] run ", cmd)
            err = run_cmd(cmd, wait=True, change_path=dir_name, fLOG=fLOG)[1]
            errs.append(err)
    if not os.path.exists(node_modules):
        raise RuntimeError(  # pragma: no cover
            "Unable to run from '{0}' commands line:\n{1}\n--due to--\n{2}".format(
                dir_name, "\n".join(cmds), "\n".join(errs)))


def nodejs_version():
    """
    Returns :epkg:`node.js` version.
    """
    out, err = run_cmd('node -v', wait=True)
    if len(err) > 0:
        raise NodeJsException(  # pragma: no cover
            "Unable to find node\n{0}".format(err))
    return out


def run_js_with_nodejs(script, path_dependencies=None, fLOG=noLOG):
    """
    Runs a :epkg:`javascript` script with :epkg:`node.js`.

    @param      script              script to run
    @param      path_dependencies   where dependencies can be found if needed
    @param      fLOG                logging function
    @return                         output of the script
    """
    script_clean = script.replace("\"", "\\\"").replace("\n", " ")
    cmd = 'node -e "{0}"'.format(script_clean)
    out, err = run_cmd(cmd, change_path=path_dependencies,
                       fLOG=fLOG, wait=True)
    if len(err) > 0:
        filtered = "\n".join(_ for _ in err.split('\n')
                             if not _.startswith("[BABEL] Note:"))
    else:
        filtered = err
    if len(filtered) > 0:
        raise NodeJsException(  # pragma: no cover
            "Execution of node.js failed.\n--CMD--\n{0}\n--ERR--\n{1}\n--OUT--\n{2}\n"
            "--SCRIPT--\n{3}".format(cmd, err, out, script))
    return out


_require_cache = {}


def require(module_name, cache_folder='.', suffix='_pyq', update=False, fLOG=noLOG):
    """
    Modified version of function *require* in
    `node_import.py <https://github.com/PiotrDabkowski/Js2Py/blob/master/js2py/node_import.py>`_.

    @param      module_name     required library name
    @param      cache_folder     location of the files the function creates
    @param      suffix          change the suffix if you use the same folder for multiple files
    @param      update          update the converted script
    @param      fLOG            logging function
    @return                     outcome of the javascript script

    The function is not fully tested.
    """
    if module_name.endswith('.js'):
        raise ValueError(  # pragma: no cover
            "module_name must the name without extension .js")
    global _require_cache
    if module_name in _require_cache and not update:
        py_code = _require_cache[module_name]
    else:
        from js2py.node_import import ADD_TO_GLOBALS_FUNC, GET_FROM_GLOBALS_FUNC
        from js2py import translate_js

        py_name = module_name.replace('-', '_')
        module_filename = '%s.py' % py_name
        full_name = os.path.join(cache_folder, module_filename)

        var_name = py_name.rpartition('/')[-1]
        in_file_name = os.path.join(
            cache_folder, "require_{0}_in{1}.js".format(module_name, suffix))
        out_file_name = os.path.join(
            cache_folder, "require_{0}_out{1}.js".format(module_name, suffix))

        code = ADD_TO_GLOBALS_FUNC
        code += """
            var module_temp_love_python = require('{0}');
            addToGlobals('{0}', module_temp_love_python);
            """.format(module_name)

        with open(in_file_name, 'w', encoding='utf-8') as f:
            f.write(code)

        pkg_name = module_name.partition('/')[0]
        install_node_js_modules(cache_folder, [pkg_name], fLOG=fLOG)

        inline_script = "(require('browserify')('%s').bundle(function (err,data)" + \
            "{fs.writeFile('%s',require('babel-core').transform(data," + \
            "{'presets':require('babel-preset-es2015')}).code,()=>{});}))"
        inline_script = inline_script % (in_file_name.replace("\\", "\\\\"),
                                         out_file_name.replace("\\", "\\\\"))
        run_js_with_nodejs(inline_script, fLOG=fLOG,
                           path_dependencies=cache_folder)

        with open(out_file_name, "r", encoding="utf-8") as f:
            js_code = f.read()

        js_code += GET_FROM_GLOBALS_FUNC
        js_code += ";var {0} = getFromGlobals('{1}');{0}".format(
            var_name, module_name)
        fLOG('[require] translating', out_file_name)
        py_code = translate_js(js_code)

        with open(full_name, 'w', encoding="utf-8") as f:
            f.write(py_code)

        _require_cache[module_name] = py_code

    context = {}
    exec(py_code, context)
    return context['var'][var_name].to_py()
