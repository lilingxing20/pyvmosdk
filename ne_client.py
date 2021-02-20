# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import constants


LOG = logging.getLogger(__name__)


class NetworkClient(BaseClient):
    """
    VMware Manager Network Client.
    """

    def __init__(self, vc_info):
        super(NetworkClient, self).__init__(vc_info)

    def create_vswtich(self, host_moid, dvpg):
        pass

    def create_portgroup(self, vs_moid, dvpg):
        pass

    def create_dvswtich(self, dvs_moid, dvpg):
        pass

    def create_dvportgroup(self, dvs_moid, dvpg):
        pass

