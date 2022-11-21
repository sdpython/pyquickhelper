"""
@brief      test tree node (time=7s)
"""
import unittest
import os
from pyquickhelper.pycode import ExtTestCase, ignore_warnings
from pyquickhelper.pycode.doc_helper import (
    find_link, validate_urls, validate_urls_in_folder)


class TestDocHelper(ExtTestCase):

    text = """

    `zoo <https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/neural_network/_base.py>`_

    `zoo <https://github.com/scikit-learn/scikit-learn/
    blob/main/sklearn/neural_network/_base1.py>`_

    `zoo <https://github.com/scikit-learn/scikit-learn/
    blob/main/sklearn/neural_network/ _base2.py>`_

    .. image:: http://www.xavierdupre.fr/app/ensae_teaching_cs/helpsphinx/_static/project_ico.png

    .. download:: http://www.xavierdupre.fr/app/ensae_teaching_cs/helpsphinx/_static/project_ico.png
    """

    exp = [
        "https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/neural_network/_base.py",
        "https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/neural_network/_base1.py",
        "https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/neural_network/_base2.py",
        "http://www.xavierdupre.fr/app/ensae_teaching_cs/helpsphinx/_static/project_ico.png",
        "http://www.xavierdupre.fr/app/ensae_teaching_cs/helpsphinx/_static/project_ico.png",
    ]

    def test_find_link(self):
        res = find_link(TestDocHelper.text)
        self.assertEqual(len(res), len(TestDocHelper.exp))
        for i in range(len(res)):  # pylint: disable=C0200
            self.assertEqual(TestDocHelper.exp[i], res[i])

    def test_validate_url(self):
        val = validate_urls(TestDocHelper.exp)
        self.assertEqual(len(val), 2)

    @ignore_warnings(ResourceWarning)
    def test_validate_url_folder(self):
        this = os.path.abspath(os.path.dirname(__file__))
        issues = []
        for issue in validate_urls_in_folder(this):
            issues.append(issue)
        self.assertIn(len(issues), (2, 3, 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
