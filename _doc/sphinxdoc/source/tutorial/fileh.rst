
Helpers about files
===================

Many times we need functions not specifically related
to the project we are working on but needed on almost
every project. File manipulation such as downloading,
unzipping. It is usually needed to write the unit tests.
We call those functions
`helpers <http://scikit-learn.org/stable/developers/utilities.html#helper-functions>`_,
`utils <http://scikit-learn.org/stable/modules/classes.html#module-sklearn.utils>`_,
`utilities <http://scikit-learn.org/stable/developers/utilities.html>`_.
Here are some tools I had to implement for other tasks.

.. contents::
    :local:

Internet
++++++++

The following function downloads a file and unzip it.
The basic function is the following:

::

    import urllib.request

    url = "..."
    filename = "..."

    with urllib.request.urlopen(url) as u:
        data = u.read()
     
    with open([filename], "wb") as f :
        f.write(data)

When the file is big, it is quite worrying not to see
the screen showing any progress. We download the file
by pieces.

::

    import urllib.request

    url = "..."
    filename = "..."
    size = 0
      
    with open(filename, "wb") as f :
        with urllib.request.urlopen(url) as ur:
            while True:
                data = ur.read(chunk)
                size += len(data)
                print("downloaded", size, "bytes")
                if len(data) > 0:
                    f.write(data)
                else:
                    break

This code can be replaced by:

::

    from pyquickhelper.filehelper import get_url_content_timeout
    get_url_content_timeout(url, output="...", encoding=None, chunk=2**24, fLOG=print)

.. autosignature:: pyquickhelper.filehelper.download_helper.get_url_content_timeout

Zip / Unzip
+++++++++++

Standard libraries of :epkg:`Python` work well.

::

    import zipfile
    with zipfile.ZipFile("test.zip", "r") as zip_ref:
        zip_ref.extractall("path_to_download")

That's what does the following:

::

    from pyquickhelper.filehelper import unzip_files
    unzip_file('test.zip', 'path_to_download', fLOG=print)

.. autosignature:: pyquickhelper.filehelper.compression_helper.unzip_files
