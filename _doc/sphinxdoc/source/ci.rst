
.. _l-ci-jenkins:

Continuous Integration
======================

The module is tested with `Travis <https://travis-ci.org/sdpython/pyquickhelper>`_, 
`AppVeyor <https://www.appveyor.com/>`_ and local testing with
`Jenkins <https://jenkins-ci.org/>`_ for a exhaustive list of unit tests,
the documentation, the setup. Everything is fully tested on Windows with the standard distribution and 
`Anaconda <http://continuum.io/downloads>`_.
There are three builds definition:

* Travis: `.travis.yml <https://github.com/sdpython/pyquickhelper/blob/master/.travis.yml>`_
* AppVeyor: `appveyor.yml <https://github.com/sdpython/pyquickhelper/blob/master/appveyor.yml>`_
* Jenkins: `.local.jenkins.win.yml <https://github.com/sdpython/pyquickhelper/blob/master/.local.jenkins.win.yml>`_

The third file by processed by *pyquickhelper* itself to produce a series of Jenkins jobs
uploaded to a server. See :func:`setup_jenkins_server_yml <pyquickhelper.jenkinshelper.jenkins_helper.setup_jenkins_server_yml>`
to configurate a local Jenkins server.

When modules depend on others modules also being tested, the 
unit tests and the documentation generation uses a local pypi server (port=8079).
It can be set up by executing the script ``auto_cmd_local_pypi.*``.

