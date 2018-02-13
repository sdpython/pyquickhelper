"""
@file
@brief Various function to install some application such as :epkg:`pandoc`.
"""
from __future__ import print_function
import re
import os

from ..filehelper import download, read_url
from ..filehelper.compression_helper import unzip_files
from ..filehelper.synchelper import explore_folder_iterfile


def download_revealjs(temp_folder=".", unzip_to=".", fLOG=print,
                      location="https://github.com/hakimel/reveal.js/releases",
                      clean=True):
    """
    Download :epkg:`reveal.js` release and unzip it.

    @param      temp_folder     where to download the setup
    @param      unzip_to        where to unzip the files
    @param      fLOG            logging function
    @param      location        location of reveal.js release
    @param      clean           clean unnecessary files
    @return                     list of downloaded and unzipped files
    """
    link = location
    page = read_url(link, encoding="utf8")
    reg = re.compile("href=\\\"(.*?[0-9.]+?[.]zip)\\\"")
    alls = reg.findall(page)
    if len(alls) == 0:
        raise Exception(
            "unable to find a link on a .zip file on page: " +
            page)

    filename = alls[0].split("/")[-1]
    filel = location.replace("releases", "") + "/archive/{0}".format(filename)
    outfile = os.path.join(temp_folder, "reveal.js." + filename)
    fLOG("download ", filel, "to", outfile)
    local = download(filel, temp_folder, fLOG=fLOG)
    fLOG("local file", local)
    unzip_files(local, where_to=unzip_to)

    # we rename
    sub = [_ for _ in os.listdir(unzip_to) if "reveal" in _]
    if len(sub) != 1:
        raise FileNotFoundError(
            "several version exists or noe of them:\n{0}".format(", ".join(sub)))
    sub = sub[0]
    master = os.path.join(unzip_to, sub)
    if not os.path.exists(master):
        raise FileNotFoundError("unable to find: " + master)
    new_master = os.path.join(unzip_to, "reveal.js")
    os.rename(master, new_master)

    if clean:
        # we clean some files
        res = explore_folder_iterfile(new_master)
        keep = []
        for r in res:
            if os.path.isdir(r):
                continue
            if ".gitignore" in r or ".travis.yml" in r or "index.html" in r \
               or ".appveyor.yml" in r \
               or "requirement" in r \
               or "README" in r or "CONTRIBUTING.md" in r:
                os.remove(r)
            elif "/test/" in r.replace("\\", "/"):
                os.remove(r)
            else:
                keep.append(r)

        # we clean the downloaded file
        os.remove(local)

    return keep


def download_requirejs(to=".", fLOG=print,
                       location="http://requirejs.org/docs/download.html",
                       clean=True):
    """
    Download `require.js <http://requirejs.org/docs/download.html>`_ release.

    @param      to              where to unzip the files
    @param      fLOG            logging function
    @param      location        location of require.js release
    @param      clean           clean unnecessary files
    @return                     list of downloaded and unzipped files
    """
    link = location
    page = read_url(link, encoding="utf8")
    reg = re.compile("href=\\\"(.*?minified/require[.]js)\\\"")
    alls = reg.findall(page)
    if len(alls) == 0:
        raise Exception(
            "unable to find a link on require.js file on page: " +
            page)

    filename = alls[0]
    local = download(filename, to, fLOG=fLOG)
    fLOG("local file", local)
    return [local]
