"""
@brief      test log(time=42s)
"""

import sys
import os
import unittest
import datetime

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.loghelper.history_helper import (
    build_history, compile_history, extract_issue_from_history
)

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


class TestHistoryHelper(ExtTestCase):

    issues = [{'body': None, 'closed_at': None, 'number': 139, 'state': 'open',
               'title': '???',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/139'},
              {'body': None, 'closed_at': None, 'number': 115, 'state': 'open', 'title': 'run notebook with starting a kernel',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/115'},
              {'body': None, 'closed_at': None, 'number': 114, 'state': 'open', 'title': 'automatically builds history with release and issues',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/114'},
              {'body': None, 'closed_at': '2018-03-19T20:31:48Z', 'number': 113, 'state': 'closed', 'title': 'propose a fix for a bug introduced by pip 9.0.2',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/113'},
              {'body': None, 'closed_at': '2018-03-15T18:20:41Z', 'number': 112, 'state': 'closed',
               'title': 'allow to set custom snippets for notebooks',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/112'},
              {'body': None, 'closed_at': '2018-03-20T23:24:09Z', 'number': 111, 'state': 'closed',
               'title': 'enable manual snippet for notebook, repace add_notebook_menu by toctree in sphinx',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/111'},
              {'body': None, 'closed_at': None, 'number': 110, 'state': 'open',
               'title': 'sphinx documentation, index is missing in latex final file',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/110'},
              {'body': None, 'closed_at': '2018-03-15T00:22:01Z', 'number': 109, 'state': 'closed',
               'title': 'run javascript producing svg and convert it into png',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/109'},
              {'body': None, 'closed_at': '2018-03-10T14:58:28Z', 'number': 108, 'state': 'closed',
               'title': 'add command lab, creates a script to start jupyter lab on notebook',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/108'},
              {'body': None, 'closed_at': '2018-03-12T22:19:19Z', 'number': 107, 'state': 'closed', 'title': 'convert svg into png for notebook snippets',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/107'},
              {'body': None, 'closed_at': '2018-03-03T14:52:08Z', 'number': 106, 'state': 'closed', 'title': 'replace pdflatex by xelatex to handle utf-8',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/106'},
              {'body': None, 'closed_at': None, 'number': 105, 'state': 'open', 'title': 'append bokeh js and css in notebook converted into rst',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/105'},
              {'body': None, 'closed_at': '2018-03-01T22:56:16Z', 'number': 104, 'state': 'closed',
               'title': 'implement visit, depart for pending_xref and rst translator',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/104'},
              {'body': None, 'closed_at': '2018-03-01T22:54:56Z', 'number': 103, 'state': 'closed', 'title': 'fix import issue for Sphinx 1.7.1',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/103'},
              {'body': None, 'closed_at': '2018-02-24T00:21:11Z', 'number': 102, 'state': 'closed', 'title': 'fix sphinx command line',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/102'},
              {'body': None, 'closed_at': '2018-02-13T23:07:46Z', 'number': 101, 'state': 'closed', 'title': 'migrate to sphinx 1.7',
               'url': 'https://api.github.com/repos/sdpython/pyquickhelper/issues/101'},
              ]

    releases = [(datetime.datetime(2020, 3, 22, 0, 57, 1), '1.9.3000', 2087804),
                (datetime.datetime(2018, 3, 22, 0, 57, 1), '1.7.2482', 2087803),
                (datetime.datetime(2018, 3, 19, 20, 33, 18), '1.7.2468', 2083943),
                (datetime.datetime(2018, 3, 3, 20, 57, 52), '1.7.2448', 2078334),
                (datetime.datetime(2018, 2, 23, 22, 53, 8), '1.7.2438', 2077672),
                (datetime.datetime(2018, 2, 23, 11, 13, 6), '1.7.2429', 2077611),
                (datetime.datetime(2018, 2, 13, 15, 14, 28), '1.6.2413', 2076866),
                (datetime.datetime(2018, 2, 4, 15, 49, 41), '1.6.2398', 647370),
                (datetime.datetime(2017, 11, 28, 18, 55, 43), '1.5.2275', 521698)]

    def test_history(self):
        self.assertRaise(lambda:
                         build_history(
                             'sdpython', 'pyquickhelper',
                             url="https://api.github.com/repos/sdpython/pyquickhelper/issues/{0}",
                             issues=TestHistoryHelper.issues,
                             max_issue=139, releases=TestHistoryHelper.releases),
                         ValueError)

    def test_history_existing(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "data", "HISTORY.rst")
        history = build_history('sdpython', 'pyquickhelper',
                                url="https://api.github.com/repos/sdpython/pyquickhelper/issues/{0}",
                                issues=TestHistoryHelper.issues,
                                max_issue=115, releases=TestHistoryHelper.releases,
                                existing_history=data)
        nb = 0
        for release in history:
            self.assertIn('issues', release)
            self.assertIn('release', release)
            nb += len(release['issues'])
        self.assertNotEmpty(history)
        self.assertGreater(nb, 1)

        output = compile_history(history)
        self.assertIn('* `139`:', output)
        nb = 0
        for h in history:
            rel = h['release']
            if rel == '1.6.2398':
                nb += 1
                self.assertNotEmpty(h['issues'])

    def test_extract_history(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "data", "HISTORY.rst")
        issues = extract_issue_from_history(data)
        self.assertEqual(len(issues), 4)
        self.assertIn(139, issues)

        with open(data, "r", encoding='utf-8') as f:
            content = f.read()
        st = StringIO(content)
        issues2 = extract_issue_from_history(st)
        self.assertEqual(len(issues2), 4)
        self.assertIn(139, issues2)
        self.assertEqual(issues, issues2)


if __name__ == "__main__":
    unittest.main()
