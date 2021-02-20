# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from .base_client import BaseClient
from .tools import constants
from .tools import vm_utils
from .tools import checker
from .tools.result_utils import DataResult


LOG = logging.getLogger(__name__)


class VMClient(BaseClient):
    """
    VMware Manager VM Client.
    """

    def __init__(self, vc_info):
        super(VMClient, self).__init__(vc_info)
        self.checker = checker.VmChecker(self.si)

    def create_vm(self, vm_cfg, location, nics, disks, cdroms):
        """
        Create VirtualMachine.

        @param vm_cfg: {"name": "vm01", "guest_id": "rhel7_64Guest",
                        "num_cpu": 4, "num_core": 2, "memoryMB": 2048}

        @param location: {"dc_moid": "datacenter-2", "cluster_moid": "domain-c14",
                   "folder_moid": "group-v4263", "ds_name": "datastore01",
                   "rp_moid": "resgroup-15"}
        可选参数rp_moid, folder_moid

        @param nics: [{"pg_moid": "network-11"}]

        @param disks: [{"ds_name": "datastore02", "vdev_node": "0:0",
                    "disk_type": "thin", "disk_size": 10}
                ]
        vdev_node: 0:0-0:6,0:8-0:15, 1:0-1:6,1:8-1:15,
                   2:0-2:6,2:8-2:15, 3:0-3:6,3:8-3:15
        disk_type: thin,eagerZeroedThick,preallocated

        @param cdroms = [{"vdev_node": "0:0",
                    "iso_file": "[datastore1] CentOS-7-x86_64-Minimal-1810.iso"}
                ]
        vdev_node: 0:0, 0:1, 1:0, 1:1
        """
        result = DataResult()
        try:
            # get dest folder
            vmfolder_mor = self.get_folder_mor(location.get('folder_moid'))
            if not vmfolder_mor:
                vmfolder_mor = self.get_dc_vm_folder_mor(location['dc_moid'])
            if location.get('rp_moid'):
                # get resource pool managed object reference
                res_pool_mor = self.get_res_pool_mor(location['rp_moid'])
            else:
                # get cluster managed object reference
                cluster_mor = self.get_cluster_mor(location['cluster_moid'])
                res_pool_mor = cluster_mor.resourcePool

            # vm config spec
            config_spec = vim.vm.ConfigSpec()
            config_spec.name = vm_cfg['name']
            config_spec.memoryMB = vm_cfg['memoryMB']
            config_spec.numCPUs = vm_cfg['num_cpu']
            config_spec.numCoresPerSocket = vm_cfg['num_core']
            config_spec.files = vm_utils.make_fileinfo(
                location['ds_name'], vm_cfg['name'])
            config_spec.guestId = vm_cfg['guest_id']
            # config_spec.version = 'vmx-07'

            # virtual device: nic
            for nic in nics:
                pg_mor = self.get_portgroup_mor(nic["pg_moid"])
                nic_spec = vm_utils.make_add_nic_device_spec(
                    pg_mor, nic.get("adapter_type", "VMXNET3"))
                config_spec.deviceChange.append(nic_spec)

            # virtual device: disk
            scsi_controllers = []
            for disk in disks:
                controller_spec = vm_utils.check_and_make_scsi_controller_spec(
                    scsi_controllers, disk)
                if controller_spec:
                    scsi_controllers.append(controller_spec.device)
                    config_spec.append(controller_spec)
                disk_spec = vm_utils.make_attach_scsi_disk_device_spec(
                    disk, scsi_controllers)
                config_spec.deviceChange.append(disk_spec)

            # virtual device: cdrom
            for cdrom in cdroms:
                cdrom_spec = vm_utils.make_add_cdrom_device_spec(cdrom)
                config_spec.deviceChange.append(cdrom_spec)

            task_mor = vmfolder_mor.CreateVM_Task(config=config_spec,
                                                  pool=res_pool_mor)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Create VM error: %s" % str(ex)
        return result

    def clone_vm(self, template_moid, vm_cfg, location, nics, disks, poweron=False, template=False):
        """
        Clone a VM from a template/VM.

        @parma template_moid: vm-10
        @param vm_cfg: {"name": "vm01", "num_cpu": 4, "num_core": 2, "memoryMB": 2048
                        "hostname": "vm01", "domain": "test.local", "uuid": "xxx",
                        "dns_list":[]}

        @param location: {"dc_moid": "datacenter-2", "cluster_moid": "domain-c14",
                        "host_moid": "host-1", "rp_moid": "resgroup-15",
                        "folder_moid": "group-v4263", "ds_name": "datastore01"}
        可选参数rp_moid, folder_moid

        @param nics: [{'ip': '10.0.0.13', 'netmask': '255.255.255.0', 'gateway': '10.0.0.1',
                    'pg_moid': 'dvportgroup-391', 'adapter_type': 'E1000'}]

        @param disks: [{"ds_name": "datastore02", "vdev_node": "0:0",
                    "disk_type": "thin", "disk_size": 10}
                ]
        vdev_node: 0:0-0:6,0:8-0:15, 1:0-1:6,1:8-1:15,
                   2:0-2:6,2:8-2:15, 3:0-3:6,3:8-3:15
        disk_type: thin,eagerZeroedThick,preallocated
        """
        result = DataResult()
        try:
            # get vm template managed object reference
            template_mor = self.get_vm_mor(template_moid)

            # get dest folder
            vmfolder_mor = self.get_folder_mor(location.get('folder_moid'))
            if not vmfolder_mor:
                vmfolder_mor = self.get_dc_vm_folder_mor(location['dc_moid'])

            if location.get('rp_moid'):
                # get resource pool managed object reference
                res_pool_mor = self.get_res_pool_mor(location['rp_moid'])
            else:
                # get cluster managed object reference
                cluster_mor = self.get_cluster_mor(location['cluster_moid'])
                res_pool_mor = cluster_mor.resourcePool

            # get host managed object reference
            host_mor = self.get_host_mor(location.get('host_moid'))

            # get vm dest datastore managed object reference
            datastore_mor = self.get_datastore_mor(location['ds_moid'])

            # Extended network pg_mor attribute
            for nic in nics:
                nic['pg_mor'] = self.get_portgroup_mor(nic['pg_moid')

            # make clone spec
            clone_spec = vim.vm.CloneSpec()
            clone_spec.powerOn = vm_cfg.get('poweron', False)
            clone_spec.template = vm_cfg.get('template', False)

            # config spec
            clone_spec.config = make_clone_config_spec(template_mor, vm_cfg, nics, disks)
            # relocate spec
            clone_spec.location = vm_utils.make_clone_relocate_spec(clone_spec, res_pool_mor, esxi_mor, datastore_mor)
            # customization spec
            clone_spec.customization = vm_utils.make_custom_spec(vm_cfg, nics, dnslist)

            try:
                task_mor = template_mor.Clone(name=vm_name,
                                            folder=vmfolder_mor,
                                            spec=clone_spec)
            except vmodl.MethodFault as ex:
                LOG.exception(ex)
                raise Exception("Clone vm error: %s" % str(ex))
            vm_info= {"name": vm_cfg['name'],
                        "uuid": vm_cfg['uuid'],
                        "num_cpu": vm_cfg['num_cpu'],
                        "num_core": vm_cfg['num_core'],
                        "memoryMB": vm_cfg['memoryMB']
                        }
            result.data = {"task_key": task_mor._moId, 'vm_info': vm_info}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Clone VM error: %s" % str(ex)
        return result

    def clone_template(self, template_moid, vm_cfg, location, nics, disks, poweron=False):
        return self.clone_vm(template_moid, vm_cfg, location, nics, disks, poweron=poweron, template=True)

    def poweron_vm(self, vm):
        """
        PowerOn VM.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm.get('moid'))
            if not vm_mor:
                result.status = False
                result.message = "Not found VM: %s" % vm
            else:
                task_mor = vm_mor.PowerOn()
                result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "PowerOn VM error: %s" % str(ex)
        return result

    def poweroff_vm(self, vm):
        """
        PowerOff VM.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm.get('moid'))
            if not vm_mor:
                result.status = False
                result.message = "Not found VM: %s" % vm
            else:
                task_mor = vm_mor.PowerOff()
                result.me = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "PowerOff VM error: %s" % str(ex)
        return result

    def reset_vm(self, vm):
        """
        Reset VM.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm.get('moid'))
            if not vm_mor:
                result.status = False
                result.message = "Not found VM: %s" % vm
            else:
                task_mor = vm_mor.ResetVM_Task()
                result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Reset VM error: %s" % str(ex)
        return result

    def suspend_vm(self, vm):
        """
        Suspend VM.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm.get('moid'))
            if not vm_mor:
                result.status = False
                result.message = "Not found VM: %s" % vm
            else:
                task_mor = vm_mor.SuspendVM_Task()
                result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Reset VM error: %s" % str(ex)
        return result

    def shutdown_vm(self, vm):
        """
        Shutdown VM Guest.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm.get('moid'))
            if not vm_mor:
                result.status = False
                result.message = "Not found VM: %s" % vm
            else:
                if vm_mor.guest.guestOperationsReady:
                    vm_mor.ShutdownGuest()
                else:
                    result.status = False
                    result.message = "This operation is not supported in the current state."
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Shutdown VM Guest error: %s" % str(ex)
        return result

    def reboot_vm(self, vm):
        """
        Reboot VM Guest.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm.get('moid'))
            if not vm_mor:
                result.status = False
                result.message = "Not found VM: %s" % vm
            else:
                if vm_mor.guest.guestOperationsReady:
                    vm_mor.RebootGuest()
                else:
                    result.status = False
                    result.message = "This operation is not supported in the current state."
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Shutdown VM Guest error: %s" % str(ex)
        return result

    def destroy_vm(self, vm):
        """
        Reboot VM.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm.get('moid'))
            if not vm_mor:
                result.status = False
                result.message = "Not found VM: %s" % vm
            else:
                task_mor = vm_mor.Destroy_Task()
                result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Shutdown VM error: %s" % str(ex)
        return result

    def unregister_vm(self, vm):
        """
        Removes this virtual machine from the inventory without removing any of the virtual machine's files on disk.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm.get('moid'))
            if not vm_mor:
                result.status = False
                result.message = "Not found VM: %s" % vm
            else:
                vm_mor.UnregisterVM()
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "unregister VM error: %s" % str(ex)
        return result

    def precheck_resize_cpu_mem(self, vm_moid):
        """
        Check whether the vm supports hot tuning memory and CPU.
        """
        result = {'memory_hot_add_enabled': False,
                  'cpu_hot_add_enabled': False}
        try:
            vm_mor = self.get_vm_mor(vm_moid)
            result['memory_hot_add_enabled'] = vm_mor.config.memoryHotAddEnabled
            result['cpu_hot_add_enabled'] = vm_mor.config.cpuHotAddEnabled
            # result['cpu_hotremove_enabled'] = vm_mor.config.cpuHotRemoveEnabled
            result['hot_plug_memory_limit'] = vm_mor.config.hotPlugMemoryLimit
            result['hot_plug_memory_increment_size'] = vm_mor.config.hotPlugMemoryIncrementSize
        except Exception as ex:
            LOG.exception(ex)
            raise Exception("Precheck resize vm cpu memery error!")
        return result

    def resize_cpu(self, vm_moid, cpu_num):
        """
        Resize VM CPU num.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)

            config_spec = vim.vm.ConfigSpec()
            config_spec.numCPUs = int(cpu_num)
            task_mor = vm_mor.ReconfigVM_Task(spec=config_spec)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Resize vm cpu error: %s" % str(ex)
        return result

    def resize_memory(self, vm_moid, memoryMB):
        """
        Resize VM memory size(MB).
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)

            config_spec = vim.vm.ConfigSpec()
            config_spec.memoryMB = memoryMB
            task_mor = vm_mor.ReconfigVM_Task(spec=config_spec)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Resize vm memory error: %s" % str(ex)
        return result

    def resize_vmdk_disks(self, vm_moid, disks):
        """
        Resize vm disk.
        @param disks: [{'dev_key': 2000, 'disk_size': 32}]
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)

            config_spec = vim.vm.ConfigSpec()
            for disk in disks:
                disk_spec = vm_utils.make_resize_disk_device_spec(vm_mor, disk["dev_key"], disk["disk_size"])
                config_spec.deviceChange.append(disk_spec)

            task_mor = vm_mor.ReconfigVM_Task(spec=config_spec)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Resize vmdk disk error: %s" % str(ex)
        return result

    def attach_scsi_disks(self, vm_moid, disks, share_disk=False):
        """
        Attach scsi disk.
        @param disks:
        [
            {'is_raw': True,
            'ds_name': 'R5-4A-HHBI-AP56-E162-T1-02-7',
            'device_name': '/vmfs/devices/disks/naa.60050764008181c850000000000008cc',
            'vdev_node': '3:0',
            'compatibility_mode': 'virtualMode',
            'disk_mode': 'persistent',
            },
            {'ds_name': 'R5-4A-HHBI-AP56-E162-T1-02-7',
            'disk_type': 'thin',
            'disk_size': 1,
            'vdev_node': '3:2',
            'disk_mode': 'persistent',
            },
        ]
        disk_mode:
            independent_persistent / persistent / independent_nonpersistent
        compatibility_mode:
            virtualMode / physicalMode
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)

            # get vm scsi controllers
            scsi_controllers = vm_utils._get_vm_scsi_controller_devices(vm_mor)
            disk_enable_uuid = False
            config_spec = vim.vm.ConfigSpec()
            for disk in disks:
                controller_spec = vm_utils.check_and_make_scsi_controller_spec(scsi_controllers, disk, share_disk)
                if controller_spec:
                    scsi_controllers.append(controller_spec.device)
                    config_spec.append(controller_spec)
                disk_spec = vm_utils.make_attach_scsi_disk_device_spec(disk, scsi_controllers, share_disk)
                config_spec.deviceChange.append(disk_spec)
                if share_disk and not disk.get("is_raw"):
                    disk_enable_uuid = True
            if disk_enable_uuid:
                extra_cfg = vm_utils.make_disk_enable_uuid_extra_config()
                config_spec.deviceChange.append(extra_cfg)
            task_mor = vm_mor.ReconfigVM_Task(spec=config_spec)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Attach scsi disks error: %s" % str(ex)
        return result

    def detach_scsi_disks(self, vm_moid, disks):
        """
        Detach scsi disk.
        @param disks: [2000, 2001]
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)

            config_spec = vim.vm.ConfigSpec()
            disk_devs = vm_utils._get_vm_disk_devices(vm_mor)
            scsi_controller_devs = vm_utils._get_vm_scsi_controller_devices(vm_mor)
            controller_dev_dict = {}
            for dev in disk_devs:
                if dev.key in disks:
                    device_spec = vm_utils.make_remove_device_spec(dev, file_operation="destroy")
                    config_spec.deviceChange.append(device_spec)

                    c_unit_number = dev.controllerKey - 1000
                    # 记录从此控制器上移除的磁盘设备数
                    if controller_dev_dict.get(c_unit_number):
                        controller_dev_dict[c_unit_number] += 1
                    else:
                        controller_dev_dict[c_unit_number] = 1
                    # 当此控制器上现有的磁盘设备数等于移除的磁盘设备数时，移除此scsi控制器
                    for dev in scsi_controller_devs:
                        if dev.busNumber == c_unit_number:
                            if len(dev.device) == controller_dev_dict.get(c_unit_number):
                                device_spec = vm_utils.make_remove_device_spec(dev)
                                config_spec.deviceChange.append(device_spec)
                            break

            task_mor = vm_mor.ReconfigVM_Task(spec=config_spec)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Detach scsi disks error: %s" % str(ex)
        return result

    def attach_ide_disks(self, vm_moid, disks):
        pass

    def dettach_ide_disks(self, vm_moid, disks):
        pass

    def attach_sata_disks(self, vm_moid, disks):
        pass

    def dettach_sata_disks(self, vm_moid, disks):
        pass

    def add_nics(self, vm_moid, nics):
        """
        Add network adapters.
        @param vm_moid: 'vm-18'
        @param nics: [{"pg_moid": "", "adapter_type": 'E1000'}]
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)

            config_spec = vim.vm.ConfigSpec()
            for nic in nics:
                pg_mor = self.get_portgroup_mor(nic["pg_moid"])
                nic_spec = vm_utils.make_add_nic_device_spec(
                    pg_mor, nic.get("adapter_type", "VMXNET3"))
                config_spec.deviceChange.append(nic_spec)

            task_mor = vm_mor.ReconfigVM_Task(spec=config_spec)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Add nics error: %s" % str(ex)
        return result

    def edit_nics(self, vm_moid, nics):
        """
        Edit network adapters.
        @param vm_moid: 'vm-18'
        @param nics: [{"pg_moid": "", "dev_key": "int, >=4000, <4100"}]
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)

            config_spec = vim.vm.ConfigSpec()
            for nic in nics:
                pg_mor = self.get_portgroup_mor(nic['pg_moid'])
                nic_spec = vm_utils.make_edit_nic_device_spec(
                    vm_mor, nic['dev_key'], pg_mor)
                config_spec.deviceChange.append(nic_spec)

            task_mor = vm_mor.ReconfigVM_Task(spec=config_spec)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Edit nics error: %s" % str(ex)
        return result

    def del_nics(self, vm_moid, nics):
        """
        Delete network adapters.
        @param nics: [{"dev_key": "int, >=4000, <4010"}]
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)

            config_spec = vim.vm.ConfigSpec()
            for nic in nics:
                nic_spec = vm_utils.make_delete_nic_device_spec(
                    vm_mor, nic['dev_key'])
                config_spec.deviceChange.append(nic_spec)

            task_mor = vm_mor.ReconfigVM_Task(spec=config_spec)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Delete nics error: %s" % str(ex)
        return result

    def mark_as_template(self, vm_moid):
         """
        Mark vm as template.
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)
            vm_mor.MarkAsTemplate()
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Mark vm as template error: %s" % str(ex)
        return result

    def vm_install_tools(self, vm_moid):
        pass

    def vm_upgrade_tools(self, vm_moid):
        """
        Upgrade VM VMware Tools.
        """
        result= DataResult()
        try:
            vm_mor= self.get_vm_mor(vm_moid)
            task_mor= vm_mor.UpgradeTools()
            result.data= {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Upgrade VMware tools error: %s" % str(ex)
        return result

    def vm_reconfigure_tools(self, vm_moid, tools_conf):
        """
        Reconfigure VM VMware tools.
        @param tools_conf: {
            "sync_host_time": True,
            "auto_upgrade": False,
        }
        """
        result= DataResult()
        try:
            vm_mor= self.get_vm_mor(vm_moid)
            config_spec= vim.vm.ConfigSpec()
            config_spec.tools= vm_mor.config.tools
            config_spec.tools.syncTimeWithHost= tools_config.get('sync_host_time', False)
            if tools_config.get('auto_upgrade', False):
                spec.tools.toolsUpgradePolicy= "upgradeAtPowerCycle"
            else:
                spec.tools.toolsUpgradePolicy= "manual"
            task_mor= vm_mor.ReconfigVM_Task(spec=config_spec)
            result.data= {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Reconfigure VM VMware tools error: %s" % str(ex)
        return result

    def vm_extra_config(self, vm_moid, options):
        """
        Add or update vm extra configure.

        @param options: {'disk.EnableUUID': 'true'}
        """
        result= DataResult()
        try:
            vm_mor= self.get_vm_mor(vm_moid)
            config_spec= vm_utils._make_extra_config(options)
            task_mor= vm_mor.ReconfigVM_Task(spec=config_spec)
            result.data= {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "Add or update vm extra configure error: %s" % str(ex)
        return result

    def check_vm_migrate(self, vm_moid, host_moid, cluster_moid):
        """
        Check vm migrate.
        """
        vm_mor = self.get_vm_mor(vm_moid)
        host_mor = self.get_host_mor(host_moid)
        cluster_mor = self.get_cluster_mor(cluster_moid)
        res_pool_mor = cluster_mor.resourcePool if cluster_mor else None
        check_result = self.checker.check_migrate(vm_mor, host_mor, res_pool_mor)
        return check_result

    def migrate_vm(self, vm_moid, host_moid=None, cluster_moid=None,
                    priority='defaultPriority'):
        """
        VM vMotion.

        @param Priority: highPriority lowPriority defaultPriority
        """
        result = DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)
            host_mor = self.get_host_mor(host_moid)
            cluster_mor = self.get_cluster_mor(cluster_moid)
            res_pool_mor = cluster_mor.resourcePool if cluster_mor else None
            priority = vim.VirtualMachine.MovePriority(priority)
            task_mor = vm_mor.Migrate(res_pool_mor, host_mor, priority)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "VM vMotion error: %s" % str(ex)
        return result

    def check_vm_relocate(self, vm_moid, relocate_config):
        """
        Check vm relocate.

        @param relocate_config[
            'host_moid': "",
            'ds_moid': "",
            'folder_moid': "",
            'nic': ["dev_key": "", "pg_moid": ""],
            'disk': ["dev_key": "", "ds_moid": "", "ds_type": ""],
            ]
        """
        vm_mor = self.get_vm_mor(vm_moid)
        host_mor = self.get_host_mor(relocate_config.get('host_moid'))
        cluster_mor = self.get_cluster_mor(relocate_config.get('cluster_moid'))
        res_pool_mor = cluster_mor.resourcePool if cluster_mor else None
        ds_mor = utils.get_datastore_mor(relocate_config.get('ds_moid'))
        folder_mor = utils.get_folder_mor(relocate_config.get('folder_moid'))

        relocate_spec = vim.vm.RelocateSpec()
        relocate_spec.folder = folder_mor
        relocate_spec.host = host_mor
        relocate_spec.pool = res_pool_mor
        relocate_spec.datastore = ds_mor

        # nic device change spec
        for nic_cfg in relocate_config.get("nics_cfg", []):
            pg_mor = self.get_portgroup_mor(nic_cfg['pg_moid'])
            nic_spec = vm_utils.make_edit_nic_device_spec(
                vm_mor, nic_cfg['dev_key'], pg_mor)
            relocate_spec.deviceChange.append(nic_spec)

        # disk device locat spec
        for disk_cfg in relocate_config.get("disks_cfg", []):
            ds_mor= utils.get_datastore_mor(disk_cfg['ds_moid'])
            disk_loc_spec= vm_utils.make_disk_locator_spec(vm_mor,
                                disk_cfg["dev_key"],
                                ds_mor,
                                disk_cfg.get("disk_type"))
            relocate_spec.disk.append(disk_loc_spec)

        check_result = self.checker.check_relocate(vm_mor, relocate_spec)
        return check_result

    def relocate_vm(self, vm_moid, relocate_config, priority='defaultPriority'):
        """
        VM Storage vMotion.

        @param relocate_config[
            'host_moid': "",
            'ds_moid': "",
            'folder_moid': "",
            'nic': ["dev_key": "", "pg_moid": ""],
            'disk': ["dev_key": "", "ds_moid": "", "ds_type": ""],
            ]
        """
        result= DataResult()
        try:
            vm_mor = self.get_vm_mor(vm_moid)
            host_mor = self.get_host_mor(relocate_config.get('host_moid'))
            cluster_mor = self.get_cluster_mor(relocate_config.get('cluster_moid'))
            res_pool_mor = cluster_mor.resourcePool if cluster_mor else None
            ds_mor = utils.get_datastore_mor(relocate_config.get('ds_moid'))
            folder_mor = utils.get_folder_mor(relocate_config.get('folder_moid'))

            relocate_spec = vim.vm.RelocateSpec()
            relocate_spec.folder = folder_mor
            relocate_spec.host = host_mor
            relocate_spec.pool = res_pool_mor
            relocate_spec.datastore = ds_mor

            # nic device change spec
            for nic_cfg in relocate_config.get("nics_cfg", []):
                pg_mor = self.get_portgroup_mor(nic_cfg['pg_moid'])
                nic_spec = vm_utils.make_edit_nic_device_spec(
                    vm_mor, nic_cfg['dev_key'], pg_mor)
                relocate_spec.deviceChange.append(nic_spec)

            # disk device locat spec
            for disk_cfg in relocate_config.get("disks_cfg", []):
                ds_mor= utils.get_datastore_mor(disk_cfg['ds_moid'])
                disk_loc_spec= vm_utils.make_disk_locator_spec(vm_mor, disk_cfg["dev_key"], ds_mor, disk_cfg.get("disk_type"))
                relocate_spec.disk.append(disk_loc_spec)

            priority = vim.VirtualMachine.MovePriority(priority)

            task_mor = vm_mor.Relocate(relocate_spec, priority)
            result.data = {"task_key": task_mor._moId}
        except Exception as ex:
            LOG.exception(ex)
            result.status = False
            result.message = "VM Storage vMotion error: %s" % str(ex)
        return result
