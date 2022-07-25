"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
from pyquickhelper.pycode import ExtTestCase, ignore_warnings
from pyquickhelper.sphinxext.sphinx_doctree_builder import DocTreeTranslator
from pyquickhelper.sphinxext.sphinx_latex_builder import EnhancedLaTeXTranslator
from pyquickhelper.sphinxext.sphinx_md_builder import MdTranslator
from pyquickhelper.sphinxext.sphinx_rst_builder import RstTranslator


class TestBuildersMissing(ExtTestCase):

    @ignore_warnings(PendingDeprecationWarning)
    def test_builders_missing(self):
        from docutils import nodes as skip_
        from sphinx.builders.latex.util import ExtBabel
        from sphinx.builders.latex.theming import Theme

        context = {'sphinxpkgoptions': '', 'latex_engine': 'pdflatex',
                   'fontenc': [], 'babel': [],
                   'polyglossia': False, 'maxlistdepth': 3,
                   'sphinxsetup': None, 'extraclassoptions': {}}

        class dummy0:
            def __init__(self):
                pass

            def __getattr__(self, name):
                if name in ("latex_elements", ):
                    return {}
                if name in ('latex_docclass', ):
                    return {}
                if name in 'numfig_format':
                    return {'figure': '%s', 'table': '%s', 'code-block': '%s'}
                if name == 'language':
                    return 'en'
                if name == "today_fmt":
                    return "%b %d, %Y"
                if name in ('numfig_secnum_depth', ):
                    return 0
                if name in ('context', ):
                    return context
                return None

        class dummy:
            def __init__(self):
                self.config = dummy0()
                self.settings = dummy0()
                self.rst_image_dest = ''
                self.md_image_dest = ''
                self.env = dummy0()
                self.context = context
                self.babel = ExtBabel('en')

            def get(self, name):  # pylint: disable=R1711
                return None

        element = skip_.section()
        element['expr'] = 'True'
        element['delimiter'] = ';'
        element['uri'] = ''
        element['type'] = ''

        cls = [EnhancedLaTeXTranslator, RstTranslator,
               MdTranslator, DocTreeTranslator]
        builder = dummy()
        document = dummy()

        for cl in cls:
            if cl == EnhancedLaTeXTranslator:
                theme = Theme('manual')
                inst = cl(document, builder, theme)
            else:
                inst = cl(document, builder)
            inst._footnote = 'nofootnote'
            inst.rst_image_dest = ''
            if hasattr(inst, 'visit_table'):
                inst.visit_table(element)
            for k in cl.__dict__:
                if (k.startswith("visit_") or k.startswith("depart_") and
                        k not in ('visit_table', 'depart_table')):
                    fct = getattr(cl, k)
                    try:
                        fct(inst, element)
                    except skip_.SkipNode:
                        pass
                    except IndexError:
                        pass
                    except KeyError:
                        pass
                    except TypeError as e:
                        if 'NoneType' in str(e) or "'<=' not supported" in str(e):
                            pass
                        else:
                            raise e
                    except ValueError as e:
                        if "max()" in str(e):
                            pass
                        else:
                            raise e
                    except Exception as e:
                        if k in ('visit_document', 'visit_enumerated_list',
                                 'visit_only', 'depart_only', 'visit_table',
                                 'depart_pending_xref'):
                            pass
                        else:
                            raise Exception(
                                f"Unable to run '{k}'") from e
            if hasattr(inst, 'depart_table'):
                inst.depart_table(element)


if __name__ == "__main__":
    unittest.main()
