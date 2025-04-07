#!/usr/bin/python
# ================================
# (C)2022-2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d utils

from typing import Union, Any, Iterable, Optional
from enum import Enum, auto
import subprocess

import lx
from modo import Vector3, Item, Mesh, Scene, dialogs
from modo.mathutils import math
import modo.constants as c


VERTEX_ZERO_NAME = 'vertex_ZERO'
EMPTY_PTAG = 'Material'
TMPROTLOC_NAME = 'tmplocal_rot_loc'


def get_user_value(name: str) -> Any:
    """gets user value by name

    Args:
        name (str): user value name

    Returns:
        Any: user value
    """
    value = lx.eval('user.value {} ?'.format(name))
    return value


def set_user_value(name: str, value: Any) -> None:
    """sets user value

    Args:
        name (str): user value name
        value (Any): value to set
    """
    lx.eval('user.value {} {{{}}}'.format(name, value))


def is_defined_user_value(name: str) -> bool:
    """checks if user value defined

    Args:
        name (str): user value name

    Returns:
        bool: True if user value existed, False otherwise
    """
    return bool(lx.eval(f'query scriptsysservice userValue.isDefined ? {name}'))


def def_new_user_value(name: str, val_type: str, val_life: str) -> None:
    """defines new user value

    Args:
        name (str): user value name
        val_type (str): user value type
        val_life (str): user value life
    """
    lx.eval(f'user.defNew {name} type:{val_type} life:{val_life}')


def delete_defined_user_value(name: str) -> None:
    """deletes user value by name

    Args:
        name (str): user value name
    """
    lx.eval(f'!user.defDelete {name}')


def parent_items_to(items: Iterable[Item], parent: Optional[Item], index=0, inplace=True):
    """parent items to an parent item at specified index

    Args:
        items (Iterable[Item]): items to be parented
        parent (Item): item to parent
        index (int, optional): parent index. Defaults to 0.
        inplace (bool, optional): parent in place. Defaults to True.
    """
    inplace_num = 1 if inplace else 0
    for item in items:
        if not parent:
            lx.eval(f'item.parent item:{{{item.id}}} parent:{{}} position:{index} inPlace:{inplace_num}')
        else:
            lx.eval(f'item.parent item:{{{item.id}}} parent:{{{parent.id}}} position:{index} inPlace:{inplace_num}')


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
        lx.eval('item.tagAdd DESC')
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
    return lx.eval('item.tag string DESC ?')


def set_description_tag(item: Item, text: str) -> None:
    """set description tag for specified item

    Args:
        item (Item): item for tag addition
        text (str): text for decription tag
    """
    item.select(replace=True)
    lx.eval('item.tagAdd DESC')
    lx.eval('item.tag string DESC "{}"'.format(text))


def get_description_tag(item: Item) -> str:
    """get description tag for specified item

    Args:
        item (Item): item to get tag

    Returns:
        str: tag text
    """
    item.select(replace=True)
    description_tag = lx.eval('item.tag string DESC ?')
    if not description_tag:
        return ''

    return description_tag


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


def get_mesh_bounding_box_size(mesh: Mesh):
    if not mesh:
        return Vector3()
    if not mesh.geometry.polygons:
        return Vector3()

    v1, v2 = map(Vector3, mesh.geometry.boundingBox)
    return v2 - v1


def get_source_of_instance(item: Item) -> Union[None, Item]:
    if item is None:
        return None
    if not item.isAnInstance:
        return item

    try:
        item_source = item.itemGraph('source').forward(0)
    except LookupError:
        print('No source of instance item found for <{}>'.format(item.name))
        return None
    if isinstance(item_source, list):
        item_source = item_source[0]
    if item_source.isAnInstance:
        return get_source_of_instance(item_source)

    return item_source


def replace_file_ext(name='log', ext='.txt'):
    try:
        basename = name.rsplit('.', 1)[0]
    except AttributeError:
        basename = name

    return '{}{}'.format(basename, ext)


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


def item_move(item: Item, amount: Vector3):
    if item is None:
        raise ValueError('No item provided')
    if amount is None:
        raise ValueError('No amount provided')

    lx.eval(f'transform.channel pos.X ?+{amount.x} item:{{{item.id}}}')
    lx.eval(f'transform.channel pos.Y ?+{amount.y} item:{{{item.id}}}')
    lx.eval(f'transform.channel pos.Z ?+{amount.z} item:{{{item.id}}}')


def item_rotate(item: Item, radians: Vector3):
    if item is None:
        raise ValueError('No item provided')
    if radians is None:
        raise ValueError('No amount provided')

    lx.eval(f'transform.channel rot.X ?+{radians.x} item:{{{item.id}}}')
    lx.eval(f'transform.channel rot.Y ?+{radians.y} item:{{{item.id}}}')
    lx.eval(f'transform.channel rot.Z ?+{radians.z} item:{{{item.id}}}')


class Axis(Enum):
    X = auto()
    Y = auto()
    Z = auto()


def item_rotate_local(item: Item, radians: float, axis: Axis):
    if item is None:
        raise ValueError('No item provided')
    if radians is None:
        raise ValueError('No amount provided')
    if axis is None:
        raise ValueError('No axis provided')

    tmploc = Scene().addItem(itype=c.LOCATOR_TYPE, name=TMPROTLOC_NAME)
    item_parent = item.parent
    item_parent_index = get_parent_index(item)
    tmploc.setParent(item)
    set_rotation_order(tmploc, axis)
    parent_items_to([tmploc,], item.parent, item_parent_index)
    parent_items_to([item,], tmploc)
    lx.eval(f'transform.channel rot.{axis.name} ?+{radians} item:{{{tmploc.id}}}')
    parent_items_to([item,], item_parent, item_parent_index)
    Scene().removeItems(tmploc)


def set_rotation_order(item: Item, axis: Axis):
    command = {
        Axis.X: 'xyz',
        Axis.Y: 'yxz',
        Axis.Z: 'zxy',
    }
    lx.eval(f'transform.channel order {command[axis]} item:{{{item.id}}}')


def item_scale(item: Item, amount: Vector3):
    if item is None:
        raise ValueError('No item provided')
    if amount is None:
        raise ValueError('No amount provided')

    lx.eval(f'transform.channel scl.X ?+{amount.x} item:{{{item.id}}}')
    lx.eval(f'transform.channel scl.Y ?+{amount.y} item:{{{item.id}}}')
    lx.eval(f'transform.channel scl.Z ?+{amount.z} item:{{{item.id}}}')


def item_set_position(item: Item, position: Vector3):
    if item is None:
        raise ValueError('No item provided')
    if position is None:
        raise ValueError('No position provided')

    lx.eval(f'transform.channel pos.X {position.x} item:{{{item.id}}}')
    lx.eval(f'transform.channel pos.Y {position.y} item:{{{item.id}}}')
    lx.eval(f'transform.channel pos.Z {position.z} item:{{{item.id}}}')


def item_set_rotation(item: Item, radians: Vector3):
    if item is None:
        raise ValueError('No item provided')
    if radians is None:
        raise ValueError('No rotation provided')

    degrees = Vector3()
    degrees.x = math.degrees(radians.x)
    degrees.y = math.degrees(radians.y)
    degrees.z = math.degrees(radians.z)

    lx.eval(f'transform.channel rot.X {degrees.x} item:{{{item.id}}}')
    lx.eval(f'transform.channel rot.Y {degrees.y} item:{{{item.id}}}')
    lx.eval(f'transform.channel rot.Z {degrees.z} item:{{{item.id}}}')


def item_set_scale(item: Item, scale: Vector3):
    if item is None:
        raise ValueError('No item provided')
    if scale is None:
        raise ValueError('No scale provided')

    lx.eval(f'transform.channel scl.X {scale.x} item:{{{item.id}}}')
    lx.eval(f'transform.channel scl.Y {scale.y} item:{{{item.id}}}')
    lx.eval(f'transform.channel scl.Z {scale.z} item:{{{item.id}}}')


def item_get_position(item: Item) -> Vector3:
    if item is None:
        raise ValueError('No item provided')

    transform = Vector3()
    transform.x = lx.eval(f'transform.channel pos.X ? item:{{{item.id}}}')
    transform.y = lx.eval(f'transform.channel pos.Y ? item:{{{item.id}}}')
    transform.z = lx.eval(f'transform.channel pos.Z ? item:{{{item.id}}}')

    return transform


def item_get_rotation(item: Item) -> Vector3:
    """Return item rotation triple in radians

    Args:
        item (Item): The item to which the rotation channel belongs

    Raises:
        ValueError: If no item provided

    Returns:
        Vector3: rotation values in radians
    """
    if item is None:
        raise ValueError('No item provided')

    transform = Vector3()
    transform.x = lx.eval(f'transform.channel rot.X ? item:{{{item.id}}}')
    transform.y = lx.eval(f'transform.channel rot.Y ? item:{{{item.id}}}')
    transform.z = lx.eval(f'transform.channel rot.Z ? item:{{{item.id}}}')

    return transform


def item_get_scale(item: Item) -> Vector3:
    if item is None:
        raise ValueError('No item provided')

    transform = Vector3()
    transform.x = lx.eval(f'transform.channel scl.X ? item:{{{item.id}}}')
    transform.y = lx.eval(f'transform.channel scl.Y ? item:{{{item.id}}}')
    transform.z = lx.eval(f'transform.channel scl.Z ? item:{{{item.id}}}')

    return transform


def safe_type(item: Item):
    if item not in Scene().groups:
        return item.type
    if item.type == 'assembly':
        return item.type
    if item.type == '':
        return 'group'


def remove_if_exist(item: Item, children):
    if not item:
        return False
    try:
        Scene().item(item.id)
        Scene().removeItems(item, children)
    except LookupError:
        return False

    return True


def is_material_ptyp(ptyp):
    if ptyp == 'Material':
        return True
    if ptyp == '':
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
        title = 'Choose Directory'

    return dialogs.dirBrowse(title=title, path=path)


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


def create_vertex_at_zero(name: str) -> Item:
    vertex_zero_mesh = Scene().addMesh(name)
    vertex_zero_mesh.select(replace=True)
    lx.eval('tool.set prim.makeVertex on 0')
    lx.eval('tool.attr prim.makeVertex cenX 0.0')
    lx.eval('tool.attr prim.makeVertex cenY 0.0')
    lx.eval('tool.attr prim.makeVertex cenZ 0.0')
    lx.eval('tool.apply')
    lx.eval('tool.set prim.makeVertex off 0')
    return vertex_zero_mesh


def replicator_link_prototype(item: Item, replicator: Item) -> None:
    lx.eval(f'item.link particle.proto {{{item.id}}} {{{replicator.id}}} replace:true')


def replicator_link_point_source(item: Item, replicator: Item) -> None:
    lx.eval(f'item.link particle.source {{{item.id}}} {{{replicator.id}}} posT:0 replace:true')


def get_vertex_zero(name: str = VERTEX_ZERO_NAME) -> Item:
    try:
        return Scene().item(name)
    except LookupError:
        return create_vertex_at_zero(name)


def get_parent_index(item: Item) -> int:
    if item is None:
        return 0
    if index := item.parentIndex:
        return index
    if index := item.rootIndex:
        return index
    return 0


def match_pos_rot(item: Item, itemTo: Item):
    lx.eval(f'item.match item pos average:false item:{{{item.id}}} itemTo:{{{itemTo.id}}}')
    lx.eval(f'item.match item rot average:false item:{{{item.id}}} itemTo:{{{itemTo.id}}}')


def match_scl(item: Item, itemTo: Item):
    lx.eval(f'item.match item scl average:false item:{{{item.id}}} itemTo:{{{itemTo.id}}}')


def is_visible(item: Item) -> bool:
    if not is_local_visible(item):
        return False

    parents = item.parents
    if not parents:
        return True

    if any(map(lambda x: is_visible_alloff(x), parents)):
        return False

    return True


def is_local_visible(item: Item) -> bool:
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


def is_visible_default(item: Item) -> bool:
    visible_channel = item.channel('visible')
    if not visible_channel:
        return False

    visible = str(visible_channel.get())

    return visible == 'default'


def is_visible_on(item: Item) -> bool:
    visible_channel = item.channel('visible')
    if not visible_channel:
        return False

    visible = str(visible_channel.get())

    return visible == 'on'


def is_visible_off(item: Item) -> bool:
    visible_channel = item.channel('visible')
    if not visible_channel:
        return False

    visible = str(visible_channel.get())

    return visible == 'off'


def is_visible_alloff(item: Item) -> bool:
    visible_channel = item.channel('visible')
    if not visible_channel:
        return False

    visible = str(visible_channel.get())

    return visible == 'allOff'


class TagSplit():
    def __init__(self, text: str):
        self.text = text

    def split(self, sep: str) -> tuple[str, str]:
        index = self.text.find(sep)

        if index == -1:
            return (self.text, '')

        return (self.text[:index], self.text[index+len(sep):])


def show_in_explorer(path: str):
    subprocess.Popen(f'explorer /select,"{path}"')
