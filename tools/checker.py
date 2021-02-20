# -*- coding:utf-8 -*-

from pyVim import task
from pyVmomi import vim
from pyVmomi import vmodl


class CheckResult:
    """
    兼容性检查结果
    """

    def __init__(self):
        # 状态 warning,error,success
        self.status = "success"
        # 消息
        self.msg = ""

    def keys(self):
        """
        当对实例化对象使用dict(obj)的时候, 会调用这个方法。
        这里定义了字典的键, 其对应的值将以obj['name']的形式取。
        """
        return ('status', 'msg')

    def __getitem__(self, item):
        """
        当使用obj['name']的形式的时候, 将调用这个方法。
        这里返回的结果就是值。
        """
        return getattr(self, item)


class VmChecker():
    """
    兼容性检查.
    """

    def __init__(self, si):
        self.vmProvisioningChecker = si.content.vmProvisioningChecker
        self.vmCompatibilityChecker = si.content.vmCompatibilityChecker

    def query_vmotion_compatibility(self, vm_mor, host_mor):
        """
        """
        pass

    def check_migrate(self, vm_mor, host_mor=None, res_pool_mor=None,
            power_state=None, test_type=None):
        """
        迁移检查.
        vm_mor: vim.VirtualMachine
        host_mor: vim.HostSystem
        res_pool_mor: vim.ResourcePool
        power_state: The power state that the virtual machines must have. If
                     this argument is not set, each virtual machine is
                     evaluated according to its current power state. possible
                     values: poweredOn, poweredOff, suspended
        test_type: The set of tests to run. If this argument is not set, all
                   tests will be run. possible values: hostTests,
                   resourcePoolTests, datastoreTests, sourceTests, networkTests
        """
        check_result = CheckResult()
        try:
            task_mor = self.vmProvisioningChecker.CheckMigrate(vm_mor,
                                                               host_mor,
                                                               res_pool_mor,
                                                               power_state,
                                                               test_type)
            task_state = task.WaitForTask(task_mor)
            if task_state == 'success':
                for result in task_mor.info.result:
                    if result.warning:
                        check_result.status = 'warning'
                        check_result.msg = result.warning[0].msg
                    elif result.error:
                        check_result.status = 'error'
                        check_result.msg = result.error[0].msg
                    else:
                        check_result.status = 'success'
                        check_result.msg = "兼容性检查成功"
            else:
                check_result.status = 'error'
                check_result.msg = "兼容性检查失败"
        except vim.fault.InvalidState as ex:
            check_result.status = 'error'
            check_result.msg = "InvalidState: %s" % str(ex)
        except vmodl.fault.NotSupported as ex:
            check_result.status = 'error'
            check_result.msg = "NotSupported: %s" % str(ex)
        except vmodl.fault.InvalidArgument as ex:
            check_result.status = 'error'
            check_result.msg = "InvalidArgument: %s" % str(ex)
        return check_result

    def check_relocate(self, vm_mor, relocate_spec, test_type=None):
        """
        放置检查.
        vm_mor: vim.VirtualMachine
        relocate_spec: vim.vm.RelocateSpec
        test_type: The set of tests to run. If this argument is not set, all
                   tests will be run. possible values: hostTests,
                   resourcePoolTests, datastoreTests, sourceTests, networkTests
        """
        check_result = CheckResult()
        try:
            task_mor = self.vmProvisioningChecker.CheckRelocate(vm_mor,
                                                                relocate_spec,
                                                                test_type)
            task_state = task.WaitForTask(task_mor)
            if task_state == 'success':
                for result in task_mor.info.result:
                    if result.warning:
                        check_result.status = 'warning'
                        check_result.msg = result.warning[0].msg
                    elif result.error:
                        check_result.status = 'error'
                        check_result.msg = result.error[0].msg
                    else:
                        check_result.status = 'success'
                        check_result.msg = "兼容性检查成功"
            else:
                check_result.status = 'error'
                check_result.msg = "兼容性检查失败"
        except vim.fault.InvalidState as ex:
            check_result.status = 'error'
            check_result.msg = "InvalidState: %s" % str(ex)
        except vmodl.fault.NotSupported as ex:
            check_result.status = 'error'
            check_result.msg = "NotSupported: %s" % str(ex)
        except vmodl.fault.InvalidArgument as ex:
            check_result.status = 'error'
            check_result.msg = "InvalidArgument: %s" % str(ex)
        return check_result

    def check_compatibility(self, vm_mor, host_mor=None, res_pool_mor=None, test_type=None):
        """
        容量检查
        vm_mor: vim.VirtualMachine
        host_mor: vim.HostSystem
        res_pool_mor: vim.ResourcePool
        test_type: The set of tests to run. If this argument is not set, all
                   tests will be run. possible values: hostTests,
                   resourcePoolTests, datastoreTests, sourceTests, networkTests
        """
        check_result = CheckResult()
        try:
            task_mor = self.vmCompatibilityChecker.\
                    CheckCompatibility(vm_mor,
                                       host_mor,
                                       res_pool_mor,
                                       test_type)
            task_state = task.WaitForTask(task_mor)
            if task_state == 'success':
                for result in task_mor.info.result:
                    if result.warning:
                        check_result.status = 'warning'
                        check_result.msg = result.warning[0].msg
                    elif result.error:
                        check_result.status = 'error'
                        check_result.msg = result.error[0].msg
                    else:
                        check_result.status = 'success'
                        check_result.msg = "兼容性检查成功"
            else:
                check_result.status = 'error'
                check_result.msg = "兼容性检查失败"
        except vim.fault.InvalidState as ex:
            check_result.status = 'error'
            check_result.msg = "InvalidState: %s" % str(ex)
        except vim.fault.NoActiveHostInCluster as ex:
            check_result.status = 'error'
            check_result.msg = "NoActiveHostInCluster: %s" % str(ex)
        except vmodl.fault.InvalidArgument as ex:
            check_result.status = 'error'
            check_result.msg = "InvalidArgument: %s" % str(ex)
        return check_result
