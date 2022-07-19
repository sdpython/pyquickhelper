# -*- coding:utf-8 -*-
"""
@file
@brief To format a pandas dataframe
"""
import warnings


def enumerate_split_df(df, common, subsets):
    """
    Splits a dataframe by columns to display shorter
    dataframes.

    @param      df      dataframe
    @param      common  common columns
    @param      subsets subsets of columns
    @return             split dataframes

    .. runpython::
        :showcode:

        from pandas import DataFrame
        from pyquickhelper.pandashelper.tblformat import enumerate_split_df

        df = DataFrame([{'A': 0, 'B': 'text'},
                        {'A': 1e-5, 'C': 'longer text'}])
        res = list(enumerate_split_df(df, ['A'], [['B'], ['C']]))
        print(res[0])
        print('-----')
        print(res[1])
    """
    for sub in subsets:
        if set(common) & set(sub):
            raise ValueError("Common columns between common={} and subset={}.".format(
                common, sub))
        yield df[common + sub]


def df2rst(df, add_line=True, align="l", column_size=None, index=False,
           list_table=False, title=None, header=True, sep=',',
           number_format=None, replacements=None, split_row=None,
           split_row_level="+", split_col_common=None,
           split_col_subsets=None, filter_rows=None,
           label_pattern=None):
    """
    Builds a string in :epkg:`RST` format from a :epkg:`dataframe`.

    :param df: dataframe
    :param add_line: (bool) add a line separator between each row
    :param align: ``r`` or ``l`` or ``c``
    :param column_size: something like ``[1, 2, 5]`` to multiply the column size,
        a dictionary (if *list_table* is False) to overwrite
        a column size like ``{'col_name1': 20}`` or ``{3: 20}``
    :param index: add the index
    :param list_table: use the
        `list_table <http://docutils.sourceforge.net/docs/ref/rst/directives.html#list-table>`_
    :param title: used only if *list_table* is True
    :param header: add one header
    :param sep: separator if *df* is a string and is a filename to load
    :param number_format: formats number in a specific way, if *number_format*
        is an integer, the pattern is replaced by
        ``{numpy.float64: '{:.2g}'}`` (if *number_format* is 2),
        see also :epkg:`pyformat.info`
    :param replacements: replacements just before converting into RST (dictionary)
    :param split_row: displays several table, one column is used as the
        name of each section
    :param split_row_level: title level if option *split_row* is used
    :param split_col_common: splits the dataframe by columns, see @see fn enumerate_split_df
    :param split_col_subsets: splits the dataframe by columns, see @see fn enumerate_split_df
    :param filter_rows: None or function to removes rows, signature
        ``def filter_rows(df: DataFrame) -> DataFrame``
    :param label_pattern: if *split_row* is used, the function may insert
        a label in front of every section, example: ``".. _lpy-{section}:"``
    :return: string

    If *list_table* is False, the format is the following.

    *None* values are replaced by empty string (4 spaces).
    It produces the following results:

    ::

        +------------------------+------------+----------+----------+
        | Header row, column 1   | Header 2   | Header 3 | Header 4 |
        | (header rows optional) |            |          |          |
        +========================+============+==========+==========+
        | body row 1, column 1   | column 2   | column 3 | column 4 |
        +------------------------+------------+----------+----------+
        | body row 2             | ...        | ...      |          |
        +------------------------+------------+----------+----------+

    If *list_table* is True, the format is the following:

    ::

        .. list-table:: title
            :widths: 15 10 30
            :header-rows: 1

            * - Treat
              - Quantity
              - Description
            * - Albatross
              - 2.99
              - anythings
            ...

    .. exref::
        :title: Convert a dataframe into RST

        .. runpython::
            :showcode:

            from pandas import DataFrame
            from pyquickhelper.pandashelper import df2rst

            df = DataFrame([{'A': 0, 'B': 'text'},
                            {'A': 1e-5, 'C': 'longer text'}])
            print(df2rst(df))

    .. exref::
        :title: Convert a dataframe into markdown

        .. runpython::
            :showcode:

            from io import StringIO
            from textwrap import dedent
            import pandas

            from_excel = dedent('''
            Op;axes;shape;SpeedUp
            ReduceMax;(3,);(8, 24, 48, 8);2.96
            ReduceMax;(3,);(8, 24, 48, 16);2.57
            ReduceMax;(3,);(8, 24, 48, 32);2.95
            ReduceMax;(3,);(8, 24, 48, 64);3.28
            ReduceMax;(3,);(8, 24, 48, 100);3.05
            ReduceMax;(3,);(8, 24, 48, 128);3.11
            ReduceMax;(3,);(8, 24, 48, 200);2.86
            ReduceMax;(3,);(8, 24, 48, 256);2.50
            ReduceMax;(3,);(8, 24, 48, 400);2.48
            ReduceMax;(3,);(8, 24, 48, 512);2.90
            ReduceMax;(3,);(8, 24, 48, 1024);2.76
            ReduceMax;(0,);(8, 24, 48, 8);19.29
            ReduceMax;(0,);(8, 24, 48, 16);11.83
            ReduceMax;(0,);(8, 24, 48, 32);5.69
            ReduceMax;(0,);(8, 24, 48, 64);5.49
            ReduceMax;(0,);(8, 24, 48, 100);6.13
            ReduceMax;(0,);(8, 24, 48, 128);6.27
            ReduceMax;(0,);(8, 24, 48, 200);5.46
            ReduceMax;(0,);(8, 24, 48, 256);4.76
            ReduceMax;(0,);(8, 24, 48, 400);2.21
            ReduceMax;(0,);(8, 24, 48, 512);4.52
            ReduceMax;(0,);(8, 24, 48, 1024);4.38
            ReduceSum;(3,);(8, 24, 48, 8);1.79
            ReduceSum;(3,);(8, 24, 48, 16);0.79
            ReduceSum;(3,);(8, 24, 48, 32);1.67
            ReduceSum;(3,);(8, 24, 48, 64);1.19
            ReduceSum;(3,);(8, 24, 48, 100);2.08
            ReduceSum;(3,);(8, 24, 48, 128);2.96
            ReduceSum;(3,);(8, 24, 48, 200);1.66
            ReduceSum;(3,);(8, 24, 48, 256);2.26
            ReduceSum;(3,);(8, 24, 48, 400);1.76
            ReduceSum;(3,);(8, 24, 48, 512);2.61
            ReduceSum;(3,);(8, 24, 48, 1024);2.21
            ReduceSum;(0,);(8, 24, 48, 8);2.56
            ReduceSum;(0,);(8, 24, 48, 16);2.05
            ReduceSum;(0,);(8, 24, 48, 32);3.04
            ReduceSum;(0,);(8, 24, 48, 64);2.57
            ReduceSum;(0,);(8, 24, 48, 100);2.41
            ReduceSum;(0,);(8, 24, 48, 128);2.77
            ReduceSum;(0,);(8, 24, 48, 200);2.02
            ReduceSum;(0,);(8, 24, 48, 256);1.61
            ReduceSum;(0,);(8, 24, 48, 400);1.59
            ReduceSum;(0,);(8, 24, 48, 512);1.48
            ReduceSum;(0,);(8, 24, 48, 1024);1.50
            ''')

            df = pandas.read_csv(StringIO(from_excel), sep=";")
            print(df.columns)

            sub = df[["Op", "axes", "shape", "SpeedUp"]]
            piv = df.pivot_table(values="SpeedUp", index=['axes', "shape"], columns="Op")
            piv = piv.reset_index(drop=False)

            print(piv.to_markdown(index=False))

    .. versionchanged:: 1.9
        Nan value are replaced by empty string even if
        *number_format* is not None.
        Parameters *replacements*, *split_row*, *split_col_subsets*,
        *split_col_common*, *filter_rows* were added.
    """
    if isinstance(df, str):
        import pandas  # pragma: no cover
        df = pandas.read_csv(  # pragma: no cover
            df, encoding="utf-8", sep=sep)

    if split_row is not None:
        gdf = df.groupby(split_row)
        rows = []
        for key, g in gdf:
            key = str(key).strip('()')
            if ':ref:' in key:
                try:
                    key = key.split("`")[1].split("<")[0].strip()
                except IndexError:  # pragma: no cover
                    pass
            if label_pattern is not None:
                lab = label_pattern.format(section=key.replace(".", "D"))
                rows.append("")
                rows.append(lab)
            rows.append("")
            rows.append(key)
            rows.append(split_row_level * len(key))
            rows.append("")
            rg = df2rst(g, add_line=add_line, align=align,
                        column_size=column_size, index=index,
                        list_table=list_table,
                        title=title, header=header, sep=sep,
                        number_format=number_format, replacements=replacements,
                        split_row=None, split_row_level=None,
                        split_col_common=split_col_common,
                        split_col_subsets=split_col_subsets,
                        filter_rows=filter_rows,
                        label_pattern=None)
            rows.append(rg)
            rows.append("")
        return "\n".join(rows)

    if split_col_common is not None:
        rows = []
        for sub in enumerate_split_df(df, split_col_common, split_col_subsets):
            rg = df2rst(sub, add_line=add_line, align=align,
                        column_size=column_size, index=index,
                        list_table=list_table,
                        title=title, header=header, sep=sep,
                        number_format=number_format,
                        replacements=replacements,
                        filter_rows=filter_rows)
            rows.append(rg)
            rows.append('')
        return "\n".join(rows)

    import numpy
    typstr = str

    if filter_rows is not None:
        df = filter_rows(df).copy()
        if df.shape[0] == 0:
            return ""
    else:
        df = df.copy()

    def patternification(value, pattern):
        if isinstance(value, float) and numpy.isnan(value):
            return ""
        return pattern.format(value)

    def nan2empty(value):
        if isinstance(value, float) and numpy.isnan(value):
            return ""
        return value

    if number_format is not None:
        if isinstance(number_format, int):
            number_format = "{:.%dg}" % number_format
            import pandas
            typ1 = numpy.float64
            _df = pandas.DataFrame({'f': [0.12]})
            typ2 = list(_df.dtypes)[0]
            number_format = {typ1: number_format, typ2: number_format}
        df = df.copy()
        for name, typ in zip(df.columns, df.dtypes):
            if name in number_format:
                pattern = number_format[name]
                df[name] = df[name].apply(
                    lambda x: patternification(x, pattern))
            elif typ in number_format:
                pattern = number_format[typ]
                df[name] = df[name].apply(
                    lambda x: patternification(x, pattern))

    # check empty strings
    col_strings = df.select_dtypes(include=[object]).columns
    for c in col_strings:
        df[c] = df[c].apply(nan2empty)

    if index:
        df = df.reset_index(drop=False).copy()
        ind = df.columns[0]

        def boldify(x):
            try:
                return f"**{x}**"
            except Exception as e:  # pragma: no cover
                raise Exception(
                    f"Unable to boldify type {type(x)}") from e

        try:
            values = df[ind].apply(boldify)
        except Exception:  # pragma: no cover
            warnings.warn("Unable to boldify the index (1).", SyntaxWarning)

        try:
            df[ind] = values
        except Exception:  # pragma: no cover
            warnings.warn("Unable to boldify the index (2).", SyntaxWarning)

    def align_string(s, align, length):
        if len(s) < length:
            if align == "l":
                return s + " " * (length - len(s))
            if align == "r":
                return " " * (length - len(s)) + s
            if align == "c":
                m = (length - len(s)) // 2
                return " " * m + s + " " * (length - m - len(s))
            raise ValueError(  # pragma: no cover
                f"align should be 'l', 'r', 'c' not '{align}'")
        return s

    def complete(cool):
        if list_table:
            i, s = cool
            if s is None:
                s = ""  # pragma: no cover
            if isinstance(s, float) and numpy.isnan(s):
                s = ""
            else:
                s = typstr(s).replace("\n", " ")
            if replacements is not None:
                if s in replacements:
                    s = replacements[s]
            return (" " + s) if s else s
        else:
            i, s = cool
            if s is None:
                s = " " * 4  # pragma: no cover
            if isinstance(s, float) and numpy.isnan(s):
                s = ""  # pragma: no cover
            else:
                s = typstr(s).replace("\n", " ")
            i -= 2
            if replacements is not None:
                if s in replacements:
                    s = replacements[s]
            s = align_string(s.strip(), align, i)
            return s

    if list_table:

        def format_on_row(row):
            one = "\n      -".join(map(complete, enumerate(row)))
            res = "    * -" + one
            return res

        rows = [f".. list-table:: {title if title else ''}".strip()]
        if column_size is None:
            rows.append("    :widths: auto")
        else:
            rows.append("    :widths: " + " ".join(map(str, column_size)))
        if header:
            rows.append("    :header-rows: 1")
        rows.append("")
        if header:
            rows.append(format_on_row(df.columns))
        rows.extend(map(format_on_row, df.values))
        rows.append("")
        table = "\n".join(rows)
        return table
    else:
        length = [(len(_) if isinstance(_, typstr) else 5) for _ in df.columns]
        for row in df.values:
            for i, v in enumerate(row):
                length[i] = max(length[i], len(typstr(v).strip()))
        if column_size is not None:
            if isinstance(column_size, list):
                if len(length) != len(column_size):
                    raise ValueError(  # pragma: no cover
                        "length and column_size should have the same size {0} != {1}".format(
                            len(length), len(column_size)))
                for i in range(len(length)):
                    if not isinstance(column_size[i], int):
                        raise TypeError(  # pragma: no cover
                            f"column_size[{i}] is not an integer")
                    length[i] *= column_size[i]
            elif isinstance(column_size, dict):
                for i, c in enumerate(df.columns):
                    if c in column_size:
                        length[i] = column_size[c]
                    elif i in column_size:
                        length[i] = column_size[i]
            else:
                raise TypeError(  # pragma: no cover
                    "column_size must be a list or a dictionary not {}".format(
                        type(column_size)))

        ic = 2
        length = [_ + ic for _ in length]
        line = ["-" * lc for lc in length]
        lineb = ["=" * lc for lc in length]
        sline = f"+{'+'.join(line)}+"
        slineb = f"+{'+'.join(lineb)}+"
        res = [sline]

        res.append(f"| {' | '.join(map(complete, zip(length, df.columns)))} |")
        res.append(slineb)
        res.extend([f"| {' | '.join(map(complete, zip(length, row)))} |"
                    for row in df.values])
        if add_line:
            t = len(res)
            for i in range(t - 1, 3, -1):
                res.insert(i, sline)
        res.append(sline)
        table = "\n".join(res) + "\n"
        return table


def df2html(self, class_table=None, class_td=None, class_tr=None,
            class_th=None):
    """
    Converts the table into a :epkg:`html` string.

    :param self: dataframe (to be added as a class method)
    :param class_table: adds a class to the tag ``table`` (None for none)
    :param class_td: adds a class to the tag ``td`` (None for none)
    :param class_tr: adds a class to the tag ``tr`` (None for none)
    :param class_th: adds a class to the tag ``th`` (None for none)
    :return: HTML
    """
    clta = f' class="{class_table}"' if class_table is not None else ""
    cltr = f' class="{class_tr}"' if class_tr is not None else ""
    cltd = f' class="{class_td}"' if class_td is not None else ""
    clth = f' class="{class_th}"' if class_th is not None else ""

    rows = [f"<table{clta}>"]
    rows.append(f"<tr{cltr}><th{clth}>" + ("</th><th%s>" %
                                                   clth).join(self.columns) + "</th></tr>")
    septd = f"</td><td{cltd}>"
    strtd = f"<tr{cltr}><td{cltd}>"

    typstr = str

    def conv(s):
        if s is None:
            return ""  # pragma: no cover
        return typstr(s)

    for row in self.values:
        s = septd.join(conv(_) for _ in row)
        rows.append(strtd + s + "</td></tr>")
    rows.append("</table>")
    rows.append("")
    return "\n".join(rows)
