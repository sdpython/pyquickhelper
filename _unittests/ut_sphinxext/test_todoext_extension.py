"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
from docutils.parsers.rst import directives
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import TodoExt, TodoExtList
from pyquickhelper.sphinxext.sphinx_todoext_extension import todoext_node, visit_todoext_node, depart_todoext_node


class TestTodoExtExtension(ExtTestCase):

    def test_post_parse_sn_todoext(self):
        directives.register_directive("todoext", TodoExt)
        directives.register_directive("todoextlist", TodoExtList)

    def test_todoext(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. todoext::
                        :title: first todo
                        :tag: bug
                        :issue: 7

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("todoext", TodoExt, todoext_node,
                  visit_todoext_node, depart_todoext_node)]

        html = rst2html(content, writer="custom", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_todoext")
        with open(os.path.join(temp, "out_todoext.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "first todo"
        if t1 not in html:
            raise Exception(html)

        t1 = "(bug)"
        if t1 not in html:
            raise Exception(html)

        t1 = 'href="http://7"'
        if t1 not in html:
            raise Exception(html)

    def test_todoextlist(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. todoext::
                        :title: first todo

                        this code shoud appear___

                    middle

                    .. todoextlist::

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("todoext", TodoExt, todoext_node,
                  visit_todoext_node, depart_todoext_node)]

        html = rst2html(content, writer="rst", keep_warnings=True,
                        directives=tives, layout="sphinx",
                        todoext_include_todosext=True)

        temp = get_temp_folder(__file__, "temp_todoextlist")
        with open(os.path.join(temp, "out_todoext.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "first todo"
        if t1 not in html:
            raise Exception(html)

        t1 = "(The `original entry"
        if t1 not in html:
            raise Exception(html)

    def test_todoext_done(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. todoext::
                        :title: first todo
                        :tag: bug
                        :issue: 7
                        :hidden:

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("todoext", TodoExt, todoext_node,
                  visit_todoext_node, depart_todoext_node)]

        html = rst2html(content, writer="custom", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_todoext")
        with open(os.path.join(temp, "out_todoext.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "first todo"
        if t1 in html:
            raise Exception(html)

        t1 = "(bug)"
        if t1 in html:
            raise Exception(html)

        t1 = 'href="http://7"'
        if t1 in html:
            raise Exception(html)


if __name__ == "__main__":
    unittest.main()
