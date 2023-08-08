import bpy
from bpy.types import PropertyGroup, Context, WindowManager as WM, Brush as BlBrush, Texture as BlTexture, ToolSettings
from bpy.props import StringProperty, PointerProperty, EnumProperty, IntProperty, CollectionProperty, BoolProperty, FloatVectorProperty
from gpu.types import GPUTexture

from os.path import basename, exists, isfile
from uuid import uuid4
from collections import defaultdict
from shutil import copyfile

from .paths import Paths
from .icons import get_preview, get_gputex, create_preview_from_filepath, clear_icon

from . import types as bm_types

AD = bm_types.AddonData
ADM = bm_types.AddonDataByMode


IconPath = Paths.Icons


lib_items_cache: dict[str, set[str]] = {}
cached_indices = {}


load_lib = None
write_lib = None


get_brush_names_by_ctx_mode = {
    'sculpt': ('Blob', 'Boundary', 'Clay', 'Clay Strips', 'Clay Thumb', 'Cloth', 'Crease', 'Draw Face Sets', 'Draw Sharp', 'Elastic Deform', 'Fill/Deepen', 'Flatten/Contrast', 'Grab', 'Inflate/Deflate', 'Layer', 'Mask', 'Multi-plane Scrape', 'Multires Displacement Eraser', 'Multires Displacement Smear', 'Nudge', 'Paint', 'Pinch/Magnify', 'Pose', 'Rotate', 'Scrape/Peaks', 'SculptDraw', 'Simplify', 'Slide Relax', 'Smooth', 'Snake Hook', 'Thumb'),
    'texture_paint': (
        'TexDraw',

        'Soften',
        'Smear',

        'Clone',

        'Fill',

        'Mask'),
    'gpencil_paint': (
        'Airbrush',
        'Ink Pen',
        'Ink Pen Rough',
        'Marker Bold',
        'Marker Chisel',
        'Pen',
        'Pencil',
        'Pencil Soft',

        'Fill Area',

        'Eraser Hard',
        'Eraser Point',
        'Eraser Soft',
        'Eraser Stroke',

        'Tint',)
}


# ----------------------------------------------------------------


def get_ts(context: bpy.types.Context) -> BlBrush:
    mode = context.mode
    if mode == 'PAINT_GPENCIL':
        mode = 'GPENCIL_PAINT'
    mode = mode.lower()

    return getattr(context.tool_settings, mode)

def get_ts_brush() -> BlBrush:
    return get_ts(bpy.context).brush

def get_ts_brush_texture_slot() -> bpy.types.BrushTextureSlot:
    if bl_brush := get_ts_brush():
        return bl_brush.texture_slot
    return None

def set_ts_brush(context: bpy.types.Context, brush: BlBrush) -> None:
    get_ts(context).brush = brush

def set_ts_texture(context: bpy.types.Context, texture: BlTexture) -> None:
    get_ts(context).brush.texture_slot.texture = texture


# ----------------------------------------------------------------


def get_item_at_index(list, index: int):
    if index < 0 or index >= len(list):
        return None
    return list[index]

def get_item_by_uuid(list, uuid: str):
    for item in list:
        if item.uuid == uuid:
            return item
    return None

def get_item(list, item: str | int):
    if isinstance(item, int):
        return get_item_at_index(list, item)
    if isinstance(item, str):
        return get_item_by_uuid(list, item)
    raise TypeError("Unexpected item type. Must be an integer (index) or a string (UUID)")

def get_item_index(list, uuid_or_ref: str | object) -> int | None:
    if isinstance(uuid_or_ref, str):
        for index, item in enumerate(list):
            if item.uuid == uuid_or_ref:
                return index
    elif isinstance(uuid_or_ref, object):
        for index, item in enumerate(list):
            if item == uuid_or_ref:
                return index
    else:
        raise TypeError("Unexpected item type. Must be an integer (index) or a string (UUID)")


def remove_item(list: list, item: int | str):
    if isinstance(item, int):
        if item < 0 or item >= len(list):
            return
            raise IndexError("Index out of range, trying to remove item at index %d from a list of %d elements" % (item, len(list)))
        item_data = list[item]
        if hasattr(item_data, 'clear_icon'):
            item_data.clear_icon()
        list.remove(item)
    elif isinstance(item, str):
        for idx, _item in enumerate(list):
            if _item.uuid == item:
                return remove_item(idx)
    elif type(item) == type(list[0]):
        for idx, _item in enumerate(list):
            if _item == item:
                return remove_item(idx)
    else:
        raise TypeError("Unexpected item type. Must be an integer (index) or a string (UUID)")


# ----------------------------------------------------------------


class IconHolder:
    @property
    def icon_path(self) -> IconPath: pass
    @property
    def icon_filepath(self) -> str: return self.icon_path(self.uuid + '.png')
    @property
    def icon_id(self) -> int: return get_preview(self.uuid, self.icon_filepath)
    @property
    def icon_gputex(self) -> GPUTexture: return get_gputex(self.uuid, self.icon_filepath)

    def asign_icon(self, filepath: str) -> None:
        create_preview_from_filepath(self.uuid, filepath, self.icon_filepath)

    def clear_icon(self) -> None:
        clear_icon(self.uuid, self.icon_filepath)


class UUUIDHolder:
    uuid: StringProperty()

    def generate_uuid(self) -> None:
        self.uuid = uuid4().hex


class CollectionItem(UUUIDHolder, IconHolder):
    name : StringProperty()


# ----------------------------------------------------------------


class LibraryBrush_Collection(CollectionItem, PropertyGroup):
    @property
    def icon_path(self) -> str:
        return IconPath.BRUSH

class LibraryTexture_Collection(CollectionItem, PropertyGroup):
    @property
    def icon_path(self) -> str:
        return IconPath.TEXTURE


class Library_Collection(UUUIDHolder, PropertyGroup):
    def update_filepath(self, context: Context):
        self.name = basename(self.filepath)[:-6].replace('_', ' ').title()

    filepath : StringProperty(update=update_filepath)
    name : StringProperty()
    brushes: CollectionProperty(type=LibraryBrush_Collection)
    textures: CollectionProperty(type=LibraryTexture_Collection)

    @property
    def is_valid(self) -> bool:
        return exists(self.filepath) and isfile(self.filepath)

    @property
    def brushes_ids(self) -> set[str]:
        if ids := lib_items_cache.get(self.uuid, None):
            return ids
        ids = {brush.uuid for brush in self.brushes}
        lib_items_cache[self.uuid] = ids
        return ids

    def add_brush(self, brush_data: 'Brush_Collection') -> LibraryBrush_Collection:
        brush_item = self.brushes.add()
        brush_item.uuid = brush_data.uuid
        return brush_item

    def add_texture(self, texture_data: 'Texture_Collection') -> LibraryTexture_Collection:
        texture_item = self.textures.add()
        texture_item.uuid = texture_data.uuid
        return texture_item

    def get_brushes(self, addon_data: 'AddonDataByMode') -> list['Brush_Collection']:
        get_item = addon_data.get_brush
        return [get_item(item.uuid) for item in self.brushes]

    def get_textures(self, addon_data: 'AddonDataByMode') -> list['Texture_Collection']:
        get_item = addon_data.get_texture
        return [get_item(item.uuid) for item in self.textures]


# ----------------------------------------------------------------


class Item(UUUIDHolder, IconHolder):
    name: StringProperty()
    type: StringProperty()
    selected: BoolProperty(name="Select Item")

    def load(self) -> None:
        raise NotImplementedError()

    def save(self) -> None:
        raise NotImplementedError()


class Texture_Collection(Item, PropertyGroup):
    format: StringProperty()

    @property
    def icon_path(self) -> str:
        return IconPath.TEXTURE

    @property
    def lib_path(self) -> str:
        return Paths.Data.TEXTURE

    @property
    def bl_texture(self) -> BlTexture or None:
        return bpy.data.textures.get(self.uuid, None)
    
    def select(self, context: Context) -> None:
        bl_texture = self.bl_texture
        if bl_texture is None:
            self.load(link=False)
            bl_texture = self.bl_texture
        set_ts_texture(context, bl_texture)

    def load(self, link: bool = False) -> None:
        global load_lib
        tex_libpath = self.lib_path(self.uuid + '.blend', as_path=False)
        with load_lib(tex_libpath, link=link, relative=False, assets_only=False) as (data_from, data_to):
            data_to.textures = [self.uuid]
            data_to.images = data_from.images

    def save(self) -> None:
        global write_lib
        tex_libpath = self.lib_path(self.uuid + '.blend', as_path=False)
        write_lib(tex_libpath, {self.id_data}, fake_user=True, compress=True)


class Brush_Collection(Item, PropertyGroup):
    def update_texture(self, context: Context):
        self.texture_uuid = '' if self.texture is None else self.texture.uuid

    texture: PointerProperty(type=Texture_Collection, update=update_texture)
    use_custom_icon: BoolProperty(name="Brush Use Custom Icon")
    texture_uuid: StringProperty(name="UUID of linked texture")

    @property
    def icon_path(self) -> str:
        return IconPath.BRUSH

    @property
    def lib_path(self) -> str:
        return Paths.Data.BRUSH

    @property
    def bl_brush(self) -> BlBrush or None:
        return bpy.data.brushes.get(self.uuid, None)

    @property
    def bl_texture(self) -> BlBrush or None:
        return bpy.data.textures.get(self.texture_uuid, None)

    def select(self, context: Context) -> None:
        bl_brush = self.bl_brush
        if bl_brush is None:
            self.load(load_default=False, link=False)
            bl_brush = self.bl_brush
        set_ts_brush(context, bl_brush)

    def load(self, load_default: bool = False, link: bool = False) -> None:
        if load_default:
            filename = self.uuid + '.default.blend'
        else:
            filename = self.uuid + '.blend'
        global load_lib
        brush_libpath = self.lib_path(filename, as_path=False)
        with load_lib(brush_libpath, link=link, relative=False, assets_only=False) as (data_from, data_to):
            data_to.brushes = [self.uuid]

    def save(self, save_default: bool = False) -> None:
        if save_default:
            filename = self.uuid + '.default.blend'
        else:
            filename = self.uuid + '.blend'
        global write_lib
        brush_libpath = self.lib_path(filename, as_path=True)
        write_lib(str(brush_libpath), {self.id_data}, fake_user=True, compress=True)

    def reset(self) -> None:
        # Get BlBrush
        bl_brush = self.bl_brush
        if bl_brush is None:
            return

        # Remove BlBrush.
        bpy.data.brushes.remove(bl_brush)
        del bl_brush

        # Replace current brush state with default state.
        copyfile(self.lib_path(self.uuid + '.default.blend'),
                 self.lib_path(self.uuid + '.blend'))


class BrushPointer_Collection(PropertyGroup):
    data: PointerProperty(type=Brush_Collection)

class TexturePointer_Collection(PropertyGroup):
    data: PointerProperty(type=Texture_Collection)


# ----------------------------------------------------------------


class CategoryItem_Brush(CollectionItem, PropertyGroup):
    @property
    def icon_path(self) -> str:
        return IconPath.BRUSH

class CategoryItem_Texture(CollectionItem, PropertyGroup):
    # This has access to UUID, name
    @property
    def icon_path(self) -> str:
        return IconPath.TEXTURE


class Category(UUUIDHolder, IconHolder):
    name: StringProperty()
    load_on_boot: BoolProperty(name="Load on Boot", description="Load Category Brushes On Blender Boot", default=False)

    @property
    def item_ids(self) -> tuple[str]:
        return tuple(item.uuid for item in self.x_items) # if item.data is not None)

    @property
    def item_indices(self) -> tuple[int]:
        return tuple(cached_indices.get(item.uuid, -1) for item in self.x_items) # if item.data is not None)

    def add_item(self, item_data: Brush_Collection | Texture_Collection) -> BrushPointer_Collection | TexturePointer_Collection:
        if not isinstance(item_data, (Brush_Collection, Texture_Collection)):
            raise TypeError("Invalid argument type, expected a Brush_Collection or Texture_Collection type")
        new_item = self.x_items.add()
        # new_item.data = item_data
        new_item.uuid = item_data.uuid
        return new_item

    def add_items(self, item_data_list: list[str] | list[Brush_Collection] | list[Texture_Collection]) -> list[BrushPointer_Collection] | list[TexturePointer_Collection]:
        return [self.add_item(item_data) for item_data in item_data_list]

    def remove_item(self, index_or_uuid: int | str) -> None:
        if not isinstance(index_or_uuid, (int, str)):
            raise TypeError("Invalid argument type, expected an integer (index) or a string (UUID)")
        remove_item(self.x_items, index_or_uuid)

    def remove_items(self, item_uuids: set[str] | list[Brush_Collection] | list[Texture_Collection]) -> None:
        ''' Input must be an array like of item UUIDs. '''
        if isinstance(item_uuids, (list, tuple)):
            if not isinstance(item_uuids[0], str):
                if hasattr(item_uuids[0], 'uuid'):
                    item_uuids = {item.uuid for item in item_uuids}
                else:
                    raise TypeError("Invalid argument type, expected an array of strins (UUIDs) or Items")
            else:
                item_uuids = set(item_uuids)
        remove_item = self.x_items.remove
        for index, cat_item in reversed(list(enumerate(self.x_items))):
            if cat_item.uuid in item_uuids:
                item_uuids.remove(cat_item.uuid)
                remove_item(index)
                if len(item_uuids) == 0:
                    break

    def clear(self):
        self.x_items.clear()


class BrushCat_Collection(Category, PropertyGroup):
    x_items: CollectionProperty(type=CategoryItem_Brush)

    # @property
    # def items(self) -> list[Brush_Collection]:
    #     return [item.data for item in self.x_items if item.data is not None]

    def get_items(self, addon_data: 'AddonDataByMode') -> list[Brush_Collection]:
        get_brush = addon_data.get_brush
        return [get_brush(item.uuid) for item in self.x_items]

    @property
    def icon_path(self) -> str:
        return IconPath.CAT_BRUSH

    def load_default(self) -> None:
        {item.load(load_default=True) for item in self.items}

    def save_default(self) -> None:
        {item.save(save_default=True) for item in self.items}


class TextureCat_Collection(Category, PropertyGroup):
    x_items: CollectionProperty(type=CategoryItem_Texture)

    # @property
    # def items(self) -> list[Texture_Collection]:
    #     return [item.data for item in self.x_items if item.data is not None]

    def get_items(self, addon_data: 'AddonDataByMode') -> list[Texture_Collection]:
        get_texture = addon_data.get_texture
        return [get_texture(item.uuid) for item in self.x_items]

    @property
    def icon_path(self) -> str:
        return IconPath.CAT_TEXTURE


# ----------------------------------------------------------------


class UIProps(PropertyGroup):
    ui_active_item_color: FloatVectorProperty(size=4, default=(0.15, 0.6, 1.0, 1.0), subtype='COLOR')
    ui_active_section: EnumProperty(
        name="Active Section",
        items=(
            ('LIBS', 'Libraries', "", 'FILE_BLEND', 0),
            ('CATS', 'Categories', "", 'ASSET_MANAGER', 1)
        )
    )

    @property
    def ui_in_libs_section(self) -> bool: return self.ui_active_section == 'LIBS'

    @property
    def ui_in_cats_section(self) -> bool: return self.ui_active_section == 'CATS'

    # ----------------------------

    ui_context_mode: EnumProperty(
        items=(
            ('sculpt', 'Sculpt', '', 'SCULPTMODE_HLT', 0),
            ('texture_paint', 'Texture Paint', '', 'TEXTURE_DATA', 1),
            ('gpencil_paint', 'Grease Pencil', '', 'OUTLINER_DATA_GP_LAYER', 2),
        )
    )

    ui_context_item: EnumProperty(
        name="Item-Type Context",
        items=(
            ('BRUSH', 'Brushes', ""),
            ('TEXTURE', 'Textures', "")
        ),
        default='BRUSH'
    )

    @property
    def is_ctx_brush(self) -> bool: return self.ui_context_item == 'BRUSH'

    @property
    def is_ctx_texture(self) -> bool: return self.ui_context_item == 'TEXTURE'


class AddonDataByMode(PropertyGroup):

    def _get_item_index(self, uuid: str) -> int:
        # Check if cache is available.
        global cached_indices
        if cached_indices == {}:
            self._update_indices()
        return cached_indices.get(uuid, -1)

    def _update_indices(self):
        global cached_indices
        cached_indices.clear()
        items = {}
        for idx, brush in enumerate(self.brushes):
            items[brush.uuid] = idx
        for idx, texture in enumerate(self.textures):
            items[texture.uuid] = idx
        cached_indices = items

    # ----------------------------

    libraries: CollectionProperty(type=Library_Collection)
    brushes: CollectionProperty(type=Brush_Collection)
    textures: CollectionProperty(type=Texture_Collection)
    brush_cats: CollectionProperty(type=BrushCat_Collection)
    texture_cats: CollectionProperty(type=TextureCat_Collection)


    # ----------------------------
    # --- UI management ---
    @property
    def selected_brushes(self: ADM) -> list[Brush_Collection]:
        return [br for br in self.brushes if br.selected]

    @property
    def selected_textures(self: ADM) -> list[Texture_Collection]:
        return [tex for tex in self.textures if tex.selected]


    # ----------------------------
    # Libraries.

    active_library_index: IntProperty(default=-1)

    @property
    def active_library(self: ADM) -> Library_Collection:
        items = self.libraries
        index = self.active_library_index
        if index < 0 or index >= len(items):
            return None
        return items[index]


    def select_library(self: ADM, lib_index_or_uuid: int | str) -> None:
        self.active_library_index = lib_index_or_uuid if isinstance(lib_index_or_uuid, int) else get_item_index(self.libraries, lib_index_or_uuid)

    def get_library(self: ADM, index_or_uuid: int | str) -> Library_Collection:
        return get_item(self.libraries, index_or_uuid)

    def remove_library(self: ADM, index_or_uuid: int = -1) -> None:
        if not isinstance(index_or_uuid, (int, str)):
            raise ValueError("Library input should be an integer (index) or a string (UUID)")

        index = index_or_uuid if isinstance(index_or_uuid, int) else get_item_index(self.libraries, index_or_uuid)
        if index < 0:
            index = self.active_library_index
        lib = self.get_library(index)
        if lib is None:
            return

        brush_uuids = {brush.uuid for brush in lib.brushes}
        texture_uuids = {texture.uuid for texture in lib.textures}

        for idx, brush in reversed(list(enumerate(self.brushes))):
            if brush.uuid in brush_uuids:
                self.remove_brush(idx)
            elif brush.texture_uuid in texture_uuids:
                brush.texture_uuid = ''

        for idx, texture in reversed(list(enumerate(self.textures))):
            if texture.uuid in texture_uuids:
                self.remove_texture(idx)

        for cat in self.brush_cats:
            for idx, item in reversed(list(enumerate(cat.x_items))):
                if item.uuid in brush_uuids:
                    cat.remove_item(idx)

        for cat in self.texture_cats:
            for idx, item in reversed(list(enumerate(cat.x_items))):
                if item.uuid in texture_uuids:
                    cat.remove_item(idx)

        self.libraries.remove(index)

        # Update cache.
        self._update_indices()

    # ----------------------------
    # Categories.

    def get_active_category(self: ADM, type: str) -> BrushCat_Collection | TextureCat_Collection | None:
        if type == 'BRUSH':
            return self.active_brush_cat
        elif type == 'TEXTURE':
            return self.active_texture_cat
        return None

    active_brush_cat_index: IntProperty(default=-1)
    active_texture_cat_index: IntProperty(default=-1)

    @property
    def active_brush_cat(self: ADM) -> BrushCat_Collection:
        return get_item_at_index(self.brush_cats, self.active_brush_cat_index)

    @property
    def active_texture_cat(self: ADM) -> TextureCat_Collection:
        return get_item_at_index(self.texture_cats, self.active_texture_cat_index)

    @property
    def active_brush_cat_items(self: ADM) -> BrushCat_Collection:
        if brush_cat := self.active_brush_cat:
            return [self.get_brush(uuid) for uuid in brush_cat.item_ids]
        return []

    @property
    def active_texture_cat_items(self: ADM) -> TextureCat_Collection:
        if texture_cat := self.active_texture_cat:
            return [self.get_brush(uuid) for uuid in texture_cat.item_ids]
        return []

    def _new_cat(self: ADM, cat_collection: BrushCat_Collection | TextureCat_Collection, name: str | None = None) -> Category:
        new_cat: BrushCat_Collection | TextureCat_Collection = cat_collection.add()
        new_cat.generate_uuid()
        new_cat.name = name if name is not None else 'New Category %i' % len(self.brush_cats)
        return new_cat

    def new_brush_cat(self: ADM, name: str | None = None) -> BrushCat_Collection:
        self.active_brush_cat_index = len(self.brush_cats)
        return self._new_cat(self.brush_cats, name)

    def new_texture_cat(self: ADM, name: str | None = None) -> TextureCat_Collection:
        self.active_texture_cat_index = len(self.texture_cats)
        return self._new_cat(self.texture_cats, name)

    def select_brush_category(self: ADM, cat_index_or_uuid: int | str | BrushCat_Collection) -> None:
        if isinstance(cat_index_or_uuid, BrushCat_Collection):
            return self.select_brush_category(cat_index_or_uuid.uuid)
        if isinstance(cat_index_or_uuid, str):
            return self.select_brush_category(get_item_index(self.brush_cats, cat_index_or_uuid))
        if not isinstance(cat_index_or_uuid, int):
            return
        if cat_index_or_uuid < 0 or cat_index_or_uuid >= len(self.brush_cats):
            return
        self.active_brush_cat_index = cat_index_or_uuid

    def select_texture_category(self: ADM, cat_index_or_uuid: int | str | TextureCat_Collection) -> None:
        if isinstance(cat_index_or_uuid, TextureCat_Collection):
            return self.select_texture_category(cat_index_or_uuid.uuid)
        if isinstance(cat_index_or_uuid, str):
            return self.select_texture_category(get_item_index(self.texture_cats, cat_index_or_uuid))
        if not isinstance(cat_index_or_uuid, int):
            return
        if cat_index_or_uuid < 0 or cat_index_or_uuid >= len(self.texture_cats):
            return
        self.active_texture_cat_index = cat_index_or_uuid


    def get_brush_cat(self: ADM, index_or_uuid: int | str):
        return get_item(self.brush_cats, index_or_uuid)

    def get_texture_cat(self: ADM, index_or_uuid: int | str):
        return get_item(self.brush_cats, index_or_uuid)


    def remove_brush_cat(self: ADM, cat: int | str):
        remove_item(self.brush_cats, cat)
        cat_count = len(self.brush_cats)
        if self.active_brush_cat_index <= cat_count:
            self.active_brush_cat_index = max(cat_count - 1, -1)

    def remove_texture_cat(self: ADM, cat: int | str):
        remove_item(self.texture_cats, cat)
        cat_count = len(self.texture_cats)
        if self.active_texture_cat_index <= cat_count:
            self.active_texture_cat_index = max(cat_count - 1, -1)


    # ----------------------------
    # Brush/Texture Utilities.

    def get_brush_uuid(self: ADM, index: int) -> str:
        return get_item_at_index(self.brushes, index).uuid

    def get_texture_uuid(self: ADM, index: int) -> str:
        return get_item_at_index(self.textures, index).uuid

    def get_brush_index(self: ADM, uuid: str) -> int:
        return self._get_item_index(uuid)

    def get_texture_index(self: ADM, uuid: str) -> int:
        return self._get_item_index(uuid)

    def get_brush(self: ADM, uuid: str) -> Brush_Collection:
        if not uuid:
            return None
        if (brush_index := self.get_brush_index(uuid)) != -1:
            return self.brushes[brush_index]
        return next(brush for brush in self.brushes if brush.uuid == uuid)

    def get_texture(self: ADM, uuid: str) -> Texture_Collection:
        if not uuid:
            return None
        if (texture_index := self.get_texture_index(uuid)) != -1:
            return self.textures[texture_index]
        return next(tex for tex in self.textures if tex.uuid == uuid)

    def get_blbrush(self: ADM, uuid: str) -> BlBrush:
        return bpy.data.brushes.get(uuid, None)

    def get_bltexture(self: ADM, uuid: str) -> BlTexture:
        return bpy.data.textures.get(uuid, None)

    # ----------------------------
    # Brush/Texture Management.

    active_brush_index: IntProperty(default=-1)
    active_texture_index: IntProperty(default=-1)

    @property
    def active_brush(self: ADM) -> Brush_Collection:
        return get_item_at_index(self.brushes, self.active_brush_index)

    @active_brush.setter
    def active_brush(self: ADM, brush: int | str | Brush_Collection):
        if isinstance(brush, Brush_Collection):
            self.active_brush = brush.uuid
        elif isinstance(brush, str):
            self.active_brush = self._get_item_index(brush)
        elif isinstance(brush, int):
            self.active_brush_index = brush

    @property
    def active_texture(self: ADM) -> Texture_Collection:
        return get_item_at_index(self.textures, self.active_texture_index)

    @active_texture.setter
    def active_texture(self: ADM, texture: int | str | Texture_Collection):
        if isinstance(texture, Texture_Collection):
            self.active_texture = texture.uuid
        elif isinstance(texture, str):
            self.active_texture = self._get_item_index(texture)
        elif isinstance(texture, int):
            self.active_texture = texture


    def select_brush(self: ADM, context: Context, index_or_uuid: int | str) -> BlBrush:
        # Resolve brush UUID.
        brush_uuid = index_or_uuid if isinstance(index_or_uuid, str) else self.get_brush_uuid(index_or_uuid)
        if not brush_uuid:
            return None

        # brush_index = get_item_index(self.brushes, index_or_uuid) if isinstance(index_or_uuid, str) else index_or_uuid
        self.active_brush_index = self.get_brush_index(brush_uuid) if isinstance(index_or_uuid, str) else index_or_uuid

        # The brush exists!
        if bl_brush := bpy.data.brushes.get(brush_uuid, None):
            # Set active brush.
            set_ts_brush(context, bl_brush)
            return bl_brush

        # Load the brush from BM library.
        with bpy.data.libraries.load(Paths.Data.BRUSH(brush_uuid + '.blend'), link=False) as (data_from, data_to):
            data_to.brushes = [brush_uuid] # data_from.brushes
        bl_brush = bpy.data.brushes[brush_uuid]
        bl_brush.use_fake_user = False # Make sure it does not use fake user so Blender free it on quit.

        # Check if brush has a texture that we need to import.
        texture_uuid = bl_brush['texture_uuid']
        if texture_uuid != '':
            # Load the texture from BM library.
            with bpy.data.libraries.load(Paths.Data.TEXTURE(texture_uuid + '.blend'), link=False) as (data_from, data_to):
                data_to.textures = [texture_uuid]
                data_to.images = data_from.images
            bl_texture = bpy.data.textures[texture_uuid]
            bl_texture.use_fake_user = False # Make sure it does not use fake user so Blender free it on quit.

            # Ensure texture is asigned to the brush.
            bl_brush.texture_slot.texture = bl_texture

        # Set active brush.
        set_ts_brush(context, bl_brush)
        return bl_brush

    def select_texture(self: ADM, context: Context, index_or_uuid: int | str) -> BlTexture:
        # Resolve brush UUID.
        tex_uuid = index_or_uuid if isinstance(index_or_uuid, str) else self.get_texture_uuid(index_or_uuid)
        if not tex_uuid:
            return None

        # tex_index = get_item_index(self.textures, index_or_uuid) if isinstance(index_or_uuid, str) else index_or_uuid
        self.active_texture_index = self.get_texture_index(tex_uuid) if isinstance(index_or_uuid, str) else index_or_uuid

        # The brush exists!
        if bl_texture := bpy.data.textures.get(tex_uuid, None):
            return bl_texture

        # Load the texture from BM library.
        with bpy.data.libraries.load(Paths.Data.TEXTURE(tex_uuid + '.blend'), link=False) as (data_from, data_to):
            data_to.textures = [tex_uuid]
            data_to.images = data_from.images
        bl_texture = bpy.data.textures[tex_uuid]
        bl_texture.use_fake_user = False # Make sure it does not use fake user so Blender free it on quit.

        # Get active brush.
        bl_brush = self.active_brush.bl_brush

        # Ensure texture is asigned to the brush.
        bl_brush.texture_slot.texture = bl_texture

        # Set active brush.
        set_ts_brush(context, bl_brush)
        return bl_brush


    def remove_brush(self: ADM, brush: int | str):
        remove_item(self.brushes, brush)

    def remove_texture(self: ADM, texture: int | str):
        remove_item(self.textures, texture)


    # -----------------------------------------------
    # Utility methods.

    def initialize(self: ADM, ctx_mode: str = 'sculpt') -> None:
        self._update_indices()
        self.load_brushes(ctx_mode)

    def load_brushes(self: ADM, ctx_mode: str = 'sculpt') -> None:
        '''
        if len(self.brushes) == 0 or len(self.brush_cats) == 0 or len([True for cat in self.brush_cats if cat.uuid == 'DEFAULT']) == 0:
            cat: bm_types.BrushCategory = self.brush_cats.add()
            cat.uuid = 'DEFAULT'
            cat.name = 'Default Brushes'
            data_brushes = bpy.data.brushes
            for br_name in get_brush_names_by_ctx_mode[ctx_mode]:
                if brush := data_brushes.get(br_name, None):
                    uuid = brush['uuid'] = 'DEFAULT_' + br_name
                    cat.add_item(uuid)

            self._update_indices()
        '''
        from .ops.op_library_actions import ImportBuiltinLibraries
        ImportBuiltinLibraries.run()
        return

        from dataclasses import dataclass

        @dataclass
        class FakeAddLibraryOp:
            filepath: str
            create_category: bool
            custom_uuid: str

        import glob
        from os.path import splitext
        for filepath in glob.glob(str(Paths.LIB / '*.blend')):
            uuid, ext = splitext(basename(filepath))

            lib = self.libraries.add()
            brush_cat = self.brush_cats.add()
            brush_cat.name = uuid
            brush_cat.uuid = uuid
            texture_cat = self.texture_cats.add()
            texture_cat.name = uuid
            texture_cat.uuid = uuid

            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                data_to.brushes = data_from.brushes
                data_to.textures = data_from.textures
                data_to.images = data_from.images

            for texture in data_to.textures:
                uuid = uuid4().hex
                texture['uuid'] = uuid

                tex = self.textures.add()

            for brush in data_to.brushes:
                uuid = uuid4().hex
                brush['uuid'] = uuid
                brush['texture_uuid'] = brush.texture['uuid'] if brush.texture is not None else ''


        return

        # TODO: Tagged for removal.
        if True:
            # Import from single (item) library files by UUID.
            for cat in self.brush_cats:
                if not cat.load_on_boot:
                    continue
                for item in cat.items:
                    item.load()

        else:
            # If libraries items have UUIDs as names.

            rel_brush_id_n_name = {item.uuid: item.name for cat in self.brush_cats if not cat.load_on_boot for item in cat.items}
            brush_uuids = set(rel_brush_id_n_name.keys())
            rel_lib_n_brushes: dict[str, list[str]] = defaultdict(list)

            for lib in self.libraries:
                if not lib.is_valid:
                    continue
                brushes_ids_to_load_from_lib = brush_uuids.intersection(lib.brushes_ids)
                rel_lib_n_brushes[lib.filepath] = {rel_brush_id_n_name[brush_id] for brush_id in brushes_ids_to_load_from_lib}

            for libpath, brushes in rel_lib_n_brushes.items():
                # link all objects starting with 'A'
                with bpy.data.libraries.load(libpath, link=True) as (data_from, data_to):
                    data_to.brushes = [name for name in data_from.brushes if name in brushes]


    def save_brushes(self: ADM, ctx_mode: str = 'sculpt') -> None:
        for brush in self.brushes:
            brush.save()


class AddonData(PropertyGroup):
    ctx_modes = ('sculpt', 'texture_paint', 'gpencil_paint')

    sculpt: PointerProperty(type=AddonDataByMode)
    texture_paint: PointerProperty(type=AddonDataByMode)
    gpencil_paint: PointerProperty(type=AddonDataByMode)

    def initialize(self) -> None:
        global load_lib
        global write_lib
        load_lib = bpy.data.libraries.load
        write_lib = bpy.data.libraries.write

        for ctx_mode in self.ctx_modes:
            # NOTE: maybe would be needed to pass the ctx_mode and add another level to the cached_indices dict.
            getattr(self, ctx_mode).initialize()

    def load_brushes(self) -> None:
        for ctx_mode in self.ctx_modes:
            getattr(self, ctx_mode).load_brushes(ctx_mode)

    def save_brushes(self) -> None:
        for ctx_mode in self.ctx_modes:
            getattr(self, ctx_mode).save_brushes(ctx_mode)



def register():
    WM.brush_manager_ui = PointerProperty(type=UIProps)

    # BlBrush.name = StringProperty(name="Brush Name", description="Override of brush name by Brush Manager")
    # BlTexture.name = StringProperty(name="Texture Name", description="Override of texture name by Brush Manager")

    BlBrush.bm_data = PointerProperty(type=Brush_Collection)
    BlTexture.bm_data = PointerProperty(type=Texture_Collection)

def unregister():
    del WM.brush_manager_ui
