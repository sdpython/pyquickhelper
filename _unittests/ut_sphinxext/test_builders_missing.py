"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

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

from src.pyquickhelper.pycode import ExtTestCase
from src.pyquickhelper.sphinxext.sphinx_doctree_builder import DocTreeTranslator
from src.pyquickhelper.sphinxext.sphinx_latex_builder import EnhancedLaTeXTranslator
from src.pyquickhelper.sphinxext.sphinx_md_builder import MdTranslator
from src.pyquickhelper.sphinxext.sphinx_rst_builder import RstTranslator


class TestBuildersMissing(ExtTestCase):

    def test_builders_missing(self):
        from docutils import nodes as skip_

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
                return None

        class dummy:
            def __init__(self):
                self.config = dummy0()
                self.settings = dummy0()
                self.rst_image_dest = ''
                self.md_image_dest = ''
                self.env = dummy0()

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
            inst = cl(builder, document)
            inst._footnote = 'nofootnote'
            inst.table = []
            inst.rst_image_dest = ''
            for k in cl.__dict__:
                if k.startswith("visit_") or k.startswith("depart_"):
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
                                "Unable to run '{0}'".format(k)) from e


if __name__ == "__main__":
    unittest.main()
