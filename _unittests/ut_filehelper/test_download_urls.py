"""
@brief      test log(time=2s)
"""
import os
import unittest
from pyquickhelper.pycode import ExtTestCase, get_temp_folder
from pyquickhelper.loghelper import fLOG
from pyquickhelper.filehelper.download_helper import (
    get_urls_content_timeout, local_url)
from pyquickhelper.filehelper.download_urls_helper import download_urls_in_folder_content


class TestDownloadUrls(ExtTestCase):

    def test_download_urls_assert(self):
        self.assertRaise(lambda: get_urls_content_timeout(dict()), TypeError)
        self.assertRaise(lambda: get_urls_content_timeout(
            [], folder=None), ValueError)

    def test_download_urls(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, 'temp_download_urls')
        urls = ['http://www.xavierdupre.fr',
                'http://www.xavierdupre.fr']
        get_urls_content_timeout(urls, folder=temp, fLOG=fLOG)
        content = os.listdir(temp)
        self.assertEqual(
            set(content), set(['dd5ba53e5e4efe59f0ce3b0ef.bin', 'summary.csv']))
        get_urls_content_timeout(urls, folder=temp, fLOG=fLOG)
        content2 = os.listdir(temp)
        self.assertEqual(set(content), set(content2))
        self.assertRaise(lambda: local_url(urls[0]), FileNotFoundError)
        loc = local_url(urls[0], folder=temp)
        self.assertIn('.bin', loc)
        u = 'http://notlocal.html'
        loc = local_url(u, folder=temp)
        self.assertEqual(loc, u)

    def test_download_urls_in_folder_content(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(
            __file__, 'temp_download_urls_in_folder_content')
        this = os.path.abspath(os.path.dirname(__file__))
        res = download_urls_in_folder_content(
            this, folder_dest=temp, raise_exception=False)
        self.assertGreater(len(res), 4)
        summary = os.path.join(temp, 'summary.csv')
        with open(summary, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('http://www.xavierdupre.fr', content)


if __name__ == "__main__":
    unittest.main()
