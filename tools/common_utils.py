# -*- coding:utf-8 -*-

from __future__ import absolute_import

import re
import six

from . import constants


def filter_vm_hostname(vm_name, hostname):
    """
    1. Host name only allowed to contain the ASCII character [0-9a-zA-Z-].
    Other are not allowed.
    2. The beginning and end character not allowed is the '-'.
    3. It is strongly recommended that do not use Numbers at the beginning,
    though it is not mandatory

    """
    if not hostname:
        hostname = vm_name
    if not re.match(r'^[a-zA-Z][a-zA-Z\d-]*[a-zA-Z\d]$', hostname):
        hostname = 'localhost'
    return hostname


def sanitize_hostname(vm_name, hostname, default_name='localhost'):
    """Return a hostname which conforms to RFC-952 and RFC-1123 specs except
       the length of hostname.

       Window, Linux, and Dnsmasq has different limitation:

       Windows: 255 (net_bios limits to 15, but window will truncate it)
       Linux: 64
       Dnsmasq: 63

       Due to nova-network will leverage dnsmasq to set hostname, so we chose
       63.

       """

    def truncate_hostname(name):
        # if len(name) > 63:
        #     logger.warning(_LW("Hostname %(hostname)s is longer than 63, "
        #                     "truncate it to %(truncated_name)s"),
        #                     {'hostname': name, 'truncated_name': name[:63]})
        return name[:63]

    if not hostname:
        hostname = vm_name
    if isinstance(hostname, six.text_type):
        # Remove characters outside the Unicode range U+0000-U+00FF
        hostname = hostname.encode('latin-1', 'ignore')
        if six.PY3:
            hostname = hostname.decode('latin-1')

    hostname = truncate_hostname(hostname)
    hostname = re.sub(r'[ _.]', '-', hostname)
    hostname = re.sub(r'[^\w.-]+', '', hostname)
    # hostname = hostname.upper()
    hostname = hostname.strip('.-')
    # NOTE(eliqiao): set hostname to default_display_name to avoid
    # empty hostname
    if hostname == "" and default_name is not None:
        return truncate_hostname(default_name)
    return hostname


def get_os_type(guest_id):
    if guest_id in constants.WIN_OS_TYPES:
        os_type = 'windows'
    elif guest_id in constants.LINUX_OS_TYPES:
        os_type = 'linux'
    else:
        os_type = 'other'
    return os_type


def get_vdev_node(disk_device_key):
    scsi_z1 = (disk_device_key - 2000) // 16
    scsi_z2 = (disk_device_key - 2000) % 16
    return "%d:%d" % (scsi_z1, scsi_z2)
        