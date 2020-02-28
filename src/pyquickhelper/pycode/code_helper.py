"""
@file
@brief Various function to clean the code.
"""
import os


def remove_extra_spaces_and_pep8(filename, apply_pep8=True, aggressive=False, is_string=None):
    """
    Removes extra spaces in a filename, replaces the file in place.

    @param      filename        file name or string (but it assumes it is python).
    @param      apply_pep8      if True, calls :epkg:`autopep8` on the file
    @param      aggressive      more aggressive
    @param      is_string       force *filename* to be a string
    @return                     number of removed extra spaces
    """
    encoding = None
    initial_content = None
    if "\n" in filename or (is_string is not None and is_string):
        ext = ".py"
        lines = filename.replace("\r", "").split("\n")
        filename = None
    else:
        ext = os.path.splitext(filename)[-1]
        if ext in (".bat", ".py", ".sh", ".pyx", ".pxd"):
            try:
                with open(filename, "r") as f:
                    lines = f.readlines()
                encoding = None
            except PermissionError as e:
                raise PermissionError(filename) from e
            except UnicodeDecodeError as e:
                try:
                    with open(filename, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    encoding = "utf-8"
                except Exception:
                    raise Exception(
                        "unable to load file {} due to unicode errors".format(filename)) from e
            initial_content = "".join(lines)
        else:
            try:
                with open(filename, "r", encoding="utf-8-sig") as f:
                    lines = f.readlines()
                encoding = "utf-8"
            except PermissionError as e:
                raise PermissionError(filename) from e
            except UnicodeDecodeError as e:
                try:
                    with open(filename, "r") as f:
                        lines = f.readlines()
                    encoding = None
                except Exception:
                    raise Exception(
                        "unable to load file {} due to unicode errors".format(filename)) from e
            initial_content = "".join(lines)

    if filename is not None and len(lines) == 0 and not filename.endswith("__init__.py"):
        raise ValueError(
            "File '{0}' is empty, encoding='{1}'.".format(filename, encoding))

    if filename is not None and ext in (".py", ".pyx", ".pxd"):
        if encoding is not None and len(lines) > 0 and "#-*-coding:utf-8-*-" in lines[0].replace(" ", ""):
            with open(filename, "r", encoding="utf8") as f:
                try:
                    lines = f.readlines()
                except UnicodeDecodeError as e:
                    raise Exception("unable to read: " + filename) from e
            encoding = "utf8"
        else:
            encoding = None

    def cdiff(lines):
        lines2 = [_.rstrip(" \r\n") for _ in lines]
        last = len(lines2) - 1
        while last >= 0 and len(lines2[last]) == 0:
            last -= 1
        last += 1
        lines2 = lines2[:last]

        diff = len("".join(lines)) - len("\n".join(lines2)) + len(lines)
        return diff, lines2

    diff, lines2 = cdiff(lines)

    if filename is not None:
        ext = os.path.splitext(filename)[-1]
    if ext in (".py", ) and apply_pep8:
        # delayed import to speed up import of pycode
        import autopep8
        options = ['', '-a'] if aggressive else ['']
        options.extend(["--ignore=E402,E731"])
        r = autopep8.fix_code(
            "\n".join(lines2), options=autopep8.parse_args(options))

        if len(lines) > 0 and (len(lines2) == 0 or len(lines2) < len(lines) // 2):
            raise ValueError("Resulting file is empty for '{3}',\ninitial number of lines {0} encoding='{1}' diff={2}".format(
                len(lines), encoding, diff, filename))
        if filename is None:
            return r
        elif r != initial_content:
            if encoding is None:
                with open(filename, "w") as f:
                    f.write(r)
            else:
                with open(filename, "w", encoding="utf8") as f:
                    f.write(r)
        if r != "".join(lines):
            diff, lines2 = cdiff(r.split("\n"))
        else:
            diff = 0
    elif ext in (".rst", ".md", ".pyx", ".pxd"):
        lines2 = [_.replace("\r", "").rstrip("\n ") for _ in lines]
        rem = set()
        for i, line in enumerate(lines2):
            if i >= 1 and line == lines2[i - 1] == "":
                rem.add(i)
        lines2 = [_ for i, _ in enumerate(lines2) if i not in rem]
        if len(lines) > 0 and len(lines2[-1]) > 0:
            lines2.append("")
        if len(lines) > 0 and len(lines2) == 0:
            begin = 5 if len(lines) > 5 else len(lines)
            mes = "Resulting file is empty for '{4}',\ninitial number of lines {0} encoding='{1}' len(rem)={2} diff={3}\nBeginning:\n{5}"
            raise ValueError(mes.format(len(lines), encoding, len(
                rem), diff, filename, "".join(lines[:begin])))
        if len(lines2) < len(lines) // 2:
            lines2_ = [_ for _ in lines2 if _ and _ != "\n"]
            lines_ = [_ for _ in lines if _ and _ != "\n"]
            if len(lines2_) < len(lines_) // 2:
                begin = 5 if len(lines_) > 5 else len(lines_)
                mes = "Resulting file is almost empty for '{4}',\ninitial number of lines {0} encoding='{1}' " + \
                      "len(rem)={2} diff={3}\nBeginning:\n{5}"
                raise ValueError(mes.format(len(lines_), encoding, len(
                    rem), diff, filename, "".join(lines_[:begin])))
        rl = "".join(lines)
        r2 = "\n".join(lines2)
        if r2 != rl:
            if encoding is None:
                with open(filename, "w") as f:
                    f.write("\n".join(lines2))
            else:
                with open(filename, "w", encoding="utf8") as f:
                    f.write("\n".join(lines2))
            diff = max(1, diff)
        else:
            diff = 0
    elif diff != 0:
        if len(lines) > 0 and (len(lines2) == 0 or len(lines2) < len(lines) // 2):
            raise ValueError("Resulting file is empty for '{3}',\ninitial number of lines {0} encoding='{1}' diff={2}".format(
                len(lines), encoding, diff, filename))
        r1 = "".join(lines)
        r2 = "\n".join(lines2)
        if r2 != r1:
            if encoding is None:
                with open(filename, "w") as f:
                    f.write("\n".join(lines2))
            else:
                with open(filename, "w", encoding="utf8") as f:
                    f.write("\n".join(lines2))

    if not os.path.exists(filename):
        raise FileNotFoundError(
            "issue when applying autopep8 with filename: {0}".format(filename))
    return diff


def remove_extra_spaces_folder(
        folder, extensions=(".py", ".rst", ".md", ".pyx", ".pxd"), apply_pep8=True,
        file_filter=None):
    """
    Removes extra files in a folder for specific file extensions.

    @param      folder          folder to explore
    @param      extensions      list of file extensions to process
    @param      apply_pep8      if True, calls :epkg:`autopep8` on the file
    @param      file_filter     None of function which filters based on the filename
    @return                     the list of modified files

    The function does not check files having
    ``/build/`` or ``/dist/`` or ``temp_``
    or ``/build2/`` or ``/build3/``
    in their name.

    The signature of *file_filter* is the following:

    ::

        def file_filter(filename):
            return True or False
    """
    # delayed import to speed up import of .pycode
    from ..filehelper.synchelper import explore_folder
    neg_pattern = "|".join("[/\\\\]{0}[/\\\\]".format(_) for _ in ["build", "build2", "build3",
                                                                   "dist", "_venv", "_todo", "dist_module27", "_virtualenv"])
    files = explore_folder(folder, neg_pattern=neg_pattern, fullname=True)[1]
    mod = []
    for f in files:
        fl = f.lower().replace("\\", "/")
        if "/temp_" not in fl and "/build/" not in fl \
                and "/dist/" not in fl \
                and "/build2/" not in fl \
                and "/build3/" not in fl \
                and "/_virtualenv/" not in fl \
                and ".egg/" not in fl \
                and "/_venv/" not in fl \
                and "/_todo/" not in fl \
                and "/dist_module27" not in fl \
                and "automation_done.rst" not in fl \
                and "auto_import.rst" not in fl \
                and os.stat(f).st_size < 200000 \
                and (file_filter is None or file_filter(f)):
            ext = os.path.splitext(f)[-1]
            if ext in extensions:
                d = remove_extra_spaces_and_pep8(f, apply_pep8=apply_pep8)
                if d != 0:
                    mod.append(f)
    return mod
