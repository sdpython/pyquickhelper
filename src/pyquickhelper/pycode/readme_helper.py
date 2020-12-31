"""
@file
@brief Helpers about readme.
"""


def clean_readme(content):
    """
    Clean instructions such as ``.. only:: html``.

    @param      content     content of an rst file
    @return                 cleaned content
    """
    lines = content.split("\n")
    indent = None
    less = None
    rows = []
    for i, line in enumerate(lines):
        sline = line.lstrip()
        if sline.startswith(".. only:: html"):
            indent = len(line) - len(sline)
            continue
        if indent is None:
            rows.append(line)
            continue
        exp = indent * " "
        if len(line) > indent + 1 and line[:indent] == exp:
            if line[indent] == " ":
                blank = sline.strip()
                if len(blank) == 0:
                    rows.append("")  # pragma: no cover
                    continue  # pragma: no cover
                if less is None:
                    less = len(line) - len(sline)
                    if less == indent:
                        raise ValueError(  # pragma: no cover
                            "Wrong format at line {0}\n{1}".format(
                                i, content))
                new_line = line[less - indent:]
                rows.append(new_line)
            else:
                rows.append(line)
                indent = None
                less = None
        else:
            rows.append(line)
    return "\n".join(rows)
