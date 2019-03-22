"""
@file
@brief Helpers around functions in :epkg:`*py:sys`.
"""
import os
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


class python_path_append:
    """
    Appends one path into
    ``PYTHONPATH``.
    """

    def __init__(self, paths, first=False):
        """
        @param      paths       paths to add
        @param      first       where to add it, first or last position
        """
        self.to_add = paths if isinstance(paths, list) else [paths]
        self.first = first

    def __enter__(self):
        """
        Modifies ``os.environ['PYTHONPATH']``.
        """
        self.store = os.environ.get('PYTHONPATH', '')
        sep = ';' if sys.platform.startswith('win') else ':'
        if self.first:
            new_value = self.to_add + [self.store]
        else:
            new_value = [self.store] + self.to_add
        new_value = sep.join(new_value).strip(sep)
        os.environ['PYTHONPATH'] = new_value

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Restores``sys.path``.
        """
        os.environ['PYTHONPATH'] = self.store
