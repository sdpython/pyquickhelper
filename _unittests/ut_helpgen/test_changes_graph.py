"""
@brief      test log(time=1s)
"""
import sys
import os
import unittest
import warnings
import pandas
from pyquickhelper.helpgen.sphinx_main_helper import produce_code_graph_changes
from pyquickhelper.pycode import fix_tkinter_issues_virtualenv, skipif_appveyor


class TestGraphChanges (unittest.TestCase):

    @skipif_appveyor("Message: 'generated new fontManager'")
    def test_graph_changes(self):
        fix_tkinter_issues_virtualenv()
        path = os.path.abspath(os.path.split(__file__)[0])
        data = os.path.join(path, "data", "changes.txt")
        df = pandas.read_csv(data, sep="\t")
        code = produce_code_graph_changes(df)

        enabled = True
        if enabled:
            # this is the code which is generate
            import matplotlib.pyplot as plt
            x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52]
            y = [0, 5, 4, 1, 1, 1, 0, 3, 0, 15, 5, 2, 1, 0, 5, 3, 1, 0, 3, 2, 0, 4, 5, 2, 12, 12,
                 5, 11, 2, 19, 21, 5, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            xl = ['2014-w20', '2014-w21', '2014-w22', '2014-w23', '2014-w24', '2014-w25', '2014-w26', '2014-w27',
                  '2014-w28', '2014-w29', '2014-w30', '2014-w31', '2014-w32',
                  '2014-w33', '2014-w34', '2014-w35', '2014-w36', '2014-w37', '2014-w38', '2014-w39', '2014-w40',
                  '2014-w41', '2014-w42', '2014-w43', '2014-w44', '2014-w45',
                  '2014-w46', '2014-w47', '2014-w48', '2014-w49', '2014-w50', '2014-w51', '2014-w52', '2015-w01',
                  '2015-w02', '2015-w03', '2015-w04', '2015-w05', '2015-w06', '2015-w07',
                  '2015-w08', '2015-w09', '2015-w10', '2015-w11', '2015-w12', '2015-w13', '2015-w14', '2015-w15',
                  '2015-w16', '2015-w17', '2015-w18', '2015-w19', '2015-w20']
            plt.close('all')
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', (DeprecationWarning, UserWarning))
                _, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))
                ax.bar(x, y)
                tig = ax.get_xticks()
                labs = []
                for t in tig:
                    if t in x:
                        labs.append(xl[x.index(t)])
                    else:
                        labs.append("")
                ax.set_xticklabels(labs)
                ax.grid(True)
                ax.set_title("commits")

        if __name__ != "__main__":
            code = code.replace("plt.show", "#plt.show")

        obj = compile(code, "", "exec")
        if sys.platform != "win32" and __name__ != "__main__":
            try:
                exec(obj, globals(), locals())
            except Exception as e:
                raise AssertionError(f"Unable to run code:\n{code}") from e


if __name__ == "__main__":
    unittest.main()
