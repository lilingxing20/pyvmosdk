# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import constants
from .tools.result_utils import DataResult


LOG = logging.getLogger(__name__)


class DatacenterClient(BaseClient):
    """
    VMware Manager Datacenter Client.
    """

    def __init__(self, vc_info):
        super(DatacenterClient, self).__init__(vc_info)

    def create_datacneter(self, dc_name, folder_moid=None):
        """
        Creates a new datacenter with the given name.
        Any % (percent) character used in this name parameter must be escaped,
        unless it is used to start an escape sequence. Clients may also escape
        any other characters in this name parameter.

        An entity name must be a non-empty string of
        less than 80 characters. The slash (/), backslash (\) and percent (%)
        will be escaped using the URL syntax. For example, %2F

        This can raise the following exceptions:
        vim.fault.DuplicateName
        vim.fault.InvalidName
        vmodl.fault.NotSupported
        vmodl.fault.RuntimeFault
        ValueError raised if the name len is > 79

        Required Privileges
        Datacenter.Create
        @param dc_name: Name for the new datacenter.
        @param folder_moid: Folder object to create DC in. If None it will
            default to rootFolder
        """
        result = DataResult()
        try:
            if len(dc_name) > 79:
                raise ValueError("The name of the datacenter must be under "
                                "80 characters.")
            folder_mor = self.get_folder_mor(folder_moid)
            if folder_mor is None:
                folder_mor = self.si.content.rootFolder

            dc_mor = folder_mor.CreateDatacenter(name=dc_name)
            result.data = {"name": dc_name, "moid": dc_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Create datacenter error: %s" % str(ex)
        return result

    def rename_datacenter(self, dc_moid, dc_name):
        """
        Rename Datacenter.
        """
        result = DataResult()
        try:
            if len(dc_name) > 79:
                raise ValueError("The name of the datacenter must be under "
                                "80 characters.")
            dc_mor = self.get_datacenter_mor(dc_moid)
            task_mor = dc_mor.CreateDatacenter(dc_name)
            result.task_key = task_mor._moId
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Rename datacenter error: %s" % str(ex)
        return result

    def destroy_datacenter(self, dc_moid):
        """
        Destroy Datacenter.
        """
        result = DataResult()
        try:
            dc_mor = self.get_folder_mor(dc_moid)
            task_mor = dc_mor.Destroy()
            result.task_key = task_mor._moId
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Destroy datacenter error: %s" % str(ex)
        return result

