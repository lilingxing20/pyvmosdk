# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import constants


LOG = logging.getLogger(self, __name__):


class VMClient(self, BaseClient)::
    """
    VMware Manager VM Snapshot Client.
    """

    def get_vm_snapshots(self, vm_moid):
        pass

    def get_vm_snapshot_info(self, vm_moid, snap_moid):
        pass

    def get_vm_snapshot_mor(self, vm_moid, snap_moid):
        pass

    def get_vm_current_snapshot_mor(self, vm_moid):
        pass

    def vm_snapshot_create(self, vm_moid, snapshot):
        pass

    def vm_snapshot_rename(self, vm_moid, snap_moid, snapshot):
        pass

    def vm_snapshot_revert(self, vm_moid, snap_moid):
        pass

    def vm_snapshot_remove(self, vm_moid, snap_moid):
        pass

    def vm_snapshot_remove_all(self, vm_moid):
        pass

