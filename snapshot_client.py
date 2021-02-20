# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import snapshot_utils as s_utils
from .tools.result_utils import DataResult


LOG = logging.getLogger(__name__)


class VMSnapshotClient(BaseClient):
    """
    VMware Manager VM Snapshot Client.
    """

    def _get_vm_snapshot_mor(self, vm_moid, snap_moid):
        """
        Get a snapshot moref of the VM.
        """
        snap_mor = None
        try:
            vm_mor = self.get_vm_mor(vm_moid)
            snap_mor = s_utils.get_vm_snapshot_mor_by_moid(vm_mor, snap_moid)
        except Exception as ex:
            LOG.exception(ex)
            raise Exception("Get snapshot mor of the VM error: %s" % str(ex))
        return snap_mor

    def _get_vm_current_snapshot_mor(self, vm_moid):
        """
        Get current snapshot of the VM.
        """
        snap_mor = None
        try:
            vm_mor = self.get_vm_mor(vm_moid)
            snap_moid = vm_mor.snapshot.currentSnapshot._moId
            snap_mor = s_utils.get_vm_snapshot_mor_by_moid(vm_mor, snap_moid)
        except Exception as ex:
            LOG.exception(ex)
            raise Exception(
                "Get current snapshot mor of the VM error: %s" % str(ex))
        return snap_mor

    def get_vm_snapshot_info(self, vm_moid, snap_moid):
        """
        Get a snapshot info of the VM.
        """
        result = DataResult()
        try:
            snap_mor = self._get_vm_snapshot_mor(vm_moid, snap_moid)
            snap_info = s_utils.snaptree_obj_to_json(snap_mor)
            result.data = {"snap_info": snap_info}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Get a snapshot info of the vm error: %s" % str(
                ex)
        return result

    def get_vm_current_snapshot_info(self, vm_moid):
        """
        Get current snapshot for virtual machine
        """
        result = DataResult()
        try:
            snap_mor = self._get_vm_current_snapshot_mor(vm_moid)
            snap_info = s_utils.snaptree_obj_to_json(snap_mor)
            result.data = {"snap_info": snap_info}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Get current snapshot info of the vm error: %s" % str(
                ex)
        return result

    def get_vm_snapshots_info(self, vm_moid):
        """
        Get all snapshots info of the VM.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)
            snap_info = s_utils.get_vm_all_snapshot_info(vm_mor)
            result.data = {"snap_info": snap_info}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Get all snapshots of the vm error: %s" % str(ex)
        return result

    def vm_snapshot_create(self, vm_moid, snapshot):
        """
        Create snapshot of the VM.

        @param snapshot: {"name": "snap01", "description": "snap 01",
                          "memory": False, "quiesce": False}
        name (str):
            The name for this snapshot. The name need not be unique for
            this virtual machine.
        description (str, optional):
            A description for this snapshot. If omitted, a default description
            may be provided.
        memory (bool):
            If TRUE, a dump of the internal state of the virtual machine
            (basically a memory dump) is included in the snapshot.
            Memory snapshots consume time and resources, and thus take longer
            to create. When set to FALSE, the power state of the snapshot is
            set to powered off.
        quiesce (bool):
            If TRUE and the virtual machine is powered on when the snapshot is
            taken, VMware Tools is used to quiesce the file system in the
            virtual machine. This assures that a disk snapshot represents a
            consistent state of the guest file systems. If the virtual machine
            is powered off or VMware Tools are not available, the quiesce flag
            is ignored.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)
            task_mor = vm_mor.CreateSnapshot(snapshot["name"],
                                             snapshot["description"],
                                             snapshot["memory"],
                                             snapshot["quiesce"])
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Create snapshot error: %s" % str(ex)
        return result

    def vm_snapshot_rename(self, vm_moid, snap_moid, snapshot):
        """
        Rename snapshot of the VM.

        @param snapshot: {"name": "snap01", "description": "snap 01"}
        """
        result = DataResult()
        try:
            snap_mor = self._get_vm_snapshot_mor(vm_moid, snap_moid)
            snap_mor.RenameSnapshot(snapshot.get('name'),
                                    snapshot.get('description'))
            snap_info = s_utils.snaptree_obj_to_json(snap_mor)
            result.data = {"snap_info": snap_info}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Rename snapshot error: %s" % str(ex)
        return result

    def vm_snapshot_revert(self, vm_moid, snap_moid):
        """
        Revert snapshot of the VM.
        """
        result = DataResult()
        try:
            snap_mor = self._get_vm_snapshot_mor(vm_moid, snap_moid)
            task_mor = snap_mor.RevertToSnapshot_Task()
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Revert snapshot of the vm error: %s" % str(ex)
        return result

    def vm_current_snapshot_revert(self, vm_moid):
        """
        Revert current snapshot of the VM.
        """
        result = DataResult()
        try:
            snap_mor = self._get_vm_current_snapshot_mor(vm_moid)
            task_mor = snap_mor.RevertToSnapshot_Task()
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Revert current snapshot of the vm error: %s" % str(
                ex)
        return result

    def vm_snapshot_remove(self, vm_moid, snap_moid):
        """
        Remove a snapshot of the VM.
        """
        result = DataResult()
        try:
            snap_mor = self._get_vm_snapshot_mor(vm_moid, snap_moid)
            task_mor = snap_mor.RemoveSnapshot_Task(True)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Remove a snapshots for vm error: %s " % str(ex)
        return result

    def vm_snapshot_remove_all(self, vm_moid):
        """
        Remove all snapshots of the VM.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)
            task_mor = vm_mor.RemoveAllSnapshots()
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Remove all snapshots for vm error: %s " % str(ex)
        return result
