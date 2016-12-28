
.. blogpost::
    :title: Major changes
    :keywords: Jenkins, documentation
    :date: 2016-09-03
    :categories: automation

    I now use YAML to define a build script.
    See `.local.jenkins.win.yml <https://github.com/sdpython/pyquickhelper/blob/master/.local.jenkins.win.yml>`_.
    I did not expect that to be so long but it did not scale anymore.
    So the process is basically to run a script which interprets the
    file `.local.jenkins.win.yml <https://github.com/sdpython/pyquickhelper/blob/master/.local.jenkins.win.yml>`_
    as a series of `Jenkins <https://jenkins.io/>`_ jobs.
    Unfortunately, I discovered many issues for some modules
    refusing to work from a virtual environment on Windows.
    It starts by running function
    :func:`setup_jenkins_server_yml <pyquickhelper.jenkinshelper.jenkins_helper.setup_jenkins_server_yml>`.
    The rest is pressing buttons.