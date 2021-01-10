"""
@file
@brief Parse a file *.yml* and convert it into a set of actions.
"""
import os
import re
from ..texthelper.templating import apply_template
from ..filehelper import read_content_ufs
from .yaml_helper_yaml import yaml_load
from .jenkins_helper import get_platform


_jenkins_split = "JENKINS_SPLIT"


def pickname(*args):
    """
    Picks the first string non null in the list.

    @param      l   list of string
    @return         string
    """
    for s in args:
        s = s.strip()
        if s:
            return s
    raise ValueError(  # pragma: no cover
        "Unable to find a non empty string in {0}".format(args))


def load_yaml(file_or_buffer, context=None, engine="jinja2", platform=None):
    """
    Loads a :epkg:`yml` file (*.yml*).

    @param      file_or_buffer      string or physical file or url
    @param      context             variables to replace in the configuration
    @param      engine              see @see fn apply_template
    @param      platform            to join path differently based on the OS
    @return                         see `PyYAML <http://pyyaml.org/wiki/PyYAMLDocumentation>`_
    """
    def replace(val, rep, into):
        if val is None:
            return val
        return val.replace(rep, into)
    content, source = read_content_ufs(file_or_buffer, add_source=True)

    def ospathjoinp(*args, **kwargs):
        p = kwargs.get('platform', platform)
        return ospathjoin(*args, platform=p)

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
    if not isinstance(context, dict):
        raise TypeError(  # pragma: no cover
            "context must be a dictionary not {}.".format(type(context)))
    if "project_name" not in context:
        project_name = infer_project_name(file_or_buffer, source)
    else:
        project_name = context["project_name"]
    if project_name.endswith("__"):
        raise ValueError(  # pragma: no cover
            "project_name is wrong, it cannot end by '__': '{0}'"
            "".format(project_name))
    if "project_name" not in context and project_name is not None:
        context["project_name"] = project_name

    if ("root_path" not in context or
            not context["root_path"].endswith(project_name)):
        context = context.copy()
        context["root_path"] = ospathjoin(
            context.get("root_path", ""), project_name, platform=platform)

    if "root_path" in context:
        if platform is None:
            platform = get_platform(platform)
        if platform.startswith("win"):
            addition = "set current={0}\\%NAME_JENKINS%".format(
                context["root_path"])
        else:
            addition = "export current={0}/$NAME_JENKINS".format(
                context["root_path"])
        content = "automatedsetup:\n  - {0}\n{1}".format(addition, content)

    content = apply_template(content, context, engine)
    try:
        return yaml_load(content), project_name
    except Exception as e:  # pragma: no cover
        raise SyntaxError(
            "Unable to parse content\n{0}".format(content)) from e


def evaluate_condition(cond, variables=None):
    """
    Evaluates a condition inserted in a :epkg:`yml` file.

    @param      cond        (str) condition
    @param      variables   (dict|None) dictionary
    @return                 boolean

    Example of a condition::

        [ ${PYTHON} == "C:\\Python370_x64" ]
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
    try:
        return eval(cond)
    except SyntaxError as e:
        raise SyntaxError(
            "Unable to interpret '{0}'\nvariables: {1}".format(cond, variables)) from e


def interpret_instruction(inst, variables=None):
    """
    Interprets an instruction with if statement.

    @param      inst        (str) instruction
    @param      variables   (dict|None)
    @return                 (str|None)

    Example of a statement::

        - if [ ${PYTHON} == "C:\\\\Python391_x64" ] then python setup.py build_sphinx fi

    Another example::

        - if [ ${VERSION} == "3.9" and ${DIST} == "std" ]
          then
            --CMD=$PYINT -u scikit-learn/bench_plot_polynomial_features_partial_fit.py;;
            --NAME=SKL_POLYF_PF;;
          fi

    In this second syntax, lines must end with ``;;``.
    If an instruction cannot be interpreted, it is left
    left unchanged as the function assumes it can only be solved
    in a bash script.

    .. versionchanged:: 1.8
        Switch to ``;;`` instead of ``;`` as a instruction separator
        for conditional instructions.
    """
    if isinstance(inst, list):
        res = [interpret_instruction(_, variables) for _ in inst]
        if any(res):
            return [_ for _ in res if _ is not None]
        return None
    if isinstance(inst, tuple):
        if len(inst) != 2 or inst[1] is None:
            raise ValueError(  # pragma: no cover
                "Unable to interpret '{}'.".format(inst))
        return (inst[0], interpret_instruction(inst[1], variables))
    if isinstance(inst, dict):
        return inst
    if isinstance(inst, (int, float)):
        return inst

    inst = inst.replace("\n", " ")
    exp = re.compile("^ *if +(.*) +then +(.*)( +else +(.*))? +fi *$")
    find = exp.search(inst)
    if find:
        gr = find.groups()
        try:
            e = evaluate_condition(gr[0], variables)
        except SyntaxError:
            # We assume the condition is a linux condition.
            return inst
        g = gr[1] if e else gr[3]
        return None if g is None else interpret_instruction(g, variables)

    if inst.startswith('--'):
        # one format like --CMD=...; --NAME==...;
        exp = re.compile("--([a-zA-Z]+?)=(.+?);;")
        find = exp.findall(inst)
        if find:
            inst = {k.strip(): v.strip() for k, v in find}
            inst = {k: (None if not v or len(v) == 0 else v)
                    for k, v in inst.items()}
            return inst
        return inst
    return inst


def enumerate_convert_yaml_into_instructions(obj, variables=None, add_environ=True):
    """
    Converts a :epkg:`yml` file into sequences of instructions,
    conditions are interpreted.

    @param      obj         yaml objects (@see fn load_yaml)
    @param      variables   additional variables to be used
    @param      add_environ add environment variables available, does not
                            overwrite existing variables
                            when the job is generated
    @return                 list of tuple(instructions, variables)

    The function expects the following list
    of steps in this order:

    * *automatedsetup*: added by this module
    * *language*: should be python
    * *python*: list of interpreters (multiplies jobs)
    * *virtualenv*: name of the virtual environment
    * *install*: list of installation steps in the virtual environment
    * *before_script*: list of steps to run
    * *script*: list of script to run (multiplies jobs)
    * *after_script*: list of steps to run
    * *documentation*: documentation to run after the

    Each step *multiplies jobs* creates a sequence of jobs and a :epkg:`Jenkins` job.
    """
    if variables is None:
        def_variables = {}
    else:
        def_variables = variables.copy()
    if 'Python37' in def_variables and 'Python38' not in def_variables:
        raise RuntimeError(  # pragma: no cover
            "Key 'Python38' is missing in {}.".format(def_variables))
    if add_environ:
        for k, v in os.environ.items():
            if k not in def_variables:
                def_variables[k] = v
    sequences = []
    count = {}
    steps = ["automatedsetup", "language", "python", "virtualenv", "install",
             "before_script", "script", "after_script",
             "documentation"]
    for key in steps:
        value = obj.get(key, None)
        if key == "language":
            if value != "python":
                raise NotImplementedError(  # pragma: no cover
                    "language must be python")
            continue  # pragma: no cover
        if value is not None:
            if key in {'python', 'script'} and not isinstance(value, list):
                value = [value]
            count[key] = len(value)
            sequences.append((key, value))

    for k in obj:
        if k not in steps:
            raise ValueError(
                "Unexpected key '{0}' found in yaml file. Expect:\n{1}".format(k, "\n".join(steps)))

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
                        raise KeyError(  # pragma: no cover
                            "The dictionary should include key 'path': {0}"
                            "".format(value))
                    for k, v in sorted(value.items()):
                        if k != 'PATH':
                            variables[k] = v
                            seq.append(('INFO', (k, v)))
                    value = value["PATH"]
            elif key == "script":
                value = interpret_instruction(value[i_script], variables)
                if isinstance(value, dict):
                    for k, v in sorted(value.items()):
                        if k not in ('CMD', 'CMDPY'):
                            seq.append(('INFO', (k, v)))
                            variables[k] = v

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


def ospathjoin(*args, **kwargs):
    """
    Simple ``o.path.join`` for a specific platform.

    @param      args        list of paths
    @param      kwargs      additional parameters, among them,
                            *platform* (win32 or ...)
    @return                 path
    """
    def build_value(*args, **kwargs):
        platform = kwargs.get('platform', None)
        if platform is None:
            return os.path.join(*args)
        elif platform.startswith("win"):
            return "\\".join(args)
        return "/".join(args)

    value = build_value(*args, **kwargs)
    if value == "/$PYINT":
        raise RuntimeError(  # pragma: no cover
            "Impossible values {} - {}.".format(args, kwargs))
    return value


def ospathdirname(lp, platform=None):
    """
    Simple ``o.path.dirname`` for a specific platform.

    @param      lp          path
    @param      platform    platform
    @return                 path
    """
    if platform is None:
        return os.path.dirname(lp)
    elif platform.startswith("win"):
        return "\\".join(lp.replace("/", "\\").split("\\")[:-1])
    return "/".join(lp.replace("\\", "/").split("/")[:-1])


def convert_sequence_into_batch_file(seq, variables=None, platform=None):
    """
    Converts a sequence of instructions into a batch file.

    @param      seq         sequence of instructions
    @param      variables   list of variables
    @param      platform    ``get_platform(platform)`` if None
    @return                 (str) batch file or a list of batch file if the constant ``JENKINS_SPLIT``
                            was found in section install (this tweak is needed when the job has to be split
                            for :epkg:`Jenkins`.
    """
    global _jenkins_split
    if platform is None:
        platform = get_platform(platform)

    iswin = platform.startswith("win")

    if iswin:
        error_level = "if %errorlevel% neq 0 exit /b %errorlevel%"
    else:
        error_level = "if [ $? -ne 0 ]; then exit $?; fi"

    interpreter = None
    venv_interpreter = None
    root_project = None
    anaconda = False
    conda = None
    echo = "@echo" if iswin else "echo"

    rowsset = []
    if iswin:
        rowsset.append("@echo off")
        rowsset.append("set PATH0=%PATH%")

    def add_path_win(rows, interpreter, platform, root_project):
        path_inter = ospathdirname(interpreter, platform)
        if len(path_inter) == 0:
            raise ValueError(  # pragma: no cover
                "Unable to guess interpreter path from '{0}', platform={1}"
                "".format(interpreter, platform))
        if iswin:
            rows.append("set PATH={0};%PATH%".format(path_inter))
        else:
            rows.append("export PATH={0}:$PATH".format(path_inter))
        if root_project is not None:
            if iswin:
                rows.append("set ROOTPROJECT={0}".format(root_project))
            else:
                rows.append("export ROOTPROJECT={0}".format(root_project))

    rows = []
    splits = [rows]
    typstr = str

    for key, value in seq:
        if key == "automatedsetup":
            rows.append("")
            rows.append(echo + " AUTOMATEDSETUP")
            rows.append("\n".join(value))
            rows.append("")
        elif key == "python":
            variables["YMLPYTHON"] = value
            if variables.get('DIST', None) == "conda":
                rows.append(echo + " conda")
                anaconda = True
                interpreter = ospathjoin(
                    value, "python", platform=platform)
                venv_interpreter = value
                if platform.startswith("win"):
                    conda = ospathjoin(
                        value, "Scripts", "conda", platform=platform)
                else:
                    conda = ospathjoin(
                        value, "bin", "conda", platform=platform)
            else:
                if iswin:
                    interpreter = ospathjoin(
                        value, "python", platform=platform)
                else:
                    interpreter = ospathjoin(
                        value, "$PYINT", platform=platform)
                venv_interpreter = value
            rows.append(echo + " interpreter=" + interpreter)

        elif key == "virtualenv":
            if isinstance(value, list):
                if len(value) != 1:
                    raise ValueError(  # pragma: no cover
                        "Expecting one value for the path of the virtual environment"
                        ":\n{0}".format(value))
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
                    '"{0}" create -y -v -p "{1}" --clone "{2}" --offline --no-update-deps'.format(conda, p, pinter))
                interpreter = ospathjoin(
                    p, "python", platform=platform)
            else:
                if iswin:
                    rows.append("set KEEPPATH=%PATH%")
                    rows.append("set PATH={0};%PATH%".format(venv_interpreter))
                else:
                    rows.append("export KEEPPATH=$PATH")
                    rows.append(
                        "export PATH={0}:$PATH".format(venv_interpreter))
                pat = '"{0}" -m virtualenv {1} --system-site-packages'
                rows.append(pat.format(interpreter, p))
                if iswin:
                    rows.append("set PATH=%KEEPPATH%")
                    interpreter = ospathjoin(
                        p, "Scripts", "python", platform=platform)
                else:
                    rows.append("export PATH=$KEEPPATH")
                    interpreter = ospathjoin(
                        p, "bin", "python", platform=platform)
            rows.append(error_level)

        elif key in {"install", "before_script", "script", "after_script", "documentation"}:
            if value is not None:
                if isinstance(value, dict):
                    if "CMD" not in value and "CMDPY" not in value:
                        raise KeyError(  # pragma: no cover
                            "A script defined by a dictionary must contain key "
                            "'{0}' or '{1}' in \n{2}".format("CMD", 'CMDPY', value))
                    if "NAME" in value:
                        if iswin:
                            rows.append("set JOB_NAME=%s" % value["NAME"])
                        else:
                            rows.append("export JOB_NAME=%s" % value["NAME"])
                    if "CMD" in value:
                        value = value["CMD"]
                    else:
                        value = evaluate_condition(
                            value["CMDPY"], variables=variables)
                elif isinstance(value, list):
                    starter = list(rows)
                elif isinstance(value, typstr):
                    pass
                else:
                    raise TypeError(  # pragma: no cover
                        "value must of type list, dict, not '{0}'\n{1}"
                        "".format(type(value), value))

                rows.append("")
                rows.append(echo + " " + key.upper())
                add_path_win(rows, interpreter, platform, root_project)
                if not isinstance(value, list):
                    value = [value, error_level]
                else:
                    keep = value
                    value = []
                    for v in keep:
                        if v.startswith(_jenkins_split):
                            if "-" in v:
                                nbrem = v.split("-")[-1]
                                try:
                                    nbrem = int(nbrem)
                                except ValueError as e:  # pragma: no cover
                                    raise ValueError(
                                        "Unable to interpret '{0}'".format(v))
                            else:
                                nbrem = 0
                            rows.extend(value)
                            value = []
                            st = list(starter)
                            if nbrem > 0:
                                st = st[:-nbrem]
                            splits.append(st)
                            rows = splits[-1]
                            add_path_win(rows, interpreter,
                                         platform, root_project)
                        else:
                            value.append(v)
                            value.append(error_level)
                rows.extend(value)
        elif key == 'INFO':
            vs = '"{0}"'.format(value[1]) if isinstance(
                value[1], str) and " " in value[1] else value[1]
            if iswin:
                rowsset.append("SET {0}={1}".format(value[0], vs))
            else:
                rowsset.append("export {0}={1}".format(value[0], vs))
        else:
            raise ValueError(  # pragma: no cover
                "unexpected key '{0}'".format(key))

    splits = [rowsset + _ for _ in splits]
    allres = []
    for rows in splits:
        try:
            res = "\n".join(rows)
        except TypeError as e:  # pragma: no cover
            raise TypeError("Unexpected type\n{0}".format(
                "\n".join([str((type(_), _)) for _ in rows]))) from e
        if _jenkins_split in res:
            raise ValueError(  # pragma: no cover
                "Constant '{0}' is present in the generated script. "
                "It can only be added to the install section."
                "".format(_jenkins_split))
        allres.append(res)
    return allres if len(allres) > 1 else allres[0]


def infer_project_name(file_or_buffer, source):
    """
    Infers a project name based on :epkg:`yml` file.

    @param      file_or_buffer      file name
    @param      source              second output of @see fn read_content_ufs
    @return                         name

    The function can infer a name for *source* in ``{'r', 'u'}``.
    For *source* equal to ``'s'``, it returns ``'unknown_string'``.
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
            raise ValueError(  # pragma: no cover
                "Unable to infer project name for '{0}'".format(
                    file_or_buffer))
        return name
    elif source == "s":
        return "unknown_string"
    else:
        raise ValueError(  # pragma: no cover
            "Unexpected value for add_source: '{0}' for '{1}'".format(
                source, file_or_buffer))
    return last


def enumerate_processed_yml(file_or_buffer, context=None, engine="jinja2", platform=None,
                            server=None, git_repo=None, add_environ=True, overwrite=False,
                            build_location=None, **kwargs):
    """
    Submits or enumerates jobs based on the content of a :epkg:`yml` file.

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

    Example of a :epkg:`yml` file
    `.local.jenkins.win.yml <https://github.com/sdpython/pyquickhelper/blob/master/.local.jenkins.win.yml>`_.
    A subfolder was added to the project location.
    A scheduler can be defined as well by adding ``SCHEDULER:'* * * * *'``.
    """
    typstr = str
    fLOG = kwargs.get('fLOG', None)
    project_name = None if context is None else context.get(
        "project_name", None)
    obj, project_name = load_yaml(
        file_or_buffer, context=context, platform=platform)
    platform_set = platform or get_platform(platform)
    for seq, var in enumerate_convert_yaml_into_instructions(obj, variables=context, add_environ=add_environ):
        conv = convert_sequence_into_batch_file(
            seq, variables=var, platform=platform)

        # we extract a suffix from the command line
        if server is not None:
            name = "_".join([project_name, var.get('NAME', ''),
                             typstr(var.get("VERSION", '')).replace(".", ""),
                             var.get('DIST', '')])

            if platform_set.startswith("win"):
                if isinstance(conv, list):
                    conv = ["SET NAME_JENKINS=" +
                            name + "\n" + _ for _ in conv]
                else:
                    conv = "SET NAME_JENKINS=" + name + "\n" + conv
            else:
                if isinstance(conv, list):
                    conv = ["export NAME_JENKINS=" +
                            name + "\n" + _ for _ in conv]
                    conv.append("export $(cat ~/.profile)")
                else:
                    conv = ("export NAME_JENKINS=" + name +
                            "\nexport $(cat ~/.profile)\n" + conv)

            import jenkins
            try:
                j = server.get_job_config(name) if not server._mock else None
            except jenkins.NotFoundException:  # pragma: no cover
                j = None
            except jenkins.JenkinsException as e:  # pragma: no cover
                from .jenkins_exceptions import JenkinsExtException
                raise JenkinsExtException(
                    "Unable to retrieve job config for name='{0}'.".format(name)) from e

            update_job = False
            if j is not None:
                if kwargs.get('update', True):
                    update_job = True
                else:
                    if fLOG is not None:  # pragma: no cover
                        fLOG("[jenkins] delete job", name)
                    server.delete_job(name)

            if git_repo is not None and project_name not in git_repo:
                git_repo += project_name

            # set up location
            if build_location is None:
                loc = None
            else:
                loc = ospathjoin(build_location, project_name,
                                 name, platform=platform)

            if overwrite or j is None:
                timeout = var.get("TIMEOUT", None)
                scheduler = var.get("SCHEDULER", None)
                clean_repo = var.get("CLEAN", True) in {
                    True, 1, "True", "true", "1"}
                if timeout is not None:
                    kwargs["timeout"] = timeout
                if scheduler is not None:
                    if "FIXED" in scheduler:
                        scheduler = scheduler.replace("FIXED", "").strip()
                        adjuster_scheduler = False
                    elif "STARTUP" in scheduler:
                        adjuster_scheduler = False
                    elif 'fixed' in scheduler.lower():
                        raise ValueError(  # pragma: no cover
                            "Scheduler should contain 'FIXED' in upper case.")
                    elif 'startup' in scheduler.lower():
                        raise ValueError(  # pragma: no cover
                            "Scheduler should contain 'STARTUP' in upper case.")
                    else:
                        adjuster_scheduler = True
                    kwargs["scheduler"] = scheduler
                    kwargs["adjuster_scheduler"] = adjuster_scheduler
                yield server.create_job_template(name, script=conv, git_repo=git_repo,
                                                 update=update_job, location=loc,
                                                 clean_repo=clean_repo, **kwargs), name, var
        else:
            yield conv, None, var
