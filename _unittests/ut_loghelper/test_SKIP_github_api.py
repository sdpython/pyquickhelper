"""
@brief      test tree node (time=12s)
"""


import sys
import os
import unittest

from pyquickhelper.pycode import is_travis_or_appveyor
from pyquickhelper.loghelper.github_api import call_github_api, GitHubApiException


class TestGitHub(unittest.TestCase):

    def test_github_api(self):
        if is_travis_or_appveyor():
            # Too many calls from many projects.
            return

        pulls = call_github_api("sdpython", "pyquickhelper", "issues")
        self.assertIsInstance(pulls, list)
        self.assertTrue(len(pulls) > 0)
        pr = call_github_api("scikit-learn", "scikit-learn", "pulls")
        self.assertIsInstance(pr, list)
        self.assertTrue(len(pr) > 0)
        try:
            stats = call_github_api(
                "scikit-learn", "scikit-learn", "stats/commit_activity")
            self.assertIsInstance(stats, list)
            self.assertTrue(len(stats) >= 0)
        except GitHubApiException as e:
            self.assertIn("[202]", str(e))
        try:
            call_github_api("scikit-learn", "scikit-learn", "traffic/views")
            self.assertTrue(False)
        except GitHubApiException as e:
            self.assertIn("message", str(e))


if __name__ == "__main__":
    unittest.main()
