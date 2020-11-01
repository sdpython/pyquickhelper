"""
@file
@brief Helpers to information for pypi version.
"""
import time
from datetime import datetime
import xmlrpc.client as xmlrpc_client


class RateLimitedServerProxy(xmlrpc_client.ServerProxy):
    """
    See this `issue
    <https://github.com/pypa/warehouse/issues/8753>`_.
    """

    def __getattr__(self, name):
        time.sleep(1)
        return super(RateLimitedServerProxy, self).__getattr__(name)


def enumerate_pypi_versions_date(name, url='https://pypi.org/pypi'):
    """
    Retrieves version and releases dates for modules
    hosted on :epkg:`pypi`.

    @param      name        module name
    @param      url         url
    @return                 list tuple (date, version, size)
    """
    pypi = RateLimitedServerProxy(url)
    available = pypi.package_releases(name, True)
    for i, ver in enumerate(available):
        try:
            res = pypi.release_urls(name, ver)
        except xmlrpc_client.Fault as e:
            raise RuntimeError(
                "Unable to retrieve url for package '{}-{}': tentative {}/{}."
                "".format(name, ver, i + 1, len(available))) from e
        for r in res:
            if isinstance(r['upload_time'], str):
                dt = datetime.strptime(
                    r['upload_time'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
            else:
                try:
                    dt = datetime(* tuple(r['upload_time'].timetuple())[:6])
                except AttributeError as e:
                    raise AttributeError(
                        "Unable to parse '{0}'".format(r['upload_time'])) from e
            yield dt, ver, r['size']
            break
