# -*- coding:utf-8 -*-

"""
VM info.

vim.vm.device.VirtualDevice[]
    @@  vim.vm.device.VirtualPCIController:      key>=100
    @@  vim.vm.device.VirtualIDEController:      key>=200
    @@  vim.vm.device.VirtualPS2Controller:      key>=300
    @@  vim.vm.device.VirtualSIOController:      key>=400
    @@  vim.vm.device.VirtualVideoCard:          key>=500
    @@  vim.vm.device.VirtualKeyboard:           key>=600
    @@  vim.vm.device.VirtualPointingDevice:     key>=700
    @@  vim.vm.device.ParaVirtualSCSIController: key>=1000
    @@  vim.vm.device.VirtualDisk:               key>=2000
    @@  vim.vm.device.VirtualCdrom:              key>=3002
    @@  vim.vm.device.VirtualVmxnet3:            key>=4000
    @@  vim.vm.device.VirtualE1000:              key>=4000
    @@  vim.vm.device.VirtualE1000e:             key>=4000
    @@  vim.vm.device.VirtualFloppy:             key>=8000
    @@  vim.vm.device.VirtualVMCIDevice:         key>=12000
"""

from __future__ import absolute_import

import ipaddress
from urllib.request import unquote
from pyVmomi import vim

from . import constants
from . import common_utils


def _get_nic_adapter_type(device):
    adapter_type = ""
    if isinstance(device, vim.vm.device.VirtualVmxnet3):
        adapter_type = 'VMXNET3'
    elif isinstance(device, vim.vm.device.VirtualE1000):
        adapter_type = 'E1000'
    elif isinstance(device, vim.vm.device.VirtualE1000e):
        adapter_type = 'E1000E'
    return adapter_type


def _get_vm_scsi_controller_devices(vm_mor):
    return [dev for dev in vm_mor.config.hardware.device
            if isinstance(dev, vim.vm.device.VirtualSCSIController)]


def _get_vm_disk_devices(vm_mor):
    return [dev for dev in vm_mor.config.hardware.device
            if isinstance(dev, vim.vm.device.VirtualDisk)]


def _get_vm_nic_adapter_devices(vm_mor):
    return [dev for dev in vm_mor.config.hardware.device
            if isinstance(dev, vim.vm.device.VirtualEthernetCard)]


def _get_vm_controllers_type_info(vm_mor):
    scsi_ctls_sharedbus = {}
    scsi_ctls_type = {}
    for dev in vm_mor.config.hardware.device:
        if dev.key in [1000, 1001, 1002, 1003]:
            scsi_ctls_sharedbus[dev.key] = dev_mor.sharedBus
            if isinstance(dev, vim.vm.device.ParaVirtualSCSIController):
                scsi_ctls_type[dev.key] = 'ParaVirtual'
            elif isinstance(dev, vim.vm.device.VirtualLsiLogicSASController):
                scsi_ctls_type[dev.key] = 'LsiLogicSAS'
            elif isinstance(dev, vim.vm.device.VirtualLsiLogicController):
                scsi_ctls_type[dev.key] = 'LsiLogic'
            elif isinstance(dev, vim.vm.device.VirtualBusLogicController):
                scsi_ctls_type[dev.key] = 'BusLogic'
            else:
                scsi_ctls_type[dev.key] = None
    return (scsi_ctls_type, scsi_ctls_sharedbus)


def _get_vm_device_by_key(vm_mor, dev_key):
    """
    Get vm device by device key.
    """
    vm_device = None
    for device in vm_mor.config.hardware.device:
        if device.key == dev_key:
            vm_device = device
            break
    return vm_device


def _vm_base_info(vm_mor):
    """
    VM base info.
    """
    base_info = {
        "name": vm_mor.name,
        "moid": vm_mor._moId,
        "folder_moid": vm_mor.parent._moId,
    }
    return base_info


def _vm_guest_info(vm_mor):
    """
    VM Guest info.
    """
    guest_info = {
        "toolsStatus": vm_mor.guest.toolsStatus,
        "toolsVersionStatus": vm_mor.guest.toolsVersionStatus,
        "toolsVersionStatus2": vm_mor.guest.toolsVersionStatus2,
        "toolsRunningStatus": vm_mor.guest.toolsRunningStatus,
        "toolsVersion": vm_mor.guest.toolsVersion,
        "toolsInstallType": vm_mor.guest.toolsInstallType,
        "guestId": vm_mor.guest.guestId,
        "guestFamily": vm_mor.guest.guestFamily,
        "guestFullName": vm_mor.guest.guestFullName,
        "hostname": vm_mor.guest.hostName,
        "ipAddress": vm_mor.guest.ipAddress,
        "guestState": vm_mor.guest.guestState,
    }
    guest_info['os_type'] = common_utils.get_os_type(guest_info['guestId'])
    return guest_info


def _vm_summary_quick_stats():
    """
    VM summary quick stats.
    """
    quick_stats = {
        "overallCpuUsage": vm_mor.summary.quickStats.overallCpuUsage,
        "overallCpuDemand": vm_mor.summary.quickStats.overallCpuDemand,
        "guestMemoryUsage": vm_mor.summary.quickStats.guestMemoryUsage,
        "hostMemoryUsage": vm_mor.summary.quickStats.hostMemoryUsage,
        # "distributedCpuEntitlement": vm_mor.summary.quickStats.distributedCpuEntitlement,
        # "distributedMemoryEntitlement": vm_mor.summary.quickStats.distributedMemoryEntitlement,
        # "staticCpuEntitlement": vm_mor.summary.quickStats.staticCpuEntitlement,
        # "staticMemoryEntitlement": vm_mor.summary.quickStats.staticMemoryEntitlement,
        # "privateMemory": vm_mor.summary.quickStats.privateMemory,
        # "sharedMemory": vm_mor.summary.quickStats.sharedMemory,
        # "swappedMemory": vm_mor.summary.quickStats.swappedMemory,
        # "balloonedMemory": vm_mor.summary.quickStats.balloonedMemory,
        # "consumedOverheadMemory": vm_mor.summary.quickStats.consumedOverheadMemory,
        # "compressedMemory": vm_mor.summary.quickStats.compressedMemory,
        "uptimeSeconds": vm_mor.summary.quickStats.uptimeSeconds or 0,
        # "ssdSwappedMemory": vm_mor.summary.quickStats.ssdSwappedMemory,
    }
    return quick_stats

def _vm_summary_config_info(vm_mor):
    """
    VM summary config info.
    """
    config_info = {
        "name": vm_mor.summary.config.name,
        "template": vm_mor.summary.config.template,
        "vmPathName": vm_mor.summary.config.vmPathName,
        "memorySizeMB": vm_mor.summary.config.memorySizeMB,
        "numCpu": vm_mor.summary.config.numCpu,
        "numEthernetCards": vm_mor.summary.config.numEthernetCards,
        "numVirtualDisks": vm_mor.summary.config.numVirtualDisks,
        "uuid": vm_mor.summary.config.uuid,
        "instanceUuid": vm_mor.summary.config.instanceUuid,
        "guestId": vm_mor.summary.config.guestId,
        "guestFullName": vm_mor.summary.config.guestFullName,
    }
    return config_info

def _vm_runtime_info(vm_mor):
    """
    VM runtime info.
    """
    run_info = {
        "powerState": vm_mor.summary.runtime.powerState,
        "host": vm_mor.summary.runtime.host.name,
        "host_moid": vm_mor.summary.runtime.host._moId,
        "bootTime": vm_mor.summary.runtime.bootTime,
        "maxCpuUsage": vm_mor.summary.runtime.maxCpuUsage,
        "maxMemoryUsage": vm_mor.summary.runtime.maxMemoryUsage,
    }
    return run_info


def _vm_storage_info(vm_mor):
    """
    VM storage info.
    """
    storage_info = {
        "committed": vm_mor.storage.committed,
        "uncommitted": vm_mor.storage.uncommitted,
        "unshared": vm_mor.storage.unshared,
        "timestamp": vm_mor.storage.timestamp,
    }
    return storage_info


def _vm_disk_info(disk_device, scsi_ctls_type, scsi_ctls_sharedbus):
    """
    VM config hardware device: disk
    """
    disk_info = {}
    disk_info['label'] = disk_device.deviceInfo.label
    vdev_node = common_utils.get_vdev_node(disk_device.key)
    disk_info['vdev_node'] = vdev_node
    disk_info['scsi_name'] = "SCSI(%s)" % vdev_node
    disk_info['file_name'] = disk_device.backing.fileName
    disk_info['capacityKB'] = disk_device.capacityInKB
    disk_info['disk_mode'] = disk_device.backing.diskMode
    disk_info['contentid'] = disk_device.backing.contentId
    disk_info['ds_name'] = disk_device.backing.datastore.name
    disk_info['ds_moid'] = disk_device.backing.datastore._moId
    disk_info['key'] = disk_device.key
    disk_info['scsi_type'] = scsi_ctls_type.get(disk_device.controllerKey)
    disk_info['scsi_shared_bus'] = scsi_ctls_sharedbus.get(
        disk_device.controllerKey)
    if isinstance(disk_device.backing,
                  vim.vm.device.VirtualDisk.RawDiskMappingVer1BackingInfo):
        is_raw_disk = True
        disk_type = 'raw'
        disk_info['uuid'] = disk_device.backing.lunUuid
        disk_info['compatibilityMode'] = disk_device.backing.compatibilityMode
    elif isinstance(disk_device.backing,
                    vim.vm.device.VirtualDisk.FlatVer2BackingInfo):
        is_raw_disk = False
        if disk_device.backing.thinProvisioned:
            disk_type = constants.DISK_TYPE_THIN
        elif disk_device.backing.eagerlyScrub:
            disk_type = constants.DISK_TYPE_EAGER_ZEROED_THICK
        else:
            disk_type = constants.DISK_TYPE_PREALLOCATED
        disk_info['uuid'] = disk_device.backing.uuid
    disk_info['disk_type'] = disk_type
    disk_info['is_raw'] = is_raw_disk
    return disk_info


def get_vm_disk_info(vm_mor, vdev_node):
    """
    Get vm disk device info.
    """
    (scsi_ctls_type, scsi_ctls_sharedbus) = _get_vm_controllers_type_info(vm_mor)
    disk_info = {}
    for device in vm_mor.config.hardware.device:
        if not isinstance(device, vim.vm.device.VirtualDisk):
            continue
        v_n = common_utils.get_vdev_node(device.key)
        if v_n != vdev_node:
            continue
        disk_info = _vm_disk_info(device, scsi_ctls_type, scsi_ctls_sharedbus)
    return disk_info


def get_vm_disks_info(vm_mor):
    """
    Get vm disks device info.
    """
    (scsi_ctls_type, scsi_ctls_sharedbus) = _get_vm_controllers_type_info(vm_mor)
    disks_info = []
    for device in vm_mor.config.hardware.device:
        if not isinstance(device, vim.vm.device.VirtualDisk):
            continue
        disk_info = _vm_disk_info(device, scsi_ctls_type, scsi_ctls_sharedbus)
        disks_info.append(disk_info)
    return disks_info


def _vm_nic_info(net_device):
    """
    VM config hardware device: nic
    """
    nic_info = {}
    nic_info['adapter_type'] = _get_nic_adapter_type(net_device)
    if isinstance(net_device.backing,
                  vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo):
        pg_type = 'vds'
        pg_moid = net_device.backing.port.portgroupKey
    elif isinstance(net_device.backing,
                    vim.vm.device.VirtualEthernetCard.NetworkBackingInfo):
        pg_type = 'vss'
        pg_moid = net_device.backing.network._moId
    else:
        pg_type = ''
        pg_moid = ''
    nic_info['pg_type'] = pg_type
    nic_info['pg_moid'] = pg_moid
    nic_info['portgroup'] = unquote(net_device.deviceInfo.summary)
    nic_info['key'] = net_device.key
    nic_info['label'] = net_device.deviceInfo.label
    nic_info['mac_addr'] = net_device.macAddress
    nic_info['connected'] = net_device.connectable.connected
    return nic_info


def get_vm_nics_info(vm_mor):
    """
    Get vm nics device info.
    """
    nics_info = []
    nics_dev = _get_vm_nic_adapter_devices(vm_mor)
    for device in nics_dev:
        nic_info = _vm_nic_info(device)
        nics_info.append(nic_info)
    return nics_info


def get_guest_iproutes(vm_mor):
    """
    """
    iproutes = []
    for ipstack in vm_mor.guest.ipStack:
        for iproute in ipstack.ipRouteConfig.ipRoute:
            iproutes.append({
                'network': iproute.network,
                'prefix': iproute.prefixLength,
                'ipaddress': iproute.gateway.ipAddress,
                'device': iproute.gateway.device,
            })
    return iproutes


def get_ip_mask_network_version(ipaddr, prefix):
    try:
        ip_prefix = "%s/%s" % (ipaddr, prefix)
        ip_net = ipaddress.ip_network(ip_prefix, strict=False)
        ip_netmask = ip_net.netmask.compressed
        ip_network = ip_net.network_address.compressed
        ip_version = ip_net.version
    except ValueError:
        ip_netmask = None
        ip_network = None
        ip_version = None
    return ip_netmask, ip_network, ip_version


def get_ipv4_gateway(iproutes, network, dev_key):
    ipv4_gateway = None
    default_ipv4_gw = None
    for iproute in iproutes:
        _dev_key = int(iproute['device']) + 4000
        ip_gateway = iproute.get('ipaddress')
        ip_network = iproute.get('network')
        if dev_key == _dev_key and ip_network == network:
            ipv4_gateway = ip_gateway
        if dev_key == _dev_key and ip_network == "0.0.0.0":
            default_ipv4_gw = ip_gateway
    if not ipv4_gateway:
        ipv4_gateway = default_ipv4_gw
    return ipv4_gateway


def get_ipv6_gateway(iproutes, network, dev_key):
    ipv6_gateway = None
    default_ipv6_gw = None
    for iproute in iproutes:
        _dev_key = int(iproute['device']) + 4000
        ip_gateway = iproute.get('ipaddress')
        ip_network = iproute.get('network')
        if dev_key == _dev_key and ip_network == network:
            ipv6_gateway = ip_gateway
        if dev_key == _dev_key and ip_network == "::":
            default_ipv6_gw = ip_gateway
    if not ipv6_gateway:
        ipv6_gateway = default_ipv6_gw
    return ipv6_gateway


def get_vm_guest_net_info(vm_mor):
    """
    """
    nics_info = get_vm_nics_info(vm_mor)
    iproutes = get_guest_iproutes(vm_mor)
    for adapter in nics_info:
        key = adapter['key']
        # 添加属性
        adapter['ipv4'] = []
        adapter['ipv6'] = []
        for net in vm_mor.guest.net:
            if key != net.deviceConfigId:
                continue
            # portgroup/connected 变量已在 get_vm_net_info 中已经赋值
            # if net.network:
            #     adapter['portgroup'] = unquote(net.network)
            # else:
            #     adapter['portgroup'] = ""
            # adapter['connected'] = net.connected
            # 云主机转模板后的网卡信息
            #  (vim.vm.GuestInfo.NicInfo) {
            #    dynamicType = <unset>,
            #    dynamicProperty = (vmodl.DynamicProperty) [],
            #    network = 'VM_126',
            #    ipAddress = (str) [],
            #    macAddress = '00:50:56:9b:9e:ab',
            #    connected = false,
            #    deviceConfigId = 4000,
            #    dnsConfig = <unset>,
            #    ipConfig = <unset>,
            #    netBIOSConfig = <unset>
            # }
            for ipconfig in net.ipConfig.ipAddress:
                ipaddr = ipconfig.ipAddress
                prefix = ipconfig.prefixLength
                ip_netmask, ip_network, ip_version = get_ip_mask_network_version(
                    ipaddr, prefix)
                if 6 == ip_version:
                    # # 忽略本地链路地址
                    # if ipaddr.startswith('fe80'):
                    #     continue
                    # # 忽略可汇聚全球单播地址
                    # mac_end3 = "".join(adapter.get('mac_addr','').split(':')[-3:])
                    # ipaddr_str = "".join(ipaddr.split(':'))
                    # if ipaddr_str.endswith(mac_end3):
                    #     continue
                    ipv6_gateway = get_ipv6_gateway(iproutes, ip_network, key)
                    adapter['ipv6'].append({'ip': ipaddr, 'prefix': prefix,
                                            'gateway': ipv6_gateway})
                elif 4 == ip_version:
                    ipv4_gateway = get_ipv4_gateway(iproutes, ip_network, key)
                    adapter['ipv4'].append({'ip': ipaddr, 'prefix': prefix,
                                            'netmask': ip_netmask,
                                            'gateway': ipv4_gateway})
                else:
                    pass
    return nics_info


##
def template_info_json(vm_mor):
    """
    Template VM info.
    """
    vm_info = {}
    if not (vm_mor and vm_mor.config):
        # vm creating
        return vm_info

    # vm base info
    base_info = _vm_base_info(vm_mor)
    vm_info.update(base_info)
    # vm config info
    config_info = _vm_summary_config_info(vm_mor)
    vm_info.update(config_info)
    # vm runntime info
    runtime_info = _vm_runtime_info(vm_mor)
    vm_info.update(runtime_info)
    # vm guest info
    guest_info = _vm_guest_info(vm_mor)
    vm_info.update(guest_info)
    # vm disks info
    vm_info['disk'] = get_vm_disks_info(vm_mor)
    # vm nics info
    guest_nets_info = get_vm_nics_info(vm_mor)
    vm_info['network'] = guest_nets_info

    return vm_info


def vm_info_json(vm_mor):
    """
    To json information for a particular virtual machine
    @ vm_mor: vim.VirtualMachine
    """
    vm_info = {}
    if not (vm_mor and vm_mor.config):
        # vm creating
        return vm_info

    # vm base info
    base_info = _vm_base_info(vm_mor)
    vm_info.update(base_info)
    # vm config info
    config_info = _vm_summary_config_info(vm_mor)
    vm_info.update(config_info)
    # vm runntime info
    runtime_info = _vm_runtime_info(vm_mor)
    vm_info.update(runtime_info)
    # vm guest info
    guest_info = _vm_guest_info(vm_mor)
    vm_info.update(guest_info)
    # vm disks info
    vm_info['disk'] = get_vm_disks_info(vm_mor)
    # vm guest network info
    guest_nets_info = get_vm_guest_net_info(vm_mor)
    vm_info['network'] = guest_nets_info

    return vm_info


def vm_guest_info_json(vm_mor):
    vm_info = {}
    if not (vm_mor and vm_mor.config):
        # vm creating
        return vm_info
    # vm base info
    base_info = _vm_base_info(vm_mor)
    vm_info.update(base_info)
    # vm guest info
    guest_info = _vm_guest_info(vm_mor)
    vm_info.update(guest_info)
    
    return vm_info


def vm_disk_info_json(vm_mor):
    """
    """
    vm_info = {}
    if not (vm_mor and vm_mor.config):
        # vm creating
        return vm_info
    # vm base info
    base_info = _vm_base_info(vm_mor)
    vm_info.update(base_info)
    # vm disks info
    vm_info['disk'] = get_vm_disks_info(vm_mor)
    return vm_info


def vm_nic_info_json(vm_mor):
    """
    """
    vm_info = {}
    if not (vm_mor and vm_mor.config):
        # vm creating
        return vm_info
    # vm base info
    base_info = _vm_base_info(vm_mor)
    vm_info.update(base_info)
    # vm nic info
    nics_info = get_vm_nics_info(vm_mor)
    vm_info['network'] = nics_info
    return vm_info


def vm_guest_net_info_json(vm_mor):
    """
    """
    vm_info = {}
    if not (vm_mor and vm_mor.config):
        # vm creating
        return vm_info
    # vm base info
    base_info = _vm_base_info(vm_mor)
    vm_info.update(base_info)
    # vm guest network info
    guest_nets_info = get_vm_guest_net_info(vm_mor)
    vm_info['network'] = guest_nets_info
    return vm_info