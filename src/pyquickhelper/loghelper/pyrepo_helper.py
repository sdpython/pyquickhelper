# -*- coding: utf-8 -*-
"""
@file
@brief   a repository class independent from the repository system (it will be guessed)
"""
from .repositories import pysvn_helper as SVN
from .repositories import pygit_helper as GIT


class SourceRepository:

    """
    Proposes the same functionality independent from the
    source chosen repository (GIT or SVN).

    On Windows, it might help to install either
    :epkg:`TortoiseSVN` or the :epkg:`GitHub` application.
    """

    def __init__(self, commandline=True):
        """
        @param      commandline     use command line or a specific module (like pysvn for example)
        """
        self.commandline = commandline
        self.module = None

    def SetGuessedType(self, location):
        """
        Guesses the repository type given a location
        and changes a member of the class.

        @param      location    location
        @return                 module to use
        """
        git = GIT.IsRepo(location, commandline=self.commandline)
        if not git:  # pragma: no cover
            svn = SVN.IsRepo(location, commandline=self.commandline)
            if not svn:
                try:
                    GIT.get_repo_version(
                        location, commandline=self.commandline, log=False)
                    self.module = GIT
                except Exception as e:
                    raise Exception(
                        "Unable to guess source repository type for location '{0}'. Error: '{1}'.".format(location, e))
            else:
                self.module = SVN
        else:
            self.module = GIT
        return self.module

    def ls(self, path):
        """
        Extracts the content of a location.

        @param      path        path
        @return                 a list
        """
        if self.module is None:
            self.SetGuessedType(path)
        return self.module.repo_ls(path, commandline=self.commandline)

    def log(self, path=None, file_detail=False):
        """
        Gets the latest changes operated on a file in a folder or a subfolder.

        @param      path            path to look
        @param      file_detail     if True, add impacted files
        @return                     list of changes, each change is a list of tuples:
                                    (author, change number (int), date (datetime),
                                    comment, full hash, link)

        The function uses a command line if an error occurred.
        It uses the xml format:

        ::

            <logentry revision="161">
                <author>xavier dupre</author>
                <date>2013-03-23T15:02:50.311828Z</date>
                <msg>pyquickhelper: first version</msg>
            </logentry>
        """
        if self.module is None:
            self.SetGuessedType(path)
        return self.module.get_repo_log(
            path, file_detail, commandline=self.commandline)

    def version(self, path=None):
        """
        Gets the latest check in number for a specific path.

        @param      path            path to look
        @return                     string or int (check in number)
        """
        if self.module is None:
            self.SetGuessedType(path)
        return self.module.get_repo_version(path, commandline=self.commandline)

    def nb_commits(self, path=None):
        """
        Returns the number of commits.

        @param      path            path to look
        @return                     number of commit
        """
        if self.module is None:
            self.SetGuessedType(path)
        return self.module.get_nb_commits(path, commandline=self.commandline)

    def get_last_commit_hash(self, path=None):
        """
        Returns the last commit.

        @param      path        path
        @return                 last commit
        """
        return self.log(path)[0][-2]
