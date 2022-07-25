"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""
import os
import unittest
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.sphinxext.revealjs.directives import (
    heading, RevealjsDirective, RvNoteDirective, RvSmallDirective,
    RvCodeDirective, visit_revealjs, depart_revealjs,
    visit_rv_code, depart_rv_code, visit_rv_small,
    depart_rv_small, visit_rv_note, depart_rv_note,
    setup)
from pyquickhelper.sphinxext.revealjs import directives as d
from pyquickhelper.sphinxext.revealjs import compat


class DummyConfig(object):

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def __getattr__(self, name):
        if name in self.kwargs:
            return self.kwargs.get(name)
        return self

    def nested_parse(self, content, content_offset, node):
        pass

    def warning(self, msg, line):
        return dict(msg=msg, line=line)


class TestHeading(ExtTestCase):

    def _get_target(self):
        return heading

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def test_it(self):
        self.assertEqual("h1", self._call_fut("h1"))
        self.assertEqual("h2", self._call_fut("h2"))
        self.assertEqual("h3", self._call_fut("h3"))
        self.assertEqual("h4", self._call_fut("h4"))
        self.assertEqual("h5", self._call_fut("h5"))
        self.assertEqual("h6", self._call_fut("h6"))

    def test_value_error(self):
        try:
            self._call_fut("unknown")
            raise AssertionError('Excpeption not raised')
        except ValueError:
            pass


class TestRevealjsDirective(ExtTestCase):

    def _get_target_class(self):
        return RevealjsDirective

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def _get_dummy_config(self, **kwargs):
        config = dict()
        config.update(kwargs)
        return DummyConfig(**config)

    def _get_params(self, **kwargs):
        from docutils.statemachine import State, StateMachine
        stm = StateMachine([], None)
        stm.reporter = None
        st = State(stm)
        params = dict(
            name='dummyname',
            arguments=['tell-k', 'test'],
            options={},
            content="test",
            lineno=1,
            content_offset=1,
            block_text="",
            state=st,
            state_machine=stm,
        )
        params.update(kwargs)
        return params

    def test_it(self):
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config()

        nodes = directive.run()
        self.assertEqual(1, len(nodes))
        self.assertEqual('tell-k test', nodes[0]['title'])
        self.assertEqual(False, nodes[0]['noheading'])
        self.assertEqual([], nodes[0]['classes'])

    def test_class_option(self):
        directive = self._make_one(**self._get_params(options={
            "class": "add-class",
        }))
        directive.state = self._get_dummy_config()
        nodes = directive.run()
        self.assertEqual('add-class', nodes[0]['classes'])

    def test_noheading_option(self):
        directive = self._make_one(**self._get_params(options={
            "noheading": None,
        }))
        directive.state = self._get_dummy_config()
        nodes = directive.run()
        self.assertEqual(True, nodes[0]['noheading'])

    def test_other_options(self):
        directive = self._make_one(**self._get_params(options={
            "title-heading": "title-heading",
        }))
        directive.state = self._get_dummy_config()
        nodes = directive.run()
        self.assertEqual("title-heading", nodes[0]['title-heading'])


class TestRvSmallDirective(ExtTestCase):

    def _get_target_class(self):
        return RvSmallDirective

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def _get_dummy_config(self, **kwargs):
        config = dict()
        config.update(kwargs)
        return DummyConfig(**config)

    def _get_params(self, **kwargs):
        from docutils.statemachine import State, StateMachine
        stm = StateMachine([], None)
        stm.reporter = None
        st = State(stm)
        params = dict(
            name='dummyname',
            arguments='',
            options={},
            content="test",
            lineno=1,
            content_offset=1,
            block_text="",
            state=st,
            state_machine=stm,
        )
        params.update(kwargs)
        return params

    def test_it(self):
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config()

        nodes = directive.run()
        self.assertEqual(1, len(nodes))
        self.assertEqual([], nodes[0]['classes'])

    def test_class_option(self):
        directive = self._make_one(**self._get_params(options={
            "class": "add-class",
        }))
        directive.state = self._get_dummy_config()
        nodes = directive.run()
        self.assertEqual('add-class', nodes[0]['classes'])


class TestRvNoteDirective(ExtTestCase):

    def _get_target_class(self):
        return RvNoteDirective

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def _get_dummy_config(self, **kwargs):
        config = dict()
        config.update(kwargs)
        return DummyConfig(**config)

    def _get_params(self, **kwargs):
        from docutils.statemachine import State, StateMachine
        stm = StateMachine([], None)
        stm.reporter = None
        st = State(stm)
        params = dict(
            name='dummyname',
            arguments='',
            options={},
            content="test",
            lineno=1,
            content_offset=1,
            block_text="",
            state=st,
            state_machine=stm,
        )
        params.update(kwargs)
        return params

    def test_it(self):
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config()

        nodes = directive.run()
        assert 1 == len(nodes)
        assert [] == nodes[0]['classes']

    def test_class_option(self):
        directive = self._make_one(**self._get_params(options={
            "class": "add-class",
        }))
        directive.state = self._get_dummy_config()
        nodes = directive.run()
        assert 'add-class' == nodes[0]['classes']


class TestRvCodeDirective(ExtTestCase):

    def _get_target_class(self):
        return RvCodeDirective

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def _get_dummy_config(self, **kwargs):
        config = dict()
        config.update(kwargs)
        return DummyConfig(**config)

    def _get_params(self, **kwargs):
        from docutils.statemachine import State, StateMachine
        stm = StateMachine([], None)
        stm.reporter = None
        st = State(stm)
        params = dict(
            name='dummyname',
            arguments='',
            options={},
            content="test",
            lineno=1,
            content_offset=1,
            block_text="",
            state=st,
            state_machine=stm,
        )
        params.update(kwargs)
        return params

    def test_it(self):
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config()

        nodes = directive.run()
        assert 1 == len(nodes)


class TestVisitRevealjs(ExtTestCase):

    def _get_target(self):
        return visit_revealjs

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_node(self, *args, **kwargs):

        class DummyNode(object):
            attrs = {
                'id': "id",
                'title': 'title',
                'noheading': False,
                'title-heading': 'h1',
                'subtitle': 'subtitle',
                'subtitle-heading': 'h2',
                'data-markdown': None,
                'data-transition': None,
                'data-background': None,
                'data-background-repeat': None,
                'data-background-size': None,
                'data-background-transition': None,
                'data-state': None,
                'data-separator': None,
                'data-vertical': None,
            }

            def __init__(self, **kwargs):
                self.attrs.update(kwargs)

            def get(self, attr, default=None):
                return self.attrs.get(attr, default)

            @property
            def rawsource(self):
                return "rawsource"

        return DummyNode(**kwargs)

    def _get_dummy_self(self, *args, **kwargs):
        class DummyBody(object):
            content = []

            def append(self, content):
                self.content.append(content)

        class DummySelf(object):
            fist_last = False

            def __init__(self, body):
                self.body = body

            def starttag(self, node, tag, **kwargs):
                ids = kwargs.pop('ids')
                if ids:
                    kwargs.update({'id': " ".join(ids)})
                attrs = [f"{k}='{v}'" for k, v in kwargs.items()]
                attrs.sort()
                return f"<{tag} {' '.join(attrs)}>"

            def set_first_last(self, node):
                self.first_last = True

        return DummySelf(DummyBody())

    def test_it(self):
        dummyself = self._get_dummy_self()
        dummynode = self._get_dummy_node()

        self._call_fut(dummyself, dummynode)
        self.assertEqual([
            compat.text("<section id='id'>"),
            compat.text('<h1>title</h1>\n'),
            compat.text('<h2>subtitle</h2>\n')
        ], dummyself.body.content)

    def test_markdown(self):
        dummyself = self._get_dummy_self()
        dummynode = self._get_dummy_node(**{"data-markdown": "hoge"})

        self._call_fut(dummyself, dummynode)
        self.assertEqual(["<section data-markdown='hoge' id='id'>"],
                         dummyself.body.content)

        dummyself = self._get_dummy_self()
        dummynode = self._get_dummy_node(**{"data-markdown": ""})

        self._call_fut(dummyself, dummynode)
        self.assertEqual([
            compat.text("<section data-markdown='' id='id'>"),
            compat.text("<script type='text/template'>\n"),
            compat.text('# title \n'),
            compat.text('## subtitle \n'),
            compat.text('rawsource'),
            compat.text('</script>\n')
        ], dummyself.body.content)


class TestDepartRevealjs(ExtTestCase):

    def _get_target(self):
        return depart_revealjs

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_self(self, *args, **kwargs):
        class DummyBody(object):
            content = []

            def append(self, content):
                self.content.append(content)

        class DummySelf(object):
            def __init__(self, body):
                self.body = body
        return DummySelf(DummyBody())

    def test_it(self):
        dummyself = self._get_dummy_self()
        self._call_fut(dummyself, None)
        assert '</section>\n' == dummyself.body.content[0]


class TestVisitRvCode(ExtTestCase):

    def _get_target(self):
        return visit_rv_code

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_node(self, *args, **kwargs):
        class DummyNode(object):
            @property
            def rawsource(self):
                return "rawsource"
        return DummyNode()

    def _get_dummy_self(self, *args, **kwargs):
        class DummyBody(object):
            content = []

            def append(self, content):
                self.content.append(content)

        class DummySelf(object):
            def __init__(self, body):
                self.body = body

            def starttag(self, node, tag):
                try:
                    return f"<{tag}>"
                except ValueError:
                    return f"<{tag}>"

        return DummySelf(DummyBody())

    def test_it(self):
        dummynode = self._get_dummy_node()
        dummyself = self._get_dummy_self()
        self._call_fut(dummyself, dummynode)
        assert '<pre>' == dummyself.body.content[0]
        assert '<code data-trim contenteditable>' ==\
            dummyself.body.content[1]
        assert 'rawsource' == dummyself.body.content[2]


class TestDepartRvCode(ExtTestCase):

    def _get_target(self):
        return depart_rv_code

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_self(self, *args, **kwargs):
        class DummyBody(object):
            content = []

            def append(self, content):
                self.content.append(content)

        class DummySelf(object):
            def __init__(self, body):
                self.body = body
        return DummySelf(DummyBody())

    def test_it(self):

        dummyself = self._get_dummy_self()
        self._call_fut(dummyself, None)
        self.assertEqual('</code>', dummyself.body.content[0])
        self.assertEqual('</pre>\n', dummyself.body.content[1])


class TestVisitRvSmall(ExtTestCase):

    def _get_target(self):
        return visit_rv_small

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_node(self, *args, **kwargs):
        class DummyNode(object):
            @property
            def rawsource(self):
                return "rawsource"
        return DummyNode()

    def _get_dummy_self(self, *args, **kwargs):
        class DummyBody(object):
            content = []

            def append(self, content):
                self.content.append(content)

        class DummySelf(object):
            def __init__(self, body):
                self.body = body
                self.first_last = False

            def starttag(self, node, tag):
                return f"<{tag}>"

            def set_first_last(self, node):
                self.first_last = True

        return DummySelf(DummyBody())

    def test_it(self):
        dummynode = self._get_dummy_node()
        dummyself = self._get_dummy_self()
        self._call_fut(dummyself, dummynode)
        self.assertEqual('<small>', dummyself.body.content[0])
        assert True is dummyself.first_last


class TestDepartRvSmall(ExtTestCase):

    def _get_target(self):
        return depart_rv_small

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_self(self, *args, **kwargs):
        class DummyBody(object):
            content = []

            def append(self, content):
                self.content.append(content)

        class DummySelf(object):
            def __init__(self, body):
                self.body = body
        return DummySelf(DummyBody())

    def test_it(self):

        dummyself = self._get_dummy_self()
        self._call_fut(dummyself, None)
        assert '</small>\n' == dummyself.body.content[0]


class TestVisitRvNote(ExtTestCase):

    def _get_target(self):
        return visit_rv_note

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_node(self, *args, **kwargs):
        class DummyNode(object):
            @property
            def rawsource(self):
                return "rawsource"
        return DummyNode()

    def _get_dummy_self(self, *args, **kwargs):
        class DummyBody(object):
            content = []

            def append(self, content):
                self.content.append(content)

        class DummySelf(object):
            def __init__(self, body):
                self.body = body
                self.first_last = False

            def starttag(self, node, tag, **kwargs):
                class_name = kwargs.pop('class')
                return f'<{tag} class="{class_name}">'

            def set_first_last(self, node):
                self.first_last = True

        return DummySelf(DummyBody())

    def test_it(self):
        dummynode = self._get_dummy_node()
        dummyself = self._get_dummy_self()
        self._call_fut(dummyself, dummynode)
        self.assertEqual('<aside class="notes">', dummyself.body.content[0])
        assert True is dummyself.first_last


class TestDepartRvNote(ExtTestCase):

    def _get_target(self):
        return depart_rv_note

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_self(self, *args, **kwargs):
        class DummyBody(object):
            content = []

            def append(self, content):
                self.content.append(content)

        class DummySelf(object):
            def __init__(self, body):
                self.body = body
        return DummySelf(DummyBody())

    def test_it(self):

        dummyself = self._get_dummy_self()
        self._call_fut(dummyself, None)
        self.assertEqual('</aside>\n', dummyself.body.content[0])


class TestSetup(ExtTestCase):

    def _get_target(self):
        return setup

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def test_it(self):

        class DummyApp(object):

            nodes = []
            directives = {}

            def info(self, info):
                self.info = info

            def add_node(self, node, html):
                self.nodes.append((node, html))

            def add_directive(self, name, directive):
                self.directives.update({name: directive})

        dummy_app = DummyApp()
        self._call_fut(dummy_app)
        self.assertEqual(d.revealjs, dummy_app.nodes[0][0])
        self.assertEqual((d.visit_revealjs, d.depart_revealjs),
                         dummy_app.nodes[0][1])

        self.assertEqual(d.rv_code, dummy_app.nodes[1][0])
        self.assertEqual((d.visit_rv_code, d.depart_rv_code),
                         dummy_app.nodes[1][1])

        self.assertEqual(d.rv_note, dummy_app.nodes[2][0])
        self.assertEqual((d.visit_rv_note, d.depart_rv_note),
                         dummy_app.nodes[2][1])

        self.assertEqual(d.rv_small, dummy_app.nodes[3][0])
        self.assertEqual((d.visit_rv_small, d.depart_rv_small),
                         dummy_app.nodes[3][1])

        self.assertEqual(d.RevealjsDirective, dummy_app.directives['revealjs'])
        self.assertEqual(d.RvCodeDirective, dummy_app.directives['rv_code'])
        self.assertEqual(d.RvNoteDirective, dummy_app.directives['rv_note'])
        self.assertEqual(d.RvSmallDirective, dummy_app.directives['rv_small'])


if __name__ == "__main__":
    unittest.main()
