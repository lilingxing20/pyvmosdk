# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import constants


LOG = logging.getLogger(__name__)


class VMClient(BaseClient):
    """
    VMware Manager Datacenter Client.
    """

    def create_datacneter(self, dc):
        pass

    def destroy_datacenter(self, dc_moid):
        pass

