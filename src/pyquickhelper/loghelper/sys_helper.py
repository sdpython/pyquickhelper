"""
@file
@brief Helpers around functions in :epkg:`*py:sys`.
"""
import sys


class sys_path_append:
    """
    Stores the content of :epkg:`*py:sys:path` and
    restores it afterwards.
    """

    def __init__(self, paths):
        """
        @param      paths       paths to add
        """
        self.to_add = paths if isinstance(paths, list) else [paths]

    def __enter__(self):
        """
        Modifies ``sys.path``.
        """
        self.store = sys.path.copy()
        sys.path.extend(self.store)

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Restores``sys.path``.
        """
        sys.path = self.store
