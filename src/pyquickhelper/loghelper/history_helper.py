"""
@file
@helper Build history for a module.
"""
from datetime import datetime, timedelta
import requests
import warnings
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
                warnings.warn('API rate limit exceeded')
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
        yield number, closed, title


def build_history(owner, repo, name=None, since=None, issues=None, url=None,
                  max_issue=None, releases=None, unpublished=False, fLOG=None):
    """
    Returns an history of a module.

    @param      owner       repo owner
    @param      repo        repository
    @param      name        None if ``name == repo``
    @param      since       not older than that date, if None,
                            do not go beyond a year
    @param      issues      see @see fn call_github_api (unit test)
    @param      url         see @see fn call_github_api (unit test)
    @param      max_issue   see @see fn call_github_api (unit test)
    @param      releases    bypass :epkg:`pypi` (unit test)
    @param      unpublished keep unpublished released
    @param      fLOG        logging function
    @return                 iterator on issues ``(number, date, title)``
    """
    if since is None:
        since = datetime.now() - timedelta(730)
    if name is None:
        name = repo

    kept_issues = []
    for issue in enumerate_closed_issues(owner, repo, since, issues=issues,
                                         url=url, max_issue=max_issue):
        kept_issues.append(issue)
        if fLOG:
            fLOG("[build_history] ", name, issue[:2])
    if len(kept_issues) == 0:
        raise ValueError("No issue found.")

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
        raise ValueError('No release found.')

    # merge
    dates = [(v[0], "v", v) for v in versions]
    dates.extend((i[1], "i", i) for i in kept_issues)
    dates.sort(reverse=True)

    merged = []
    current = None
    if unpublished:
        current = dict(release="current", size=0,
                       date=datetime.now(), issues=[])
    for d, v, obj in dates:
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
=======
History
=======
{% for release in releases %}
{{ release['release'] }} - {{ release['date'].strftime("%Y-%m-%d") }} - {{ '%1.2fMb' % (release['size'] * 2**(-20)) }}
{{ '=' * (len(release['release']) + 22) }}
{% for issue in release['issues'] %}
* `{{issue['number']}}`: {{issue['title']}} ({{issue['date'].strftime("%Y-%m-%d")}}) {% endfor %}
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
