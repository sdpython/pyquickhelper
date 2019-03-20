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

    def __init__(self, paths, position=-1):
        """
        @param      paths       paths to add
        @param      position    where to add it
        """
        self.to_add = paths if isinstance(paths, list) else [paths]
        self.position = position

    def __enter__(self):
        """
        Modifies ``sys.path``.
        """
        self.store = sys.path.copy()
        if self.position == -1:
            sys.path.extend(self.to_add)
        else:
            for p in reversed(self.to_add):
                sys.path.insert(self.position, p)

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Restores``sys.path``.
        """
        sys.path = self.store
