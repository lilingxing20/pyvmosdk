# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import constants


LOG = logging.getLogger(__name__)


class HostClient(BaseClient):
    """
    VMware Manager ESXi Host Client.
    """
    def query_host_connection_info(self, dc_moid, auth_info):
        pass

    def host_added_to_cluster(self, auth_info, c_moid, f_moid=None):
        pass

    def host_added_to_datacenter(self, auth_info, dc_moid, f_moid=None):
        pass

    def host_move_into_cluster(self, h_moid, c_moid):
        pass

    def host_move_into_datacenter(self, h_moid, dc_moid):
        pass

    def host_maintenance_enter(self, h_moid):
        pass

    def host_maintenance_exit(self, h_moid):
        pass

    def host_disconnect(self, h_moid):
        pass

    def host_reconnect(self, h_moid):
        pass

    def host_destroy(self, h_moid):
        pass




