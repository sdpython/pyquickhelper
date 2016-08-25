"""
@file
@brief Parse a file *.yml* and convert it into a set of actions.

.. todoext::
    :title: define Jenkins job with .yml
    :tag: enhancement
    :cost: 4
    :date: 2016-08-25
    :issue: 29
    :hidden:
    :release:1.4

    The current build system is not easy to read.
    This should make things more clear and easier to maintain.

.. versionadded:: 1.4
"""
import os
import re
import sys
import yaml
from ..texthelper.templating import apply_template
from ..filehelper import read_content_ufs


def pickname(*l):
    """
    pick the first string non null in the list

    @param      l   list of string
    @return         string
    """
    for s in l:
        s = s.strip()
        if s:
            return s
    raise ValueError("Unable to find a non empty string in {0}".format(l))


def load_yaml(file_or_buffer, context=None, engine="jinja2", platform=None):
    """
    loads a yaml file (.yml)

    @param      file_or_buffer      string or physical file or url
    @param      context             variables to replace in the configuration
    @param      engine              see @see fn apply_template
    @return                         see `PyYAML <http://pyyaml.org/wiki/PyYAMLDocumentation>`_
    """
    def replace(val, rep, into):
        if val is None:
            return val
        else:
            return val.replace(rep, into)
    content, source = read_content_ufs(file_or_buffer, add_source=True)
    project_name = infer_project_name(file_or_buffer, source)

    def ospathjoinp(*l, platform=platform):
        return ospathjoin(*l, platform=platform)

    if context is None:
        context = dict(replace=replace, ospathjoin=ospathjoinp,
                       pickname=pickname)
    else:
        fs = [("replace", replace), ("ospathjoin", ospathjoinp),
              ("pickname", pickname)]
        if any(_[0] not in context for _ in fs):
            context = context.copy()
            for k, f in fs:
                if k not in context:
                    context[k] = f
    if "project_name" not in context and project_name is not None:
        context["project_name"] = project_name

    content = apply_template(content, context, engine)
    return yaml.load(content), project_name


def evaluate_condition(cond, variables=None):
    """
    evaluate a condition inserted in a yaml file

    @param      cond        (str) condition
    @param      variables   (dict|None) dictionary
    @return                 boolean

    Example of a condition::

        [ ${PYTHON} == "C:\\Python35_x64" ]
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

        if [ ${PYTHON} == "C:\\\\Python35_x64" ]; then python setup.py build_sphinx; fi
    """
    if isinstance(inst, list):
        res = [interpret_instruction(_, variables) for _ in inst]
        if any(res):
            return [_ for _ in res if _ is not None]
        else:
            return None
    elif isinstance(inst, tuple):
        return (inst[0], interpret_instruction(inst[1], variables))
    elif isinstance(inst, dict):
        return inst
    elif isinstance(inst, (int, float)):
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


def enumerate_convert_yaml_into_instructions(obj, variables=None, add_environ=True):
    """
    convert a yaml file into sequences of instructions,
    conditions are interpreted

    @param      obj         yaml objects (@see fn load_yaml)
    @param      variables   additional variables to be used
    @param      add_environ add environment variables available, does not
                            overwrite existing variables
                            when the job is generated
    @return                 list of tuple(instructions, variables)

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
    if variables is None:
        def_variables = {}
    else:
        def_variables = variables.copy()
    if add_environ:
        for k, v in os.environ.items():
            if k not in def_variables:
                def_variables[k] = v
    sequences = []
    count = {}
    steps = ["language", "python", "virtualenv", "install",
             "before_script", "script", "after_script",
             "documentation"]
    for key in steps:
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

    for k in obj:
        if k not in steps:
            raise ValueError(
                "Unexpected key '{0}' found in yaml file".format(k))

    # multiplications
    i_python = 0
    i_script = 0
    notstop = True
    while notstop:
        seq = []
        add = True
        variables = def_variables.copy()
        for key, value in sequences:
            if key == "python":
                value = value[i_python]
                if isinstance(value, dict):
                    if 'PATH' not in value:
                        raise KeyError(
                            "The dictionary should include key 'path': {0}".format(value))
                    for k, v in sorted(value.items()):
                        if k != 'PATH':
                            variables[k] = v
                            seq.append(('INFO', (k, v)))
                    value = value["PATH"]
            elif key == "script":
                value = value[i_script]
                if isinstance(value, dict) and "NAME" in value:
                    seq.append(('INFO', ('NAME', value["NAME"])))
                    variables["NAME"] = value["NAME"]
                i_script += 1
                if i_script >= count['script']:
                    i_script = 0
                    i_python += 1
                    if i_python >= count['python']:
                        notstop = False
            if value is not None and value != 'None':
                seq.append((key, value))
                variables[key] = value
            else:
                add = False
        if add:
            r = interpret_instruction(seq, variables)
            if r is not None:
                yield r, variables


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


def convert_sequence_into_batch_file(seq, variables=None, platform=None):
    """
    converts a sequence of instructions into a batch file

    @param      seq         sequence of instructions
    @param      variables   list of variables
    @param      platform    ``sys.platform`` if None
    @return                 (str) batch file
    """
    if platform is None:
        platform = sys.platform
    rows = []
    iswin = platform.startswith("win")

    if iswin:
        error_level = "if %errorlevel% neq 0 exit /b %errorlevel%"
    else:
        error_level = "if [ $? -ne 0 ]; then exit $?; fi"
    interpreter = None
    pip = None
    venv = None
    anaconda = False
    conda = None
    echo = "@echo" if iswin else "echo"
    rowsset = []
    if iswin:
        rowsset.append("@echo off")
        rowsset.append("set PATH0=%PATH%")

    def add_path_win(rows, interpreter, pip, platform):
        path_inter = ospathdirname(interpreter, platform)
        if len(path_inter) == 0:
            raise ValueError(
                "Unable to guess interpreter path from '{0}', platform={1}".format(interpreter, platform))
        if iswin:
            rows.append("set PATH={0};%PATH%".format(path_inter))
        else:
            rows.append("export PATH={0}:$PATH".format(path_inter))
        path_pip = ospathdirname(pip, platform)
        if path_pip != path_inter:
            if iswin:
                rows.append("set PATH={0};%PATH%".format(path_pip))
            else:
                rows.append("export PATH={0}:$PATH".format(path_pip))

    for key, value in seq:
        if key == "python":
            if variables.get('DIST', None) == "conda":
                rows.append(echo + " conda")
                anaconda = True
                interpreter = ospathjoin(
                    value, "python", platform=platform)
                pip = ospathjoin(value, "Scripts",
                                 "pip", platform=platform)
                venv = ospathjoin(
                    value, "Scripts", "virtualenv", platform=platform)
                conda = ospathjoin(
                    value, "Scripts", "conda", platform=platform)
            else:
                interpreter = ospathjoin(
                    value, "python", platform=platform)
                pip = ospathjoin(value, "Scripts",
                                 "pip", platform=platform)
                venv = ospathjoin(value, "Scripts",
                                  "virtualenv", platform=platform)
            rows.append(echo + " interpreter=" + interpreter)

        elif key == "virtualenv":
            if isinstance(value, list):
                if len(value) != 1:
                    raise ValueError(
                        "Expecting one value for the path of the virtual environment:\n{0}".format(value))
                value = value[0]
            p = value["path"] if isinstance(value, dict) else value
            rows.append("")
            rows.append(echo + " CREATE VIRTUAL ENVIRONMENT in %s" % p)
            if not anaconda:
                if iswin:
                    rows.append('if not exist "{0}" mkdir "{0}"'.format(p))
                else:
                    rows.append('if [-f {0}]; then mkdir "{0}"; fi'.format(p))
            if anaconda:
                pinter = ospathdirname(interpreter, platform=platform)
                rows.append(
                    '"{0}" create -p "{1}" --clone "{2}" --offline'.format(conda, p, pinter))
                interpreter = ospathjoin(
                    p, "python", platform=platform)
                pip = ospathjoin(p, "Scripts", "pip",
                                 platform=platform)
            else:
                rows.append(
                    '"{0}" --system-site-packages "{1}"'.format(venv, p))
                interpreter = ospathjoin(
                    p, "Scripts", "python", platform=platform)
                pip = ospathjoin(p, "Scripts", "pip",
                                 platform=platform)
            rows.append(error_level)

        elif key in {"install", "before_script", "script", "after_script", "documentation"}:
            if value is not None:
                if isinstance(value, dict):
                    if "CMD" not in value:
                        raise KeyError(
                            "A script defined by a dictionary must contain key '{0}' in \n{1}".format("CMD", value))
                    if "NAME" in value:
                        rows.append("set JOB_NAME=%s" % value["NAME"])
                    value = value["CMD"]
                rows.append("")
                rows.append(echo + " " + key.upper())
                add_path_win(rows, interpreter, pip, platform)
                if not isinstance(value, list):
                    value = [value]
                rows.extend(value)
                rows.append(error_level)
        elif key == 'INFO':
            rowsset.append("SET {0}={1}".format(value[0], value[1]))
        else:
            raise ValueError("unexpected key '{0}'".format(key))
    rows = rowsset + rows
    try:
        return "\n".join(rows)
    except TypeError as e:
        raise TypeError("Unexpected type\n{0}".format(
            "\n".join([str((type(_), _)) for _ in rows]))) from e


def infer_project_name(file_or_buffer, source):
    """
    infer a project name based on yaml file

    @param      file_or_buffer      file name
    @param      source              second output of @see fn read_content_ufs
    @return                         name

    The function can infer a name for *source* in ``{'r', 'u'}``.
    For *source* equal to ``'s'``, it returns ``'<unknown>'``.
    """
    if source == "r":
        fold = os.path.dirname(file_or_buffer)
        last = os.path.split(fold)[-1]
    elif source == "u":
        spl = file_or_buffer.split('/')
        pos = -2
        name = None
        while len(spl) > -pos:
            name = spl[pos]
            if name in {'master'}:
                pos -= 1
            elif 'github' in name:
                break
            else:
                break
        if name is None:
            raise ValueError(
                "Unable to infer project name for '{0}'".format(file_or_buffer))
        return name
    elif source == "s":
        return "<unknown>"
    else:
        raise ValueError("Unexpected value for add_source: '{0}' for '{1}'".format(
            source, file_or_buffer))
    return last


def enumerate_processed_yml(file_or_buffer, context=None, engine="jinja2", platform=None,
                            server=None, git_repo=None, add_environ=True, overwrite=False,
                            build_location=None, **kwargs):
    """
    submit or enumerate jobs based on the content of a yml file

    @param      file_or_buffer      filename or string
    @param      context             variables to replace in the configuration
    @param      engine              see @see fn apply_template
    @param      server              see @see cl JenkinsExt
    @param      platform            plaform where the job will be executed
    @param      git_repo            git repository (if *server* is not None)
    @param      add_environ         add environment variable before interpreting the job
    @param      overwrite           overwrite the job if it already exists in Jenkins
    @param      build_location      location for the build
    @param      kwargs              see @see me create_job_template
    @return                         enumerator for *(job, name, variables)*

    Example of a yml file `.local.jenkins.win.yml <https://github.com/sdpython/pyquickhelper/blob/master/.local.jenkins.win.yml>`_.
    """
    fLOG = kwargs.get('fLOG', None)
    project_name = None if context is None else context.get(
        "project_name", None)
    obj, project_name = load_yaml(
        file_or_buffer, context=context, platform=platform)
    for seq, var in enumerate_convert_yaml_into_instructions(obj, variables=context, add_environ=add_environ):
        conv = convert_sequence_into_batch_file(
            seq, variables=var, platform=platform)

        # we extract a suffix from the command line
        if server is not None:
            name = "_".join([project_name, var.get('NAME', ''), str(var.get("VERSION", '')).replace(".", ""),
                             var.get('DIST', '')])
            conv = "SET NAME_JENKINS=" + name + "\n" + conv
            import jenkins
            try:
                j = server.get_job_config(name) if not server._mock else None
            except jenkins.NotFoundException:
                j = None
            except jenkins.JenkinsException as e:
                from .jenkins_helper import JenkinsExtException
                raise JenkinsExtException(
                    "unable to retrieve job config for name={1}".format(name)) from e

            update_job = False
            if j is not None:
                if kwargs.get('update', True):
                    update_job = True
                else:
                    if fLOG is not None:
                        fLOG("[jenkins] delete job", name)
                    server.delete_job(name)

            if project_name not in git_repo:
                git_repo += project_name

            # set up location
            if build_location is None:
                loc = None
            else:
                loc = os.path.join(build_location, name)

            if overwrite or j is None:
                yield server.create_job_template(name, script=conv, git_repo=git_repo,
                                                 update=update_job, location=loc, **kwargs), name, var
        else:
            yield conv, None, var
