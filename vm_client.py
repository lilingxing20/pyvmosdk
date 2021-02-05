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
    VMware Manager VM Client.
    """

    def create_vm(self, vm):
        pass

    def clone_vm(self, vm):
        pass

    def poweron_vm(self, vm_moid):
        pass

    def poweroff_vm(self, vm_moid):
        pass

    def reset_vm(self, vm_moid):
        pass

    def suspend_vm(self, vm_moid):
        pass

    def shutdown_guest(self, vm_moid):
        pass

    def reboot_guest(self, vm_moid):
        pass

    def destroy_vm(self, vm_moid):
        pass

    def remove_vm(self, vm_moid):
        pass

    def resize_cpu(self, vm_moid, cpu):
        pass

    def resize_memory(self, vm_moid, mem):
        pass

    def resize_vmdk_disks(self, vm_moid, disks):
        pass

    def attach_vmdk_disks(self, vm_moid, disks):
        pass

    def dettach_vmdk_disks(self, vm_moid, disks):
        pass

    def attach_rdm_disks(self, vm_moid, disks):
        pass

    def dettach_rdm_disks(self, vm_moid, disks):
        pass

    def add_nics(self, vm_moid, nics):
        pass

    def edit_nics(self, vm_moid, nics):
        pass

    def del_nics(self, vm_moid, nics):
        pass

    def clone_template(self, vm_moid, template):
        pass

    def mark_as_template(self, vm_moid):
        pass

    def vm_upgrade_tools(self, vm_moid):
        pass

    def vm_install_tools(self, vm_moid):
        pass

