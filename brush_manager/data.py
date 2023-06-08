from bpy.types import PropertyGroup
from bpy.props import StringProperty, PointerProperty, EnumProperty, IntProperty, CollectionProperty, BoolProperty
from gpu.types import GPUTexture

from .paths import Paths
from .icons import get_preview, get_gputex


IconPath = Paths.Data.Icons



class UUID_Collection(PropertyGroup):
    uuid: StringProperty()


# ----------------------------------------------------------------


class Library_Collection(PropertyGroup):
    filepath : StringProperty()
    name : StringProperty()
    brushes: CollectionProperty(type=UUID_Collection)
    textures: CollectionProperty(type=UUID_Collection)


# ----------------------------------------------------------------


class Item:
    uuid: StringProperty()
    name: StringProperty()
    type: StringProperty()

    def icon_path(self) -> str: pass
    def icon_id(self) -> str | int: return get_preview(self.uuid)
    def icon_gputex(self) -> GPUTexture: return get_gputex(self.uuid, self.icon_path())

class Brush_Collection(Item, PropertyGroup):
    texture_uuid: StringProperty()

class Texture_Collection(Item, PropertyGroup):
    format: StringProperty()


# ----------------------------------------------------------------


class Category:
    uuid: StringProperty()
    name: StringProperty()
    items: CollectionProperty(type=UUID_Collection)

    def icon_path(self) -> str: raise NotImplementedError
    def icon_id(self) -> str | int: return get_preview(self.uuid)
    def icon_gputex(self) -> GPUTexture: return get_gputex(self.uuid, self.icon_path())

    def add_item(self, uuid: str) -> UUID_Collection:
        new_item: UUID_Collection = self.items.add()
        new_item.uuid = uuid
        return new_item

    def remove_item(self, uuid: str) -> None:
        for idx, item in enumerate(self.items):
            if item.uuid == uuid:
                self.items.remove(idx)
                break

    def clear(self):
        self.items.clear()

class BrushCat_Collection(Category, PropertyGroup):
    def icon_path(self) -> str: return IconPath.CAT_BRUSH(self.uuid)

class TextureCat_Collection(Category, PropertyGroup):
    def icon_path(self) -> str: return IconPath.CAT_TEXTURE(self.uuid)


# ----------------------------------------------------------------


class AddonData(PropertyGroup):
    ui_active_section: EnumProperty(
        name="Active Section",
        items=(
            ('LIBS', 'Libraries', ""),
            ('CATS', 'Categories', "")
        )
    )

    @property
    def ui_in_libs_section(self) -> bool: return self.active_section == 'LIBS'

    @property
    def ui_in_cats_section(self) -> bool: return self.active_section == 'CATS'

    # ----------------------------

    ui_item_type_context: EnumProperty(
        name="Item-Type Context",
        items=(
            ('BRUSH', 'Brushes', ""),
            ('TEXTURE', 'Textures', "")
        )
    )

    @property
    def ui_in_brush_context(self) -> bool: return self.ui_item_type_context == 'BRUSH'

    @property
    def ui_in_texture_context(self) -> bool: return self.ui_item_type_context == 'TEXTURE'

    # ----------------------------

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
