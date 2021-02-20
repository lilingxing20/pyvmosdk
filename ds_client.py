# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import constants


LOG = logging.getLogger(__name__)


class DatastoreClient(BaseClient):
    """
    VMware Manager Datastore Client.
    """

    def __init__(self, vc_info):
        super(DatastoreClient, self).__init__(vc_info)

    def create_vmfs_datastore(self, dc):
        pass

    def destroy_datastore(self, ds_name):
        pass

