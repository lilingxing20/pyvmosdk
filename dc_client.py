# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import constants


LOG = logging.getLogger(__name__)


class DatacenterClient(BaseClient):
    """
    VMware Manager Datacenter Client.
    """

    def __init__(self, vc_info):
        super(DatacenterClient, self).__init__(vc_info)

    def create_datacneter(self, dc):
        pass

    def destroy_datacenter(self, dc_moid):
        pass

