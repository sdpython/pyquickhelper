"""
@file
@brief Puts everything related to package :epkg:`yaml` in a separate files.
"""
import yaml
try:
    from yaml import FullLoader as Loader
except ImportError:  # pragma: no cover
    Loader = None


def yaml_load(content):
    """
    Parses a :epkg:`yml` file with :epkg:`yaml`.

    @param      content     string
    @return                 structured data
    """
    if Loader is None:
        return yaml.load(content)
    return yaml.load(content, Loader=Loader)
