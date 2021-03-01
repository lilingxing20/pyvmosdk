# -*- coding:utf-8 -*-

"""
数据返回属性实体
"""


class DataResult(object):
    """数据返回属性：
        $ DataResult().status   # True/False
        $ DataResult().message  # ""
        $ DataResult().data     # {}
        $ DataResult().task_key # ""
    字典使用方式：
        $ dict(DataResult())
    """

    def __init__(self):
        # 状态 True/False
        self.status = True

        # 消息
        self.message = ""

        # 数据
        self.data = None

        # 任务Key
        self.task_key = ""

    def keys(self):
        """
        当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取
        """
        return ('status', 'message', 'data', 'task_key')

    def __getitem__(self, item):
        """
        当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值
        """
        return getattr(self, item)