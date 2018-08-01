"""
@file
@brief Puts everything related to package :epkg:`yaml` in a separate files.
"""
import yaml


def yaml_load(content):
    """
    Parses a :epkg:`yml` file with :epkg:`yaml`.

    @param      content     string
    @return                 structured data
    """
    return yaml.load(content)
