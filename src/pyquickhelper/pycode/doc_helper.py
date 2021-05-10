"""
@file
@brief Helpers to improve documentation.
"""
import re
from urllib.request import urlopen
from ..filehelper.synchelper import explore_folder_iterfile


def find_link(text):
    """
    Finds all links following RST format in a documentation.

    :param text: text
    :return: all urls
    """
    url = "https?://[-a-zA-Z0-9@:%._\\+~#=]+?[-a-zA-Z0-9@:%._\\+~#=/&?\\n ]*?"
    reg = [re.compile("[<](%s)[>]" % url),
           re.compile("[.]{2} image:: (%s)\\n" % url),
           re.compile("[.]{2} download:: (%s)\\n" % url)]
    res = []
    for r in reg:
        a = r.findall(text)
        if len(a) > 0:
            res.extend([_.replace("\n", "").replace(" ", "") for _ in a])
    return res


def validate_urls(urls):
    """
    Checks that all urls are valid.
    """
    issue = []
    for u in urls:
        try:
            with urlopen(u, timeout=10) as f:
                content = f.read(10)
            if len(content) != 10:
                issue.append((u, "Cannot download"))
        except Exception as e:
            issue.append((u, e))
    return issue


def validate_urls_in_folder(folder, ext="py,rst,ipynb",
                            neg_pattern=".*__pycache__.*",
                            recursive=True, verbose=False):
    """
    Looks for all files in a folder and return all invalid urls.

    :param folder: folder to look into
    :param ext: files extension to look into
    :param neg_pattern: exclude files following that pattern
    :param recursive: look into sub folders
    :param verbose: use :epkg:`tqdm` to display a progress bar
    :return: enumerator on issues
    """
    if isinstance(ext, str):
        ext = ext.split(",")
    pattern = ".*[.](%s)$" % "|".join(["(%s)" % e for e in ext])
    for name in explore_folder_iterfile(
            folder, pattern=pattern, neg_pattern=None,
            fullname=True, recursive=recursive, verbose=verbose):
        with open(name, "r", encoding="utf-8") as f:
            content = f.read()
        urls = find_link(content)
        issues = validate_urls(urls)
        for issue in issues:
            yield (name, ) + issue
