
.. blogpost::
    :title: Upload a single binary on PyPI
    :keywords: PyPI, upload
    :date: 2018-05-21
    :categories: build

    The packages for multiple distribution are built
    on different machine but the upload takes place on
    a single machine. I retrieved all available builds
    and moved them to the *dist* folder.
    The file ``.pypirc`` was saved into my home with
    the following content:

    ::

        [distutils]
        index-servers =
          pypi

        [pypi]
        repository=https://upload.pypi.org/legacy/
        username=sloaned
        password=********

    I then ran the following command line (and for another package):

    ::

        twine upload -r pypi dist\csharpy-0.1.53-cp36-cp36m-linux_x86_64.whl

    However this cannot be uploaded to :epkg:`PyPI` as it only accepts
    binaries built for manylinux and this can only be done with a
    `Centos <https://www.centos.org/>`_ distribution
    (see `manylinux <https://github.com/pypa/manylinux>`_).
    I gave up and switched to the description of the
    package installation on linux.
