
REST API, local file store
==========================

Benchmarking usually happens on a different job when running
CI jobs and cannot be included in the documentation unless
they are stored somewhere. A REST API is better than
a local file because it can be distance and do not rely
on local path. These functions are a simple implementation
of an API to store and retrieve dataframes with :epkg:`FastAPI`.

.. contents::
    :local:

REST API
++++++++

.. autosignature:: pyquickhelper.server.filestore_fastapi.fast_api_submit

.. autosignature:: pyquickhelper.server.filestore_fastapi.fast_api_query

.. autosignature:: pyquickhelper.server.filestore_fastapi.fast_api_content

.. autosignature:: pyquickhelper.server.filestore_fastapi.create_app

File Storage
++++++++++++

.. autosignature:: pyquickhelper.server.filestore_sqlapi.SqlLite3FileStore
