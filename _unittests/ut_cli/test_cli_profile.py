"""
@brief      test tree node (time=7s)
"""
import os
import unittest
import time
from pyquickhelper.loghelper import fLOG, BufferedPrint
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.__main__ import main
from pyquickhelper.pycode.profiling import profile


def to_profile(args):
    st = BufferedPrint()
    main(args=args, fLOG=st.fprint)
    return str(st)


class TestCliProfile(ExtTestCase):

    def test_profile(self):
        "checks that bokeh is not loaded"
        prof = self.profile(lambda: to_profile(["clean_files", "--help"]))[1]
        self.assertNotIn("bokeh", prof.lower())

    def test_profile_stat_help(self):
        st = BufferedPrint()
        main(args=['profile_stat', '--help'], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: profile_stat", res)

    def test_profile_stat(self):

        def f0(t):
            time.sleep(t)

        def f1(t):
            time.sleep(t)

        def f2():
            f1(0.1)
            f1(0.01)

        def f3():
            f0(0.2)
            f1(0.5)

        def f4():
            f2()
            f3()

        ps = profile(f4)[0]  # pylint: disable=W0632
        ps.dump_stats("temp_stat.prof")

        with self.subTest(calls=False, output=None):
            st = BufferedPrint()
            main(args=['profile_stat', '-f', "temp_stat.prof",
                       '--calls', '0'], fLOG=st.fprint)
            self.assertIn('percall', str(st))

        with self.subTest(calls=False, output="txt"):
            st = BufferedPrint()
            main(args=['profile_stat', '-f', "temp_stat.prof",
                       '--calls', '0', '-o', 'temp_output.txt'], fLOG=st.fprint)
            with open("temp_output.txt", "r", encoding='utf-8') as f:
                content = f.read()
            self.assertIn('percall', str(st))
            self.assertIn('percall', content)

        with self.subTest(calls=False, output='csv'):
            st = BufferedPrint()
            main(args=['profile_stat', '-f', "temp_stat.prof",
                       '--calls', '0', '-o', 'temp_output.csv'], fLOG=st.fprint)
            with open("temp_output.csv", "r", encoding='utf-8') as f:
                content = f.read()
            self.assertIn('percall', str(st))
            self.assertIn('ncalls1,', content)

        with self.subTest(calls=False, output='xlsx'):
            st = BufferedPrint()
            main(args=['profile_stat', '-f', "temp_stat.prof",
                       '--calls', '0', '-o', 'temp_output.xlsx'], fLOG=st.fprint)
            self.assertExists('temp_output.xlsx')
            self.assertIn('percall', str(st))

    def test_profile_stat_gr(self):

        def f0(t):
            time.sleep(t)

        def f1(t):
            time.sleep(t)

        def f2():
            f1(0.1)
            f1(0.01)

        def f3():
            f0(0.2)
            f1(0.5)

        def f4():
            f2()
            f3()

        ps = profile(f4)[0]  # pylint: disable=W0632
        ps.dump_stats("temp_gr_stat.prof")

        with self.subTest(calls=False, output=None):
            st = BufferedPrint()
            main(args=['profile_stat', '-f', "temp_gr_stat.prof",
                       '--calls', '1'], fLOG=st.fprint)
            self.assertIn('+++', str(st))

        with self.subTest(calls=False, output="txt"):
            st = BufferedPrint()
            main(args=['profile_stat', '-f', "temp_gr_stat.prof",
                       '--calls', '1', '-o', 'temp_gr_output.txt'], fLOG=st.fprint)
            with open("temp_gr_output.txt", "r", encoding='utf-8') as f:
                content = f.read()
            self.assertIn('+++', str(st))
            self.assertIn('+++', content)

        with self.subTest(calls=False, output='csv'):
            st = BufferedPrint()
            main(args=['profile_stat', '-f', "temp_gr_stat.prof",
                       '--calls', '1', '-o', 'temp_gr_output.csv'], fLOG=st.fprint)
            with open("temp_gr_output.csv", "r", encoding='utf-8') as f:
                content = f.read()
            self.assertIn('+++', str(st))
            self.assertIn(',+', content)

        with self.subTest(calls=False, output='xlsx'):
            st = BufferedPrint()
            main(args=['profile_stat', '-f', "temp_gr_stat.prof",
                       '--calls', '1', '-o', 'temp_gr_output.xlsx'], fLOG=st.fprint)
            self.assertIn('+++', str(st))
            self.assertExists('temp_gr_output.xlsx')


if __name__ == "__main__":
    unittest.main()
