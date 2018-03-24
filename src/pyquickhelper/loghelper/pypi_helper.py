"""
@file
@brief Helpers to information for pypi version.
"""
from datetime import datetime
import sys
if sys.version_info[0] == 2:
    import xmlrpclib as xmlrpc_client
else:
    import xmlrpc.client as xmlrpc_client


def enumerate_pypi_versions_date(name, url='https://pypi.python.org/pypi'):
    """
    Retrieves version and releases dates for modules
    hosted on :epkg:`pypi`.

    @param      name        module name
    @param      url         url
    @return                 list tuple (date, version, size)
    """
    pypi = xmlrpc_client.ServerProxy(url)
    available = pypi.package_releases(name, True)
    for ver in available:
        res = pypi.release_urls(name, ver)
        for r in res:
            yield datetime(* tuple(r['upload_time'].timetuple())[:6]), ver, r['size']
            break
