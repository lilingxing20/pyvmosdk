# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .session import VcenterSession
from .tools import version_utils as v_utils
from .tools import vm
from .tools import constants


LOG = logging.getLogger(__name__)
# python3 default encoding: utf-8
# reload(sys)
# sys.setdefaultencoding('utf-8')


class BaseClient(VcenterSession):
    """
    VMware Base Client.
    """

    def __init__(self, vc_info):
        super(BaseClient, self).__init__(vc_info)
        self._check_min_version()

    def _check_min_version(self):
        min_version = v_utils.convert_version_to_int(constants.MIN_VC_VERSION)
        vc_version = self.get_vc_version()
        if v_utils.convert_version_to_int(vc_version) < min_version:
            raise Exception(('Detected vCenter version %(version)s. PYVMOSDk '
                             'requires VMware vCenter version %(min_version)s or greater.')
                            % {'version': vc_version,
                               'min_version': constants.MIN_VC_VERSION})

    def get_mors(self, vimfolder, vimtype):
        """
        Return managed object reference list.

        @param vimfolder: vim.Folder
        @param vimtype: 
        *  vim.ClusterComputeResource
        *  vim.Datacenter
        *  vim.Datastore
        *  vim.dvs.DistributedVirtualPortgroup
        *  vim.dvs.VmwareDistributedVirtualSwitch
        *  vim.Folder
        *  vim.HostSystem
        *  vim.Network
        *  vim.ResourcePool
        *  vim.StoragePod
        *  vim.VirtualApp
        *  vim.VirtualMachine
        """
        container = self.si.content.viewManager.CreateContainerView(
            vimfolder, vimtype, True)
        mors = container.view
        container.Destroy()
        return mors

    def get_mor_by_moid(self, vimtype, moid):
        """
        Return managed object reference.

        @param vimtype: 
        *  vim.ClusterComputeResource
        *  vim.Datacenter
        *  vim.Datastore
        *  vim.dvs.DistributedVirtualPortgroup
        *  vim.dvs.VmwareDistributedVirtualSwitch
        *  vim.Folder
        *  vim.HostSystem
        *  vim.Network
        *  vim.ResourcePool
        *  vim.StoragePod
        *  vim.VirtualApp
        *  vim.VirtualMachine

        @param moid: managed object id (str)
        """
        mors = self.get_mors(self.si.content.rootFolder, vimtype)
        mor = None
        if moid:
            for o in mors:
                if o._moId == moid:
                    mor = o
                    break
        return mor

    def get_mors_by_name(self, vimtype, name):
        """
        Return managed object reference.

        @param vimtype: 
        *  vim.ClusterComputeResource
        *  vim.Datacenter
        *  vim.Datastore
        *  vim.dvs.DistributedVirtualPortgroup
        *  vim.dvs.VmwareDistributedVirtualSwitch
        *  vim.Folder
        *  vim.HostSystem
        *  vim.Network
        *  vim.ResourcePool
        *  vim.StoragePod
        *  vim.VirtualApp
        *  vim.VirtualMachine

        @param name: managed object name (str)
        """
        mors = self.get_mors(self.si.content.rootFolder, vimtype)
        mor_list = []
        if name:
            mor_list = [mor for mor in mors if mor.name == name]
        return mor_list

    def get_datacenters(self):
        pass

    def get_datacenter_info(self, dc_moid):
        pass

    def get_datacenter_mor(self, dc_moid):
        return self.get_mor_by_moid([vim.Datacenter], dc_moid)

    def get_clusters(self, dc_moid=None):
        pass

    def get_cluster_info(self, c_moid):
        pass

    def get_cluster_mor(self, c_moid):
        return self.get_mor_by_moid([vim.ClusterComputeResource], c_moid)

    def get_cluster_mor_by_name(self, c_moid):
        pass

    def get_res_pool_mor(self, r_moid):
        return self.get_mor_by_moid([vim.ResourcePool], r_moid)

    def get_hosts(self, dc_moid=None, c_moid=None):
        pass

    def get_host_info(self, h_moid):
        pass

    def get_host_mor(self, h_moid):
        return self.get_mor_by_moid([vim.HostSystem], h_moid)

    def get_host_mor_by_name(self, h_name):
        pass

    def get_datastores(self, dc_moid=None):
        pass

    def get_datastore_info(self, ds_moid):
        pass

    def get_datastore_mor(self, ds_moid):
        return self.get_mor_by_moid([vim.Datastore], ds_moid)

    def get_dvswitchs(self, dc_moid=None):
        pass

    def get_dvswitch_info(self, dvs_moid):
        pass

    def get_dvswitch_mor(self, dvs_moid):
        return self.get_mor_by_moid([vim.dvs.VmwareDistributedVirtualSwitch], dvs_moid)

    def get_dvs_portgroups(self, dc_moid=None):
        pass

    def get_dvs_portgroup_info(self, pg_moid):
        pass

    def get_dvs_portgroup_mor(self, pg_moid):
        return self.get_mor_by_moid([vim.dvs.DistributedVirtualPortgroup], pg_moid)

    def get_portgroups(self, dc_moid=None):
        pass

    def get_portgroup_info(self, pg_moid):
        pass

    def get_portgroup_mor(self, pg_moid):
        return self.get_mor_by_moid([vim.Network], pg_moid)

    def get_vm_templates(self, dc_moid=None):
        pass

    def get_vm_template_info(self, vm_moid):
        pass

    def get_vm_template_mor(self, vm_moid):
        return self.get_mor_by_moid([vim.VirtualMachine], vm_moid)

    def get_vms(self, dc_moid, c_moid, h_moid):
        pass

    def get_vm_info(self, vm_moid):
        vm_mor = self.get_vm_mor(vm_moid)
        return vm.vm_info_json(vm_mor)

    def get_vm_guest_info(self, vm_moid):
        vm_mor = self.get_vm_mor(vm_moid)
        return vm.vm_guest_info_json(vm_mor)

    def get_vm_guest_net_info(self, vm_moid):
        vm_mor = self.get_vm_mor(vm_moid)
        return vm.vm_guest_net_info_json(vm_mor)

    def get_vm_mor(self, vm_moid):
        return self.get_mor_by_moid([vim.VirtualMachine], vm_moid)

    def get_folders(self, type):
        pass

    def get_folder_info(self, f_moid):
        pass

    def get_folder_mor(self, f_moid):
        return self.get_mor_by_moid([vim.Folder], f_moid)

    def get_folder_child_mor(self, f_moid):
        pass

    def get_dc_vm_folder_mor(self, dc_moid, folder_moid=None):
        """
        Get datacenter vm root folder.
        """
        dc_mor = self.get_datacenter_mor(dc_moid)
        if not dc_mor:
            raise Exception("Not found datacenter: %s" % dc_moid)
        return dc_mor.vmFolder

    def get_dc_host_folder_mor(self, dc_moid, folder_moid=None):
        """
        Get datacenter host root folder.
        """
        pass

    def get_dc_network_folder_mor(self, dc_moid, folder_moid=None):
        """
        Get datacenter network root folder.
        """
        pass

    def get_dc_datastore_folder_mor(self, dc_moid, folder_moid=None):
        """
        Get datacenter datastore root folder.
        """
        pass

    def get_tasks(self, managed_entity):
        pass

    def get_recent_tasks(self, moid=None):
        pass

    def get_task_info(self, task_key, moid=None):
        pass

    def get_task_mor(self, task_key, moid=None):
        pass

    def get_task_result_mor(self, task_key, moid=None):
        pass

    def get_task_entity_mor(self, task_key, moid=None):
        pass

    def cancel_task(self, task_key, moid=None):
        pass

    def get_events(self, moid=None):
        pass
