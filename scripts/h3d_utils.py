#!/usr/bin/python
# ================================
# (C)2022-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d utils

from typing import Union, Any, Iterable

import lx
import modo
import modo.mathutils as mmu


VERTEX_ZERO_NAME = 'vertex_ZERO'
EMPTY_PTAG = 'Material'


def get_user_value(name: str) -> Any:
    """gets user value by name

    Args:
        name (str): user value name

    Returns:
        Any: user value
    """
    value = lx.eval("user.value {} ?".format(name))
    return value


def set_user_value(name: str, value: Any) -> None:
    """sets user value

    Args:
        name (str): user value name
        value (Any): value to set
    """
    lx.eval("user.value {} {{{}}}".format(name, value))


def is_defined_user_value(name: str) -> bool:
    """checks if user value defined

    Args:
        name (str): user value name

    Returns:
        bool: True if user value existed, False otherwise
    """
    return bool(lx.eval(f"query scriptsysservice userValue.isDefined ? {name}"))


def def_new_user_value(name: str, val_type: str, val_life: str) -> None:
    """defines new user value

    Args:
        name (str): user value name
        val_type (str): user value type
        val_life (str): user value life
    """
    lx.eval(f"user.defNew {name} type:{val_type} life:{val_life}")


def delete_defined_user_value(name: str) -> None:
    """deletes user value by name

    Args:
        name (str): user value name
    """
    lx.eval(f"!user.defDelete {name}")


def parent_items_to(items: Iterable[modo.Item], parent: modo.Item, index=0):
    """parent items to an parent item at specified index

    Args:
        items (Iterable[modo.Item]): items to be parented
        parent (modo.Item): item to parent
        index (int, optional): parent index. Defaults to 0.
    """
    for item in items:
        if not parent:
            lx.eval(f"item.parent item:{{{item.id}}} parent:{{}} position:{index} inPlace:1")
        else:
            lx.eval(f"item.parent item:{{{item.id}}} parent:{{{parent.id}}} position:{index} inPlace:1")


def set_mesh_debug_info(mesh, info_str, debug_mode=False):
    """saving info_str to mesh description tag

    Args:
        mesh (Item): mesh item to store a tag
        info_str (str): tag string
        debug_mode (bool, optional): set tag if debug_mode enabled. Defaults to False.
    """
    if not mesh:
        return
    if debug_mode:
        mesh.select(replace=True)
        lx.eval("item.tagAdd DESC")
        lx.eval('item.tag string DESC "{}"'.format(info_str))


def get_mesh_debug_info(mesh):
    """read string from mesh description tag

    Args:
        mesh (_type_): mesh to get tag string

    Returns:
        str: tag string
    """
    if not mesh:
        return None

    mesh.select(replace=True)
    return lx.eval("item.tag string DESC ?")


def set_description_tag(item: modo.Item, text: str) -> None:
    """set description tag for specified item

    Args:
        item (modo.Item): item for tag addition
        text (str): text for decription tag
    """
    item.select(replace=True)
    lx.eval("item.tagAdd DESC")
    lx.eval('item.tag string DESC "{}"'.format(text))


def get_description_tag(item: modo.Item) -> str:
    """get description tag for specified item

    Args:
        item (modo.Item): item to get tag

    Returns:
        str: tag text
    """
    item.select(replace=True)
    description_tag = lx.eval("item.tag string DESC ?")
    if not description_tag:
        return ""

    return description_tag


def get_full_mesh_area(mesh):
    if not mesh:
        return None
    if mesh.type != "mesh":
        return 0.0

    full_area = sum([poly.area for poly in mesh.geometry.polygons])
    return full_area


def merge_two_meshes(mesh1, mesh2):
    if not mesh1:
        return
    if not mesh2:
        return

    lx.eval("select.type item")
    mesh1.select(replace=True)
    mesh2.select()
    lx.eval("layer.mergeMeshes true")


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
        item_source = item.itemGraph("source").forward(0)
    except LookupError:
        print("No source of instance item found for <{}>".format(item.name))
        return None
    if item_source.isAnInstance:
        return get_source_of_instance(item_source)

    return item_source


def replace_file_ext(name="log", ext=".txt"):
    try:
        basename = name.rsplit(".", 1)[0]
    except AttributeError:
        basename = name

    return "{}{}".format(basename, ext)


def itype_str(type_int: Union[int, None]) -> str:
    """convert int modo item type to str type.
    example: c.MESH_TYPE to 'mesh'"""
    if type_int is None:
        raise TypeError

    if isinstance(type_int, str):
        return str(type_int)

    str_type = lx.service.Scene().ItemTypeName(type_int)
    if str_type is None:
        raise TypeError

    return str_type


def itype_int(type_str: Union[str, None]) -> int:
    """convert str modo item type to int type.
    example: 'mesh' to c.MESH_TYPE"""
    if type_str is None:
        raise TypeError

    int_type = lx.service.Scene().ItemTypeLookup(type_str)
    if int_type is None:
        raise TypeError

    return int_type


def item_rotate(item, rads):
    if not item:
        print("item_rotate(): not item.")
        return
    if not rads:
        print("item_rotate(): not rads.")
        return
    if len(rads) != 3:
        print("item_rotate(): len(rads) != 3")
        return

    # get current rotation
    rotation = mmu.Vector3(item.rotation.get())
    # update item rotation
    rotation_upd = (rotation.x + rads.x, rotation.y + rads.y, rotation.z + rads.z)
    # set item rotation
    item.rotation.set(rotation_upd)


def safe_type(item):
    if item not in modo.Scene().groups:
        return item.type
    if item.type == "assembly":
        return item.type
    if item.type == "":
        return "group"


def remove_if_exist(item, children):
    if not item:
        return False
    try:
        modo.Scene().item(item.id)
        modo.Scene().removeItems(item, children)
    except LookupError:
        return False

    return True


def is_material_ptyp(ptyp):
    if ptyp == "Material":
        return True
    if ptyp == "":
        return True

    return False


def get_ptag_type(mask_item):
    ptyp = mask_item.channel('ptyp').get()
    if not ptyp:
        return EMPTY_PTAG
    return ptyp


def get_ptag(mask_item):
    ptag = mask_item.channel('ptag').get()
    return ptag


def get_item_mask(mask_item):
    mask_item.select(True)
    item_mask = lx.eval('mask.setMesh ?')
    return item_mask


def get_directory(
    title: Union[str, None], path: Union[str, None] = None
) -> Union[str, None]:
    if not title:
        title = "Choose Directory"

    return modo.dialogs.dirBrowse(title=title, path=path)


def is_preset_browser_opened() -> bool:
    return bool(lx.eval('layout.createOrClose PresetBrowser presetBrowserPalette ?'))


def open_preset_browser():
    lx.eval(
        'layout.createOrClose PresetBrowser presetBrowserPalette true Presets '
        'width:800 height:600 persistent:true style:palette'
    )


def close_preset_browser():
    lx.eval(
        'layout.createOrClose PresetBrowser presetBrowserPalette false Presets width:800 height:600 '
        'persistent:true style:palette'
    )


def display_preset_browser(enable: bool):
    if enable:
        open_preset_browser()
    else:
        close_preset_browser()


def switch_preset_browser():
    display_preset_browser(not is_preset_browser_opened())


def create_vertex_at_zero(name: str) -> modo.Item:
    vertex_zero_mesh = modo.Scene().addMesh(name)
    vertex_zero_mesh.select(replace=True)
    lx.eval('tool.set prim.makeVertex on 0')
    lx.eval('tool.attr prim.makeVertex cenX 0.0')
    lx.eval('tool.attr prim.makeVertex cenY 0.0')
    lx.eval('tool.attr prim.makeVertex cenZ 0.0')
    lx.eval('tool.apply')
    lx.eval('tool.set prim.makeVertex off 0')
    return vertex_zero_mesh


def replicator_link_prototype(item: modo.Item, replicator: modo.Item) -> None:
    lx.eval(f'item.link particle.proto {{{item.id}}} {{{replicator.id}}} replace:true')


def replicator_link_point_source(item: modo.Item, replicator: modo.Item) -> None:
    lx.eval(f'item.link particle.source {{{item.id}}} {{{replicator.id}}} posT:0 replace:true')


def get_vertex_zero(name: str = VERTEX_ZERO_NAME) -> modo.Item:
    try:
        return modo.Scene().item(name)
    except LookupError:
        return create_vertex_at_zero(name)


def get_parent_index(item: modo.Item) -> int:
    if index := item.parentIndex:
        return index
    if index := item.rootIndex:
        return index
    return 0


def match_pos_rot(item: modo.Item, itemTo: modo.Item):
    lx.eval(f'item.match item pos average:false item:{{{item.id}}} itemTo:{{{itemTo.id}}}')
    lx.eval(f'item.match item rot average:false item:{{{item.id}}} itemTo:{{{itemTo.id}}}')


def match_scl(item: modo.Item, itemTo: modo.Item):
    lx.eval(f'item.match item scl average:false item:{{{item.id}}} itemTo:{{{itemTo.id}}}')


def is_visible(item: modo.Item) -> bool:
    if not is_local_visible(item):
        return False

    parents = item.parents
    if not parents:
        return True

    if any(map(lambda x: is_visible_alloff(x), parents)):
        return False

    return True


def is_local_visible(item: modo.Item) -> bool:
    visible_channel = item.channel('visible')
    if not visible_channel:
        return False

    visible = str(visible_channel.get())
    visible_values = {
        'default': True,
        'on': True,
        'off': False,
        'allOff': False,
    }

    result = visible_values.get(visible, False)
    return result


def is_visible_default(item: modo.Item) -> bool:
    visible_channel = item.channel('visible')
    if not visible_channel:
        return False

    visible = str(visible_channel.get())

    return visible == 'default'


def is_visible_on(item: modo.Item) -> bool:
    visible_channel = item.channel('visible')
    if not visible_channel:
        return False

    visible = str(visible_channel.get())

    return visible == 'on'


def is_visible_off(item: modo.Item) -> bool:
    visible_channel = item.channel('visible')
    if not visible_channel:
        return False

    visible = str(visible_channel.get())

    return visible == 'off'


def is_visible_alloff(item: modo.Item) -> bool:
    visible_channel = item.channel('visible')
    if not visible_channel:
        return False

    visible = str(visible_channel.get())

    return visible == 'allOff'
