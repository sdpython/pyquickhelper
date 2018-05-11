"""
@file
@brief Put everything related to yaml in a separate files.
"""
import yaml


def yaml_load(content):
    """
    Parses a :epkg:`yml` file with :epkg:`yaml`.

    @param      content     string
    @return                 structured data
    """
    return yaml.load(content)
