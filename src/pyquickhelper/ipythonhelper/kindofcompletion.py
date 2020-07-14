"""
@file
@brief A custom way to add auto completion to IPython
"""

import os


class AutoCompletion:

    """
    You can add auto completion object to IPython by adding member
    to an instance of this class.

    All members must begin by ``_``
    """

    def __init__(self, value=None):
        """
        constructor

        @param      value       any value of object
        """
        self._value = value

    @property
    def _(self):
        """
        return the value
        """
        return self._value

    def _add(self, member, value):
        """
        add a member to this class, add an ``AutoCompletion`` instance,
        creates one if value is not from ``AutoCompletion`` type

        @param      member    name of the new member
        @param      value     value to add
        @return               (AutoCompletion)
        """
        if member in self.__dict__:
            raise NameError(  # pragma: no cover
                "Unable to add member {0} because it already exists".format(
                    member))
        if member.startswith("_"):
            raise NameError(  # pragma: no cover
                "A member cannot start by _: {0}".format(member))
        if isinstance(value, AutoCompletion):
            self.__dict__[member] = value
            return value
        value = AutoCompletion(value)
        self.__dict__[member] = value
        return value

    @property
    def _members(self):
        """
        returns all the members
        """
        return [_ for _ in self.__dict__ if not _.startswith("_")]

    def __len__(self):
        """
        returns the number of elements
        """
        return 1 + sum(len(self.__dict__[_]) for _ in self._members)

    def __str__(self):
        """
        returns a string
        """
        ch = self._members
        if len(ch) == 0:
            return ""
        rows = []
        for i, c in enumerate(sorted(ch)):
            pref = " |  " if i < len(ch) - 1 else "    "
            name = " |- " + c
            rows.append(name)
            sub = str(self.__dict__[c])
            if len(sub) > 0:
                lin = sub.split("\n")
                lin = [(pref + _) for _ in lin]
                rows.extend(lin)
        return "\n".join(rows)


class AutoCompletionFile(AutoCompletion):

    """
    builds a tree based on a list of files,
    the class adds ``A__`` before every folder or file starting with ``_``

    .. exref::
        :title: File autocompletion in IPython

        The following code:

        ::

            from pyquickhelper.ipythonhelper import AutoCompletionFile
            d = AutoCompletionFile(".")

        Will produce the following auto completion picture:

        @image images/completion.png
    """

    def __init__(self, value):
        """
        constructor

        @param  value       directory
        """
        if not os.path.exists(value):
            raise FileNotFoundError(  # pragma: no cover
                "{0} does not exists".format(value))
        AutoCompletion.__init__(self, os.path.normpath(os.path.abspath(value)))
        self._populate()

    def _filter(self, s):
        """
        Removes unexpected characters for a file name.

        @param      s       filename
        @return             cleaned filename
        """
        s = s.replace("'", "_") \
            .replace('"', "_") \
            .replace('(', "_") \
            .replace(')', "_") \
            .replace('[', "_") \
            .replace(']', "_") \
            .replace('{', "_") \
            .replace('}', "_") \
            .replace('.', "_") \
            .replace(':', "_") \
            .replace('/', "_") \
            .replace('\\', "_") \
            .replace('!', "_") \
            .replace('$', "_") \
            .replace('-', "_") \
            .replace('#', "_") \
            .replace('*', "_")
        if s.startswith("_"):
            s = "A__" + s
        return s

    def _populate(self):
        """
        populate the class with files and folder in the folder
        this class holds
        """
        if os.path.isdir(self._):
            files = os.listdir(self._)
            for file in files:
                fullname = os.path.join(self._, file)
                obj = AutoCompletionFile(fullname)
                self._add(self._filter(file), obj)
