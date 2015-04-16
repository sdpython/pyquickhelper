#-*- coding:utf-8 -*-
"""
@file
@brief To format a pandas dataframe
"""


def len_modified(s):
    """
    estimate the length of a string for rst (issues with utf8 characters)

    @param      s       string
    @return             length

    The function is currently calling ``len`` but it returns some issues if the
    encoding was not ``utf8``.
    """
    if not isinstance(s, str  # unicode#
                      ):
        raise TypeError("expect a string, got {0}".format(type(s)))
    return len(s)


def df2rst(df, add_line=True, align=None):
    """
    builds a string in RST format from a dataframe
    @param      df              dataframe
    @param      add_line        (bool) add a line separator between each row
    @param      align           a string in [l,r,c,p{5cm}] or a list of the same,
                                or something like ``['1x','2x','5x']`` to specify a ratio
                                between column (alignment is left)
    @return                     string

    It produces the following results:

    @code
    +------------------------+------------+----------+----------+
    | Header row, column 1   | Header 2   | Header 3 | Header 4 |
    | (header rows optional) |            |          |          |
    +========================+============+==========+==========+
    | body row 1, column 1   | column 2   | column 3 | column 4 |
    +------------------------+------------+----------+----------+
    | body row 2             | ...        | ...      |          |
    +------------------------+------------+----------+----------+
    @endcode
    """
    length = [len_modified(_) for _ in df.columns]
    for row in df.values:
        for i, v in enumerate(row):
            length[i] = max(length[i], len_modified(str  # unicode#
                                                    (v)))

    if align is not None:
        if isinstance(align, str  # unicode#
                      ):
            align = [align] * len_modified(length)

        if isinstance(align, list):
            if len(align) != len(length):
                raise ValueError(
                    "align has not a good length: {0} and {1}".format(str(align), str(df.columns)))
            ratio = len([_ for _ in align if "x" in _]) > 0
            if ratio:
                head = ""
                ratio = []
                for _ in align:
                    try:
                        i = int(_.strip(" x"))
                        ratio.append(i)
                    except:
                        raise ValueError(
                            "unable to parse {0} in {1}".format(_, str(align)))

                mini = max(length)
                length2 = [mini * r for r in ratio]

                # we reduce
                for i in range(8, 1, -1):
                    length3 = [k // i for k in length2]
                    notgood = [k < l for k, l in zip(length3, length)]
                    notgood = [_ for _ in notgood if _]
                    if not notgood:
                        length2 = length3
                        break
                length = length2
            else:
                head = ".. tabularcolumns:: " + \
                    "|%s|" % "|".join(align) + "\n\n"
        else:
            raise TypeError(str(type(align)))
    else:
        head = ""

    ic = 3
    length = [_ + ic for _ in length]
    line = ["-" * l for l in length]
    lineb = ["=" * l for l in length]
    sline = "+%s+" % ("+".join(line))
    slineb = "+%s+" % ("+".join(lineb))
    res = [sline]

    def complete(cool):
        s, i = cool
        s = str(s) + " "
        i -= 2
        if len_modified(s) < i:
            s += " " * (i - len_modified(s))
        return s

    res.append("| %s |" % " | ".join(map(complete, zip(df.columns, length))))
    res.append(slineb)
    res.extend(["| %s |" % " | ".join(map(complete, zip(row, length)))
                for row in df.values])
    if add_line:
        t = len(res)
        for i in range(t - 1, 3, -1):
            res.insert(i, sline)
    res.append(sline)
    table = "\n".join(res) + "\n"

    return head + table


def df2html(self, class_table=None, class_td=None, class_tr=None,
            class_th=None):
    """
    convert the table into a html string

    @param  class_table     adds a class to the tag ``table`` (None for none)
    @param  class_td        adds a class to the tag ``td`` (None for none)
    @param  class_tr        adds a class to the tag ``tr`` (None for none)
    @param  class_th        adds a class to the tag ``th`` (None for none)
    """
    clta = ' class="%s"' % class_table if class_table is not None else ""
    cltr = ' class="%s"' % class_tr if class_tr is not None else ""
    cltd = ' class="%s"' % class_td if class_td is not None else ""
    clth = ' class="%s"' % class_th if class_th is not None else ""

    rows = ["<table%s>" % clta]
    rows.append(("<tr%s><th%s>" % (cltr, clth)) + ("</th><th%s>" %
                                                   clth).join(self.columns) + "</th></tr>")
    septd = "</td><td%s>" % cltd
    strtd = "<tr%s><td%s>" % (cltr, cltd)
    for row in self.values:
        s = septd.join([str(_) for _ in row])
        rows.append(strtd + s + "</td></tr>")
    rows.append("</table>")
    rows.append("")
    return "\n".join(rows)
