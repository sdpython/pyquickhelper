
.. blogpost::
    :title: Debug, traceback
    :keywords: traceback
    :date: 2020-08-11
    :categories: debug

    A trick I use sometimes to print the traceback without
    stopping the program.

    .. runpython::
        :showcode:

        import traceback

        try:
            assert False
        except AssertionError:
            tb = traceback.extract_stack()
            print()
            for line in tb:
                if ("tf2onnx" in line.filename and "site-packages" not in line.filename and
                        'python3' not in line.filename):
                    print('  File "{}", line {}'.format(line.filename, line.lineno))
