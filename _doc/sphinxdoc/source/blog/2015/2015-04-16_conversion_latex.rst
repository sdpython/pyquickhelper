
.. blogpost::
    :title: Conversion to latex is taking for ever
    :keywords: pdflatex, Jenkins
    :date: 2015-04-16
    :categories: documentation, latex

    The unit tests are now scheduled using
    `Jenkins <https://jenkins-ci.org/>`_.
    When the documentation is generated for the first
    time after a fresh installation of the machine (latex,
    sphinx...), the compilation can take for ever.
    This is due to extra packages needed by latex.
    When the process is run from a command line, a
    windows shows up asking for approval before
    going on installing the missing latex packages.
    As this command line is showing up in the output,
    it is just needed to executed from a command line window
    to import the missing package.
    After this short break, the latex compilation
    runs fine on Jenkins.
