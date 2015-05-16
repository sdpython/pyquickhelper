"""
@brief      test log(time=80s)
@author     Xavier Dupre
"""
import os
import sys
import unittest
import shutil


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

from src.pyquickhelper.loghelper.flog import fLOG, download
from src.pyquickhelper.helpgen import generate_help_sphinx
from src.pyquickhelper import get_temp_folder

if sys.version_info[0] == 2:
    from codecs import open


class TestSphinxDocFull (unittest.TestCase):

    def test_full_documentation(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if "travis" in sys.executable or sys.version_info[0] == 2:
            # travis due to the following:
            #       sitep = [_ for _ in site.getsitepackages() if "packages" in _]
            # AttributeError: 'module' object has no attribute
            # 'getsitepackages'
            # it also fails for python 2.7 (encoding issue)
            return

        temp = get_temp_folder(__file__, "temp_full_doc_template")
        url = "https://github.com/sdpython/python3_module_template/archive/master.zip"
        fLOG("download", url)
        download(url, temp)
        assert not os.path.exists(os.path.join(temp, "src"))
        root = os.path.join(temp, "python3_module_template-master")

        fLOG("generate documentation", root)
        var = "project_name"

        # we modify conf.py to let it find pyquickhelper
        pyq = os.path.abspath(os.path.dirname(src.__file__))
        confpy = os.path.join(root, "_doc", "sphinxdoc", "source", "conf.py")
        with open(confpy, "r", encoding="utf8") as f:
            lines = f.read().split("\n")
        for i, line in enumerate(lines):
            if line.startswith("sys."):
                break
        addition = "sys.path.append(r'{0}')".format(pyq)
        lines[i] = "{0}\n{1}".format(addition, lines[i])
        with open(confpy, "w", encoding="utf8") as f:
            f.write("\n".join(lines))

        # test
        for i in range(0, 2):
            fLOG("\n")
            fLOG("\n")
            fLOG("\n")
            fLOG("#################################################", i)
            fLOG("#################################################", i)
            fLOG("#################################################", i)

            if "conf" in sys.modules:
                del sys.modules["conf"]

            generate_help_sphinx(var, module_name=var, root=root,
                                 layout=["pdf", "html"],
                                 extra_ext=["tohelp"],
                                 from_repo=False,
                                 use_run_cmd=True)

            files = [os.path.join(root, "_doc", "sphinxdoc", "build", "html", "index.html"),
                     os.path.join(
                root, "_doc", "sphinxdoc", "build", "html", "all_example.html"),
                os.path.join(
                root, "_doc", "sphinxdoc", "build", "html", "all_indexes.html"),
                os.path.join(
                root, "_doc", "sphinxdoc", "build", "html", "all_notebooks.html"),
            ]
            for f in files:
                if not os.path.exists(f):
                    raise FileNotFoundError(f)

            assert not os.path.exists(os.path.join(temp, "_doc"))

            rss = os.path.join(
                root, "_doc", "sphinxdoc", "source", "blog", "rss.xml")
            with open(rss, "r", encoding="utf8") as f:
                content_rss = f.read()

            assert "__BLOG_ROOT__" not in content_rss
            # this should be replaced when uploading the stream onto the website
            # the website is unknown when producing the documentation
            # it should be resolved when uploading (the documentation could be
            # uploaded at different places)

            # checks some links were processed
            fhtml = os.path.join(temp, "python3_module_template-master",
                                 "_doc", "sphinxdoc", "build", "html", "index.html")
            with open(fhtml, "r", encoding="utf8") as f:
                content = f.read()
            assert '<td><a class="reference internal" href="index_ext-tohelp.html#ext-tohelp"><span>ext-tohelp</span></a></td>' in content

            # checks some links were processed
            fhtml = os.path.join(temp, "python3_module_template-master",
                                 "_doc", "sphinxdoc", "build", "html", "all_notebooks.html")
            with open(fhtml, "r", encoding="utf8") as f:
                content = f.read()
            assert '<a href="notebooks/custom_notebooks.html" title="Custom Notebooks"' in content

            # checks some links were processed
            fhtml = os.path.join(temp, "python3_module_template-master",
                                 "_doc", "sphinxdoc", "source", "all_notebooks.rst")
            with open(fhtml, "r", encoding="utf8") as f:
                content = f.read()
            assert 'notebooks/custom_notebooks' in content

            # checks slideshow was added
            fhtml = os.path.join(temp, "python3_module_template-master",
                                 "build", "notebooks", "bslides", "custom_notebooks.ipynb")
            with open(fhtml, "r", encoding="utf8") as f:
                content = f.read()
            assert '"slide"' in content

            # reveal.js
            rev = [os.path.join(root, "_doc", "sphinxdoc", "source", "phdoc_static", "reveal.js"),
                   os.path.join(root, "_doc", "sphinxdoc", "build", "html", "_downloads", "reveal.js"), ]
            for r in rev:
                if not os.path.exists(r):
                    raise FileNotFoundError(r)


if __name__ == "__main__":
    unittest.main()
