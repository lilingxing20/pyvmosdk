# -*- coding:utf-8 -*-

"""
Virtual machine snapshot manipulation tool functions.
"""

from __future__ import absolute_import


def snaptree_obj_to_json(snaptree_obj):
    """
    Snapshot tree object to json
    """
    snapshot_info = {}
    try:
        snapshot_info['moid'] = snaptree_obj.snapshot._moId
        snapshot_info['vm_moid'] = snaptree_obj.vm._moId
        snapshot_info['name'] = snaptree_obj.name
        snapshot_info['description'] = snaptree_obj.description
        snapshot_info['id'] = snaptree_obj.id
        snapshot_info['create_time'] = snaptree_obj.createTime
        snapshot_info['state'] = snaptree_obj.state
        snapshot_info['quiesced'] = snaptree_obj.quiesced
        snapshot_info['replay_supported'] = snaptree_obj.replaySupported
    except Exception as ex:
        raise Exception("snapshot tree object to json error: %s" % str(ex))
    return snapshot_info


def get_vm_snapshot_by_moid(snapshots, snap_moid):
    """
    Get snapshot tree objects recursively.
    """
    snaptree_obj = None
    for s in snapshots:
        if s.snapshot._moId == snap_moid:
            snaptree_obj = s
            break
        else:
            snaptree_obj = get_vm_snapshot_by_moid(s.childSnapshotList,
                                                   snap_moid)
    return snaptree_obj


def get_vm_snapshot_mor_by_moid(vm_mor, snap_moid):
    """
    Get snapshot mor.
    """
    try:
        snaptree_obj = get_vm_snapshot_by_moid(vm_mor.snapshot.rootSnapshotList,
                                               snap_moid)
        return snaptree_obj.snapshot
    except Exception as ex:
        raise Exception("get vm snapshot mor error: %s" % str(ex))


def all_snapshot_obj_to_json(snapshots):
    """
    All snapshot tree objects to json recursively.
    """
    snapshots_info = []
    for s in snapshots:
        snapshot_info = snaptree_obj_to_json(s)
        snapshots_info.append(snapshot_info)
        child_snapshots_info = all_snapshot_obj_to_json(s.childSnapshotList)
        snapshot_info["child_snapshots"] = child_snapshots_info
    return snapshots_info


def get_vm_all_snapshot_info(vm_mor):
    """
    Get all snapshot info recursively.
    """
    try:
        return all_snapshot_obj_to_json(vm_mor.snapshot.rootSnapshotList)
    except Exception as ex:
        raise Exception("get vm all snapshot info error: %s" % str(ex))