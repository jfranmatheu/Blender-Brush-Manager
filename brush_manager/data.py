import bpy
from bpy.types import PropertyGroup, Context, WindowManager as WM
from bpy.props import StringProperty, PointerProperty, EnumProperty, IntProperty, CollectionProperty, BoolProperty, FloatVectorProperty
from gpu.types import GPUTexture

from os.path import basename, exists, isfile
from uuid import uuid4
from collections import defaultdict

from .paths import Paths
from .icons import get_preview, get_gputex


IconPath = Paths.Data.Icons


lib_items_cache: dict[str, set[str]] = {}


def get_item_at_index(list, index: int):
    if index < 0 or index >= len(list):
        return None
    return list[index]

def remove_item(list: list, item: int | str):
        if isinstance(item, int):
            list.remove(item)
        elif isinstance(item, str):
            for idx, _item in enumerate(list):
                if _item.uuid == item:
                    return remove_item(idx)


class IconHolder:
    @property
    def icon_path(self) -> IconPath: pass
    @property
    def icon_id(self) -> int: return get_preview(self.uuid, self.icon_path(self.uuid + '.png'))
    @property
    def icon_gputex(self) -> GPUTexture: return get_gputex(self.uuid, self.icon_path(self.uuid + '.png'))


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
        self.name = basename(self.filepath)[:-6]

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


# ----------------------------------------------------------------


class Item(UUUIDHolder, IconHolder):
    name: StringProperty()
    type: StringProperty()

class Brush_Collection(Item, PropertyGroup):
    use_custom_icon: BoolProperty(name="Brush Use Custom Icon")
    texture_uuid: StringProperty(name="UUID of linked texture")

    @property
    def icon_path(self) -> str:
        return IconPath.BRUSH

class Texture_Collection(Item, PropertyGroup):
    format: StringProperty()

    @property
    def icon_path(self) -> str:
        return IconPath.TEXTURE


# ----------------------------------------------------------------


class CategoryItem(CollectionItem, PropertyGroup):
    pass


class Category(UUUIDHolder, IconHolder):
    name: StringProperty()
    items: CollectionProperty(type=CategoryItem)
    load_on_boot: BoolProperty(name="Load on Boot", description="Load Category Brushes On Blender Boot", default=False)

    def add_item(self, uuid: str) -> CategoryItem:
        new_item: CategoryItem = self.items.add()
        new_item.uuid = uuid
        return new_item

    def remove_item(self, item: int | str) -> None:
        remove_item(self.items, item)

    def clear(self):
        self.items.clear()

class BrushCat_Collection(Category, PropertyGroup):
    @property
    def icon_path(self) -> str:
        return IconPath.CAT_BRUSH

class TextureCat_Collection(Category, PropertyGroup):
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

    ui_item_type_context: EnumProperty(
        name="Item-Type Context",
        items=(
            ('BRUSH', 'Brushes', ""),
            ('TEXTURE', 'Textures', "")
        ),
        default='BRUSH'
    )

    @property
    def ui_in_brush_context(self) -> bool: return self.ui_item_type_context == 'BRUSH'

    @property
    def ui_in_texture_context(self) -> bool: return self.ui_item_type_context == 'TEXTURE'


class AddonData(PropertyGroup):
    cache_items = {}

    libraries: CollectionProperty(type=Library_Collection)
    brushes: CollectionProperty(type=Brush_Collection)
    textures: CollectionProperty(type=Texture_Collection)
    brush_cats: CollectionProperty(type=BrushCat_Collection)
    texture_cats: CollectionProperty(type=TextureCat_Collection)

    # ----------------------------

    active_library_index: IntProperty(default=-1)

    @property
    def active_library(self) -> Library_Collection:
        items = self.libraries
        index = self.active_library_index
        if index < 0 or index >= len(items):
            return None
        return items[index]

    # ----------------------------

    def get_active_category(self, type: str) -> BrushCat_Collection | TextureCat_Collection | None:
        if type == 'BRUSH':
            return self.active_brush_cat
        elif type == 'TEXTURE':
            return self.active_texture_cat
        return None

    active_brush_cat_index: IntProperty(default=-1)
    active_texture_cat_index: IntProperty(default=-1)

    @property
    def active_brush_cat(self) -> BrushCat_Collection:
        items = self.brush_cats
        index = self.active_brush_cat_index
        if index < 0 or index >= len(items):
            return None
        return items[index]

    @property
    def active_texture_cat(self) -> TextureCat_Collection:
        items = self.texture_cats
        index = self.active_texture_cat_index
        if index < 0 or index >= len(items):
            return None
        return items[index]

    # ----------------------------

    active_item_index: IntProperty(default=-1)

    def active_item(self):
        if self.ui_in_libs_section:
            active_lib = self.active_library
            if self.ui_in_brush_context:
                items = active_lib.brushes
            elif self.ui_in_texture_context:
                items = active_lib.textures
            else:
                return None
        elif self.ui_in_cats_section:
            if self.ui_in_brush_context:
                items = self.active_brush_cat.items
            elif self.ui_in_texture_context:
                items = self.active_texture_cat.items
            else:
                return None
        else:
            return None
        if items is None:
            return None
        index = self.active_item_index
        if index < 0 or index >= len(items):
            return None
        return items[index]

    # ----------------------------

    def get_library(self, index: int):
        return get_item_at_index(self.libraries, index)

    def remove_library(self, index: int = -1):
        if index < 0:
            index = self.active_library_index
        lib: Library_Collection = self.get_library(index)
        if lib is None:
            return

        brush_uuids = {brush.uuid for brush in lib.brushes}
        texture_uuids = {texture.uuid for texture in lib.textures}

        for idx, brush in enumerate(reversed(self.brushes)):
            if brush.uuid in brush_uuids:
                self.remove_brush(idx)
            elif brush.texture_uuid in texture_uuids:
                brush.texture_uuid = ''

        for idx, texture in enumerate(reversed(self.textures)):
            if texture.uuid in texture_uuids:
                self.remove_texture(idx)

        for cat in self.brush_cats:
            for idx, item in enumerate(reversed(cat.items)):
                if item.uuid in brush_uuids:
                    cat.remove_item(idx)

        for cat in self.texture_cats:
            for idx, item in enumerate(reversed(cat.items)):
                if item.uuid in texture_uuids:
                    cat.remove_item(idx)

        self.libraries.remove(index)

    # ----------------------------

    def get_brush_cat(self, index: int):
        return get_item_at_index(self.brush_cats, index)

    def get_texture_cat(self, index: int):
        return get_item_at_index(self.texture_cats, index)

    def remove_brush_cat(self, cat: int | str):
        remove_item(self.brush_cats, cat)

    def remove_texture_cat(self, cat: int | str):
        remove_item(self.texture_cats, cat)

    # ----------------------------

    def get_brush_data(self, uuid: str) -> Brush_Collection:
        if not uuid:
            return None
        if brush := self.cache_items.get(uuid, None):
            return brush
        return next(brush for brush in self.brushes if brush.uuid == uuid)

    def get_texture_data(self, uuid: str) -> Texture_Collection:
        if not uuid:
            return None
        if texture := self.cache_items.get(uuid, None):
            return texture
        return next(tex for tex in self.textures if tex.uuid == uuid)


    def get_brush_uuid(self, index: int):
        return get_item_at_index(self.brushes, index).uuid

    def get_texture_uuid(self, index: int):
        return get_item_at_index(self.textures, index).uuid

    def remove_brush(self, brush: int | str):
        remove_item(self.brushes, brush)

    def remove_texture(self, texture: int | str):
        remove_item(self.textures, texture)
    

    # -----------------------------------------------

    def load_brushes(self) -> None:
        rel_brush_id_n_name = {item.uuid: item.name for cat in self.brush_cats if not cat.load_on_boort for item in cat.items}
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


def register():
    WM.brush_manager_ui = PointerProperty(type=UIProps)


def unregister():
    del WM.brush_manager_ui
