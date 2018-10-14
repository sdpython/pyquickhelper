"""
@file
@brief Regular expressions.
"""

_setup_pattern_copy_exts = ['ico', '7z', 'dll', 'so', 'yml', 'rst', 'ipynb', 'gif', 'jpg', 'jpeg', 'png', 'txt',
                            'zip', 'gz', 'html', 'exe', 'js', 'css', 'tex', 'data', 'csv', 'tpl']
_setup_pattern_copy = ".*[.]({0})$".format('|'.join('({0})'.format(_)
                                                    for _ in _setup_pattern_copy_exts))
