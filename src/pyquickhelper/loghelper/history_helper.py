"""
@file
@helper Build history for a module.

.. versionadded:: 1.7
"""
from datetime import datetime, timedelta
import re
import warnings
import requests
from jinja2 import Template
from .github_api import call_github_api
from .pypi_helper import enumerate_pypi_versions_date


def enumerate_closed_issues(owner, repo, since=None, issues=None,
                            url=None, max_issue=None):
    """
    Enumerates github issues for a repo and an owner
    since a given date.

    @param      owner       repo owner
    @param      repo        repository
    @param      since       not older than that date, if None,
                            do not go beyond a year
    @param      issues      to bypass @see fn call_github_api
    @param      url         if available, something like
                            ``https://api.github.com/repos/sdpython/pyquickhelper/issues/{0}``
    @param      max_issue   max number of issues
    @return                 iterator on issues ``(number, date, title)``
    """
    if since is None:
        since = datetime.now() - timedelta(365)
    if issues is None and url is not None and max_issue is not None:
        issues = [dict(url=url.format(k)) for k in range(max_issue, 0, -1)]
    elif issues is None:
        issues = call_github_api(owner, repo, 'issues?state=closed')
    if len(issues) == 0:
        raise ValueError("No issue found.")
    for issue in issues:
        if 'title' not in issue:
            url = issue['url']
            response = requests.get(url)
            content = response.json()
            if 'API rate limit exceeded' in content.get('message', ''):
                warnings.warn('API rate limit exceeded', ResourceWarning)
                break
        else:
            content = issue
        closed = content.get('closed_at', None)
        if closed is None:
            continue
        title = content['title']
        closed = datetime.strptime(closed.strip('Z'), "%Y-%m-%dT%H:%M:%S")
        number = content['number']
        if closed < since:
            break
        if ("[WIP]" not in title and
                "[remove]" not in title.lower() and
                "[removed]" not in title.lower() and
                "[DEL]" not in title and
                "[WONT]" not in title and
                "[SKIP]" not in title and
                "[won't fix]" not in title.lower() and
                "[WONTDO]" not in title):
            yield number, closed, title


def build_history(owner, repo, name=None, since=None, issues=None, url=None,
                  max_issue=None, releases=None, unpublished=False,
                  existing_history=None, skip_issues=None, fLOG=None):
    """
    Returns an history of a module.

    @param      owner               repo owner
    @param      repo                repository
    @param      name                None if ``name == repo``
    @param      since               not older than that date, if None,
                                    do not go beyond a year
    @param      issues              see @see fn call_github_api (unit test)
    @param      url                 see @see fn call_github_api (unit test)
    @param      max_issue           see @see fn call_github_api (unit test)
    @param      releases            bypass :epkg:`pypi` (unit test)
    @param      unpublished         keep unpublished released
    @param      existing_history    existing history, retrieves existing issues stored
                                    in that file
    @param      skip_issues         skip a given list of issues when building the history
    @param      fLOG                logging function
    @return                         iterator on issues ``(number, date, title)``
    """
    if since is None:
        since = datetime.now() - timedelta(730)
    if name is None:
        name = repo

    kept_issues = []
    if existing_history is not None:
        res = extract_issue_from_history(existing_history)
        for k, v in sorted(res.items()):
            if skip_issues is not None and k in skip_issues:
                continue
            kept_issues.append((k, v[0], v[1]))

    for issue in enumerate_closed_issues(owner, repo, since, issues=issues,
                                         url=url, max_issue=max_issue):
        if skip_issues is not None and issue[0] in skip_issues:
            continue
        kept_issues.append(issue)
        if fLOG:
            fLOG("[build_history] ", name, issue[:2])
    if len(kept_issues) == 0:
        raise ValueError("No issue found.")

    # remove duplicates
    current = kept_issues
    kept_issues = []
    done = set()
    for nb, dt, desc in current:
        if nb not in done:
            kept_issues.append((nb, dt, desc))
            done.add(nb)
    kept_issues.sort()

    if releases is None:
        versions = []
        for date, version, size in enumerate_pypi_versions_date(name):
            if date < since:
                break
            if fLOG:
                fLOG("[build_history] ", name, version, date)
            versions.append((date, version, size))
    else:
        versions = releases
    if len(versions) == 0:
        versions = [(datetime.now(), '0.0.0', 0)]

    # merge
    dates = [(v[0], "v", v) for v in versions]
    dates.extend((i[1], "i", i) for i in kept_issues)
    dates.sort(reverse=True)

    merged = []
    current = None
    if unpublished:
        current = dict(release="current", size=0,
                       date=datetime.now(), issues=[])
    for _, v, obj in dates:
        if v == 'v':
            if current is not None:
                merged.append(current)
            current = dict(release=obj[1], size=obj[2], date=obj[0], issues=[])
        elif v == 'i':
            if current is not None:
                issue = dict(title=obj[2], date=obj[1], number=obj[0])
                current['issues'].append(issue)

    if current is not None:
        merged.append(current)
    return merged


_template = """

.. _l-HISTORY:

=======
History
=======
{% for release in releases %}
{{ release['release'] }} - {{ release['date'].strftime("%Y-%m-%d") }} - {{ '%1.2fMb' % (release['size'] * 2**(-20)) }}
{{ '=' * (len(release['release']) + 22) }}
{% for issue in release['issues'] %}
* `{{issue['number']}}`: {{issue['title']}} ({{issue['date'].strftime("%Y-%m-%d")}}){% endfor %}
{% endfor %}
"""


def compile_history(releases, template=None):
    """
    Compile history and produces a :epkg:`rst` file.

    @param      releases    output of @see fn build_history
    @param      template    :epkg:`jinja2` template (None means default one)
    @return                 output
    """
    if template is None:
        global _template
        template = _template
    tmpl = Template(template)
    return tmpl.render(releases=releases, len=len)


class open_stream_file:
    """
    Opens a stream or a filename.
    It works with keyword ``with``.

    .. runpython::
        :showcode:

        from pyquickhelper.loghelper.history_helper import open_stream_file
        from io import StringIO
        st = StringIO("a\\nb")
        with open_stream_file(st) as f:
            for line in f.readlines():
                print(line)
    """

    def __init__(self, name, mode="r", encoding="utf-8"):
        """
        @param  name        stream or filename
        @param  mode        open mode, works only if filename
        @param  encoding    encoding, works only if filename
        """
        self.name = name
        self.mode = mode
        self.encoding = encoding

    def __enter__(self):
        """
        Opens the stream or the file.
        """
        if hasattr(self, '_content'):
            del self._content
        if hasattr(self.name, "read"):
            self.st = self.name
        else:
            self.st = open(self.name, self.mode, encoding=self.encoding)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Leaves the stream or the filename.
        """
        if hasattr(self.name, "read"):
            pass
        else:
            self.st.close()
        if hasattr(self, '_content'):
            del self._content

    def read(self, size=None):
        """
        Reads some bytes.

        @param      size        number of bytes or characters to read
        @return                 content
        """
        return self.st.read(size=size)

    def readline(self):
        """
        Basic implementation.

        @return     next line
        """
        if hasattr(self.st, "readline"):
            return self.st.readline()
        else:
            if hasattr(self, '_content'):
                self._content = self.read().split('\n')
                self._pos = 0
            if self._pos >= len(self._content):
                return None
            res = self._content[self._pos]
            self._pos += 1
            return res

    def readlines(self):
        """
        Basic implementation.

        @return     all text lines
        """
        if hasattr(self.st, "readlines"):
            return self.st.readlines()
        else:
            line = self.readline()
            lines = []
            while line:
                lines.append(line)
                line = self.readline()
            return lines


def extract_issue_from_history(filename_or_stream):
    """
    Extracts issues from exsiting history stored
    in ``HISTORY.rst``. The pattern must extract
    from the following lines:

    ::

        * `133`: add a collapsible container, adapt it for runpython (2018-04-22)

    @param      filename        stream or filename
    @return                     ancient history, dictionary *{issue: (date, description)}*
    """
    with open_stream_file(filename_or_stream, mode='r', encoding='utf-8') as f:
        lines = f.readlines()
    reg = re.compile('`([0-9]+)`:(.*?)[(]([-0-9]{10})')
    res = {}
    for line in lines:
        match = reg.search(line)
        if match:
            gr = match.groups()
            issue = gr[0]
            desc = gr[1].strip()
            date = datetime.strptime(gr[2], '%Y-%m-%d')
            res[int(issue)] = (date, desc)
    return res
