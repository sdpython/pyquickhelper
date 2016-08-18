"""
@file
@brief Parse a file *.yml* and convert it into a set of actions.

.. todoext::
    :title: define Jenkins job with .yml
    :tag: enhancement
    :cost: 0.1
    :date: 2016-08-16
    :issue: 29

    The current build system is not easy to read.
    This should make things more clear and easier to maintain.

.. versionadded:: 1.4
"""
import os
import re
import sys
import yaml
from ..texthelper.templating import apply_template


def load_yaml(file_or_buffer, context=None, engine="jinja2"):
    """
    loads a yaml file (.yml)

    @param      file_or_buffer      string or physical file
    @param      context             variables to replace in the configuration
    @param      engine              see @see fn apply_template
    @return                         see `PyYAML <http://pyyaml.org/wiki/PyYAMLDocumentation>`_
    """
    typstr = str  # unicode#
    if len(file_or_buffer) < 5000 and os.path.exists(file_or_buffer):
        with open(file_or_buffer, "r", encoding="utf-8") as f:
            file_or_buffer = f.read()
    if context is None:
        context = dict()
    file_or_buffer = apply_template(file_or_buffer, context, engine)
    return yaml.load(file_or_buffer)


def evaluate_condition(cond, variables=None):
    """
    evaluate a condition inserted in a yaml file

    @param      cond        (str) condition
    @param      variables   (dict|None) dictionary
    @return                 boolean

    Example of a condition::

        [ ${PYTHON} == "C:\\Python35_x64\\pythonw.exe" ]
    """
    if variables is not None:
        for k, v in variables.items():
            rep = "${%s}" % k
            vv = '"%s"' % v
            cond = cond.replace(rep, vv)
            cond = cond.replace(rep.upper(), vv)
    cond = cond.strip()
    if cond.startswith("[") and cond.endswith("]"):
        e = eval(cond)
        return all(e)
    else:
        return eval(cond)


def interpret_instruction(inst, variables=None):
    """
    interpret an instruction with if statement

    @param      inst        (str) instruction
    @param      variables   (dict|None)
    @return                 (str|None)

    Example of a statement::

        if [ ${PYTHON} == "C:\\\\Python35_x64\\\\pythonw.exe" ] then python setup.py build_sphinx fi
    """
    if isinstance(inst, list):
        res = [interpret_instruction(_, variables) for _ in inst]
        if len(res) == 1 and res[0] is None:
            return None
        else:
            return res
    elif isinstance(inst, tuple):
        return (inst[0], interpret_instruction(inst[1], variables))
    elif isinstance(inst, dict):
        return inst
    else:
        inst = inst.replace("\n", " ")
        exp = re.compile("^ *if +(.*) +then +(.*)( +else +(.*))? +fi *$")
        find = exp.search(inst)
        if find:
            gr = find.groups()
            e = evaluate_condition(gr[0], variables)
            return gr[1] if e else gr[3]
        else:
            return inst


def enumerate_convert_yaml_into_instructions(obj):
    """
    convert a yaml file into sequences of instructions

    @param      obj     yaml objects (@see fn load_yaml)
    @return             list of instructions

    The function expects the following list
    of steps in this order:

    * language: should be python
    * python: list of interpreters (multiplies jobs)
    * virtualenv: name of the virtual environment
    * install: list of installation steps in the virtual environment
    * before_script: list of steps to run
    * script: list of script to run (multiplies jobs)
    * after_script: list of steps to run
    * documentation: documentation to run after the

    Each step *multiplies jobs* creates a sequence of jobs
    and a Jenkins job.
    """
    sequences = []
    count = {}
    for key in ["language", "python", "virtualenv", "install",
                "before_script", "script", "after_script",
                "documentation"]:
        value = obj.get(key, None)
        if key == "language":
            if value != "python":
                raise NotImplementedError("language must be python")
            continue
        elif value is not None:
            if key in {'python', 'script'} and not isinstance(value, list):
                value = [value]
            count[key] = len(value)
            sequences.append((key, value))

    # multiplications
    i_python = 0
    i_script = 0
    notstop = True
    while notstop:
        seq = []
        add = True
        variables = {}
        for key, value in sequences:
            if key == "python":
                value = value[i_python]
            elif key == "script":
                value = value[i_script]
                i_script += 1
                if i_script >= count['script']:
                    i_script = 0
                    i_python += 1
                    if i_python >= count['python']:
                        notstop = False
            if value is not None and value != 'None' and value != "conda|":
                seq.append((key, value))
                variables[key] = value
            else:
                add = False
        if add:
            yield interpret_instruction(seq, variables)


def ospathjoin(*l, platform=None):
    """
    simple ``o.path.join`` for a specific platform

    @param      l           list of paths
    @param      platform    platform
    @return                 path
    """
    if platform is None:
        return os.path.join(*l)
    elif platform.startswith("win"):
        return "\\".join(l)
    else:
        return "/".join(l)


def ospathdirname(l, platform=None):
    """
    simple ``o.path.dirname`` for a specific platform

    @param      l           path
    @param      platform    platform
    @return                 path
    """
    if platform is None:
        return os.path.dirname(l)
    elif platform.startswith("win"):
        return "\\".join(l.replace("/", "\\").split("\\")[:-1])
    else:
        return "/".join(l.replace("\\", "/").split("/")[:-1])


def convert_sequence_into_batch_file(seq, platform=None):
    """
    converts a sequence of instructions into a batch file

    @param      seq         sequence of instructions
    @param      platform    ``sys.platform`` if None
    @return                 (str) batch file
    """
    if platform is None:
        platform = sys.platform
    rows = []
    if platform.startswith("win"):
        error_level = "if %errorlevel% neq 0 exit /b %errorlevel%"
        interpreter = None
        pip = None
        venv = None
        anaconda = False
        conda = None
        rows.append("@echo off")

        def add_path_win(rows):
            path_inter = ospathdirname(interpreter)
            rows.append("set PATH={0};%PATH%".format(path_inter))
            path_pip = ospathdirname(pip)
            if path_pip != path_inter:
                rows.append("set PATH={0};%PATH%".format(path_pip))

        for key, value in seq:

            if key == "python":
                if value.startswith("conda|"):
                    anaconda = True
                    interpreter = ospathjoin(
                        value[6:], "python.exe", platform=platform)
                    pip = ospathjoin(value[6:], "Scripts",
                                     "pip.exe", platform=platform)
                    venv = ospathjoin(
                        value[6:], "Scripts", "virtualenv.exe", platform=platform)
                    conda = ospathjoin(
                        value[6:], "Scripts", "conda.exe", platform=platform)
                else:
                    interpreter = ospathjoin(
                        value, "python.exe", platform=platform)
                    pip = ospathjoin(value, "Scripts",
                                     "pip.exe", platform=platform)
                    venv = ospathjoin(value, "Scripts",
                                      "virtualenv.exe", platform=platform)

            elif key == "virtualenv":
                if isinstance(value, list):
                    if len(value) != 1:
                        raise ValueError(
                            "Expecting one value for the path of the virtual environment:\n{0}".format(value))
                    value = value[0]
                p = value["path"] if isinstance(value, dict) else value
                rows.append("")
                rows.append("@echo CREATE VIRTUAL ENVIRONMENT in %s" % p)
                rows.append('if not exist "{0}" mkdir "{0}"'.format(p))
                if anaconda:
                    rows.append(
                        '"{0}" create -p "{1}" --clone "{2}" --offline'.format(conda, p, pinter))
                    interpreter = ospathjoin(
                        p, "python.exe", platform=platform)
                    pip = ospathjoin(p, "Scripts", "pip.exe",
                                     platform=platform)
                else:
                    rows.append(
                        '"{0}" --system-site-packages "{1}"'.format(venv, p))
                    interpreter = ospathjoin(
                        p, "Scripts", "python.exe", platform=platform)
                    pip = ospathjoin(p, "Scripts", "pip.exe",
                                     platform=platform)
                rows.append(error_level)

            elif key in {"install", "before_script", "script", "after_script", "documentation"}:
                if value is not None:
                    rows.append("")
                    rows.append("@echo " + key.upper())
                    add_path_win(rows)
                    if not isinstance(value, list):
                        value = [value]
                    rows.extend(value)
                    rows.append(error_level)
            else:
                raise ValueError("unexpected key '{0}'".format(key))
        return "\n".join(rows)
    else:
        raise NotImplementedError(
            "not implemented (convert_sequence_into_batch_file): " + platform)
