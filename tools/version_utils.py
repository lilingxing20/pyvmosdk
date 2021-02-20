# -*- coding:utf-8 -*-

"""
Helpers for comparing version strings.

.. versionadded:: 1.6
"""

from __future__ import absolute_import

import six


def convert_version_to_int(version):
    """Convert a version to an integer.

    *version* must be a string with dots or a tuple of integers.

    .. versionadded:: 2.0
    """
    try:
        if isinstance(version, six.string_types):
            version = convert_version_to_tuple(version)
        if isinstance(version, tuple):
            return six.moves.reduce(lambda x, y: (x * 1000) + y, version)
    except Exception as ex: 
        msg = "Version %s is invalid." % version
        six.raise_from(ValueError(msg), ex) 


def convert_version_to_str(version_int):
    """Convert a version integer to a string with dots.

    .. versionadded:: 2.0
    """
    version_numbers = []
    factor = 1000
    while version_int != 0:
        version_number = version_int - (version_int // factor * factor)
        version_numbers.insert(0, six.text_type(version_number))
        version_int = version_int // factor

    return '.'.join(map(str, version_numbers))


def convert_version_to_tuple(version_str):
    """Convert a version string with dots to a tuple.

    .. versionadded:: 2.0
    """
    return tuple(int(part) for part in version_str.split('.'))