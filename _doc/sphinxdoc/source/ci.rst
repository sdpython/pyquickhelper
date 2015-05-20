Continuous Integration
======================

The module is tested with `Travis <https://travis-ci.org/sdpython/pyquickhelper>`_.
I use `Jenkins <https://jenkins-ci.org/>`_ on an Azure machine to run the unit tests, generate
the documentation and the setup. Everything is fully tested on Windows with the standard distribution,
`Anaconda <http://continuum.io/downloads>`_ and `WinPython <https://winpython.github.io/>`_.
The list of jobs I used to get it done is defined by the function
`setup_jenkins_server <http://www.xavierdupre.fr/app/ensae_teaching_cs/helpsphinx3/ensae_teaching_cs/automation/jenkins_helper.html#ensae_teaching_cs.automation.jenkins_helper.setup_jenkins_server>`_.

The continuous integration for Windows may move to `AppVeyor <http://www.appveyor.com/>`_ some day.

When modules depend on others modules also being tested, the 
unit tests and the documentation generation uses a local pypi server (port=8079).
It can be set up by executing the script ``auto_cmd_local_pypi.*``.

