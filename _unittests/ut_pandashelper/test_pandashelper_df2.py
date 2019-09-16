"""
@brief      test log(time=3s)
"""

import os
import unittest
import numpy
import pandas
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pandashelper import df2html, df2rst


class TestPandasHelper_df2(ExtTestCase):

    def test_df2html(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2html(df)
        self.assertStartsWith("<table>", conv)
        self.assertEndsWith("</table>\n", conv)

    def test_df2rst(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2rst(df)
        self.assertIn("| city      | year | time     | seconds |", conv)
        self.assertIn("| PARIS     | 2011 | 02:06:29 | 7589    |", conv)

    def test_df2rst_split_row(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2rst(df, split_row="city")
        self.assertIn("+++++++++", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)
        self.assertIn("| PARIS | 2011 | 02:06:29 | 7589    |", conv)

        conv = df2rst(df, split_row="year")
        self.assertIn("++++", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)
        self.assertIn("| FUKUOKA   | 1976 | 02:12:35 | 7955    |", conv)

        conv = df2rst(df, split_row=["city", "year"])
        self.assertIn("'AMSTERDAM', 1975", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)

    def test_df2rst_split_row_label(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2rst(df, split_row="city")
        self.assertIn("+++++++++", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)
        self.assertIn("| PARIS | 2011 | 02:06:29 | 7589    |", conv)

        conv = df2rst(df, split_row="year", label_pattern=".. _lpy-{section}:")
        self.assertIn("++++", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)
        self.assertIn("| FUKUOKA   | 1976 | 02:12:35 | 7955    |", conv)
        self.assertIn(".. _lpy-1949:", conv)

    def test_df2rst_split_col(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        self.assertRaise(lambda: df2rst(df, split_col_common=["city", "time"],
                                        split_col_subsets=[['time'], ['seconds']]),
                         ValueError)
        conv = df2rst(df, split_col_common=["city", "year"],
                      split_col_subsets=[['time'], ['seconds']])
        self.assertIn("| CHICAGO   | 2005 | 7622    |", conv)

    def test_df2rst_split_col_row(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2rst(df, split_row="city",
                      split_col_common=["city", "year"],
                      split_col_subsets=[['time'], ['seconds']])
        self.assertIn("+++++++++", conv)
        self.assertIn("| STOCKOLM | 2007 | 8456    |", conv)

    def test_df2rst_split_col_row_ref(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        df['city'] = df.city.apply(
            lambda v: ':ref:`{0} <{0}-h>`'.format(v))  # pylint: disable=W0108
        conv = df2rst(df, split_row="city",
                      split_col_common=["city", "year"],
                      split_col_subsets=[['time'], ['seconds']])
        self.assertIn("+++++++++", conv)
        self.assertIn(
            "| :ref:`AMSTERDAM <AMSTERDAM-h>` | 1982 | 02:12:15 |", conv)

    def test_df2rst_split_col_row_ref2(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        df['city'] = df.city.apply(
            lambda v: ':ref:`{0}`'.format(v))  # pylint: disable=W0108
        conv = df2rst(df, split_row="city",
                      split_col_common=["city", "year"],
                      split_col_subsets=[['time'], ['seconds']])
        self.assertIn("+++++++++", conv)
        self.assertIn("| :ref:`AMSTERDAM` | 1982 | 02:12:15 |", conv)

    def test_df2rst_split_col_row_ref2_func(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        df['city'] = df.city.apply(
            lambda v: ':ref:`{0}`'.format(v))  # pylint: disable=W0108
        conv = df2rst(df, split_row=lambda index: df.loc[index, "city"].split("`")[1],
                      split_col_common=["city", "year"],
                      split_col_subsets=[['time'], ['seconds']])
        self.assertIn("+++++++++", conv)
        self.assertIn("| :ref:`AMSTERDAM` | 1982 | 02:12:15 |", conv)

    def test_df2rst_split_col_row_ref2_func2(self):

        def build_key_split(key, index):
            new_key = str(key).split('`')[1].split('<')[0].strip()
            return new_key

        df = pandas.DataFrame([
            {'name': ':ref:`A <A>`', 'value': 1},
            {'name': ':ref:`A <A2>`', 'value': 2},
            {'name': ':ref:`B <B>`', 'value': 3},
            {'name': ':ref:`B <B2>`', 'value': 4},
            {'name': ':ref:`A <A3>`', 'value': 5},
        ])
        conv = df2rst(df, split_row=lambda index: build_key_split(
            df.loc[index, "name"], index))
        self.assertIn("| :ref:`B <B>`  | 3     |", conv)

    def test_df2rst_split_col_complex(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "unittst.csv")
        df = pandas.read_csv(mara)
        common = ['name', 'problem', 'scenario']
        subsets = [
            ['opset11', 'opset10', 'opset9'],
            ['ERROR-msg'], ['RT/SKL-N=1', 'N=10', 'N=100', 'N=1000', 'N=10000',
                            'N=100000', 'RT/SKL-N=1-min', 'RT/SKL-N=1-max', 'N=10-min', 'N=10-max',
                            'N=100-min', 'N=100-max', 'N=1000-min', 'N=1000-max', 'N=10000-min',
                            'N=10000-max', 'N=100000-min', 'N=100000-max']
        ]

        def build_key_split(key, index):
            new_key = str(key).split('`')[1].split('<')[0].strip()
            return new_key

        def filter_rows(df):
            for c in ['ERROR-msg', 'RT/SKL-N=1']:
                if c in df.columns:
                    return df[df[c].apply(lambda x: pandas.notnull(x) and x not in (None, '', 'nan'))]
            return df

        conv = df2rst(df, number_format=2,
                      replacements={'nan': '', 'ERR: 4convert': ''},
                      split_row=lambda index, dp=df: build_key_split(
                          dp.loc[index, "name"], index),
                      split_col_common=common,
                      split_col_subsets=subsets,
                      filter_rows=filter_rows)
        self.assertIn("| :ref:`ARDRegression <l-ARDRegression-b-reg-default>`     | b-reg     | default  "
                      "|               | ?       | ?      |", conv)
        spl = conv.split("+=============================")
        self.assertEqual(len(spl), 7)

    def test_df2rst_column_size(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2rst(df, column_size={'city': 40})
        self.assertIn(
            "| city                                     | year | time     | seconds |", conv)
        self.assertIn(
            "| PARIS                                    | 2006 | 02:08:03 | 7683    |", conv)

    def test_df2rst_column_size_i(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2rst(df, column_size={0: 40})
        self.assertIn(
            "| city                                     | year | time     | seconds |", conv)
        self.assertIn(
            "| PARIS                                    | 2006 | 02:08:03 | 7683    |", conv)


if __name__ == "__main__":
    unittest.main()
