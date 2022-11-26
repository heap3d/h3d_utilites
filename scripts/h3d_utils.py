#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d utils

import lx
import modo
import modo.mathutils as mmu


# obsolete class. leaved for compatibility
class H3dUtils:
    @staticmethod
    def get_user_value(name):
        value = lx.eval('user.value {} ?'.format(name))
        return value

    @staticmethod
    def set_user_value(name, value):
        lx.eval('user.value {} {{{}}}'.format(name, value))

    @staticmethod
    def parent_items_to(items, parent):
        # clear selection
        modo.Scene().deselect()
        # select items
        for item in items:
            item.select()
        # select parent item
        parent.select()
        # parent items to parent item
        lx.eval('item.parent inPlace:1')

    @staticmethod
    def set_mesh_debug_info(mesh, info_str, debug_mode=False):
        if not mesh:
            return
        if debug_mode:
            mesh.select(replace=True)
            lx.eval('item.tagAdd DESC')
            lx.eval('item.tag string DESC "{}"'.format(info_str))

    @staticmethod
    def get_mesh_debug_info(mesh):
        if not mesh:
            return None

        mesh.select(replace=True)
        return lx.eval('item.tag string DESC ?')

    @staticmethod
    def get_full_mesh_area(mesh):
        if not mesh:
            return None
        if mesh.type != 'mesh':
            return 0.0

        full_area = sum([poly.area for poly in mesh.geometry.polygons])
        return full_area

    @staticmethod
    def merge_two_meshes(mesh1, mesh2):
        if not mesh1:
            return
        if not mesh2:
            return
        lx.eval('select.type item')
        mesh1.select(replace=True)
        mesh2.select()
        lx.eval('layer.mergeMeshes true')

    @staticmethod
    def get_mesh_bounding_box_size(mesh):
        if not mesh:
            return mmu.Vector3()
        if not mesh.geometry.polygons:
            return mmu.Vector3()
        v1, v2 = map(mmu.Vector3, mesh.geometry.boundingBox)
        return v2 - v1

    @staticmethod
    def get_source_of_instance(item):
        if item is None:
            return None
        if not item.isAnInstance:
            return item

        try:
            item_source = item.itemGraph('source').forward(0)
        except LookupError:
            print('No source of instance item found for <{}>'.format(item.name))
            return None
        if item_source.isAnInstance:
            return H3dUtils.get_source_of_instance(item_source)
        else:
            return item_source

    @staticmethod
    def replace_file_ext(name='log', ext='.txt'):
        basename = name.rsplit('.', 1)[0]
        return '{}{}'.format(basename, ext)

    @staticmethod
    def type_int_to_str(type_int):
        return lx.service.Scene().ItemTypeName(type_int)

    @staticmethod
    def type_str_to_int(type_str):
        return lx.service.Scene().ItemTypeLookup(type_str)


def get_user_value(name):
    value = lx.eval('user.value {} ?'.format(name))
    return value


def set_user_value(name, value):
    lx.eval('user.value {} {{{}}}'.format(name, value))


def parent_items_to(items, parent):
    # clear selection
    modo.Scene().deselect()
    # select items
    for item in items:
        item.select()
    # select parent item
    parent.select()
    # parent items to parent item
    lx.eval('item.parent inPlace:1')


def set_mesh_debug_info(mesh, info_str, debug_mode=False):
    """saving info_str to mesh description tag"""
    if not mesh:
        return
    if debug_mode:
        mesh.select(replace=True)
        lx.eval('item.tagAdd DESC')
        lx.eval('item.tag string DESC "{}"'.format(info_str))


def get_mesh_debug_info(mesh):
    """read string from mesh description tag"""
    if not mesh:
        return None

    mesh.select(replace=True)
    return lx.eval('item.tag string DESC ?')


def get_full_mesh_area(mesh):
    if not mesh:
        return None
    if mesh.type != 'mesh':
        return 0.0

    full_area = sum([poly.area for poly in mesh.geometry.polygons])
    return full_area


def merge_two_meshes(mesh1, mesh2):
    if not mesh1:
        return
    if not mesh2:
        return
    lx.eval('select.type item')
    mesh1.select(replace=True)
    mesh2.select()
    lx.eval('layer.mergeMeshes true')


def get_mesh_bounding_box_size(mesh):
    if not mesh:
        return mmu.Vector3()
    if not mesh.geometry.polygons:
        return mmu.Vector3()
    v1, v2 = map(mmu.Vector3, mesh.geometry.boundingBox)
    return v2 - v1


def get_source_of_instance(item):
    if item is None:
        return None
    if not item.isAnInstance:
        return item

    try:
        item_source = item.itemGraph('source').forward(0)
    except LookupError:
        print('No source of instance item found for <{}>'.format(item.name))
        return None
    if item_source.isAnInstance:
        return H3dUtils.get_source_of_instance(item_source)
    else:
        return item_source


def replace_file_ext(name='log', ext='.txt'):
    basename = name.rsplit('.', 1)[0]
    return '{}{}'.format(basename, ext)


def itype_str(type_int):
    """convert int modo item type to str type.
    example: c.MESH_TYPE to 'mesh' """
    return lx.service.Scene().ItemTypeName(type_int)


def itype_int(type_str):
    """convert str modo item type to int type.
    example: 'mesh' to c.MESH_TYPE"""
    return lx.service.Scene().ItemTypeLookup(type_str)


def item_rotate(item, rads):
    if not item:
        print('item_rotate(): not item.')
        return
    if not rads:
        print('item_rotate(): not rads.')
        return
    if len(rads) != 3:
        print('item_rotate(): len(rads) != 3')
        return
    # get current rotation
    rotation = mmu.Vector3(item.rotation.get())
    # update item rotation
    rotation_upd = (rotation.x + rads.x, rotation.y + rads.y, rotation.z + rads.z)
    # set item rotation
    item.rotation.set(rotation_upd)
