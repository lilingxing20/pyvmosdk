# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import constants


LOG = logging.getLogger(__name__)


class TemplateClient(BaseClient):
    """
    VMware Manager VM Template Client.
    """

    def __init__(self, vc_info):
        super(TemplateClient, self).__init__(vc_info)

    def import_ova_template(self):
        pass

    def import_ovf_template(self):
        pass

    def export_ova_template(self):
        pass

    def export_ovf_template(self):
        pass

    def mark_as_vm(self, template_moid):
        pass
