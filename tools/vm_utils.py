# -*- coding:utf-8 -*-

"""
Virtual machine manipulation tool functions.
"""

from __future__ import absolute_import

import logging
import uuid

from pyVmomi import vim, vmodl

from . import constants
from . import common_utils
from . import vm


LOG = logging.getLogger(__name__)


def _set_disk_type(disk_backing, disk_type):
    if disk_type == constants.DISK_TYPE_THIN:
        disk_backing.eagerlyScrub = None
        disk_backing.thinProvisioned = True
    elif disk_type == constants.DISK_TYPE_PREALLOCATED:
        disk_backing.eagerlyScrub = None
        disk_backing.thinProvisioned = False
    elif disk_type == constants.DISK_TYPE_EAGER_ZEROED_THICK:
        disk_backing.eagerlyScrub = True
        disk_backing.thinProvisioned = False
    return disk_backing


def _make_extra_config(options):
    extra_cfgs = []
    for k, v in options.items():
        opt = vim.option.OptionValue()
        opt.key = k
        opt.value = v
        extra_cfgs.append(opt)
    return extra_cfgs


def make_disk_enable_uuid_extra_config():
    options = {'disk.EnableUUID': 'true'}
    extra_cfgs = _make_extra_config(options)
    return extra_cfgs[0]


def make_add_nic_device_spec(pg_mor, adapter_type):
    """
    Make add nic device spec.
    """
    nic_spec = vim.vm.device.VirtualDeviceSpec()
    nic_spec.operation = 'add'
    nic_spec.device = constants.NIC_DEVICE_SPCE[adapter_type]
    if isinstance(pg_mor, vim.dvs.DistributedVirtualPortgroup):
        # add dvsp
        nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        nic_spec.device.backing.port = vim.dvs.PortConnection()
        nic_spec.device.backing.port.portgroupKey = pg_mor.key
        nic_spec.device.backing.port.switchUuid = pg_mor.config.distributedVirtualSwitch.uuid
    else:
        # add svsp
        nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
        nic_spec.device.backing.network = pg_mor
        nic_spec.device.backing.deviceName = pg_mor.name
    nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    nic_spec.device.connectable.startConnected = True
    nic_spec.device.connectable.allowGuestControl = True
    nic_spec.device.connectable.connected = True
    # nic_spec.device.connectable.status = 'untried'
    nic_spec.device.wakeOnLanEnabled = True
    # nic_spec.device.addressType = 'assigned'
    return nic_spec


def make_edit_nic_device_spec(vm_mor, nic_dev_key, pg_mor):
    """
    Make edit nic device spec.
    """
    if nic_dev_key < 4000 or nic_dev_key >= 4100:
        raise Exception("The vm nic device key error!")

    nic_spec = vim.vm.device.VirtualDeviceSpec()
    nic_spec.operation = 'edit'
    device = vm._get_vm_device_by_key(vm_mor, nic_dev_key)
    if not device:
        raise Exception("The vm %s nic device %s not found!" %
                        (vm_mor.name, nic_dev_key))
    nic_spec.device = device
    if isinstance(pg_mor, vim.dvs.DistributedVirtualPortgroup):
        # edit dvsp
        nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        nic_spec.device.backing.port = vim.dvs.PortConnection()
        nic_spec.device.backing.port.portgroupKey = pg_mor.key
        nic_spec.device.backing.port.switchUuid = pg_mor.config.distributedVirtualSwitch.uuid
    else:
        # edit svsp
        nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
        nic_spec.device.backing.network = pg_mor
        nic_spec.device.backing.deviceName = pg_mor.name
    return nic_spec


def make_delete_nic_device_spec(vm_mor, nic_dev_key):
    """
    Make delete nic device spec.
    """
    if nic_dev_key < 4000 or nic_dev_key >= 4100:
        raise Exception("The vm nic device key error!")

    nic_spec = vim.vm.device.VirtualDeviceSpec()
    nic_spec.operation = "remove"
    device = vm._get_vm_device_by_key(vm_mor, nic_dev_key)
    if not device:
        raise Exception("The vm %s nic device %s not found!" %
                        (vm_mor.name, nic_dev_key))
    nic_spec.device = device
    return nic_spec


def make_resize_disk_device_spec(vm_mor, dev_key, disk_size):
    """
    Make resize disk device spec.
    """
    device_spec = vim.vm.device.VirtualDeviceSpec()
    device_spec.operation = "edit"
    device_spec.device = vm._get_vm_device_by_key(vm_mor, dev_key)
    # reset disk size
    device_spec.device.capacityInKB = int(disk_size) * 1024 * 1024
    return device_spec


def _check_or_add_controller(scsi_controllers, bus_number,
                             sharedbus_mode='noSharing'):
    """
    Check scsi controller device, or add controller device
    @param sharedBus: noSharing, virtualSharing, physicalSharing
    """
    f_controller = None
    scsi_controller0_type = None
    controller_spec = None
    for c in scsi_controllers:
        if c.busNumber == bus_number:
            f_controller = c
        if c.key == 1000:
            # BusLogic, LsiLogic, LsiLogicSAS, ParaVirtual
            scsi_controller0_type = constants.SCSI_CONTROLLER_NAME[c.__class__.__name__]
    if not f_controller:
        if not scsi_controller0_type:
            raise Exception("Not found SCSI controller 0 !")

        scsi_ctl_spec = constants.SCSI_CONTROLLER_SPEC.get(
            scsi_controller0_type)
        if not scsi_ctl_spec:
            raise Exception("The scsi controller type error: %s" %
                            scsi_controller0_type)
        LOG.info("Add SCSI controller: %s." % scsi_controller0_type)
        controller_spec = vim.vm.device.VirtualDeviceSpec()
        controller_spec.operation = 'add'
        controller_spec.device = scsi_ctl_spec
        controller_spec.device.key = 1000 + bus_number
        controller_spec.device.controllerKey = 100
        controller_spec.device.unitNumber = 3 + bus_number
        controller_spec.device.busNumber = bus_number
        controller_spec.device.hotAddRemove = True
        controller_spec.device.sharedBus = sharedbus_mode
        controller_spec.device.scsiCtlrUnitNumber = 7
    else:
        if sharedbus_mode != f_controller.sharedBus:
            LOG.error(
                'The current SCSI controller bus share mode does not match !')
            raise Exception(
                'The current SCSI controller bus share mode does not match !')
    return controller_spec


def check_and_make_scsi_controller_spec(scsi_controllers, disk, share_disk=False):
    """
    Check and make scsi controller spec.
    """
    c_bus_number = disk['vdev_node'].split(':')[0]
    if disk.get('is_raw') and share_disk:
        sharedbus_mode = "physicalSharing"
    else:
        sharedbus_mode = "noSharing"
    return _check_or_add_controller(scsi_controllers,
                                    int(c_bus_number),
                                    sharedbus_mode=sharedbus_mode)


def make_attach_scsi_disk_device_spec(disk, share_disk=False):
    """ 
    Make attach scsi disk device spec.
    diskMode:
        - independent_persistent: Same as persistent, but not affected by
          snapshots.
        - persistent: Changes are immediately and permanently written to the
          virtual disk.
        - independent_nonpersistent: Same as nonpersistent, but not affected by
          snapshots.
        - undoable: Changes are made to a redo log, but you are given the
          option to commit or undo.
        - nonpersistent: Changes to virtual disk are made to a redo log and
          discarded at power off.
        - append: Changes are appended to the redo log; you revoke changes by
          removing the undo log.

        compatibilityMode:
        - physicalMode: A disk device backed by a physical compatibility mode
          raw disk mapping cannot use disk modes, and commands are passed
          straight through to the LUN indicated by the raw disk mapping.
        - virtualMode: A disk device backed by a virtual compatibility mode raw
          disk mapping can use disk modes.

        共享盘默认值
        RDM: physicalMode
        VMDK: independent_persistent
    """
    (c_bus_number, d_unit_number) = disk['vdev_node'].split(':')
    # init virtual device spec
    disk_spec = vim.vm.device.VirtualDeviceSpec()
    disk_spec.operation = "add"
    disk_spec.device = vim.vm.device.VirtualDisk()
    disk_spec.device.unitNumber = int(d_unit_number)
    disk_spec.device.key = 2000 + \
        int(c_bus_number) * 16 + int(d_unit_number)
    disk_spec.device.controllerKey = 1000 + int(c_bus_number)
    # create disk backing info
    if disk.get('is_raw'):
        # create raw disk backing info
        disk_spec.device.backing = vim.vm.device.VirtualDisk.RawDiskMappingVer1BackingInfo()
        disk_spec.device.backing.compatibilityMode = disk.get(
            'compatibility_mode', 'physicalMode')
        if disk.get('disk_path'):
            disk_spec.device.backing.fileName = disk['disk_path']
        else:
            disk_spec.fileOperation = "create"
            disk_spec.device.backing.deviceName = disk['device_name']
    else:
        # create vmdk disk backing info
        disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        if disk.get('disk_path'):
            disk_spec.device.backing.fileName = disk['disk_path']
        else:
            disk_spec.fileOperation = "create"
            disk_spec.device.backing.uuid = disk.get('disk_uuid')
            # set disk type
            disk_spec.device.backing = _set_disk_type(disk_spec.device.backing,
                                                      disk['disk_type'])
            # set disk size
            disk_spec.device.capacityInKB = int(
                disk['disk_size']) * 1024 * 1024
        if share_disk:
            disk_spec.device.backing.sharing = 'sharingMultiWriter'
    # default disk mode: persistent
    disk_spec.device.backing.diskMode = disk.get('disk_mode', 'persistent')
    if disk.get('ds_name'):
        disk_spec.device.backing.fileName = "[%s]" % disk['ds_name']
    return disk_spec


def make_remove_device_spec(device, file_operation=None):
    """
    Make detach disk device spec.
    @file_operation: destroy / destroy / destroy
    """
    device_spec = vim.vm.device.VirtualDeviceSpec()
    device_spec.operation = "remove"
    if file_operation:
        device_spec.fileOperation = file_operation
    device_spec.device = device
    return device_spec


def make_add_cdrom_device_spec(cdrom):
    """
    Make add cdrom device spec.
    @param cdrom: {
        "vdev_node": "0:0",
        "iso_file": "[datastore01] CentOS-7-x86_64-Minimal-1810.iso",
    }
    """
    (c_bus_number, d_unit_number) = cdrom['vdev_node'].split(':')
    cdrom_spec = vim.vm.device.VirtualDeviceSpec()
    cdrom_spec.operation = "add"
    cdrom_spec.device = vim.vm.device.VirtualCdrom()
    cdrom_spec.device.key = 3000 + int(c_bus_number) * 2 + int(d_unit_number)

    connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    connectable.allowGuestControl = True
    backing = vim.vm.device.VirtualCdrom.RemotePassthroughBackingInfo()
    if cdrom.get('iso_file'):
        backing = vim.vm.device.VirtualCdrom.IsoBackingInfo(
            fileName=cdrom['iso_file'])
        connectable.startConnected = True
    cdrom_spec.device.backing = backing
    cdrom_spec.device.connectable = connectable
    cdrom_spec.device.controllerKey = 200 + int(c_bus_number)
    cdrom_spec.device.unitNumber = int(d_unit_number)
    return cdrom_spec


def make_fileinfo(ds_name, vm_name):
    """
    Make vmx file info.
    """
    fileinfo = vim.vm.FileInfo()
    fileinfo.logDirectory = None
    fileinfo.snapshotDirectory = None
    fileinfo.suspendDirectory = None
    fileinfo.vmPathName = "[%s] %s" % (ds_name, vm_name)
    return fileinfo


def _clone_vm_config_nic(config_spec, template_mor, nets):
    """
    @param nets:
        [{'ip': '10.0.0.13', 'netmask': '255.255.255.0', 'gateway': '10.0.0.1',
        'pg_moid': 'dvportgroup-391', 'adapter_type': 'E1000',
        'pg_mor': <object>},
        ]
    """
    template_nic_devs = vm._get_vm_nic_adapter_devices(template_mor)
    while len(template_nic_devs) > len(nets):
        nets.append(None)
    while len(template_nic_devs) < len(nets):
        template_nic_devs.append(None)
    for (dev, net) in zip(template_nic_devs, nets):
        nic_spec = vim.vm.device.VirtualDeviceSpec()
        if not net:
            # remove
            nic_spec.operation = "remove"
            nic_spec.device = dev
        else:
            pg_mor = net['pg_mor']
            adapter_type = net.get('adapter_type', 'VMXNET3')
            is_pg_dvsp = isinstance(
                pg_mor, vim.dvs.DistributedVirtualPortgroup)
            if dev is None:
                # add
                nic_spec.operation = 'add'
                nic_spec.device = constants.NIC_DEVICE_SPCE.get(adapter_type)
            else:
                nic_spec.operation = "edit"
                nic_spec.device = dev

            if is_pg_dvsp:
                # add dvsp
                nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
                nic_spec.device.backing.port = vim.dvs.PortConnection()
                nic_spec.device.backing.port.portgroupKey = pg_mor.key
                nic_spec.device.backing.port.switchUuid = pg_mor.config.distributedVirtualSwitch.uuid
            else:
                # add svsp
                nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                nic_spec.device.backing.network = pg_mor
                nic_spec.device.backing.deviceName = pg_mor.name
        nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic_spec.device.connectable.startConnected = True
        nic_spec.device.connectable.allowGuestControl = True
        nic_spec.device.connectable.connected = True
        # nic_spec.device.connectable.status = 'untried'
        nic_spec.device.wakeOnLanEnabled = True
        # nic_spec.device.addressType = 'assigned'
        config_spec.deviceChange.append(nic_spec)


def _get_available_vdev_node(devs, allocated_vdev_node):
    all_vdev_node = ["%d:%d" % (a, b) for a in range(4)
                     for b in range(16) if b != 7]
    used_vdev_node = ["%d:%d" % (
        dev.controllerKey-1000, dev.unitNumber) for dev in devs if dev]
    available_vdev_node = [
        n for n in all_vdev_node if n not in used_vdev_node and n not in allocated_vdev_node]
    if len(available_vdev_node) < 1:
        raise Exception("No SCSI controllers are available !")
    return available_vdev_node[0]


def _clone_vm_config_disk(config_spec, template_mor, disks):
    """
    @@@@ disk_type: [None|thin|eagerZeroedThick|preallocated]
    """
    template_disk_devs = vm._get_vm_disk_devices(template_mor)
    template_scsi_controllers = vm._get_vm_scsi_controller_devices(template_mor)

    while len(template_disk_devs) > len(disks):
        disks.append(None)
    while len(template_disk_devs) < len(disks):
        template_disk_devs.append(None)
    allocated_vdev_node = []
    for (dev, disk) in zip(template_disk_devs, disks):
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        if disk is None:
            # remove
            disk_spec.operation = "remove"
            disk_spec.device = dev
        else:
            disk_size = disk['disk_size']
            disk_type = disk['disk_type']
            if dev is None:
                # add
                disk_spec.fileOperation = "create"
                disk_spec.operation = "add"
                disk_spec.device = vim.vm.device.VirtualDisk()
                disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
                disk_spec.device.backing.diskMode = 'persistent'
                if disk.get('ds_name'):
                    disk_spec.device.backing.fileName = "[%s]" % disk['ds_name']
                # set scsi vdev node
                available_vdev_node = disk.get('vdev_node')
                if not available_vdev_node:
                    available_vdev_node = _get_available_vdev_node(
                        template_disk_devs, allocated_vdev_node)
                    allocated_vdev_node.append(available_vdev_node)
                    disk['vdev_node'] = available_vdev_node

                (c_bus_number, d_unit_number) = available_vdev_node.split(':')

                controller_spec = check_and_make_scsi_controller_spec(
                    template_scsi_controllers, disk)
                if controller_spec:
                    template_scsi_controllers.append(controller_spec.device)
                    config_spec.append(controller_spec)

                disk_spec.device.unitNumber = int(d_unit_number)
                disk_spec.device.controllerKey = 1000 + int(c_bus_number)
                disk_spec.device.key = 2000 + \
                    int(c_bus_number) * 16 + int(d_unit_number)
            else:
                # edit
                disk_spec.operation = "edit"
                disk_spec.device = dev
            # for relocate use
            disk_spec.device.backing.datastore = disk['ds_mor']
            # update disk type
            disk_spec.device.backing = _set_disk_type(disk_spec.device.backing,
                                                      disk['disk_type'])
            # update disk size
            new_disk_kb = int(disk_size) * 1024 * 1024
            if disk_spec.device.capacityInKB < new_disk_kb:
                disk_spec.device.capacityInKB = new_disk_kb
        config_spec.deviceChange.append(disk_spec)


def make_clone_config_spec(template_mor, vm_cfg, nics, disks):
    """
    Make clone config spec.

    vim.vm.ConfigSpec()
    vim.vm.device.VirtualDiskSpec()
    """
    config_spec = vim.vm.ConfigSpec()
    # config_spec.memoryHotAddEnabled = True
    # config_spec.cpuHotAddEnabled = True
    # config_spec.cpuHotRemoveEnabled = True
    config_spec.memoryMB = vm_cfg['memoryMB']
    config_spec.numCPUs = int(vm_cfg['num_cpu']) * int(vm_cfg['num_core'])
    config_spec.numCoresPerSocket = vm_cfg['num_core']
    if not vm_cfg.get('uuid'):
        vm_cfg['uuid'] = str(uuid.uuid1())
    config_spec.uuid = vm_cfg['uuid']

    # update device config
    _clone_vm_config_nic(config_spec, template_mor, nics)
    _clone_vm_config_disk(config_spec, template_mor, disks)

    return config_spec


def make_clone_relocate_spec(clone_spec, res_pool_mor, esxi_mor, datastore_mor):
    """
    Make clone relocate spec.

    Disk Transform Rule:
        [thin, preallocated, eagerZeroedThick] -> thin
        [thin, preallocated]                   -> preallocated
        [thin, preallocated, eagerZeroedThick] -> eagerZeroedThick
    """
    # https://github.com/vmware/pyvmomi/blob/master/docs/vim/vm/RelocateSpec.rst
    relocate_spec = vim.vm.RelocateSpec()
    relocate_spec.pool = res_pool_mor
    relocate_spec.host = esxi_mor
    relocate_spec.datastore = datastore_mor

    for disk_spec in clone_spec.config.deviceChange:
        if isinstance(disk_spec.device, vim.vm.device.VirtualDisk) \
                and disk_spec.operation == 'edit':
            disk_locator = vim.vm.RelocateSpec.DiskLocator()
            disk_locator.diskId = disk_spec.device.key
            disk_locator.diskBackingInfo = disk_spec.device.backing
            if disk_spec.device.backing.datastore:
                disk_locator.datastore = disk_spec.device.backing.datastore
            relocate_spec.disk.append(disk_locator)
    return relocate_spec


def sysprep_customization(hostname, domain='localhost.domain',
                          workgroup='WORKGROUP', passwd='password',
                          os_type='linux'):
    """
    hostname setting
    """
    sysprep_custom = None
    fixedname = vim.vm.customization.FixedName(name=hostname)
    if os_type == 'linux':
        sysprep_custom = vim.vm.customization.LinuxPrep(hostName=fixedname,
                                                        domain=domain,
                                                        timeZone='Asia/Shanghai')
    elif os_type == 'windows':
        # timeZone: https://technet.microsoft.com/en-us/library/ms145276(v=sql.90).aspx
        password_custom = vim.vm.customization.Password(
            value=passwd, plainText=True)
        guiunattended = vim.vm.customization.GuiUnattended(password=password_custom,
                                                           timeZone=210,
                                                           autoLogon=True,
                                                           autoLogonCount=1)
        userdata = vim.vm.customization.UserData(fullName=hostname,
                                                 orgName=hostname,
                                                 computerName=fixedname,
                                                 productId='')
        # identification = vim.vm.customization.Identification(joinDomain=domain,
        #                                                      domainAdmin=domain,
        #                                                      domainAdminPassword=password_custom)
        identification = vim.vm.customization.Identification(
            joinWorkgroup=workgroup)
        sysprep_custom = vim.vm.customization.Sysprep(guiUnattended=guiunattended,
                                                      userData=userdata,
                                                      identification=identification)
    return sysprep_custom


def network_customization(vm_net):
    """
    VM network setting
    vm_net: [
            {'ip': '10.0.0.13', 'netmask': '255.255.255.0', 'gateway': '10.0.0.1',
             'ipv6': '2001::4', 'prefixv6': 112, 'gatewayv6': '2001::1',
            },
            ]
    """
    adaptermap_custom = []
    for net in vm_net:
        if net:
            adaptermap = vim.vm.customization.AdapterMapping()
            if net.get('ip') and net.get('netmask'):
                fixedip = vim.vm.customization.FixedIp(ipAddress=net['ip'])
                adaptermap.adapter = \
                    vim.vm.customization.IPSettings(ip=fixedip,
                                                    subnetMask=net['netmask'],
                                                    gateway=net.get('gateway'))
            else:
                dhcpip = vim.vm.customization.DhcpIpGenerator()
                adaptermap.adapter = vim.vm.customization.IPSettings(ip=dhcpip)
            if net.get('ipv6') and net.get('prefixv6'):
                fixedipv6 = vim.vm.customization.FixedIpV6(ipAddress=net['ipv6'],
                                                           subnetMask=net['prefixv6'])
                ipv6spec = vim.vm.customization.IPSettings.IpV6AddressSpec()
                ipv6spec.ip.append(fixedipv6)
                ipv6spec.gateway.append(net.get('gatewayv6'))
                adaptermap.adapter.ipV6Spec = ipv6spec
            adaptermap_custom.append(adaptermap)
    return adaptermap_custom


def dns_customization(dnslist):
    """
    dnslist = ['10.1.10.14', '10.1.10.15']
    """
    return vim.vm.customization.GlobalIPSettings(dnsServerList=dnslist)


def make_custom_spec(vm_mor, vm_cfg, nics, dnslist):
    """
    Make vm custom spec.
    """
    # Verify vm hostname
    hostname = common_utils.sanitize_hostname(
        vm_cfg['name'], vm_cfg.get('hostname'))

    # Get vm system type
    vm_cfg['os_type'] = common_utils.get_os_type(vm_mor.config.guestId)

    custom_spec = vim.vm.customization.Specification()
    # Make sysprep (hostname/domain/timezone/workgroup) customization
    custom_spec.identity = sysprep_customization(
        hostname=hostname,
        domain=vm_cfg.get('domain'),
        os_type=vm_cfg('os_type'))
    # Make network customization
    custom_spec.nicSettingMap = network_customization(nics)
    # Make dns customization
    custom_spec.globalIPSettings = dns_customization(dnslist)

    return custom_spec


def make_disk_locator_spec(relocate_spec, disk_dev, ds_mor, disk_type=None):
    """
    Make disk locator spec.
    """
    disk_locator = vim.vm.RelocateSpec.DiskLocator()
    disk_locator.datastore = ds_mor
    disk_locator.diskId = disk_dev.key
    # set disk type
    disk_locator.diskBackingInfo = _set_disk_type(disk_dev.backing,
                                                    disk_type)
    relocate_spec.disk.append(disk_locator)