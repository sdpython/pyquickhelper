"""
@file
@brief Calls :epkg:`github` API.
"""
import requests


class GitHubApiException(Exception):
    """
    Exception raised when a call to github rest api failed.
    """

    def __init__(self, response, url):
        """
        Merges everything into a string.
        """
        Exception.__init__(self, "response={0}\nurl={1}\ntext={2}\nstatus={3}".format(
            response, url, response.text, response.status_code))


def call_github_api(owner, repo, ask, auth=None, headers=None):
    """
    Calls `GitHub REST API <https://developer.github.com/v3/>`_.

    @param      owner       owner of the project
    @param      auth        tuple *(user, password)*
    @param      repo        repository name
    @param      ask         query (see below)
    @param      header      dictionary
    @return                 json

    Example for *ask*:

    * ``commits``
    * ``downloads``
    * ``forks``
    * ``issues``
    * ``pulls``
    * ``stats/code_frequency`` - Needs authentification
    * ``stats/commit_activity`` - Needs authentification
    * ``stats/punch_card`` - Needs authentification
    * ``traffic/popular/referrers`` - Must have push access to repository
    * ``traffic/popular/paths`` - Must have push access to repository
    * ``traffic/views`` - Must have push access to repository
    * ``traffic/clones`` - Must have push access to repository

    GitHub limits the number of requets per hour:
    `Rate Limiting <https://developer.github.com/v3/#rate-limiting>`_.
    """
    url = 'https://api.github.com/repos/{0}/{1}/{2}'.format(
        owner, repo, ask.strip('/'))
    response = requests.get(url, auth=auth, headers=headers)
    if response.status_code != 200:
        raise GitHubApiException(response, url)
    return response.json()
