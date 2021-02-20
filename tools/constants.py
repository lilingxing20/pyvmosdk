# -*- coding:utf-8 -*-

from pyVmomi import vim


MIN_VC_VERSION = '5.5.0'

DISK_TYPE_THIN = 'thin'
DISK_TYPE_PREALLOCATED = 'preallocated'
DISK_TYPE_EAGER_ZEROED_THICK = 'eagerZeroedThick'

NIC_DEVICE_SPCE = {
    'E1000': vim.vm.device.VirtualE1000(),
    'E1000E': vim.vm.device.VirtualE1000e(),
    'VMXNET3': vim.vm.device.VirtualVmxnet3(),
}

SCSI_CONTROLLER_SPEC = {
    'BusLogic': vim.vm.device.VirtualBusLogicController(),
    'LsiLogic': vim.vm.device.VirtualLsiLogicController(),
    'LsiLogicSAS': vim.vm.device.VirtualLsiLogicSASController(),
    'ParaVirtual': vim.vm.device.ParaVirtualSCSIController(),
}

SCSI_CONTROLLER_NAME = {
    'vim.vm.device.VirtualBusLogicController': 'BusLogic',
    'vim.vm.device.VirtualLsiLogicController': 'LsiLogic',
    'vim.vm.device.VirtualLsiLogicSASController': 'LsiLogicSAS',
    'vim.vm.device.ParaVirtualSCSIController': 'ParaVirtual',
}


LINUX_OS_TYPES = set([
    'centos64Guest',
    'centosGuest',
    'coreos64Guest',
    'debian4_64Guest',
    'debian4Guest',
    'debian5_64Guest',
    'debian5Guest',
    'debian6_64Guest',
    'debian6Guest',
    'debian7_64Guest',
    'debian7Guest',
    'debian8_64Guest',
    'debian8Guest',
    'fedora64Guest',
    'fedoraGuest',
    'freebsd64Guest',
    'freebsdGuest',
    'opensuse64Guest',
    'opensuseGuest',
    'oracleLinux64Guest',
    'oracleLinuxGuest',
    'other24xLinux64Guest',
    'other24xLinuxGuest',
    'other26xLinux64Guest',
    'other26xLinuxGuest',
    'other3xLinux64Guest',
    'other3xLinuxGuest',
    'otherGuest',
    'otherGuest64',
    'otherLinux64Guest',
    'otherLinuxGuest',
    'redhatGuest',
    'rhel2Guest',
    'rhel3_64Guest',
    'rhel3Guest',
    'rhel4_64Guest',
    'rhel4Guest',
    'rhel5_64Guest',
    'rhel5Guest',
    'rhel6_64Guest',
    'rhel6Guest',
    'rhel7_64Guest',
    'rhel7Guest',
    'sles10_64Guest',
    'sles10Guest',
    'sles11_64Guest',
    'sles11Guest',
    'sles12_64Guest',
    'sles12Guest',
    'sles64Guest',
    'slesGuest',
    'suse64Guest',
    'suseGuest',
    'ubuntu64Guest',
    'ubuntuGuest',
])

WIN_OS_TYPES = set([
    'win2000AdvServGuest',
    'win2000ProGuest',
    'win2000ServGuest',
    'win31Guest',
    'win95Guest',
    'win98Guest',
    'windows7_64Guest',
    'windows7Guest',
    'windows7Server64Guest',
    'windows8_64Guest',
    'windows8Guest',
    'windows8Server64Guest',
    'windows9_64Guest',
    'windows9Guest',
    'windows9Server64Guest',
    'windowsHyperVGuest',
    'winLonghorn64Guest',
    'winLonghornGuest',
    'winMeGuest',
    'winNetBusinessGuest',
    'winNetDatacenter64Guest',
    'winNetDatacenterGuest',
    'winNetEnterprise64Guest',
    'winNetEnterpriseGuest',
    'winNetStandard64Guest',
    'winNetStandardGuest',
    'winNetWebGuest',
    'winNTGuest',
    'winVista64Guest',
    'winVistaGuest',
    'winXPHomeGuest',
    'winXPPro64Guest',
    'winXPProGuest',
])


# task type
CLONE_VM = "clone_vm"
VM_CREATE_SNAPSHOT = "vm_create_snapshot"
VM_CURRENT_SNAPSHOT = "vm_current_snapshot"
VM_ATTACH_DISK = "vm_attach_disk"
VM_EDIT_DISK = "vm_edit_disk"
VM_ADD_NIC = "vm_add_nic"
VM_EDIT_NIC = "vm_add_nic"
VM_RESIZE = "vm_resize"