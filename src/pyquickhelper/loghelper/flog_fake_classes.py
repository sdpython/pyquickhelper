# -*- coding: utf-8 -*-
"""
@file
@brief Exception specific to this module.
"""
import logging
import logging.handlers


class PQHException (Exception):

    """
    custom exception for this file
    """
    pass


class FlogStatic:

    """
    static variable for the log
    """

    def __init__(self):
        """
        constructor
        """
        self.store_log_values = dict()
        self.store_log_values["__log_const"] = "temp_log.txt"
        self.store_log_values["__log_path"] = "."
        self.store_log_values["__log_file_name"] = None
        self.store_log_values["__log_file"] = None
        self.store_log_values["__log_file_sep"] = "\n"
        self.store_log_values["__log_display"] = False
        self.store_log_values["month_date"] = {"jan": 1, "feb": 2, "mar": 3, "apr": 4,
                                               "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


class LogFakeFileStream:

    """
    a fake file
    """

    def __init__(self):
        """
        does nothing
        """
        pass

    def open(self):
        """
        does nothing
        """
        pass

    def write(self, s):
        """
        does nothing
        """
        pass

    def close(self):
        """
        does nothing
        """
        pass

    def flush(self):
        """
        does nothing
        """
        pass


class LogFileStream:

    """
    log as writing in a file
    """

    def __init__(self, filename):
        """
        creates a logger
        """
        if filename is None:
            filename = "temp_log.txt"
        self.pqlogger = logging.getLogger('logger.pyquickhelper')
        self.pqlogger.setLevel(logging.INFO)
        handler = logging.handlers.RotatingFileHandler(filename)
        self.pqlogger.addHandler(handler)

    def open(self):
        """
        does nothing
        """
        pass

    def write(self, s):
        """
        does nothing
        """
        self.pqlogger.info(s)

    def close(self):
        """
        does nothing
        """
        pass

    def flush(self):
        """
        does nothing
        """
        pass
