# -*- coding: utf-8 -*-
"""
@file
@brief Custom functions to post process latex output before compiling it.
"""


def find_custom_latex_processing(name):
    """
    Determines the corresponding post processing function
    associated to name.
    """
    raise ValueError(
        "Unable to find any post processing function associated to '{0}'".format(name))
