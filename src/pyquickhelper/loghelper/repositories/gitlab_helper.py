# -*- coding: utf-8 -*-
"""
@file
@brief Wrapper around GitLab API.
"""

import json


class GitLabException(Exception):

    """
    specific exception, stores the request
    """

    def __init__(self, mes, req=None):
        """
        @param  mes     message
        @param  req     request which caused the failure
        """
        Exception.__init__(self, mes)
        self.request = req

    def __str__(self):
        """
        usual
        """
        if self.request is None:
            return Exception.__str__(self)
        else:
            return "{0}\nCODE: {1}\n[giterror]\n{2}".format(
                Exception.__str__(self), self.request.status_code, self.request.content)


class GitLabAPI:

    """
    Wrapper around GitLab Server.

    The API is defined at `gitlabhq/doc/api <https://github.com/gitlabhq/gitlabhq/tree/master/doc/api>`_
    """

    def __init__(self, host, verify_ssl=True):
        """
        constructor

        @param      host            git lab host
        @param      verify_ssl      use_ssl (SSL connection)
        """
        self.host = host.rstrip("/")
        if not self.host.startswith(
                "https://") and not self.host.startswith("http://"):
            raise GitLabException("host should start with https:// or http://")

        self.api_url = self.host + "/api/v3"
        self.verify_ssl = verify_ssl

    def login(self, user, password):
        """
        login

        @param      user        user
        @param      password    password
        """
        import requests
        data = {"login": user, "password": password}
        url = "{0}/Session".format(self.api_url)
        request = requests.post(url, data=data, verify=self.verify_ssl,
                                headers={"connection": "close"})
        if request.status_code == 201:
            self.token = json.loads(
                request.content.decode("utf-8"))['private_token']
            self.headers = {"PRIVATE-TOKEN": self.token, "connection": "close"}
        elif request.status_code == 404:
            raise GitLabException("unable to login to " + url, request)
        else:
            msg = json.loads(request.content.decode("utf-8"))['message']
            raise GitLabException(
                "unable to login to " + url + "\n" + msg, request)

    def get_projects(self, page=1, per_page=100):
        """
        returns a list of dictionaries

        @return     list of dictionaries
        """
        import requests
        data = {'page': page, 'per_page': per_page}

        request = requests.get(
            self.api_url, params=data, headers=self.headers, verify=self.verify_ssl)
        if request.status_code == 200:
            return json.loads(request.content.decode("utf-8"))
        else:
            raise GitLabException(
                "unable to retreive the list of projects: {0}".format(request), request)
