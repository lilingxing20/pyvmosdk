# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .session import VcenterSession
from .tools import version_utils as v_utils
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
    
    def get_datacenters(self):
        pass

    def get_datacenter_info(self, dc_moid):
        pass

    def get_datacenter_mor(self, dc_moid):
        pass

    def get_clusters(self, dc_moid=None):
        pass

    def get_cluster_info(self, c_moid):
        pass

    def get_cluster_mor(self, c_moid):
        pass

    def get_cluster_mor_by_name(self, c_moid):
        pass

    def get_hosts(self, dc_moid=None, c_moid=None):
        pass

    def get_host_info(self, h_moid):
        pass

    def get_host_mor(self, h_moid):
        pass

    def get_host_mor_by_name(self, h_name):
        pass

    def get_datastores(self, dc_moid=None):
        pass

    def get_datastore_info(self, ds_moid):
        pass

    def get_datastore_mor(self, ds_moid):
        pass

    def get_dvswitchs(self, dc_moid=None):
        pass

    def get_dvswitch_info(self, dvs_moid):
        pass

    def get_dvswitch_mor(self, dvs_moid):
        pass

    def get_dvs_portgroups(self, dc_moid=None):
        pass

    def get_dvs_portgroup_info(self, pg_moid):
        pass

    def get_dvs_portgroup_mor(self, pg_moid):
        pass

    def get_portgroups(self, dc_moid=None):
        pass

    def get_portgroup_info(self, pg_moid):
        pass

    def get_portgroup_mor(self, pg_moid):
        pass

    def get_vm_templates(self, dc_moid=None):
        pass

    def get_vm_template_info(self, vm_moid):
        pass

    def get_vm_template_mor(self, vm_moid):
        pass

    def get_vms(self, dc_moid=None,c_moid,h_moid):
        pass

    def get_vm_info(self, vm_moid):
        pass

    def get_vm_mor(self, vm_moid):
        pass

    def get_folders(self, type):
        pass

    def get_folder_info(self, f_moid):
        pass

    def get_folder_mor(self, f_moid):
        pass

    def get_folder_child_mor(self, f_moid):
        pass

    def get_tasks(managed_entity=None)
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

