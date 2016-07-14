"""
@brief      test log(time=1s)
"""
import os
import sys
import unittest
import warnings
import threading
import time


if sys.version_info[0] == 2:
    from Tkinter import TclError
else:
    from tkinter import TclError

try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.funcwin import main_loop_functions


def my_tst_function(a, b):
    """
    return a+b
    @param      a   (float) float
    @param      b   (float) float
    @return         a+b
    """
    return a + b


class TestWindowsAutopy3(unittest.TestCase):

    def test_open_window_params(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        import autopy3
        import autopy3.key
        import autopy3.mouse
        import autopy3.screen
        temp = get_temp_folder(__file__, "temp_autopy3")
        root = [None]

        def f():
            fLOG("size", autopy3.screen.get_size())
            icon = autopy3.bitmap.Bitmap.open(
                os.path.join(temp, "..", "data", "icon.png"))
            img = os.path.join(temp, "screen.png")
            screen = autopy3.bitmap.capture_screen()
            pos = screen.find_bitmap(icon)
            iter = 0
            while not pos and iter < 3:
                if iter > 1:
                    fLOG("iter", iter, pos)
                time.sleep(1)
                screen = autopy3.bitmap.capture_screen()
                pos = screen.find_bitmap(icon)
                iter += 1
            if not pos:
                warnings.warn("unable to find icon in the screen")
                pos = (117, 108)
            screen.save(img)
            fLOG("pos=", pos)

            # test
            fLOG((1, 1), autopy3.screen.point_visible(
                1, 1), autopy3.screen.get_size())
            if not autopy3.screen.point_visible(1, 1):
                warnings.warn("autopy3.screen.point_visible is False")

            # closes the window
            if False and autopy3.screen.point_visible(1, 1):
                # does not seem to work (point not visible)
                dend = (986 - 117, 116 - 108)
                end = (dend[0] + pos[0], dend[1] + pos[1])
                autopy3.mouse.move(end[0], end[1])
                autopy3.mouse.click(button=autopy3.mouse.LEFT_BUTTON)
            else:
                root[0].event_generate("<Alt-F4>")

        th = threading.Thread(target=f)
        th.start()

        try:
            r = main_loop_functions(
                dict(my_tst_function=my_tst_function), init_pos=(100, 100), mainloop=False)
            root[0] = r
            r.mainloop()
        except TclError as e:
            warnings.warn("TclError" + str(e))


if __name__ == "__main__":
    unittest.main()
