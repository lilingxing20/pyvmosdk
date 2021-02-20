# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import constants
from .tools.result_utils import DataResult


LOG = logging.getLogger(__name__)


class VMClient(BaseClient):
    """
    VMware Manager Folder Client.
    """

    def create_folder(self, folder, folder_type='vm'):
        """
        Create folder managed object.

        @param folder: {
            "name": "f01",
            "parent_folder_moid": "group-v1|group-h1|group-s1|group-n1"
            "dc_moid": "datacenter-1"
        }
        @param folder_type: "vm|host|network|datastore"
        """
        result = DataResult()
        try:
            parent_f_mor = None
            if folder.get('parent_folder_moid'):
                # get parent folder mor
                parent_f_mor = self.get_folder_mor(
                    folder['parent_folder_moid'])
            else:
                # get datacenter root folder
                dc_mor = self.get_datacenter_mor(folder['dc_moid'])
                if folder_type = 'vm':
                    parent_f_mor = dc_mor.vmFolder
                elif folder_type = 'host':
                    parent_f_mor = dc_mor.hostFolder
                elif folder_type = 'network':
                    parent_f_mor = dc_mor.networkFolder
                elif folder_type = 'datastore':
                    parent_f_mor = dc_mor.datastoreFolder
                else:
                    raise Exception("The folder type error: %s" % folder_type)
            try:
                new_f_mor = parent_f_mor.CreateFolder(folder['name'])
            except vim.fault.DuplicateName as ex:
                for mor in parent_f_mor.childEntity:
                    if mor.name == new_folder_name:
                        new_f_mor = mor
                        break
            new_f_info = {'name': new_f_mor.name, 'moid': new_f_mor._moId}
            result.data = {"folder_info": new_f_info}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Create vm folder error: %s" % str(ex)
        return result

    def create_vm_folder(self, folder, dc_moid):
        """
        Create vm/template view folder managed object.
        """
        return self.create_folder(folder, folder_type='vm')

    def create_host_folder(self, folder, dc_moid):
        """
        Create host view folder managed object.
        """
        return self.create_folder(folder, folder_type='host')

    def create_network_folder(self, folder, dc_moid):
        """
        Create network view folder managed object.
        """
        return self.create_folder(folder, folder_type='network')

    def create_datastore_folder(self, folder, dc_moid):
        """
        Create datastore view folder managed object.
        """
        return self.create_folder(folder, folder_type='datastore')

    def delete_folder(self, folder_moid):
        """ Delete vm/template view folder managed object.
        """
        # get folder mor
        folder_mor = utils.get_folder_mor(self.si, moid=folder_moid)
        task_mor = folder_mor.Destroy()
        task_state = task.WaitForTask(task_mor)
        return task_state
