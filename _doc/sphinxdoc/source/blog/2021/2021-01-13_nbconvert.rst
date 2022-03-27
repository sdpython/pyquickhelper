
.. blogpost::
    :title: Issue with nbconvert: unknown exporter "python"
    :keywords: linux, logging
    :date: 2021-01-13
    :categories: security

    I bumped into the following error:

    ::

        nbconvert.exporters.base.ExporterNameError:
        Unknown exporter "python", did you mean one of: ?

    This issue was raised by the following piece of code:

    ::

        from nbconvert.exporters import get_exporter
        get_exporter("python")

    And this code gave another reason for the error:

    ::

        Permission denied: '/usr/share/jupyter/nbconvert/templates/conf.json'

    And this file is only available to another user.
    I don't know why *nbconvert* looks into that folder,
    it was run from a virtual environment created with
    option `--system-site-packages`.
    Anyway, removing the folder `/usr/share/jupyter/nbconvert/templates/`
    fixes the issue.
