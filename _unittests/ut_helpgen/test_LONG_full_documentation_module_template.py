"""
@brief      test log(time=285s)
@author     Xavier Dupre
"""
import os
import sys
import unittest
import warnings
import logging
from docutils.parsers.rst import roles
from sphinx.util.logging import getLogger
import pyquickhelper
from pyquickhelper.loghelper.flog import fLOG, download
from pyquickhelper.loghelper import CustomLog, sys_path_append
from pyquickhelper.helpgen.sphinx_main import generate_help_sphinx
from pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor
from pyquickhelper.filehelper.synchelper import remove_folder


class TestSphinxFullDocumentationModuleTemplate(unittest.TestCase):

    def test_full_documentation_module_template(self):
        """
        This test might fail in sphinx-gallery due to a very long filename.
        Please look into the following commit:
        https://github.com/sdpython/sphinx-gallery/commit/3ae9f13250cf25c75e1b17b2fade98b7a9940b0d.
        """
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            # travis fails due to the following:
            #       sitep = [_ for _ in site.getsitepackages() if "packages" in _]
            # AttributeError: 'module' object has no attribute
            # 'getsitepackages'
            # It fails for python 2.7 (encoding issue).
            return

        temp = get_temp_folder(__file__, "temp_full_documentation_module_template",
                               clean=__name__ != "__main__")

        clog = CustomLog(temp)
        this_pyq = os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(pyquickhelper.__file__), "..")))

        class MyStream:
            def __init__(self):
                self.rows = []

            def write(self, text):
                clog(
                    "[warning*] {0} - '{1}'".format(len(self), text.strip("\n\r ")))
                self.rows.append(text)

            def getvalue(self):
                return "\n".join(self.rows)

            def __len__(self):
                return len(self.rows)

        rem = os.path.join(
            temp, "python3_module_template-master", "_doc", "sphinxdoc", "build")
        if os.path.exists(rem):
            remove_folder(rem)
        url = "https://github.com/sdpython/python3_module_template/archive/master.zip"
        fLOG("[ut] download", url)
        download(url, temp, fLOG=fLOG, flatten=False)
        self.assertTrue(not os.path.exists(os.path.join(temp, "src")))
        root = os.path.join(temp, "python3_module_template-master")

        with sys_path_append(os.path.join(root, "src")):
            # Checks that the unit test might fails.
            coucou = os.path.join(temp, "python3_module_template-master", "_doc", "sphinxdoc", "source", "gallery",
                                  "python3_module_template.subproject2.exclude_from_code_coverage.NotImplementedClass.__init__.examples")
            if not os.path.exists(coucou):
                fLOG("[ut] creating file '{0}'".format(coucou))
                clog("[ut] creating file '{0}'".format(coucou))
                dirname = os.path.dirname(coucou)
                os.makedirs(dirname)
                try:
                    # replicating what sphinx_gallery does
                    open(coucou, "w").close()
                except Exception as e:
                    warnings.warn(
                        "Unable to create '{0}' due to '{1}'".format(coucou, e))
            else:
                fLOG("[ut] file exists '{0}'".format(coucou))
                clog("[ut] file exists '{0}'".format(coucou))

            # documentation
            fLOG("generate documentation", root)
            var = "python3_module_template"

            # we modify conf.py to let it find pyquickhelper
            pyq = os.path.abspath(os.path.dirname(pyquickhelper.__file__))
            confpy = os.path.join(
                root, "_doc", "sphinxdoc", "source", "conf.py")
            if not os.path.exists(confpy):
                raise FileNotFoundError(
                    "Unable to find '{0}' and\n{1}".format(confpy, os.listdir(temp)))
            with open(confpy, "r", encoding="utf8") as f:
                lines = f.read().split("\n")
            fi = len(lines) - 1
            for i, line in enumerate(lines):
                if line.startswith("sys."):
                    fi = i
                    break
            addition = "sys.path.append(r'{0}')".format(pyq)
            lines[fi] = "{0}\n{1}".format(addition, lines[fi])
            with open(confpy, "w", encoding="utf8") as f:
                f.write("\n".join(lines))

            # test
            for i in range(0, 3):
                fLOG("\n")
                fLOG("\n")
                fLOG("\n")
                fLOG("#################################################", i)
                fLOG("#################################################", i)
                fLOG("#################################################", i)

                # we add access to pyquickhelper
                p = os.path.abspath(os.path.dirname(pyquickhelper.__file__))
                p = os.path.join(p, 'src')
                fLOG("PYTHONPATH=", p)
                os.environ["PYTHONPATH"] = p
                if p not in sys.path:
                    pos = len(sys.path)
                    sys.path.append(p)
                else:
                    pos = -1

                if "conf" in sys.modules:
                    del sys.modules["conf"]

                fLOG("[test_full_documentation] **********************************")
                fLOG("[test_full_documentation] begin",
                     list(roles._roles.keys()))
                fLOG("[test_full_documentation] **********************************")

                direct_call = i % 2 == 0
                layout = ["html"]

                logger1 = getLogger("docassert")
                logger2 = getLogger("tocdelay")
                logger3 = getLogger("downloadlink")
                log_capture_string = MyStream()  # StringIO()
                ch = logging.StreamHandler(log_capture_string)
                ch.setLevel(logging.DEBUG)
                logger1.logger.addHandler(ch)
                logger2.logger.addHandler(ch)
                logger3.logger.addHandler(ch)

                with warnings.catch_warnings(record=True) as ww:
                    warnings.simplefilter("always")
                    generate_help_sphinx(var, module_name=var, root=root,
                                         layout=layout, extra_ext=["tohelp"],
                                         from_repo=False, direct_call=direct_call,
                                         parallel=1, fLOG=clog, extra_paths=[this_pyq],
                                         nbformats=['html', 'ipynb', 'rst', 'slides'])
                    for w in ww:
                        if isinstance(w, dict):
                            rows = [
                                "----"] + ["{0}={1}".format(k, v) for k, v in sorted(w.items())]
                            sw = "\n".join(rows)
                        elif isinstance(w, warnings.WarningMessage):
                            rows = [
                                "-----", str(type(w)), w.filename, str(w.lineno), str(w.message)]
                            sw = "\n".join(rows)
                        else:
                            sw = str(w)
                        if "WARNING:" in sw and "ERROR/" in sw:
                            raise Exception(
                                "A warning is not expected:\n{0}".format(sw))

                fLOG("[test_full_documentation] **********************************")
                fLOG("[test_full_documentation] END")
                fLOG("[test_full_documentation] **********************************")

                lines = log_capture_string.getvalue().split("\n")
                for line in lines:
                    if not line.strip():
                        continue
                    if "[docassert]" in line:
                        raise Exception(line)
                    if "[tocdelay]" in line:
                        fLOG("   ", line)
                    if '[tocdelay] ERROR' in line:
                        raise Exception(line)
                    if '[downloadlink]' in line:
                        fLOG(line)

                # we clean
                if "pyquickhelper" in sys.modules:
                    del sys.modules["pyquickhelper"]
                os.environ["PYTHONPATH"] = ""
                if pos >= 0:
                    del sys.path[pos]

                # blog index
                blog = os.path.join(root, "_doc", "sphinxdoc",
                                    "build", "html", "blog", "blogindex.html")
                with open(blog, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("2015", content)
                self.assertIn(
                    '"2016/2016-06-11_blogpost_with_label.html"', content)
                spl = content.split("2016-06")
                if len(spl) <= 2:
                    raise Exception("Two expected:\n" + content)

                # checkings
                files = [os.path.join(root, "_doc", "sphinxdoc", "build", "html", "index.html"),
                         os.path.join(root, "_doc", "sphinxdoc",
                                      "build", "html", "all_indexes.html"),
                         os.path.join(root, "_doc", "sphinxdoc",
                                      "build", "html", "all_notebooks.html"),
                         ]
                for f in files:
                    if not os.path.exists(f):
                        raise FileNotFoundError(
                            "Not found '{0}'\n---\n{1}".format(f, "\n".join(lines)))

                self.assertTrue(not os.path.exists(os.path.join(temp, "_doc")))

                rss = os.path.join(
                    root, "_doc", "sphinxdoc", "source", "blog", "rss.xml")
                with open(rss, "r", encoding="utf8") as f:
                    content_rss = f.read()

                self.assertTrue("__BLOG_ROOT__" not in content_rss)
                # this should be replaced when uploading the stream onto the website
                # the website is unknown when producing the documentation
                # it should be resolved when uploading (the documentation could be
                # uploaded at different places)

                # checks some links were processed
                fhtml = os.path.join(temp, "python3_module_template-master",
                                     "_doc", "sphinxdoc", "build", "html", "index.html")
                with open(fhtml, "r", encoding="utf8") as f:
                    content = f.read()
                if '<td><p><a class="reference internal" href="index_ext-tohelp.html#ext-tohelp"><span class="std std-ref">ext-tohelp</span></a></p></td>' not in content:
                    raise Exception(content)

                # checks some links were processed
                fhtml = os.path.join(temp, "python3_module_template-master",
                                     "_doc", "sphinxdoc", "build", "html", "all_notebooks.html")
                with open(fhtml, "r", encoding="utf8") as f:
                    content = f.read()
                if '<img alt="_images/custom_notebooks.thumb.png" src="_images/custom_notebooks.thumb.png" />' not in content:
                    raise Exception(content)

                # checks slideshow was added
                fhtml = os.path.join(temp, "python3_module_template-master",
                                     "build", "notebooks", "bslides", "custom_notebooks.ipynb")
                with open(fhtml, "r", encoding="utf8") as f:
                    content = f.read()
                self.assertTrue('"slide"' in content)

                # reveal.js + images
                rev = [os.path.join(root, "_doc", "sphinxdoc", "source", "phdoc_static", "reveal.js"),
                       os.path.join(root, "_doc", "sphinxdoc", "build",
                                    "html", "_downloads", "reveal.js"),
                       os.path.join(root, "_doc", "sphinxdoc", "build",
                                    "html", "notebooks", "reveal.js"),
                       os.path.join(root, "_doc", "sphinxdoc", "build", "html",
                                    "notebooks", "Python_logo_and_wordmark.png"),
                       os.path.join(root, "_doc", "sphinxdoc", "build", "html",
                                    "notebooks", "custom_notebooks.slides.html"),
                       os.path.join(root, "_doc", "sphinxdoc", "build", "html",
                                    "notebooks", "custom_notebooks.html"),
                       os.path.join(root, "_doc", "sphinxdoc", "build", "html",
                                    "_downloads", "rss.xml")]
                for r in rev:
                    if not os.path.exists(r):
                        logs = os.path.join(temp, "log_custom_000.txt")
                        with open(logs, "r", encoding='utf-8') as f:
                            content = f.read()
                        found = os.listdir(os.path.dirname(r))
                        found2 = os.listdir(os.path.dirname(
                            r.replace("build", "source").replace("/html", "")))
                        raise FileNotFoundError(
                            "Unable to find '{0}' in\n{1}\n----\n{2}\n---LOGS--\n{3}".format(
                                r, "\n".join(sorted(found)), "\n".join(sorted(found2)), content))

                history = os.path.join(
                    root, "_doc", "sphinxdoc", "build", "html", "HISTORY.html")
                if not os.path.exists(history):
                    raise FileNotFoundError(history)
                with open(history, "r", encoding="utf-8") as f:
                    content = f.read()

                tofind = 'python3_module_template'
                if tofind not in content:
                    raise Exception(
                        "Unable to find '{0}' in\n{1}".format(tofind, content))

                # notebook links
                files = [os.path.join(root, "_doc", "sphinxdoc", "build", "html",
                                      "notebooks", "custom_notebooks.html"),
                         ]
                for name in files:
                    with open(name, "r", encoding="utf-8") as f:
                        content = f.read()
                    if "https://unpkg.com/@jupyter-widgets/html-manager@%5E0.20.0/dist/embed-amd.js" in content:
                        raise AssertionError("Absolute link in %r." % name)
                    if "https://cdnjs.cloudflare" in content:
                        raise AssertionError(
                            "Absolute cloudflare link in %r." % name)
                    if "reveal.js/dist" in content:
                        raise AssertionError("Wrong link in slides %r." % name)

            # final check
            logs = os.path.join(temp, "log_custom_000.txt")
            with open(logs, "r", encoding='utf-8') as f:
                content = f.read()
            if "[downloadlink] node" not in content:
                raise Exception(content)
            if "[downloadlink] HTML" not in content:
                raise Exception(content)
            if "[downloadlink] copy" not in content:
                raise Exception(content)


if __name__ == "__main__":
    unittest.main()
